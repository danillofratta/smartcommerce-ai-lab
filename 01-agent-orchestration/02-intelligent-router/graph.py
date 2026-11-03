from functools import partial

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents import agent_router, agent_vendas, agent_pedidos, agent_pagamentos, agent_suporte
from state import State

def build_graph(llm: BaseChatModel) -> CompiledStateGraph:
    """Build the workflow with the model supplied by the caller."""
    workflow = StateGraph(State)

    workflow.add_node("router", partial(agent_router, llm=llm))
    workflow.add_node("vendas", partial(agent_vendas, llm=llm))
    workflow.add_node("pedidos", partial(agent_pedidos, llm=llm))
    workflow.add_node("pagamentos", partial(agent_pagamentos, llm=llm))
    workflow.add_node("suporte", partial(agent_suporte, llm=llm))

    members = ["vendas", "pedidos", "pagamentos", "suporte"]
    for member in members:
        workflow.add_edge(member, END)

    workflow.add_conditional_edges(
        "router",
        lambda state: state["agent_name"],
        {name: name for name in members},
    )
    workflow.set_entry_point("router")
    return workflow.compile()
