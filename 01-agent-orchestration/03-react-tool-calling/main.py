import json
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError

from graph import build_graph


def create_model() -> ChatGroq:
    load_dotenv()

    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")

    print(f"Usando modelo: {model_name}")

    return ChatGroq(model=model_name, temperature=0, max_retries=0)

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
    llm = create_model()
    app = build_graph(llm)

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
    except GraphRecursionError:
        print("Limite de etapas atingido. Não foi possível concluir o atendimento.")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

    print("\n[END]")        
