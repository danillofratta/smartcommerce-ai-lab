import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from prompts import ANALYST_PROMPT, POLICIES_PROMPT, SERVICE_PROMPT
from state import State

load_dotenv()

model_name = os.getenv("LLM_MODEL")
if not model_name:
    raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")

llm = ChatGroq(model=model_name, temperature=0, max_retries=0)


def _run_agent(state: State, agent_name: str, role_prompt: str) -> AIMessage:
    response = llm.invoke(
        [SystemMessage(content=role_prompt), *state["messages"]]
    )
    response.name = agent_name
    return response

def agent_analyst_node(state: State) -> dict:
    result = _run_agent(state, "analyst", ANALYST_PROMPT)
    print("\n[ANALISTA]", flush=True)
    print(result.content, flush=True)
    return {"messages": [result]}

def agent_policies_node(state: State) -> dict:
    result = _run_agent(state, "policies", POLICIES_PROMPT)
    print("\n[POLÍTICAS]", flush=True)
    print(result.content, flush=True)
    return {"messages": [result]}

def agent_service_node(state: State) -> dict:
    result = _run_agent(state, "service", SERVICE_PROMPT)
    return {"messages": [result]}
