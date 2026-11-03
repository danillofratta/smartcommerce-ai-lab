import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from graph import build_graph


def create_model() -> ChatGroq:
    load_dotenv()
    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")
    return ChatGroq(model=model_name, temperature=0, max_retries=0)


def main() -> None:
    llm = create_model()
    app = build_graph(llm)
    print(f"Usando modelo: {llm.model_name}")
    customer_request = input("Digite a solicitação do cliente: ")
    final_state = app.invoke(
        {
            "messages": [HumanMessage(content=customer_request)]
        }
    )
    print("Área:", final_state["agent_name"])
    print("Motivo:", final_state["motivo"])
    print("Resposta:", final_state["resposta"])


if __name__ == "__main__":
    main()
