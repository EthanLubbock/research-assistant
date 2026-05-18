import logging
from typing import Any

from tavily import TavilyClient

from shared.config import get_settings

logger = logging.getLogger(__name__)


def _get_tavily_client() -> TavilyClient:
    settings = get_settings()
    tavily_api_key = settings.tavily_api_key.strip()
    if not tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is set but empty")

    if "your-tavily-api-key" in tavily_api_key.lower():
        raise RuntimeError("TAVILY_API_KEY is still a placeholder value")

    return TavilyClient(api_key=tavily_api_key)


def tavily_search(query: str) -> list[dict[str, str]]:
    """Run a Tavily search and return normalized search results."""
    if not query or not query.strip():
        logger.warning("Skipping Tavily search because query is empty")
        return []

    try:
        client = _get_tavily_client()
        response: dict[str, Any] = client.search(
            query=query.strip(),
            max_results=5,
            include_answer=False,
            include_raw_content=False,
        )

        normalized_results: list[dict[str, str]] = []
        for item in response.get("results", []):
            if not isinstance(item, dict):
                continue

            normalized_results.append(
                {
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                    "content": str(item.get("content", "")).strip(),
                }
            )

        return normalized_results
    except Exception as exc:
        logger.exception("Tavily search failed for query '%s': %s", query, exc)
        return []
