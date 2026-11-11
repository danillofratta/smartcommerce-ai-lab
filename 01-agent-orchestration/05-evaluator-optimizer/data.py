"""Entrada sintética do laboratório. Valores financeiros em centavos."""
SAMPLE_REQUEST = (
    'Comprei um notebook há 12 dias, recebi há 5 dias e quero devolver '
    'porque não gostei do produto. Paguei R$ 1.800.'
)
SAMPLE_ORDER = {
    'days_since_purchase': 12,
    'days_received': 5,
    'has_defect': False,
    'value_cents': 180_000,
}
