from typing import Literal, TypedDict
from pydantic import BaseModel, Field
from typing import NotRequired

MAX_ATTEMPTS = 3

PolicyResult = Literal['ELIGIBLE', 'NOT_ELIGIBLE', 'NEEDS_INFO', 'HUMAN_REVIEW_REQUIRED']
FinalStatus = Literal['PENDING', 'APPROVED', 'REJECTED']

class RefundState(TypedDict):
    request: str
    order: dict

    policy_result: NotRequired[PolicyResult]
    draft_response: NotRequired[str]
    feedback: NotRequired[str]
    evaluation_ok: NotRequired[bool]
    attempts: NotRequired[int]
    guardrail_issues: NotRequired[list[str]]
    # APPROVED refere-se ao texto, não à autorização de um reembolso.
    final_status: NotRequired[FinalStatus]
    final_response: NotRequired[str]    


class EvaluationResult(BaseModel):
    approved: bool = Field(strict=True, description='Indica se o texto foi aprovado')
    feedback: str = Field(description='Feedback para corrigir o rascunho')
    missing_requirements: list[str] = Field(description='Requisitos ausentes no texto')
