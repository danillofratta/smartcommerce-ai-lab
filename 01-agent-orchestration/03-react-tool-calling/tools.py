

from langchain.tools import tool
from data import get_order_store


@tool
def get_order(order_id: str) -> dict:
    """Consulta o pedido pelo ID fornecido"""
    order = get_order_store(order_id)
    if not order:
        return {"error": "Pedido não encontrado"}
    return {
        "order_id": order_id,
        "customer": order["customer"],
        "total_cents": order["total_cents"],
        "status": order["status"]
    }

@tool
def get_payment(order_id: str) -> dict:
    """Consulta o pagamento pelo ID do pedido fornecido"""
    order = get_order_store(order_id)
    if not order:
        return {"error": "Pedido não encontrado"}
    return {
        "payment_id": order_id,
        "customer": order["customer"],
        "total_cents": order["total_cents"],
        "status": order["payment_status"]
    }

@tool
def get_delivery(order_id: str) -> dict:
    """Consulta a entrega pelo ID do pedido fornecido"""
    order = get_order_store(order_id)
    if not order:
        return {"error": "Pedido não encontrado"}
    return {
        "delivery_id": order_id,
        "customer": order["customer"],
        "total_cents": order["total_cents"],
        "estimated_delivery": order["estimated_delivery"],
        "status": order["delivery_status"]
    }