"""Centralized configuration for the Research Agent.

All configurable settings in one place. Values can be overridden via
environment variables where noted.

Environment Variables:
    Web Search (set one of these for web search capability):
        TAVILY_API_KEY  - Tavily API key (recommended, https://tavily.com)
        SERPAPI_API_KEY - SerpAPI key for Google Search
        BRAVE_API_KEY   - Brave Search API key
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SearchConfig:
    """Configuration for web search providers.

    The agent will use the first available provider based on environment variables.
    Priority order: Tavily > SerpAPI > Brave
    """

    @property
    def tavily_api_key(self) -> str | None:
        """Tavily API key (recommended for research queries)."""
        return os.environ.get("TAVILY_API_KEY")

    @property
    def serpapi_api_key(self) -> str | None:
        """SerpAPI key for Google Search."""
        return os.environ.get("SERPAPI_API_KEY")

    @property
    def brave_api_key(self) -> str | None:
        """Brave Search API key."""
        return os.environ.get("BRAVE_API_KEY")

    @property
    def is_configured(self) -> bool:
        """Check if any search provider is configured."""
        return bool(self.tavily_api_key or self.serpapi_api_key or self.brave_api_key)

    @property
    def active_provider(self) -> str | None:
        """Get the name of the active search provider."""
        if self.tavily_api_key:
            return "tavily"
        if self.serpapi_api_key:
            return "serpapi"
        if self.brave_api_key:
            return "brave"
        return None


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for the Claude agent."""

    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 10
    mcp_server_name: str = "research-tools"
    mcp_server_version: str = "1.0.0"


@dataclass(frozen=True)
class WebConfig:
    """Configuration for the web server."""

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"


@dataclass(frozen=True)
class PathConfig:
    """Path configuration for outputs and resources."""

    _base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def outputs_dir(self) -> Path:
        """Directory for generated outputs (reports, diagrams, etc.)."""
        path = self._base_dir / "outputs"
        path.mkdir(exist_ok=True)
        return path

    @property
    def templates_dir(self) -> Path:
        """Directory for templates (if extracted from code)."""
        return Path(__file__).parent / "templates"


@dataclass(frozen=True)
class Config:
    """Root configuration object combining all settings."""

    agent: AgentConfig = field(default_factory=AgentConfig)
    web: WebConfig = field(default_factory=WebConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    search: SearchConfig = field(default_factory=SearchConfig)


# Global config instance
config = Config()


def get_outputs_dir() -> Path:
    """Get the outputs directory. Convenience function for common use case."""
    return config.paths.outputs_dir
