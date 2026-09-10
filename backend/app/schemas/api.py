"""Schemas for the HTTP API (request bodies and history responses)."""
from typing import Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="The blog topic to generate.")
    as_of: Optional[str] = Field(
        default=None,
        description="ISO date used for recency decisions. Defaults to today.",
    )


class BlogSummary(BaseModel):
    id: str
    topic: str
    title: str
    mode: str = ""
    blog_kind: str = ""
    needs_research: bool = False
    created_at: Optional[str] = None


class BlogDetail(BlogSummary):
    markdown: str = ""
    file_path: str = ""
    evidence_count: int = 0
    task_count: int = 0
