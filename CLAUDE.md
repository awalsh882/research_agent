# Workflow

```bash
# Activate virtual environment
source venv/bin/activate

# Start the web server
python -m research_agent.web

# Run CLI agent
python -m research_agent.agent

# Test imports
python -c "from research_agent.agent import get_agent_options; print('OK')"
```

# Codebase Structure

## Main Package: `research_agent/`

| File | Purpose |
|------|---------|
| `agent.py` | Main agent with ClaudeSDKClient, system prompt, `get_agent_options()` |
| `config.py` | Centralized configuration using dataclasses |
| `web.py` | FastAPI web server, routes, serves static files |
| `websocket_handler.py` | `WebSocketHandler` class for real-time chat |
| `tasks.py` | Task progress tracking (`.task-progress.json`) |

## Tools: `research_agent/tools/`

| File | Purpose |
|------|---------|
| `registry.py` | `ToolRegistry` class + `@registered_tool` decorator |
| `web_search.py` | Web search tool (Tavily/SerpAPI/Brave) |
| `report_tool.py` | Report generation orchestration |
| `report_builder.py` | `DocxReportBuilder` class (Builder pattern) |
| `report_html.py` | HTML report generation |
| `task_tool.py` | `update_tasks`, `clear_tasks` tools |
| `introspection.py` | `list_tools` tool |

## Frontend: `research_agent/static/` and `templates/`

| File | Purpose |
|------|---------|
| `static/styles.css` | All CSS (~900 lines) |
| `static/app.js` | All JavaScript (~700 lines) |
| `templates/index.html` | Main HTML template |

# Key Patterns

## Tool Registration

Tools use the `@registered_tool` decorator and are explicitly registered at startup:

```python
# In agent.py at startup:
ToolRegistry.register_all()

# In registry.py - register_all() imports tool modules:
from research_agent.tools import web_search      # noqa: F401
from research_agent.tools import report_tool     # noqa: F401
from research_agent.tools import task_tool       # noqa: F401
from research_agent.tools import introspection   # noqa: F401
```

To add a new tool:
1. Create `tools/my_tool.py` with `@registered_tool` decorator
2. Add import to `ToolRegistry.register_all()` in `registry.py`

## WebSocket Messages

Message types handled by `WebSocketHandler`:
- `query` - User sends a message
- `new_session` - Start fresh conversation
- `interrupt` - Stop current generation
- `set_model` - Change Claude model

## Design Principles

- **Sandi Metz rules**: Small classes, small methods, single responsibility
- **Builder pattern**: Used in `report_builder.py` for DOCX generation
- **Explicit registration**: Prefer `register_all()` over import side-effects
- **Type hints**: All function signatures should have annotations

# Common Tasks

## Add a New Tool

```python
# tools/my_tool.py
from research_agent.tools.registry import registered_tool

@registered_tool(
    name="my_tool",
    description="Does something useful",
    parameters={"param1": "Description"},
    parameter_types={"param1": str},
)
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": "Result"}]}
```

Then add to `registry.py`:
```python
from research_agent.tools import my_tool  # noqa: F401
```

## Modify System Prompt

Edit `_SYSTEM_PROMPT_BASE` in `agent.py`. The tools section is generated dynamically from the registry.

## Update UI

- CSS: `static/styles.css`
- JS: `static/app.js`
- HTML: `templates/index.html`
- Fallback: `HTML_TEMPLATE` in `web.py` (for backwards compatibility)

# Environment

```bash
# Required
export ANTHROPIC_API_KEY="your-key"

# Optional - for web search
export TAVILY_API_KEY="your-key"      # Recommended
export SERPAPI_API_KEY="your-key"     # Alternative
export BRAVE_API_KEY="your-key"       # Alternative
```
