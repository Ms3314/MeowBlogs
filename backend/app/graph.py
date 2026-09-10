"""LangGraph wiring, ported 1:1 from 1main_research_fineimages.ipynb.

Reducer subgraph:  merge_content -> decide_images -> generate_and_place_images
Main graph:        router_node -> (research_node) -> orchestrator -> fanout(worker) -> reducer
"""
from langgraph.graph import END, START, StateGraph

from app.nodes.decide_images_node import decide_images
from app.nodes.fanout_node import fanout
from app.nodes.generate_images_node import generate_and_place_images
from app.nodes.merge_node import merge_content
from app.nodes.orchestrator_node import orchestrator
from app.nodes.research_node import research_node
from app.nodes.router_node import route_next, router_node
from app.nodes.worker_node import worker
from app.schemas.state import State


def build_reducer_subgraph():
    # build reducer graph
    reducer_graph = StateGraph(State)
    reducer_graph.add_node("merge_content", merge_content)
    reducer_graph.add_node("decide_images", decide_images)
    reducer_graph.add_node("generate_and_place_images", generate_and_place_images)

    reducer_graph.add_edge(START, "merge_content")
    reducer_graph.add_edge("merge_content", "decide_images")
    reducer_graph.add_edge("decide_images", "generate_and_place_images")
    reducer_graph.add_edge("generate_and_place_images", END)
    return reducer_graph.compile()


def build_graph():
    reducer_subgraph = build_reducer_subgraph()

    g = StateGraph(State)
    g.add_node("orchestrator", orchestrator)
    g.add_node("worker", worker)
    g.add_node("reducer", reducer_subgraph)
    g.add_node("router_node", router_node)
    g.add_node("research_node", research_node)

    # g.add_edge(START , "orchestrator")
    g.add_edge(START, "router_node")
    g.add_conditional_edges("router_node", route_next, {"research": "research_node", "orchestrator": "orchestrator"})
    g.add_edge("research_node", "orchestrator")
    g.add_conditional_edges("orchestrator", fanout, ["worker"])
    g.add_edge("worker", "reducer")
    g.add_edge("reducer", END)

    return g.compile()


graph_app = build_graph()
