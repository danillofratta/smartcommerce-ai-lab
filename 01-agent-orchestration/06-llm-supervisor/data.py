"""Synthetic fixtures and fictional policy v1. No external commerce services."""

SAMPLE_ORDER = {'order_id': '1024', 'status': 'SHIPPED', 'product': 'Notebook'}
SAMPLE_REQUEST = (
    'Fiz o pedido 1024, o pagamento foi aprovado, mas ainda não recebi o produto. '
    'Se não chegar amanhã, quero cancelar e receber meu dinheiro de volta.'
)
ORDERS = {'1024': SAMPLE_ORDER}
PAYMENTS = {'1024': {'status': 'APPROVED', 'amount_cents': 250000}}
SHIPMENTS = {'1024': {'status': 'IN_TRANSIT', 'eta_days': 1, 'delivered': False}}


def refund_policy(order_id: str) -> dict:
    """Evaluated in Python; this never authorizes a transfer."""
    order = ORDERS.get(order_id)
    payment = PAYMENTS.get(order_id)
    shipment = SHIPMENTS.get(order_id)
    if not order or not payment or not shipment:
        return {'status': 'NEEDS_INFO', 'explanation': 'Faltam dados para analisar o reembolso.'}
    if payment['status'] != 'APPROVED':
        return {'status': 'NO_APPROVED_PAYMENT', 'explanation': 'Não há pagamento aprovado para reembolsar.'}
    if order['status'] == 'PROCESSING':
        return {'status': 'ELIGIBLE_TO_REQUEST', 'explanation': 'Antes do envio, pode solicitar cancelamento para análise.'}
    if shipment['delivered']:
        return {'status': 'HUMAN_REVIEW', 'explanation': 'Produto entregue: devolução depende de análise humana.'}
    if shipment['eta_days'] < 0:
        return {'status': 'HUMAN_REVIEW', 'explanation': 'Entrega atrasada: pode solicitar análise humana de cancelamento/reembolso.'}
    return {
        'status': 'WAIT_FOR_DELIVERY',
        'explanation': 'A previsão ainda não venceu. Se não chegar até o prazo informado, solicite análise de cancelamento/reembolso. Não há aprovação automática.',
    }
