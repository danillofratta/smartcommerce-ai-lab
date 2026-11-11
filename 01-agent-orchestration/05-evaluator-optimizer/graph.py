from functools import partial
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents import (
    evaluator_node, finalizer_node, policy_check_node, refund_generator_node, route_after_evaluation,
)
from state import EvaluationResult, RefundState


def build_graph(llm: BaseChatModel) -> CompiledStateGraph:
    evaluator = llm.with_structured_output(EvaluationResult, include_raw=True)
    
    workflow = StateGraph(RefundState)
    
    workflow.add_node('policy_check_node', policy_check_node)
    workflow.add_node('refund_generator_node', partial(refund_generator_node, llm=llm))
    workflow.add_node('evaluator_node', partial(evaluator_node, evaluator=evaluator))
    workflow.add_node('finalizer_node', finalizer_node)
    
    workflow.add_edge(START, 'policy_check_node')
    workflow.add_edge('policy_check_node', 'refund_generator_node')
    workflow.add_edge('refund_generator_node', 'evaluator_node')
    
    workflow.add_conditional_edges(
        'evaluator_node', 
        route_after_evaluation, {
        "RETRY": "refund_generator_node",
        "FINALIZE": "finalizer_node",
    })

    workflow.add_edge("finalizer_node", END)

    return workflow.compile()
