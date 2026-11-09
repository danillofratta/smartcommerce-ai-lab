import operator
from typing import Annotated, Literal, TypedDict


class State(TypedDict, total=False):
    pedido: dict
    avaliacoes: Annotated[list[dict], operator.add]
    status_pedido: Literal["CONFIRMADO", "RETIDO"]
    parecer_final: str
