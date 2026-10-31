import os

import json

from langchain_core.messages import ToolMessage
from dotenv import load_dotenv
from tools import get_order, get_payment, get_delivery
from langgraph.prebuilt import ToolNode,  tools_condition
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import START, MessagesState, StateGraph

load_dotenv()

model_name = os.getenv("LLM_MODEL")
if not model_name:
    raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")

print(f"Usando modelo: {model_name}")


llm = ChatGroq(model=model_name, temperature=0, max_retries=0)
list_tools = [get_order, get_payment, get_delivery]
llm_with_tools = llm.bind_tools(list_tools)

def call_agent(state: MessagesState) -> dict:
    instructions = SystemMessage(content="""
        Você é o atendente da SmartCommerce.
        Responda em português, com clareza e cordialidade.

        Consulte primeiro o pedido para verificar sua existência.
        Se não encontrar, informe ao cliente e encerre.
        Quando perguntarem sobre pagamento, consulte a ferramenta de pagamento.
        Quando perguntarem sobre entrega, consulte a ferramenta de entrega.
        Use somente os dados retornados pelas ferramentas.
        Se uma informação estiver ausente ou unknown, informe que está indisponível.
        Na resposta final, cumprimente o cliente pelo nome quando disponível.
        """)    
    response = llm_with_tools.invoke(
        [instructions, *state["messages"]]
    )
    return {"messages": [response]}

def build_graph() -> StateGraph:
    workflow = StateGraph(MessagesState)

    workflow.add_node("call_agent", call_agent)
    workflow.add_node("tools", ToolNode(list_tools))

    workflow.add_edge(START, "call_agent")

    workflow.add_conditional_edges(
        "call_agent",
        tools_condition,
    )

    workflow.add_edge("tools", "call_agent")

    return workflow

workflow = build_graph()

app = workflow.compile()

def print_message(message: BaseMessage) -> None:
    if isinstance(message, AIMessage):
        if message.tool_calls:
            print("\n[AGENT]")
            for call in message.tool_calls:
                name = call["name"].lstrip("_")
                arguments = ", ".join(
                    f"{key}={value}"
                    for key, value in call["args"].items()
                )
                print(f"Solicitando {name}({arguments})")
        else:
            print("\n[AGENT - FINAL]")
            print(message.content)

    elif isinstance(message, ToolMessage):
        name = (message.name or "unknown").lstrip("_")
        print(f"\n[TOOL: {name}]")

        try:
            data = json.loads(message.content)
        except (json.JSONDecodeError, TypeError):
            print(message.content)
            return

        if not isinstance(data, dict):
            print(data)
            return

        if "error" in data:
            print(f"Erro: {data['error']}")
            return

        status = data.get("status", "unknown")
        if name == "get_order":
            print(f"Pedido encontrado: {status}")
        else:
            print(f"Status: {status}")

        if data.get("estimated_delivery"):
            print(f"Previsão: {data['estimated_delivery']}")


if __name__ == "__main__":
    print("SMARTCOMMERCE AI — REACT AGENT")

    customer_request = input("Digite a solicitação do cliente: ")
    print(f"\nCliente:\n{customer_request}")

    initial_state = {
        "messages": [HumanMessage(content=customer_request)]
    }

    config = {
        "recursion_limit": 12
    }

    try:
        for step in app.stream(initial_state, config=config, stream_mode="updates"):
            for update in step.values():
                for message in update.get("messages", []):
                    print_message(message)
    except Exception as e:
        print(f"Erro durante a execução: {e}")

    print("\n[END]")        
