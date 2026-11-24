import operator
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field

MAX_STEPS = 8
MAX_AGENT_CALLS = 2
RECURSION_LIMIT = 2 * MAX_STEPS + 5
AgentName = Literal['pedidos', 'pagamentos', 'logistica', 'reembolsos', 'FINISH']


class SupervisorDecision(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    next_agent: AgentName
    reason: str = Field(min_length=1, max_length=1000)


class AgentResult(TypedDict):
    agent: str
    data: dict
    summary: str


class State(TypedDict):
    request: str
    order_id: str
    next_agent: AgentName
    decision_reason: str
    agent_results: Annotated[list[AgentResult], operator.add]
    execution_history: Annotated[list[dict], operator.add]
    steps: int
    final_status: str
    final_response: str
