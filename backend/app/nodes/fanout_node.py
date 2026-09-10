"""Fanout node: spins one worker per task using LangGraph Send."""
from langgraph.types import Send

from app.schemas.state import State


# this fanout is used for spinning different workers
def fanout(state):  # workers are spawned using the Send function and puts in results
    ans = []
    # this worker is being called and returned from here so the sections is added in the state
    for tasks in state["plan"].tasks:
        ans.append(Send(
            "worker",
            {
                "task": tasks,
                "topic": state["topic"],
                "plan": state["plan"],
                "as_of": state["as_of"],
                "recency_bias": state["recency_days"],
                "mode": state["mode"],
                "evidence": [e.model_dump() for e in state.get("evidence", [])]
            }
            ))
    return ans
