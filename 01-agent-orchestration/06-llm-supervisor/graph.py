from functools import partial

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents import (
    finalizer_node, logistica_node, pagamentos_node, pedidos_node,
    reembolsos_node, solicitacao_node, supervisor_node,
)
from state import AgentName, State, SupervisorDecision


def router(state: State) -> AgentName:
    return state['next_agent']


def build_graph(llm: BaseChatModel) -> CompiledStateGraph:
    supervisor = llm.with_structured_output(
        SupervisorDecision, method='function_calling', include_raw=True,
    )
    workflow = StateGraph(State)
    workflow.add_node('solicitacao', solicitacao_node)
    workflow.add_node('supervisor', partial(supervisor_node, supervisor=supervisor))
    
    specialists = {
        'pedidos': pedidos_node, 
        'pagamentos': pagamentos_node,
        'logistica': logistica_node, 
        'reembolsos': reembolsos_node,
    }

    for name, node in specialists.items():
        workflow.add_node(name, node)
        workflow.add_edge(name, 'supervisor')

    workflow.add_node('FINISH', finalizer_node)
    
    workflow.add_edge(START, 'solicitacao')
    workflow.add_edge('solicitacao', 'supervisor')
    workflow.add_conditional_edges(
        'supervisor', 
        router, 
        {
            **{name: name for name in specialists}, 
            'FINISH': 'FINISH',
        }
    )
    workflow.add_edge('FINISH', END)
    return workflow.compile()
