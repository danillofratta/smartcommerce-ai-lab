PEDIDOS_SIMULADOS = {
    1024: {
        "order_id": 1024,
        "customer": "Maria",
        "product": "Notebook Dell",
        "total": 3200.00,
        "quantity": 1,
        "zipcode": "93500-000",
        "payment_status": "approved",
        "stock_available": 5,
        "delivery_available": True
    },
    1025: {
        "order_id": 1025,
        "customer": "João",
        "product": "Smartphone",
        "total": 1800.00,
        "quantity": 2,
        "zipcode": "01000-000",
        "payment_status": "declined",  # Pagamento Recusado
        "stock_available": 10,
        "delivery_available": True
    },
    1026: {
        "order_id": 1026,
        "customer": "Ana",
        "product": "Cadeira Gamer",
        "total": 1200.00,
        "quantity": 3,
        "zipcode": "99999-999",
        "payment_status": "approved",
        "stock_available": 0,  # Sem Estoque
        "delivery_available": False  # Sem entrega para o CEP
    }
}