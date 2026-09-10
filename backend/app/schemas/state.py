"""LangGraph shared state (ported verbatim from the notebook)."""
import operator
from typing import Annotated, List, Optional, TypedDict

from app.schemas.content import EvidenceItem, Plan


class State(TypedDict):
    topic: str
    sections: Annotated[List[tuple[int, str]], operator.add]
    # comes from the routing decision
    needs_research: bool
    queries: list[str]
    evidence: list[EvidenceItem]
    mode: str

    as_of: str  # ISO date , this will be added when it is called
    recency_days: str  # 7 for weekly and 30 for hybrid , this is used for the days

    # for the images section over here
    merged_md: str
    md_with_placeholders: str
    image_specs: list

    # comes from the orchestrator
    plan: Optional[Plan]
    # answer
    final: str
