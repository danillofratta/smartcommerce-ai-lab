import argparse
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data import SAMPLE_ORDER, SAMPLE_REQUEST
from graph import build_graph
from state import RECURSION_LIMIT


def create_model() -> ChatGroq:
    load_dotenv()
    model_name = os.getenv('LLM_MODEL')
    if not model_name:
        raise ValueError('Defina LLM_MODEL no .env ou nas variáveis de ambiente.')
    if not os.getenv('GROQ_API_KEY'):
        raise ValueError('Defina GROQ_API_KEY no .env ou nas variáveis de ambiente.')
    return ChatGroq(model=model_name, temperature=0, max_retries=0, timeout=30)


def main() -> None:
    parser = argparse.ArgumentParser(description='Lab 06: LLM Supervisor')
    parser.add_argument('--request', default=SAMPLE_REQUEST)
    parser.add_argument('--order-id', default=SAMPLE_ORDER['order_id'])
    args = parser.parse_args()

    model = create_model()

    print(f'LIVE: Groq / {model.model_name}; dados de negócio fictícios.')

    app = build_graph(model)
    initial = {'request': args.request, 'order_id': args.order_id}
    print(f"Solicitação: {args.request}")
    # values includes reducers: a plain dict.update over updates would lose history.
    final = None
    previous_history, previous_results = [], []
    for state in app.stream(initial, config={'recursion_limit': RECURSION_LIMIT}, stream_mode='values'):
        final = state
        history = state.get('execution_history', [])
        results = state.get('agent_results', [])
        if history and len(history) > len(previous_history):
            decision = history[-1]
            print(f"\nSupervisor [{decision['source']}]: {decision['next_agent']} — {decision['reason']}")
        if results and len(results) > len(previous_results):
            print(f"Especialista {results[-1]['agent']}: {results[-1]['summary']}")
        previous_history, previous_results = history, results
    print(f"\nStatus: {final['final_status']}")
    print(f"Resposta:\n{final['final_response']}")


if __name__ == '__main__':
    main()
