import os

from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import  add_messages

load_dotenv()

model_name = os.getenv("LLM_MODEL")
if not model_name:
    raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")

print(f"Usando modelo: {model_name}")

llm = ChatGroq(model=model_name, temperature=0, max_retries=0)

class RouterResult(BaseModel):
    agent_name: Literal["vendas", "pedidos", "pagamentos", "suporte"]
    motivo: str

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent_name: str
    motivo: str
    resposta: str

def _run_agent(state: State, agent_name: str, role_prompt: str) -> AIMessage:
    response = llm.invoke([SystemMessage(content=role_prompt), *state["messages"]])
    response.name = agent_name
    return response

def agent_vendas(state: State) -> dict:
    prompt = """
    #CONTEXT
    Você é um agente de vendas.

    #INSTRUCTIONS
    Responda ao cliente de forma educada e profissional.

    #OUTPUT
    Produza somente o texto da resposta ao cliente.
    
    """
    result = _run_agent(state, "Agente de Vendas", prompt)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_pedidos(state: State) -> dict:
    prompt = """
    #CONTEXT
    Você é um agente de pedidos.

    #INSTRUCTIONS
    Responda ao cliente de forma educada e profissional.

    #OUTPUT
    Produza somente o texto da resposta ao cliente.

    """
    result = _run_agent(state, "Agente de Pedidos", prompt)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_pagamentos(state: State) -> dict:
    prompt = """
    #CONTEXT
    Você é um agente de pagamentos.

    #INSTRUCTIONS
    Responda ao cliente de forma educada e profissional.

    #OUTPUT
    Produza somente o texto da resposta ao cliente.
    """
    result = _run_agent(state, "Agente de Pagamentos", prompt)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_suporte(state: State) -> dict:
    prompt = """
    #CONTEXT
    Você é um agente de suporte.

    #INSTRUCTIONS
    Responda ao cliente de forma educada e profissional.

    #OUTPUT
    Produza somente o texto da resposta ao cliente.

    """
    result = _run_agent(state, "Agente de Suporte", prompt)
    return {
        "messages": [result],
        "resposta": result.content
    }

def agent_router(state: State) -> dict:
    prompt = """
    #CONTEXT
    Você é um agente roteador.

    #INSTRUCTIONS
    Direcione o cliente para o agente apropriado com base na solicitação.

    Escolha pela intenção da solicitação:
    - vendas: interesse em comprar produtos.
    - pedidos: entrega ou acompanhamento de pedido.
    - pagamentos: cobrança ou confirmação de pagamento.
    - suporte: problemas técnicos ou solicitação pouco clara.

    Retorne a área escolhida em agent_name.
    Retorne uma justificativa curta em motivo.

    """
    structured_model = llm.with_structured_output(RouterResult)
    result = structured_model.invoke(
        [SystemMessage(content=prompt), *state["messages"]]
    )
    return {
        "agent_name": result.agent_name,
        "motivo": result.motivo
    }

workflow = StateGraph(State)

workflow.add_node("router", agent_router)
workflow.add_node("vendas", agent_vendas)
workflow.add_node("pedidos", agent_pedidos)
workflow.add_node("pagamentos", agent_pagamentos)
workflow.add_node("suporte", agent_suporte)

for member in ["vendas", "pedidos", "pagamentos", "suporte"]:
    workflow.add_edge(member, END)

workflow.add_conditional_edges(
    "router",
    lambda state: state["agent_name"],
    {
        name: name 
        for name in ["vendas", "pedidos", "pagamentos", "suporte"]
    },
)

workflow.set_entry_point("router")

app = workflow.compile()

if __name__ == "__main__":
    customer_request = input("Digite a solicitação do cliente: ")
    final_state = app.invoke(
        {
            "messages": [HumanMessage(content=customer_request)]
        }
    )
    print("Área:", final_state["agent_name"])
    print("Motivo:", final_state["motivo"])
    print("Resposta:", final_state["resposta"])
