from typing import Annotated, Literal, NotRequired, TypedDict
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

AgentName = Literal["vendas", "pedidos", "pagamentos", "suporte"]


class RouterResult(BaseModel):
    agent_name: AgentName
    motivo: str

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent_name: NotRequired[AgentName]
    motivo: NotRequired[str]
    resposta: NotRequired[str]
