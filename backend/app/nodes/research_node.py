"""Research node: runs Tavily for each query and dedupes into evidence."""
from datetime import date, timedelta
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import llm
from app.schemas.content import EvidenceItem, EvidencePack
from app.schemas.state import State
from app.tools.tavily import _tavily_search
from app.utils.dates import _iso_to_date

RESEARCH_SYSTEM = """
    You are a research synthesizer for technical writing.

    Given raw web search results, produce a deduplicated list of EvidenceItem objects.

    Rules:
    - Only include items with a non-empty url.
    - Prefer relevant + authoritative sources (company blogs, docs, reputable outlets).
    - If a published date is explicitly present in the result payload, keep it as YYYY-MM-DD.
    If missing or unclear, set published_at=null. Do NOT guess.
    - Keep snippets short.
    - Deduplicate by URL.
"""


# what we are doing over here is that
# we are calling the tavily search for each of the search queries decided by the router node
# the thing is that the research_node being hit means that there is something to research
# using an LLM we are getting the non duplicate items / search results only
def research_node(state: State):
    # take the queries from the state
    queries = state["queries"]  # a query is a different thing
    max_queries = 6

    raw_results: List[dict] = []
    # for each of this query we need to call tavily
    for i in queries:
        raw_results.extend(_tavily_search(i, max_results=max_queries))  # so each item of the tavily search result is unpacked and added in the raw results
    # now we do an llm call to make this raw-result un duplicated and nice
    if not raw_results:
        return {"evidence": []}  # we dont have any evidence now
    # for each of the results we need to
    extractor = llm.with_structured_output(EvidencePack)  # THIS SHUD RETURN LIKE THIS
    pack = extractor.invoke(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(content=f"Raw results:\n {raw_results}")
        ]
    )

    # now we are mapping out evidence based on the url itself maybe this is to make sure we use from only one url
    dedup = {}
    for e in pack.evidence:
        if e.url:
            dedup[e.url] = e  # the thing we see is as per the url we do stuff
    evidence = list(dedup.values())
    mode = state.get("mode", "closed_book")
    if (mode == "open_book"):
        as_of = date.fromisoformat(state["as_of"])
        cutoff = as_of - timedelta(days=int(state["recency_days"]))
        fresh: List[EvidenceItem] = []
        for e in evidence:
            d = _iso_to_date(e.published_at)
            if d and d >= cutoff:
                fresh.append(e)
        evidence = fresh

    return {"evidence": evidence}
