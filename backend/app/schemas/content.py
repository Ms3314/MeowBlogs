"""Core content schemas: tasks, plan, evidence and router decisions."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    title: str
    goal: str = Field(
        description="one sentence to what the reader should understand after reading this section"
    ),
    bullets: List[str] = Field(
        min_length=3,
        max_length=5,
        description="3-5 non overlappint subpoints to cover in this section"
    )
    target_words: int = Field(
        description="target word count for this section 120-500"
    )
    tags: list[str] = Field(default_factory=list)
    requires_code: bool = False
    requires_research: bool = False
    requires_citations: bool = False


class Plan(BaseModel):
    blog_title: str
    audience: str = Field(description="here we need to define the target audience for the blog")
    tasks: List[Task]
    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = "explainer"
    tone: Literal[
        "Conversational",
        "Casual",
        "Professional",
        "Authoritative",
        "Inspirational",
        "Motivational",
        "Humorous",
        "Irreverent",
        "Instructional",
        "Educational"
    ] = Field(description="this is defining the tone in which the blog should be it can be in one of these")
    constraints: List[str] = Field(default_factory=list)


# this refers to an individual evidence item from the tavily search
class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: Optional[str] = None  # not nessesary that these shud exist
    snippet: Optional[str] = None
    source: Optional[str] = None


# this is just a set of evidenceItems
class EvidencePack(BaseModel):
    evidence: list[EvidenceItem] = Field(default_factory=list)


# this will be the structured output from the LLM for the router_node
class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["closed_book", "hybrid", "open_book"]
    queries: List[str] = Field(default_factory=list)
