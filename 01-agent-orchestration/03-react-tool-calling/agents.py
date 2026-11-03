from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import Runnable

from prompts import AGENT_PROMPT
from state import State


def call_agent(state: State, llm_with_tools: Runnable) -> dict[str, list[AIMessage]]:
    instructions = SystemMessage(content=AGENT_PROMPT)
    response = llm_with_tools.invoke(
        [instructions, *state["messages"]]
    )
    return {"messages": [response]}
