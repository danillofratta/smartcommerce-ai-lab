from langchain_core.messages import HumanMessage

from graph import app

if __name__ == "__main__":
    customer_request = (
        "Comprei um fone Bluetooth há 8 dias, mas o produto chegou com defeito. "
        "Gostaria de trocar."
    )
    print("Cliente:", flush=True)
    print(customer_request, flush=True)

    final_state = app.invoke(
        {
            "messages": [HumanMessage(content=customer_request)]
        }
    )
    print("\n[ATENDIMENTO]")
    print(final_state["messages"][-1].content)
    print("\n[END]")

