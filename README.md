# Investment Research Agent

A conversational research agent with memory, powered by the Claude Agent SDK. Provides structured analysis for institutional investment research with multi-turn context and professional report generation.

## Features

- **Multi-turn conversations** - Agent remembers context across the session
- **Structured analysis** - Responses formatted for institutional investors
- **Web search** - Real-time access to current news, earnings, and market data
- **Report generation** - Export research to HTML and Word documents
- **Web interface** - Split-pane UI with chat and viewer panels
- **Slash commands** - Quick actions via `/clear`, `/new`, `/stop`, `/help`
- **Tool introspection** - Agent can report its own capabilities

## Getting Started

### Prerequisites

- Python 3.10+
- An Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)

### Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

4. (Optional) Enable web search with one of these providers:
   ```bash
   # Tavily (recommended for research - https://tavily.com)
   export TAVILY_API_KEY="your-tavily-key"

   # Or SerpAPI (Google Search)
   export SERPAPI_API_KEY="your-serpapi-key"

   # Or Brave Search
   export BRAVE_API_KEY="your-brave-key"
   ```

### Running the Agent

**Command Line:**
```bash
python -m research_agent.agent
```

**Web Interface:**
```bash
python -m research_agent.web
```
Then open http://localhost:8000 in your browser.

## Example Conversation

```
Query: I'm looking at DocuSign ahead of earnings. What should I focus on?

[Agent provides structured analysis of key metrics, competitive position,
 and what to watch in the upcoming earnings]

Query: How does their net retention compare to peers?

[Agent builds on previous context, provides specific NRR comparisons
 with Adobe Sign, PandaDoc, and other e-signature players]

Query: Generate a research report for this analysis

[Agent creates a professional Word document with executive summary,
 financial analysis, risks, and key takeaways]
```

## Commands

### CLI Commands

| Command | Description |
|---------|-------------|
| `quit` / `exit` / `q` | End the session |
| `new` | Start a fresh conversation (clears context) |
| `example` | Show example multi-turn conversation |

### Web UI Slash Commands

Type `/` in the chat input to see available commands with autocomplete:

| Command | Description |
|---------|-------------|
| `/clear` | Clear the chat history |
| `/new` | Start a new session (clears context) |
| `/stop` | Stop the current generation |
| `/help` | Show available commands |

## Response Format

Initial queries receive structured responses:

- **Key Answer** - Direct, concise takeaway (2-3 sentences)
- **Supporting Analysis** - Detailed reasoning, data points, and context
- **Risks & Considerations** - Counterarguments and factors that could invalidate the thesis
- **Further Research** - Suggested areas for deeper due diligence

Follow-up questions get more conversational responses while maintaining analytical rigor.

## Tools

The agent has access to:

| Tool | Description |
|------|-------------|
| `web_search` | Search the web for current news, earnings, analyst opinions, and market data |
| `generate_report` | Creates a professional equity research report in HTML and Word formats |
| `list_tools` | Returns a list of available tools and their capabilities |

- Ask the agent to "search for DocuSign Q3 earnings" to get real-time information
- Ask "generate a report" after completing an analysis to save it as a document
- Ask "what tools do you have?" to see available capabilities

## Project Structure

```
research_agent/
├── __init__.py          # Package exports
├── agent.py             # Main agent with ClaudeSDKClient
├── config.py            # Centralized configuration
├── web.py               # FastAPI web interface with split-pane UI
└── tools/
    ├── __init__.py
    ├── registry.py      # Self-registering tool system
    ├── web_search.py    # Web search tool (Tavily/SerpAPI/Brave)
    ├── report_tool.py   # Report generation (HTML + DOCX)
    ├── report_html.py   # HTML template for OneNote-compatible output
    └── introspection.py # Tool introspection (list_tools)

outputs/                 # Generated files
├── *.html               # Research reports (viewable in browser)
└── *.docx               # Research reports (downloadable)

docs/                    # Claude Agent SDK documentation
```

## Customization

### Configuration

Edit `research_agent/config.py` to modify:

- **`AgentConfig`** - Model, max_turns, MCP server settings
- **`WebConfig`** - Host, port, log level for web UI
- **`PathConfig`** - Output directories
- **`SearchConfig`** - Web search provider configuration (via environment variables)

### Adding New Tools

Tools self-register using the `@registered_tool` decorator:

```python
from research_agent.tools.registry import registered_tool

@registered_tool(
    name="my_tool",
    description="Does something useful",
    parameters={"param1": "Description of param1"},
    parameter_types={"param1": str},
)
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    # Implementation
    return {"content": [{"type": "text", "text": "Result"}]}
```

The tool is automatically:
- Registered with the MCP server
- Added to the system prompt
- Available for introspection via `list_tools`

## Documentation

See the [docs/](docs/) folder for Claude Agent SDK documentation:

- [Overview](docs/overview.md) - SDK concepts and architecture
- [Python Reference](docs/python.md) - Complete API reference
- [Sessions](docs/sessions.md) - Session management and resumption
- [Streaming Input](docs/streaming-input.md) - ClaudeSDKClient for interactive sessions

## License

Use of the Claude Agent SDK is governed by Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).
