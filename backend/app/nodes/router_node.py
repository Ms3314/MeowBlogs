"""Router node: decides whether web research is needed before planning."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import llm
from app.schemas.content import RouterDecision
from app.schemas.state import State

# we will make a router first which we decide if research/internet search is required or not
ROUTER_SYSTEM = """
    You are a routing module for a technical blog planner.
    Decide whether web research is needed BEFORE planning.

    Modes:
    - closed_book (needs_research=false):
    Evergreen topics where correctness does not depend on recent facts (concepts, fundamentals).
    - hybrid (needs_research=true):
    Mostly evergreen but needs up-to-date examples/tools/models to be useful.
    - open_book (needs_research=true):
    Mostly volatile: weekly roundups, "this week", "latest", rankings, pricing, policy/regulation.

    If needs_research=true:
    - Output 3–10 high-signal queries.
    - Queries should be scoped and specific (avoid generic queries like just "AI" or "LLM").
    - If user asked for "last week/this week/latest", reflect that constraint IN THE QUERIES.
"""


def router_node(state: State) -> dict:
    # we take the relevant stuff at the node like
    topic = state["topic"]
    decider = llm.with_structured_output(RouterDecision)
    llm_out = decider.invoke(
        [
            SystemMessage(
                content=ROUTER_SYSTEM
            ),
            HumanMessage(
                content=f"Topic : {topic} \n as of Date : {state['as_of']}"
            )
        ]
    )
    recency_days = None
    if (llm_out.mode == "hybrid"):
        recency_days = 7
    elif (llm_out.mode == "open_book"):
        recency_days = 30
    else:
        recency_days = 3650

    return {
        "needs_research": llm_out.needs_research,
        "mode": llm_out.mode,
        "queries": llm_out.queries,  # these queries are high signals queries on which we probably need to search
        "recency_days": recency_days
    }  # on the internet


def route_next(state: State) -> str:
    return "research" if state["needs_research"] else "orchestrator"
