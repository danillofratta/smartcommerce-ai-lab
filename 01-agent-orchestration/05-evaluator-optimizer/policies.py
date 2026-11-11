"""Regras fictícias para estudo; não representam legislação brasileira."""
from state import PolicyResult


def check_policy(order: dict) -> PolicyResult:
    days_received = order.get('days_received')
    has_defect = order.get('has_defect')
    value_cents = order.get('value_cents')
    if (
        type(days_received) is not int or days_received < 0
        or type(has_defect) is not bool
        or type(value_cents) is not int or value_cents < 0
    ):
        return 'NEEDS_INFO'
    deadline = 30 if has_defect else 7
    if days_received > deadline:
        return 'NOT_ELIGIBLE'
    if value_cents > 200_000:
        return 'HUMAN_REVIEW_REQUIRED'
    return 'ELIGIBLE'
