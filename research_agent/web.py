#!/usr/bin/env python3
"""Web UI for the Investment Research Agent.

A simple FastAPI-based web interface for interacting with the research agent.
Supports message queueing and interruption.

Usage:
    python -m research_agent.web

Then open http://localhost:8000 in your browser.
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

from research_agent.agent import get_agent_options

app = FastAPI(title="Investment Research Agent")

# Store active sessions
sessions: dict[str, ClaudeSDKClient] = {}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Research Agent</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: #16213e;
            padding: 1rem 2rem;
            border-bottom: 1px solid #0f3460;
        }

        header h1 {
            font-size: 1.5rem;
            color: #e94560;
        }

        header p {
            color: #888;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }

        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
            width: 100%;
            margin: 0 auto;
            padding: 1rem;
        }

        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: #16213e;
            border-radius: 8px;
            margin-bottom: 1rem;
            min-height: 400px;
            max-height: calc(100vh - 250px);
        }

        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 8px;
            line-height: 1.6;
        }

        .message.user {
            background: #0f3460;
            margin-left: 2rem;
        }

        .message.assistant {
            background: #1a1a2e;
            border: 1px solid #0f3460;
            margin-right: 2rem;
        }

        .message.system {
            background: #2d132c;
            border: 1px solid #e94560;
            text-align: center;
            font-size: 0.9rem;
            color: #e94560;
        }

        .message.tool {
            background: #1e3a5f;
            border: 1px solid #4a9eff;
            font-size: 0.9rem;
        }

        .message.queued {
            background: #2d2d44;
            border: 1px dashed #666;
            opacity: 0.7;
        }

        .message-label {
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .message h2 {
            color: #e94560;
            font-size: 1.1rem;
            margin: 1rem 0 0.5rem 0;
        }

        .message h2:first-child {
            margin-top: 0;
        }

        .message p {
            margin-bottom: 0.75rem;
        }

        .message ul, .message ol {
            margin-left: 1.5rem;
            margin-bottom: 0.75rem;
        }

        .message li {
            margin-bottom: 0.25rem;
        }

        .message code {
            background: #0f3460;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }

        .message pre {
            background: #0f3460;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            margin-bottom: 0.75rem;
        }

        .message pre code {
            background: none;
            padding: 0;
        }

        #input-container {
            display: flex;
            gap: 0.5rem;
        }

        #query-input {
            flex: 1;
            padding: 1rem;
            border: 1px solid #0f3460;
            border-radius: 8px;
            background: #16213e;
            color: #eee;
            font-size: 1rem;
            resize: none;
            min-height: 60px;
        }

        #query-input:focus {
            outline: none;
            border-color: #e94560;
        }

        #query-input::placeholder {
            color: #666;
        }

        button {
            padding: 1rem 2rem;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #ff6b6b;
        }

        button:disabled {
            background: #444;
            cursor: not-allowed;
        }

        #stop-btn {
            background: #ff9800;
            display: none;
        }

        #stop-btn:hover {
            background: #ffb74d;
        }

        #stop-btn.visible {
            display: block;
        }

        #status {
            text-align: center;
            padding: 0.5rem;
            color: #888;
            font-size: 0.85rem;
        }

        .status-connected {
            color: #4ade80 !important;
        }

        .status-error {
            color: #e94560 !important;
        }

        .status-processing {
            color: #ff9800 !important;
        }

        .cost-info {
            font-size: 0.8rem;
            color: #888;
            margin-top: 0.5rem;
            text-align: right;
        }

        .controls {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .controls button {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            background: #0f3460;
        }

        .controls button:hover {
            background: #1a4a7a;
        }

        .typing-indicator {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #1a1a2e;
            border-radius: 8px;
            color: #888;
        }

        .typing-indicator span {
            animation: blink 1.4s infinite both;
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes blink {
            0%, 80%, 100% { opacity: 0; }
            40% { opacity: 1; }
        }

        .queue-indicator {
            font-size: 0.8rem;
            color: #ff9800;
            margin-top: 0.25rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>Investment Research Agent</h1>
        <p>Conversational research assistant for institutional investors</p>
    </header>

    <main>
        <div class="controls">
            <button onclick="newSession()">New Session</button>
            <button onclick="clearChat()">Clear Chat</button>
        </div>

        <div id="chat-container"></div>

        <div id="input-container">
            <textarea
                id="query-input"
                placeholder="Ask a research question... (Press Enter to send, Shift+Enter for new line)"
                rows="2"
            ></textarea>
            <button id="send-btn" onclick="sendMessage()">Send</button>
            <button id="stop-btn" onclick="stopGeneration()">Stop</button>
        </div>

        <div id="status">Connecting...</div>
        <div id="queue-status" class="queue-indicator"></div>
    </main>

    <script>
        let ws = null;
        let sessionId = null;
        let totalCost = 0;
        let isProcessing = false;
        let messageQueue = [];

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                updateStatus('Connected', 'status-connected');
                document.getElementById('send-btn').disabled = false;
            };

            ws.onclose = () => {
                updateStatus('Disconnected - Reconnecting...', 'status-error');
                document.getElementById('send-btn').disabled = true;
                setTimeout(connect, 2000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                updateStatus('Connection error', 'status-error');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
        }

        function updateStatus(text, className) {
            const status = document.getElementById('status');
            status.textContent = text;
            status.className = className || '';
        }

        function updateQueueStatus() {
            const queueStatus = document.getElementById('queue-status');
            if (messageQueue.length > 0) {
                queueStatus.textContent = `${messageQueue.length} message${messageQueue.length > 1 ? 's' : ''} queued`;
            } else {
                queueStatus.textContent = '';
            }
        }

        function handleMessage(data) {
            const container = document.getElementById('chat-container');

            // Remove typing indicator if present
            const typingEl = document.getElementById('typing-indicator');
            if (typingEl) typingEl.remove();

            if (data.type === 'session_id') {
                sessionId = data.session_id;
                return;
            }

            if (data.type === 'text') {
                // Find or create assistant message
                let msgEl = document.getElementById('current-response');
                if (!msgEl) {
                    msgEl = document.createElement('div');
                    msgEl.id = 'current-response';
                    msgEl.className = 'message assistant';
                    msgEl.innerHTML = '<div class="message-label">Assistant</div><div class="content"></div>';
                    container.appendChild(msgEl);
                }

                const contentEl = msgEl.querySelector('.content');
                contentEl.innerHTML = formatMarkdown(data.content);
                container.scrollTop = container.scrollHeight;
            }

            if (data.type === 'tool_use') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message tool';
                msgEl.innerHTML = `
                    <div class="message-label">Tool: ${data.tool_name}</div>
                    <div class="content">${data.tool_name === 'generate_report' ? 'Generating research report...' : JSON.stringify(data.input, null, 2)}</div>
                `;
                container.appendChild(msgEl);
                container.scrollTop = container.scrollHeight;
            }

            if (data.type === 'tool_result') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message tool';
                msgEl.innerHTML = `
                    <div class="message-label">Tool Result</div>
                    <div class="content">${formatMarkdown(data.content)}</div>
                `;
                container.appendChild(msgEl);
                container.scrollTop = container.scrollHeight;
            }

            if (data.type === 'interrupted') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message system';
                msgEl.textContent = 'Generation stopped';
                container.appendChild(msgEl);
                finishProcessing();
            }

            if (data.type === 'done') {
                // Clear current response ID so next response creates new element
                const currentEl = document.getElementById('current-response');
                if (currentEl) currentEl.id = '';

                if (data.cost) {
                    totalCost += data.cost;
                    const costEl = document.createElement('div');
                    costEl.className = 'cost-info';
                    costEl.textContent = `Turn: $${data.cost.toFixed(4)} | Session: $${totalCost.toFixed(4)}`;
                    container.appendChild(costEl);
                }

                container.scrollTop = container.scrollHeight;
                finishProcessing();
            }

            if (data.type === 'error') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message system';
                msgEl.textContent = 'Error: ' + data.message;
                container.appendChild(msgEl);
                finishProcessing();
            }
        }

        function finishProcessing() {
            isProcessing = false;
            document.getElementById('stop-btn').classList.remove('visible');
            updateStatus('Connected', 'status-connected');

            // Process next queued message if any
            if (messageQueue.length > 0) {
                const nextQuery = messageQueue.shift();
                updateQueueStatus();

                // Update the queued message to show it's now being processed
                const queuedMsgs = document.querySelectorAll('.message.queued');
                if (queuedMsgs.length > 0) {
                    queuedMsgs[0].classList.remove('queued');
                    queuedMsgs[0].classList.add('user');
                }

                processQuery(nextQuery);
            }
        }

        function formatMarkdown(text) {
            if (!text) return '';

            // Escape HTML
            text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

            // Headers
            text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
            text = text.replace(/^# (.+)$/gm, '<h2>$1</h2>');

            // Bold
            text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            // Italic
            text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

            // Code blocks
            text = text.replace(/```(\w*)\\n([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>');

            // Inline code
            text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

            // Lists
            text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
            text = text.replace(/(<li>.*<\\/li>\\n?)+/g, '<ul>$&</ul>');

            // Paragraphs
            text = text.replace(/\\n\\n/g, '</p><p>');
            text = '<p>' + text + '</p>';

            // Clean up empty paragraphs
            text = text.replace(/<p>\s*<\/p>/g, '');
            text = text.replace(/<p>\s*(<h2>)/g, '$1');
            text = text.replace(/(<\/h2>)\s*<\/p>/g, '$1');
            text = text.replace(/<p>\s*(<ul>)/g, '$1');
            text = text.replace(/(<\/ul>)\s*<\/p>/g, '$1');
            text = text.replace(/<p>\s*(<pre>)/g, '$1');
            text = text.replace(/(<\/pre>)\s*<\/p>/g, '$1');

            return text;
        }

        function processQuery(query) {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;

            isProcessing = true;
            document.getElementById('stop-btn').classList.add('visible');
            updateStatus('Processing...', 'status-processing');

            // Add typing indicator
            const container = document.getElementById('chat-container');
            const typingEl = document.createElement('div');
            typingEl.id = 'typing-indicator';
            typingEl.className = 'typing-indicator';
            typingEl.innerHTML = '<span>.</span><span>.</span><span>.</span>';
            container.appendChild(typingEl);
            container.scrollTop = container.scrollHeight;

            // Send to server
            ws.send(JSON.stringify({
                type: 'query',
                query: query,
                session_id: sessionId
            }));
        }

        function sendMessage() {
            const input = document.getElementById('query-input');
            const query = input.value.trim();

            if (!query || !ws || ws.readyState !== WebSocket.OPEN) return;

            const container = document.getElementById('chat-container');

            if (isProcessing) {
                // Queue the message
                messageQueue.push(query);
                updateQueueStatus();

                // Show queued message in chat
                const msgEl = document.createElement('div');
                msgEl.className = 'message queued';
                msgEl.innerHTML = `<div class="message-label">Queued</div><div class="content">${formatMarkdown(query)}</div>`;
                container.appendChild(msgEl);
                container.scrollTop = container.scrollHeight;

                input.value = '';
                return;
            }

            // Add user message to chat
            const msgEl = document.createElement('div');
            msgEl.className = 'message user';
            msgEl.innerHTML = `<div class="message-label">You</div><div class="content">${formatMarkdown(query)}</div>`;
            container.appendChild(msgEl);

            input.value = '';
            processQuery(query);
        }

        function stopGeneration() {
            if (!isProcessing || !ws || ws.readyState !== WebSocket.OPEN) return;

            ws.send(JSON.stringify({ type: 'interrupt' }));
            updateStatus('Stopping...', 'status-error');
        }

        function newSession() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Clear queue
                messageQueue = [];
                updateQueueStatus();

                ws.send(JSON.stringify({ type: 'new_session' }));
                sessionId = null;
                totalCost = 0;
                isProcessing = false;
                document.getElementById('stop-btn').classList.remove('visible');
                clearChat();

                const container = document.getElementById('chat-container');
                const msgEl = document.createElement('div');
                msgEl.className = 'message system';
                msgEl.textContent = 'New session started';
                container.appendChild(msgEl);

                updateStatus('Connected', 'status-connected');
            }
        }

        function clearChat() {
            document.getElementById('chat-container').innerHTML = '';
        }

        // Handle Enter key
        document.getElementById('query-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Connect on load
        connect();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML page."""
    return HTML_TEMPLATE


