"""WebSocket handler for real-time chat with the research agent.

This module extracts WebSocket handling logic from web.py into a dedicated class
following the Single Responsibility Principle.
"""

import asyncio
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

from research_agent.agent import get_agent_options

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections for real-time chat.

    Encapsulates all WebSocket communication logic including:
    - Client lifecycle management
    - Message routing
    - Response streaming
    - Interrupt handling
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, websocket: WebSocket):
        """Initialize handler with WebSocket connection.

        Args:
            websocket: The FastAPI WebSocket connection
        """
        self._websocket = websocket
        self._client: ClaudeSDKClient | None = None
        self._session_id: int | None = None
        self._model = self.DEFAULT_MODEL
        self._response_task: asyncio.Task | None = None

    async def handle(self) -> None:
        """Main entry point - handle the WebSocket connection."""
        await self._websocket.accept()
        logger.info("WebSocket connected")

        try:
            await self._message_loop()
        except WebSocketDisconnect:
            pass
        finally:
            await self._cleanup()

    async def _message_loop(self) -> None:
        """Process incoming WebSocket messages."""
        while True:
            data = await self._websocket.receive_json()
            await self._route_message(data)

    async def _route_message(self, data: dict[str, Any]) -> None:
        """Route message to appropriate handler."""
        message_type = data.get("type", "")

        handlers = {
            "new_session": self._handle_new_session,
            "interrupt": self._handle_interrupt,
            "set_model": self._handle_set_model,
            "query": self._handle_query,
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(data)

    async def _handle_new_session(self, _data: dict[str, Any]) -> None:
        """Handle new session request."""
        logger.info("New session requested - destroying client")
        await self._cancel_response()
        await self._close_client()

    async def _handle_interrupt(self, _data: dict[str, Any]) -> None:
        """Handle interrupt request."""
        if self._client and self._response_task and not self._response_task.done():
            try:
                await self._client.interrupt()
            except Exception:
                pass
            await self._cancel_response()

    async def _handle_set_model(self, data: dict[str, Any]) -> None:
        """Handle model change request."""
        new_model = data.get("model", self.DEFAULT_MODEL)
        logger.info(f"Model changed to {new_model} - destroying client")
        self._model = new_model
        await self._close_client()

    async def _handle_query(self, data: dict[str, Any]) -> None:
        """Handle query request."""
        query = data.get("query", "")

        if not query:
            await self._send_error("Empty query")
            return

        try:
            # Execute task planning hook before agent processes
            await self._execute_task_planning_hook(query)

            await self._ensure_client()
            await self._client.query(query)
            self._response_task = asyncio.create_task(self._stream_response())
            await self._response_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            await self._send_error(str(e))

    async def _execute_task_planning_hook(self, query: str) -> None:
        """Execute the task planning hook to auto-create task plans.

        Args:
            query: The user's query text.
        """
        try:
            from research_agent.hooks import TaskPlanningHook

            hook = TaskPlanningHook()
            plan_created = await hook.execute(query, preserve_existing=True)

            if plan_created:
                # Notify frontend that tasks were auto-created
                await self._websocket.send_json({
                    "type": "tasks_updated",
                    "auto_created": True,
                })
        except Exception as e:
            # Don't fail the query if hook fails - just log it
            logger.warning(f"Task planning hook failed: {e}")

    async def _ensure_client(self) -> None:
        """Create client if needed, or reuse existing."""
        if self._client is None:
            logger.info(f"Creating new client for model {self._model}")
            options = get_agent_options(model=self._model)
            self._client = ClaudeSDKClient(options=options)
            await self._client.__aenter__()
            self._session_id = id(self._client)
            await self._send_session_info()
        else:
            logger.info(f"Reusing existing client (session_id={self._session_id})")

    async def _stream_response(self) -> None:
        """Stream agent response to WebSocket."""
        current_text = ""
        turn_cost = 0.0

        try:
            async for message in self._client.receive_response():
                await self._process_message(message)
                if isinstance(message, ResultMessage) and message.total_cost_usd:
                    turn_cost = message.total_cost_usd

            await self._send_done(turn_cost)
        except asyncio.CancelledError:
            await self._send_interrupted()
            raise

    async def _process_message(self, message: Any) -> None:
        """Process a single message from the agent."""
        if isinstance(message, AssistantMessage):
            await self._process_assistant_message(message)

    async def _process_assistant_message(self, message: AssistantMessage) -> None:
        """Process assistant message blocks."""
        for block in message.content:
            if isinstance(block, TextBlock):
                await self._send_text(block.text)
            elif isinstance(block, ToolUseBlock):
                await self._send_tool_use(block)
            elif isinstance(block, ToolResultBlock):
                await self._send_tool_result(block)

    async def _send_text(self, text: str) -> None:
        """Send text message."""
        await self._websocket.send_json({"type": "text", "content": text})

    async def _send_tool_use(self, block: ToolUseBlock) -> None:
        """Send tool use message."""
        await self._websocket.send_json({
            "type": "tool_use",
            "tool_name": block.name,
            "input": block.input,
        })

    async def _send_tool_result(self, block: ToolResultBlock) -> None:
        """Send tool result message."""
        content = self._extract_tool_content(block)
        await self._websocket.send_json({"type": "tool_result", "content": content})

    @staticmethod
    def _extract_tool_content(block: ToolResultBlock) -> str:
        """Extract text content from tool result block."""
        content = ""
        if block.content:
            for item in block.content:
                if hasattr(item, "text"):
                    content += item.text
        return content

    async def _send_session_info(self) -> None:
        """Send session info to client."""
        await self._websocket.send_json({
            "type": "session_id",
            "session_id": str(self._session_id),
            "model": self._model,
        })

    async def _send_done(self, cost: float) -> None:
        """Send done message."""
        await self._websocket.send_json({"type": "done", "cost": cost})

    async def _send_interrupted(self) -> None:
        """Send interrupted message."""
        await self._websocket.send_json({"type": "interrupted"})

    async def _send_error(self, message: str) -> None:
        """Send error message."""
        await self._websocket.send_json({"type": "error", "message": message})

    async def _cancel_response(self) -> None:
        """Cancel ongoing response task."""
        if self._response_task and not self._response_task.done():
            self._response_task.cancel()
            try:
                await self._response_task
            except asyncio.CancelledError:
                pass

    async def _close_client(self) -> None:
        """Close the SDK client."""
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None
            self._session_id = None

    async def _cleanup(self) -> None:
        """Clean up resources on disconnect."""
        await self._cancel_response()
        await self._close_client()


async def handle_websocket(websocket: WebSocket) -> None:
    """Convenience function to handle a WebSocket connection.

    Args:
        websocket: The FastAPI WebSocket connection
    """
    handler = WebSocketHandler(websocket)
    await handler.handle()
