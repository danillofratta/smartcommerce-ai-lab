import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from graph import build_graph
from data import PEDIDOS_SIMULADOS

def create_model() -> ChatGroq:
    load_dotenv()

    model_name = os.getenv("LLM_MODEL")
    if not model_name:
        raise ValueError("Defina LLM_MODEL no .env ou nas variáveis de ambiente.")

    print(f"Usando modelo: {model_name}")

    return ChatGroq(model=model_name, temperature=0, max_retries=0)

def analisar_pedido(app, order_id: int):
    pedido = PEDIDOS_SIMULADOS.get(order_id)
    if not pedido:
        raise ValueError(f"Pedido com ID {order_id} não encontrado.")

    print(f"\n==========================================")
    print(f"  INICIANDO ANÁLISE DO PEDIDO {order_id}")
    print(f"==========================================")

    estado_inicial = {"pedido": pedido, "avaliacoes": []}

    for step in app.stream(estado_inicial, stream_mode="updates"):
        for node, output in step.items():
            print(f"Node: {node}")
            if "avaliacoes" in output:
                print(f"Avaliação do especialista: {output['avaliacoes']}")
            elif "parecer_final" in output:
                print(f"Status do pedido: {output['status_pedido']}")
                print(f"Parecer final: {output['parecer_final']}")

def main() -> None:
    app = build_graph(create_model())
    for order_id in PEDIDOS_SIMULADOS:
        analisar_pedido(app, order_id)


if __name__ == "__main__":
    main()
