# Investment Research Agent

A conversational research agent with memory, powered by the Claude Agent SDK. Provides structured analysis for institutional investment research with multi-turn context and professional report generation.

## Features

- **Multi-turn conversations** - Agent remembers context across the session
- **Structured analysis** - Responses formatted for institutional investors
- **Report generation** - Export research to professional Word documents
- **Web interface** - Browser-based UI for interactive sessions
- **Architecture visualization** - Developer tool to inspect agent structure

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

## Commands (CLI)

| Command | Description |
|---------|-------------|
| `quit` / `exit` / `q` | End the session |
| `new` | Start a fresh conversation (clears context) |
| `example` | Show example multi-turn conversation |

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
| `generate_report` | Creates a professional equity research report as a Word document (.docx) |

Ask the agent to "generate a report" after completing an analysis to save it as a formal document.

## Project Structure

```
research_agent/
├── __init__.py          # Package exports
├── agent.py             # Main agent with ClaudeSDKClient
├── web.py               # FastAPI web interface
├── architecture.py      # Developer tool for architecture diagrams
└── tools/
    ├── __init__.py
    └── report_tool.py   # Report generation tool

outputs/                 # Generated files
├── *.docx               # Research reports
└── agent_architecture.drawio

docs/                    # Claude Agent SDK documentation
```

## Developer Tools

**Generate architecture diagram:**
```bash
python -m research_agent.architecture
```
Creates a draw.io diagram visualizing the agent's components, tools, and data flow.

## Customization

Edit `research_agent/agent.py` to modify:

- **`SYSTEM_PROMPT`** - Customize the analyst persona and response format
- **`ClaudeAgentOptions`** - Configure max_turns, tools, and other settings
- **`research_tools_server`** - Add or modify available tools

## Documentation

See the [docs/](docs/) folder for Claude Agent SDK documentation:

- [Overview](docs/overview.md) - SDK concepts and architecture
- [Python Reference](docs/python.md) - Complete API reference
- [Sessions](docs/sessions.md) - Session management and resumption
- [Streaming Input](docs/streaming-input.md) - ClaudeSDKClient for interactive sessions

## License

Use of the Claude Agent SDK is governed by Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).
