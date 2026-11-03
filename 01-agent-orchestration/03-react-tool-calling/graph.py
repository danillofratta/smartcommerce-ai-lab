from functools import partial

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agents import call_agent
from state import State
from tools import get_delivery, get_order, get_payment


def build_graph(llm: BaseChatModel) -> CompiledStateGraph:
    """Bind tool schemas and build an executable graph without provider setup."""
    list_tools = [get_order, get_payment, get_delivery]
    llm_with_tools = llm.bind_tools(list_tools)
    workflow = StateGraph(State)

    workflow.add_node("call_agent", partial(call_agent, llm_with_tools=llm_with_tools))
    workflow.add_node("tools", ToolNode(list_tools))

    workflow.add_edge(START, "call_agent")

    workflow.add_conditional_edges(
        "call_agent",
        tools_condition,
    )

    workflow.add_edge("tools", "call_agent")

    return workflow.compile()
