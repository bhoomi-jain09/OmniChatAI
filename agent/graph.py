from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agent.state import chatstate
from agent.nodes import chatnode
from retrieve_all_threads.tool import tools
from langgraph.checkpoint.memory import checkpointer

tool_node = ToolNode(tools)

graph = StateGraph(chatstate)
graph.add_node("chatnode", chatnode)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatnode")
graph.add_conditional_edges("chatnode", tools_condition)
graph.add_edge("tools", "chatnode")

workflow = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads() -> list:
    """Return all thread IDs that have at least one checkpoint."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)
