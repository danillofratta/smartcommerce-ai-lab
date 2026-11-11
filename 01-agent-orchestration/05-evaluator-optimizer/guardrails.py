"""Validações ilustrativas para o laboratório."""

import re

from state import PolicyResult


_COMPLETED_OPERATION = re.compile(
    r"\b(?:reembolso|estorno)\b.{0,70}?\b(?:já\s+)?"
    r"(?:foi|está|será)\s+"
    r"(?:realizado|feito|efetuado|processado|executado|"
    r"concluído|aprovado)\b",
    re.IGNORECASE,
)


def _claims_completed_operation(text: str) -> bool:
    for match in _COMPLETED_OPERATION.finditer(text):
        if re.search(
            r"\b(?:não|nunca|jamais)\b",
            match.group(0),
        ):
            continue

        prefix = text[max(0, match.start() - 25):match.start()]

        if re.search(
            r"\b(?:nenhum|nenhuma|sem)\s*$",
            prefix,
        ):
            continue

        return True

    return False


def validate_draft(
    draft: str,
    policy: PolicyResult,
) -> list[str]:

    issues: list[str] = []
    text = " ".join(draft.lower().split())

    if not text:
        issues.append("O rascunho está vazio.")

    if _claims_completed_operation(text):
        issues.append(
            "O rascunho afirma ou promete uma operação "
            "financeira não executada."
        )

    if policy == "HUMAN_REVIEW_REQUIRED":
        if not any(
            term in text
            for term in (
                "análise humana",
                "revisão humana",
                "aprovação humana",
            )
        ):
            issues.append(
                "É obrigatório informar a necessidade "
                "de análise humana."
            )

    if policy == "NOT_ELIGIBLE":
        if "você pode solicitar a devolução" in text:
            issues.append(
                "O texto contradiz a inelegibilidade "
                "determinada pela política."
            )

    return issues


def render_safe_response(policy: PolicyResult) -> str:
    """Gera uma resposta oficial sem texto livre do LLM."""

    responses = {
        "ELIGIBLE": (
            "Sua solicitação atende à política fictícia "
            "da SmartCommerce para iniciar a análise "
            "de devolução ou troca. "
            "Nenhum reembolso foi executado."
        ),
        "NOT_ELIGIBLE": (
            "Pelas informações fornecidas, o prazo "
            "previsto na política fictícia da SmartCommerce "
            "foi ultrapassado. "
            "Nenhum reembolso foi executado."
        ),
        "NEEDS_INFO": (
            "Precisamos confirmar os dias desde o "
            "recebimento, a existência de defeito e "
            "o valor pago antes de avaliar sua solicitação. "
            "Nenhum reembolso foi executado."
        ),
        "HUMAN_REVIEW_REQUIRED": (
            "Sua solicitação exige análise humana antes "
            "de qualquer decisão. "
            "Nenhum reembolso foi aprovado ou executado."
        ),
    }

    return responses[policy]