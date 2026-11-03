from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from prompts import (
    PAGAMENTOS_PROMPT, PEDIDOS_PROMPT, ROUTER_PROMPT,
    SUPORTE_PROMPT, VENDAS_PROMPT,
)
from state import RouterResult, State


def _run_agent(
    state: State, agent_name: str, role_prompt: str, llm: BaseChatModel
) -> AIMessage:
    response = llm.invoke([SystemMessage(content=role_prompt), *state["messages"]])
    response.name = agent_name
    return response

def agent_vendas(state: State, *, llm: BaseChatModel) -> dict:
    result = _run_agent(state, "Agente de Vendas", VENDAS_PROMPT, llm)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_pedidos(state: State, *, llm: BaseChatModel) -> dict:
    result = _run_agent(state, "Agente de Pedidos", PEDIDOS_PROMPT, llm)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_pagamentos(state: State, *, llm: BaseChatModel) -> dict:
    result = _run_agent(state, "Agente de Pagamentos", PAGAMENTOS_PROMPT, llm)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_suporte(state: State, *, llm: BaseChatModel) -> dict:
    result = _run_agent(state, "Agente de Suporte", SUPORTE_PROMPT, llm)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_router(state: State, *, llm: BaseChatModel) -> dict:
    structured_model = llm.with_structured_output(RouterResult)
    result = structured_model.invoke(
        [SystemMessage(content=ROUTER_PROMPT), *state["messages"]]
    )
    return {
        "agent_name": result.agent_name,
        "motivo": result.motivo
    }
