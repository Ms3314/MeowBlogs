"""Shared LLM client used by every agent node (mirrors the notebook's `llm`)."""
from langchain_openai import ChatOpenAI

from app.config import LLM_MODEL

llm = ChatOpenAI(model=LLM_MODEL)
