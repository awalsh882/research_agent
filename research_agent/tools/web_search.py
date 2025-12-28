"""Web search tool for the Investment Research Agent.

Provides real-time web search capabilities using configurable search APIs.
Supports multiple providers (Tavily, SerpAPI, Brave) with graceful fallbacks.
"""

import os
from typing import Any

import httpx

from research_agent.tools.registry import registered_tool


# Search provider configurations
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY")


async def _search_tavily(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Search using Tavily API (recommended for research)."""
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable not set")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": num_results,
                "search_depth": "advanced",  # Better for research queries
                "include_answer": True,
                "include_raw_content": False,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        # Include the AI-generated answer if available
        if data.get("answer"):
            results.append({
                "title": "AI Summary",
                "url": "",
                "snippet": data["answer"],
            })

        for result in data.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", ""),
            })

        return results[:num_results]


async def _search_serpapi(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Search using SerpAPI (Google Search)."""
    if not SERPAPI_API_KEY:
        raise ValueError("SERPAPI_API_KEY environment variable not set")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://serpapi.com/search",
            params={
                "api_key": SERPAPI_API_KEY,
                "q": query,
                "num": num_results,
                "engine": "google",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for result in data.get("organic_results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
            })

        return results[:num_results]


async def _search_brave(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Search using Brave Search API."""
    if not BRAVE_API_KEY:
        raise ValueError("BRAVE_API_KEY environment variable not set")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={
                "q": query,
                "count": num_results,
            },
            headers={
                "X-Subscription-Token": BRAVE_API_KEY,
                "Accept": "application/json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for result in data.get("web", {}).get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("description", ""),
            })

        return results[:num_results]


def _get_available_provider() -> str | None:
    """Determine which search provider is available based on API keys."""
    if TAVILY_API_KEY:
        return "tavily"
    if SERPAPI_API_KEY:
        return "serpapi"
    if BRAVE_API_KEY:
        return "brave"
    return None


def _format_results(results: list[dict[str, str]], query: str) -> str:
    """Format search results for display."""
    if not results:
        return f"No results found for: {query}"

    lines = [f"## Web Search Results for: {query}\n"]

    for i, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        snippet = result.get("snippet", "No description available")

        if url:
            lines.append(f"### {i}. {title}")
            lines.append(f"**URL:** {url}")
        else:
            # AI summary doesn't have URL
            lines.append(f"### {title}")

        lines.append(f"{snippet}\n")

    return "\n".join(lines)


@registered_tool(
    name="web_search",
    description=(
        "Search the web for real-time information. Use this to find current news, "
        "recent earnings reports, analyst opinions, market data, company announcements, "
        "and other time-sensitive information. Returns titles, URLs, and snippets from "
        "top search results."
    ),
    parameters={
        "query": "The search query (e.g., 'DocuSign Q3 2024 earnings results')",
        "num_results": "Number of results to return (default: 5, max: 10)",
    },
    parameter_types={
        "query": str,
        "num_results": int,
    },
)
async def web_search(args: dict[str, Any]) -> dict[str, Any]:
    """Execute a web search and return formatted results.

    Args:
        args: Dict with:
            - query: Search query string
            - num_results: Optional number of results (default: 5)

    Returns:
        Tool result with formatted search results or error message.
    """
    query = args.get("query", "")
    num_results = min(args.get("num_results", 5), 10)  # Cap at 10

    if not query:
        return {
            "content": [{"type": "text", "text": "Error: query parameter is required"}],
            "is_error": True,
        }

    # Check for available provider
    provider = _get_available_provider()

    if not provider:
        return {
            "content": [{
                "type": "text",
                "text": (
                    "Web search is not configured. Please set one of the following "
                    "environment variables:\n"
                    "- TAVILY_API_KEY (recommended for research)\n"
                    "- SERPAPI_API_KEY (Google Search)\n"
                    "- BRAVE_API_KEY (Brave Search)\n\n"
                    "Get a free Tavily API key at: https://tavily.com"
                ),
            }],
            "is_error": True,
        }

    try:
        # Execute search with available provider
        if provider == "tavily":
            results = await _search_tavily(query, num_results)
        elif provider == "serpapi":
            results = await _search_serpapi(query, num_results)
        elif provider == "brave":
            results = await _search_brave(query, num_results)
        else:
            results = []

        formatted = _format_results(results, query)

        return {
            "content": [{
                "type": "text",
                "text": formatted,
            }]
        }

    except httpx.HTTPStatusError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Search API error ({provider}): {e.response.status_code} - {e.response.text[:200]}",
            }],
            "is_error": True,
        }
    except httpx.TimeoutException:
        return {
            "content": [{
                "type": "text",
                "text": f"Search request timed out ({provider}). Please try again.",
            }],
            "is_error": True,
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Search error: {e}",
            }],
            "is_error": True,
        }
