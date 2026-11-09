from functools import partial

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.language_models.chat_models import BaseChatModel
from agents import agente_estoque, agente_financeiro, agente_logistica, agente_consolidador
from state import State

def build_graph(llm: BaseChatModel) -> CompiledStateGraph:
    workflow = StateGraph(State)

    workflow.add_node("estoque", partial(agente_estoque, llm=llm))
    workflow.add_node("financeiro", partial(agente_financeiro, llm=llm))
    workflow.add_node("logistica", partial(agente_logistica, llm=llm))
    workflow.add_node("consolidador", partial(agente_consolidador, llm=llm))

    workflow.add_edge(START, "estoque")
    workflow.add_edge(START, "financeiro")
    workflow.add_edge(START, "logistica")

    # Aguarda as três avaliações antes de executar a consolidação.
    workflow.add_edge(["estoque", "financeiro", "logistica"], "consolidador")

    workflow.add_edge("consolidador", END)

    app = workflow.compile()
    return app
