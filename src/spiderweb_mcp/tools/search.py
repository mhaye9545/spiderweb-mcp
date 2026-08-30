"""
Web search tool integration using a local SearXNG instance.
Provides private web search without leaking metadata or tracking info externally.
"""

from typing import Any, Dict, List

import httpx
from fastmcp import FastMCP

# Default endpoint for local SearXNG instance
SEARXNG_URL = "http://127.0.0.1:8888/search"


def register_search_tools(mcp: FastMCP) -> None:
    """Register web search tools with the FastMCP gateway."""

    @mcp.tool()
    async def web_search(query: str, max_results: int = 5) -> str:
        """Perform a private web search query using the local SearXNG engine.

        Args:
            query: The search terms / query string.
            max_results: Maximum number of relevant snippets to return (default 5).

        Returns:
            Formatted plain-text search results with title, URL, and snippet.
        """
        params = {
            "q": query,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(SEARXNG_URL, params=params)
                response.raise_for_status()
                data = response.json()

            results: List[Dict[str, Any]] = data.get("results", [])
            if not results:
                return f"No results found for query: {query}"

            formatted: List[str] = []
            for item in results[:max_results]:
                title = item.get("title", "No Title")
                url = item.get("url", "")
                content = item.get("content", "").strip()
                formatted.append(f"### {title}\nURL: {url}\n{content}")

            return "\n\n---\n\n".join(formatted)

        except httpx.HTTPError as err:
            return f"Error connecting to local search backend: {err}"
