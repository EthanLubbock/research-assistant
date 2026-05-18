from __future__ import annotations

import logging
from typing import Any

from tavily import TavilyClient

from shared.config import settings

logger = logging.getLogger(__name__)


def tavily_search(query: str) -> list[dict[str, str]]:
    """Run a Tavily search and return normalized search results."""
    if not query or not query.strip():
        logger.warning("Skipping Tavily search because query is empty")
        return []

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
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
