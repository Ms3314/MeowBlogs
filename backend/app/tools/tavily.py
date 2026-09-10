"""Tavily web-search helper (ported from the notebook)."""
from typing import List

from langchain_community.tools.tavily_search import TavilySearchResults


def _tavily_search(query: str, max_results: int = 5) -> List[dict]:
    # so for each query we will be returning the top results
    tool = TavilySearchResults(max_results=max_results)
    results = tool.invoke({"query": query})

    normalized: List[dict] = []
    for r in results or []:
        normalized.append(
            {
                "title": r.get("title") or "",
                "url": r.get("url") or "",
                "snippet": r.get("content") or r.get("snippet") or "",
                "published_at": r.get("published_date") or r.get("published_at"),
                "source": r.get("source"),
            }
        )
    return normalized
