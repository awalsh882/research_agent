# Investment Research Agent

A conversational research agent with memory, powered by the Claude Agent SDK. Provides structured analysis for institutional investment research with multi-turn context and professional report generation.

## Overview

This project demonstrates how to build a production-quality AI agent using the Claude Agent SDK. It serves as both a functional investment research tool and a reference implementation for:

- **MCP Tool Integration** - Custom tools with self-registration pattern
- **WebSocket Streaming** - Real-time response streaming to web UI
- **Multi-turn Conversations** - Persistent context across messages
- **Report Generation** - Structured document output (HTML + DOCX)

## Features

- **Multi-turn conversations** - Agent remembers context across the session
- **Structured analysis** - Responses formatted for institutional investors
- **Web search** - Real-time access to current news, earnings, and market data
- **Report generation** - Export research to HTML and Word documents
- **Web interface** - Split-pane UI with chat, viewer, and task panels
- **Model selection** - Switch between Claude Sonnet 4, Opus 4, and 3.5 models
- **Task tracking** - Real-time progress display for multi-step analyses
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
| `update_tasks` | Track progress on multi-step analyses (visible in UI task panel) |
| `clear_tasks` | Clear the current task progress |
| `list_tools` | Returns a list of available tools and their capabilities |

**Example prompts:**
- "Search for DocuSign Q3 earnings" - triggers web search for real-time information
- "Generate a report" - creates HTML + DOCX documents after completing an analysis
- "What tools do you have?" - agent introspects its own capabilities

## Project Structure

```
research_agent/
├── __init__.py              # Package exports
├── agent.py                 # Main agent with ClaudeSDKClient, system prompt
├── config.py                # Centralized configuration (dataclasses)
├── web.py                   # FastAPI web server and routes
├── websocket_handler.py     # WebSocket connection handler (extracted class)
├── tasks.py                 # Task progress tracking (.task-progress.json)
│
├── static/                  # Frontend assets (extracted from web.py)
│   ├── styles.css           # All CSS (~900 lines)
│   └── app.js               # All JavaScript (~700 lines)
│
├── templates/
│   └── index.html           # Main HTML template
│
└── tools/                   # MCP tools with self-registration
    ├── __init__.py          # Package init
    ├── registry.py          # ToolRegistry + @registered_tool decorator
    ├── web_search.py        # Web search (Tavily/SerpAPI/Brave)
    ├── report_tool.py       # Report generation orchestration
    ├── report_builder.py    # DOCX generation (Builder pattern)
    ├── report_html.py       # HTML report generation
    ├── task_tool.py         # Task progress tools (update_tasks, clear_tasks)
    └── introspection.py     # Tool introspection (list_tools)

outputs/                     # Generated files appear here
├── *.html                   # Research reports (viewable in browser)
└── *.docx                   # Research reports (downloadable)

diagrams/                    # Architecture diagrams
└── architecture.drawio      # Draw.io diagram of system architecture

docs/                        # Claude Agent SDK documentation
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

**Important:** Add your tool module to `ToolRegistry.register_all()` in `registry.py`:

```python
@classmethod
def register_all(cls) -> None:
    from research_agent.tools import web_search      # noqa: F401
    from research_agent.tools import report_tool     # noqa: F401
    from research_agent.tools import my_new_tool     # Add your tool here
    cls._initialized = True
```

## Architecture

### Key Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Builder** | `report_builder.py` | Construct DOCX reports step-by-step |
| **Registry** | `registry.py` | Self-registering tools with metadata |
| **Handler** | `websocket_handler.py` | Encapsulate WebSocket connection logic |

### Data Flow

```
User Input (Web UI)
       │
       ▼
┌──────────────────┐
│  WebSocket       │  ← websocket_handler.py
│  Handler         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ClaudeSDKClient │  ← agent.py (from claude_agent_sdk)
│  + MCP Server    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Tool Registry   │  ← registry.py
│  (web_search,    │
│   generate_report│
│   update_tasks)  │
└────────┬─────────┘
         │
         ▼
   Response Stream
   (text, tool_use,
    tool_result)
         │
         ▼
   Web UI Updates
```

### Tool Registration Flow

```python
# 1. At startup, agent.py calls:
ToolRegistry.register_all()

# 2. This imports tool modules, triggering @registered_tool decorators
# 3. Each decorator registers the tool with ToolRegistry
# 4. get_agent_options() builds MCP server with registered tools
# 5. ClaudeSDKClient receives tool definitions
```

## Documentation

See the [docs/](docs/) folder for Claude Agent SDK documentation:

- [Overview](docs/overview.md) - SDK concepts and architecture
- [Python Reference](docs/python.md) - Complete API reference
- [Sessions](docs/sessions.md) - Session management and resumption
- [Streaming Input](docs/streaming-input.md) - ClaudeSDKClient for interactive sessions

---

## For AI Agents

This section provides context for AI agents (Claude, etc.) working on this codebase.

### Quick Context

- **Purpose**: Investment research agent with web UI
- **SDK**: Claude Agent SDK (`claude_agent_sdk` package)
- **Framework**: FastAPI + WebSocket for real-time streaming
- **Tools**: MCP tools registered via `@registered_tool` decorator

### Key Entry Points

| File | Purpose | When to modify |
|------|---------|----------------|
| `agent.py` | System prompt, agent configuration | Changing agent behavior |
| `websocket_handler.py` | WebSocket message handling | Modifying real-time communication |
| `tools/registry.py` | Tool registration system | Adding new tools |
| `static/app.js` | Frontend JavaScript | UI behavior changes |
| `static/styles.css` | Frontend styling | Visual changes |

### Common Tasks

**Add a new tool:**
1. Create `tools/my_tool.py` with `@registered_tool` decorator
2. Add import to `ToolRegistry.register_all()` in `registry.py`
3. Tool automatically available to agent

**Modify the system prompt:**
- Edit `_SYSTEM_PROMPT_BASE` in `agent.py`
- Tools section is generated dynamically from registry

**Change WebSocket behavior:**
- Modify `WebSocketHandler` class in `websocket_handler.py`
- Message types: `query`, `new_session`, `interrupt`, `set_model`

**Update the UI:**
- CSS: `static/styles.css`
- JS: `static/app.js`
- HTML: `templates/index.html`
- Fallback template in `web.py` (for backwards compatibility)

### Code Style

- **Sandi Metz principles**: Small classes, small methods, single responsibility
- **Builder pattern**: Used for report generation (`report_builder.py`)
- **Explicit > implicit**: Tool registration via `register_all()` not import side-effects
- **Type hints**: All function signatures should have type annotations

### Testing

```bash
# Run from project root with venv activated
./venv/bin/python -c "from research_agent.agent import get_agent_options; print('OK')"
./venv/bin/python -m research_agent.web  # Start web server
```

---

## License

Use of the Claude Agent SDK is governed by Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).
