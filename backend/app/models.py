"""ORM models for persisted blog generations."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text

from app.db import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    title = Column(String, default="")
    mode = Column(String, default="")
    blog_kind = Column(String, default="")
    needs_research = Column(Boolean, default=False)
    markdown = Column(Text, default="")
    file_path = Column(String, default="")
    plan_json = Column(Text, default="")
    evidence_json = Column(Text, default="")
    image_specs_json = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def summary(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "title": self.title,
            "mode": self.mode,
            "blog_kind": self.blog_kind,
            "needs_research": bool(self.needs_research),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
