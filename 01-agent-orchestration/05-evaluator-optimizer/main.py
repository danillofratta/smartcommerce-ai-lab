import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data import SAMPLE_ORDER, SAMPLE_REQUEST
from graph import build_graph


def create_model() -> ChatGroq:
    load_dotenv()

    model_name = os.getenv("LLM_MODEL")

    if not model_name:
        raise ValueError(
            "Defina LLM_MODEL no .env ou nas variáveis de ambiente."
        )

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "Defina GROQ_API_KEY no .env ou nas variáveis de ambiente."
        )

    return ChatGroq(
        model=model_name,
        temperature=0,
        max_retries=0,
    )


def main() -> None:

    app = build_graph(create_model())

    state = {
        "request": SAMPLE_REQUEST,
        "order": SAMPLE_ORDER.copy(),
    }

    print(f"Solicitação: {state['request']}")

    try:
        for update_by_node in app.stream(
            state,
            config={"recursion_limit": 20},
            stream_mode="updates",
        ):
            for node, update in update_by_node.items():
                state.update(update)

                print(f"\nNó: {node}")

                if node == "policy_check_node":
                    print(f"Política: {update['policy_result']}")

                elif node == "refund_generator_node":
                    print(
                        f"Tentativa {update['attempts']}: "
                        f"{update['draft_response']}"
                    )

                elif node == "evaluator_node":
                    verdict = (
                        "APROVADO"
                        if update["evaluation_ok"]
                        else "REPROVADO"
                    )

                    print(f"Avaliação: {verdict}")
                    print(f"Feedback: {update['feedback']}")

                elif node == "finalizer_node":
                    print(
                        f"Status final: {update['final_status']}"
                    )

    except Exception as exc:
        print(
            f"Falha técnica na execução: "
            f"{type(exc).__name__}: {exc}"
        )
        raise

    print("\nExecução encerrada")
    print(f"Status: {state['final_status']}")

    if state["final_status"] == "TEXT_APPROVED":
        print(
            f"Resposta oficial:\n{state['final_response']}"
        )
    else:
        print(
            "Nenhuma resposta foi aprovada. "
            "É necessária revisão manual."
        )


if __name__ == "__main__":
    main()