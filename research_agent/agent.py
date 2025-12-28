#!/usr/bin/env python3
"""Investment Research Agent for institutional investors.

A conversational research agent with memory that provides structured analysis
for investment research queries using the Claude Agent SDK.

Usage:
    python -m research_agent.agent                    # Interactive conversation
    python -m research_agent.agent "your query here"  # Start with initial query

Example conversation:
    Query: Analyze DocuSign ahead of their next earnings release
    [... structured analysis ...]

    Query: What are the key metrics I should focus on?
    [... follows up with context from previous response ...]

    Query: How does their competitive position compare to Adobe Sign?
    [... continues building on the conversation ...]
"""

import sys
import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
)

from research_agent.config import config
from research_agent.tools.registry import ToolRegistry

# Import tools to trigger registration (order matters - report_tool before introspection)
import research_agent.tools.web_search  # noqa: F401
import research_agent.tools.report_tool  # noqa: F401
import research_agent.tools.introspection  # noqa: F401


# Base system prompt without tools section (tools are added dynamically)
_SYSTEM_PROMPT_BASE = """You are an institutional investment research analyst providing analysis to professional investors at hedge funds, asset managers, and pension funds.

This is a conversational research session. You have memory of the full conversation, so you can:
- Build on previous analyses when the user asks follow-up questions
- Reference earlier points without the user needing to repeat context
- Deepen analysis progressively as the conversation evolves
- Track multiple companies or themes discussed in the session

For initial queries or new topics, structure your response as:

## Key Answer
[Direct, concise answer in 2-3 sentences - the core takeaway for a busy PM]

## Supporting Analysis
[Detailed reasoning, data points, frameworks, and quantitative considerations]

## Risks & Considerations
[Counterarguments, key risks, and factors that could invalidate the thesis]

## Further Research
[Specific areas or data sources for deeper due diligence]

For follow-up questions, you may use a more conversational format while maintaining analytical rigor.

Guidelines:
- Be direct and avoid hedging language when evidence supports a clear view
- Acknowledge uncertainty explicitly when data is limited or conflicting
- Use precise terminology appropriate for institutional investors
- Reference relevant market dynamics, valuation frameworks, and industry metrics
- Focus on actionable insights rather than generic observations
- When asked to compare or contrast, be specific about relative positioning
- Use web_search to find current information like recent earnings, news, analyst opinions, and market data
- Always cite sources when using information from web search results

IMPORTANT: When you call list_tools, report ONLY the tools returned by that tool. Do not add or embellish with other capabilities.

Note: This analysis is for informational purposes only and does not constitute investment advice. Always conduct independent due diligence before making investment decisions."""


def get_system_prompt() -> str:
    """Build the complete system prompt with dynamically generated tools section."""
    return _SYSTEM_PROMPT_BASE + "\n\n" + ToolRegistry.get_system_prompt_section()


# For backwards compatibility
SYSTEM_PROMPT = get_system_prompt()


# Example multi-turn conversation for illustration
EXAMPLE_CONVERSATION = """
Example Multi-Turn Research Session:
=====================================

User: I'm looking at DocuSign ahead of earnings. What should I focus on?

Agent: [Provides structured analysis of DocuSign's key metrics, competitive
       position, and what to watch in the upcoming earnings]

User: How does their net retention compare to peers?

Agent: [Builds on previous context, provides specific NRR comparisons with
       Adobe Sign, PandaDoc, and other e-signature players]

User: What's the bear case here?

Agent: [References the analysis so far and articulates the key risks -
       competition from bundled solutions, SMB churn, macro sensitivity]

User: Compare this setup to where Salesforce was before their last print

Agent: [Draws parallels and contrasts between DOCU and CRM situations,
       leveraging the full conversation context]

The agent maintains context throughout, enabling deeper and more nuanced
analysis as the conversation progresses.
"""

def _create_mcp_server():
    """Create MCP server with all registered tools."""
    return create_sdk_mcp_server(
        name=config.agent.mcp_server_name,
        version=config.agent.mcp_server_version,
        tools=ToolRegistry.get_tools(),
    )


def get_agent_options() -> ClaudeAgentOptions:
    """Get the agent options with MCP server configured."""
    server_name = config.agent.mcp_server_name
    return ClaudeAgentOptions(
        model=config.agent.model,
        system_prompt=get_system_prompt(),
        max_turns=config.agent.max_turns,
        mcp_servers={server_name: _create_mcp_server()},
        allowed_tools=ToolRegistry.get_allowed_tools(server_name),
    )


async def run_conversation() -> None:
    """Run an interactive conversation with the research agent."""
    print("\n" + "=" * 70)
    print("INVESTMENT RESEARCH AGENT")
    print("=" * 70)
    print("\nConversational research session with memory.")
    print("The agent remembers context from earlier in the conversation.")
    print("\nType 'quit' or 'exit' to end. Type 'new' to start fresh.\n")

    options = get_agent_options()

    async with ClaudeSDKClient(options=options) as client:
        total_cost = 0.0

        while True:
            try:
                user_input = input("Query: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nSession ended.")
                if total_cost > 0:
                    print(f"Total session cost: ${total_cost:.4f}")
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("\nSession ended.")
                if total_cost > 0:
                    print(f"Total session cost: ${total_cost:.4f}")
                break

            if user_input.lower() == "new":
                print("\n[Starting new conversation - previous context cleared]\n")
                # Exit and restart with fresh client
                return await run_conversation()

            if user_input.lower() == "example":
                print(EXAMPLE_CONVERSATION)
                continue

            # Send query to the agent
            print()
            await client.query(user_input)

            # Stream and display response
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text)
                elif isinstance(message, ResultMessage):
                    if message.total_cost_usd and message.total_cost_usd > 0:
                        total_cost += message.total_cost_usd
                        print(f"\n[Turn cost: ${message.total_cost_usd:.4f} | "
                              f"Session total: ${total_cost:.4f}]")

            print()  # Blank line before next prompt


async def run_single_query(prompt: str) -> None:
    """Run a single query and exit (starts a conversation that can be continued)."""
    options = get_agent_options()

    print("\n" + "=" * 70)
    print("QUERY:", prompt)
    print("=" * 70 + "\n")

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                if message.total_cost_usd and message.total_cost_usd > 0:
                    print(f"\n[Cost: ${message.total_cost_usd:.4f}]")


async def main() -> None:
    """Main entry point with CLI argument handling."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg in ("--help", "-h"):
            print(__doc__)
            return

        if arg == "--example":
            print(EXAMPLE_CONVERSATION)
            return

        # Treat all other arguments as the initial query, then continue conversation
        query_text = " ".join(sys.argv[1:])
        await run_single_query(query_text)
        return

    # Default: interactive conversation
    await run_conversation()


if __name__ == "__main__":
    anyio.run(main)
