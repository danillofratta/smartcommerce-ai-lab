from langgraph.graph import END, StateGraph

from agents import agent_analyst_node, agent_policies_node, agent_service_node
from state import State

workflow = StateGraph(State)

workflow.add_node("analyst", agent_analyst_node)
workflow.add_node("policies", agent_policies_node)
workflow.add_node("service", agent_service_node)

workflow.add_edge("analyst", "policies")
workflow.add_edge("policies", "service")
workflow.add_edge("service", END)

workflow.set_entry_point("analyst")

app = workflow.compile()
