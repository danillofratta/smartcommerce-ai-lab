list_orders = {
    1024: {
        "customer": "Maria",
        "product": "Notebook Dell",
        "status": "confirmed",
        "total_cents": 320000,
        "payment_status": "approved",
        "delivery_status": "shipped",
        "estimated_delivery": "05/11/2026",
    },
    1025: {
        "customer": "João",
        "product": "Mouse Logitech",
        "status": "pending_payment",
        "total_cents": 15000,
        "payment_status": "pending",
        "delivery_status": "pending",
        "estimated_delivery": "05/15/2026"
    }
}

def get_order_store(order_id: int | str) -> dict:
    # Converte para int com segurança (caso venha como string)
    try:
        order_key = int(order_id)
    except (ValueError, TypeError):
        return {}
    
    # Retorna o dicionário do pedido ou {} se não encontrar
    return list_orders.get(order_key, {})