@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    """Serve files from the outputs directory."""
    outputs_dir = Path(__file__).parent.parent / "outputs"
    file_path = outputs_dir / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return {"error": "File not found"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time chat with interrupt support."""
    await websocket.accept()

    session_id = None
    client = None
    response_task = None

    async def process_response():
        """Process agent response in a separate task for interrupt support."""
        nonlocal client
        current_text = ""
        turn_cost = 0.0

        try:
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            current_text = block.text
                            await websocket.send_json({
                                "type": "text",
                                "content": current_text
                            })
                        elif isinstance(block, ToolUseBlock):
                            await websocket.send_json({
                                "type": "tool_use",
                                "tool_name": block.name,
                                "input": block.input
                            })
                        elif isinstance(block, ToolResultBlock):
                            content = ""
                            if block.content:
                                for item in block.content:
                                    if hasattr(item, "text"):
                                        content += item.text
                            await websocket.send_json({
                                "type": "tool_result",
                                "content": content
                            })

                elif isinstance(message, ResultMessage):
                    if message.total_cost_usd:
                        turn_cost = message.total_cost_usd

            await websocket.send_json({
                "type": "done",
                "cost": turn_cost
            })
        except asyncio.CancelledError:
            # Task was cancelled due to interrupt
            await websocket.send_json({"type": "interrupted"})
            raise

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "new_session":
                # Cancel any ongoing response
                if response_task and not response_task.done():
                    response_task.cancel()
                    try:
                        await response_task
                    except asyncio.CancelledError:
                        pass

                # Close existing client if any
                if client:
                    await client.__aexit__(None, None, None)
                session_id = None
                client = None
                continue

            if data.get("type") == "interrupt":
                # Interrupt the current response
                if client and response_task and not response_task.done():
                    try:
                        await client.interrupt()
                    except Exception:
                        pass
                    response_task.cancel()
                    try:
                        await response_task
                    except asyncio.CancelledError:
                        pass
                continue

            if data.get("type") == "query":
                query = data.get("query", "")

                if not query:
                    await websocket.send_json({"type": "error", "message": "Empty query"})
                    continue

                try:
                    # Create or reuse client
                    if client is None:
                        options = get_agent_options()
                        client = ClaudeSDKClient(options=options)
                        await client.__aenter__()
                        session_id = id(client)
                        await websocket.send_json({"type": "session_id", "session_id": str(session_id)})

                    # Send query
                    await client.query(query)

                    # Process response in a task so we can interrupt it
                    response_task = asyncio.create_task(process_response())
                    await response_task

                except asyncio.CancelledError:
                    # Response was interrupted
                    pass
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

    except WebSocketDisconnect:
        pass
    finally:
        # Cancel any ongoing response
        if response_task and not response_task.done():
            response_task.cancel()
            try:
                await response_task
            except asyncio.CancelledError:
                pass

        if client:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass


def main():
    """Run the web server."""
    import uvicorn
    print("\n" + "=" * 60)
    print("Investment Research Agent - Web UI")
    print("=" * 60)
    print("\nStarting server at http://localhost:8000")
    print("Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
