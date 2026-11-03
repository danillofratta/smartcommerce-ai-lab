"""Offline software tests with scripted decisions; not LLM quality evaluations."""

import importlib.util
import socket
import sys
from pathlib import Path
from unittest.mock import Mock

import dotenv
import langchain_groq
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError


LAB_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def lab(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Provider setup and network are forbidden in offline tests")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(dotenv, "load_dotenv", forbidden)
    monkeypatch.setattr(langchain_groq, "ChatGroq", forbidden)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    modules = {}
    for name in ("state", "prompts", "agents", "graph", "main"):
        spec = importlib.util.spec_from_file_location(name, LAB_DIR / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def test_imports_do_not_require_provider_configuration(lab, capsys):
    assert callable(lab["graph"].build_graph)
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("route,agent_name,prompt_name", [
    ("vendas", "Agente de Vendas", "VENDAS_PROMPT"),
    ("pedidos", "Agente de Pedidos", "PEDIDOS_PROMPT"),
    ("pagamentos", "Agente de Pagamentos", "PAGAMENTOS_PROMPT"),
    ("suporte", "Agente de Suporte", "SUPORTE_PROMPT"),
])
def test_graph_runs_only_selected_specialist(lab, route, agent_name, prompt_name):
    llm = Mock()
    llm.with_structured_output.return_value.invoke.return_value = (
        lab["state"].RouterResult(agent_name=route, motivo="Decisão simulada")
    )
    llm.invoke.return_value = AIMessage(content="Resposta simulada")
    app = lab["graph"].build_graph(llm)
    request = HumanMessage(content="Solicitação de teste")

    updates = list(app.stream({"messages": [request]}, stream_mode="updates"))

    assert [next(iter(step)) for step in updates] == ["router", route]
    assert updates[0]["router"] == {
        "agent_name": route, "motivo": "Decisão simulada",
    }
    llm.with_structured_output.assert_called_once_with(lab["state"].RouterResult)
    llm.with_structured_output.return_value.invoke.assert_called_once()
    llm.invoke.assert_called_once()
    history = llm.invoke.call_args.args[0]
    assert isinstance(history[0], SystemMessage)
    assert history[0].content == getattr(lab["prompts"], prompt_name)
    assert history[1].content == request.content
    assert updates[1][route]["messages"][0].name == agent_name


def test_final_state_preserves_request_route_and_response(lab):
    llm = Mock()
    llm.with_structured_output.return_value.invoke.return_value = (
        lab["state"].RouterResult(agent_name="suporte", motivo="Pedido pouco claro")
    )
    llm.invoke.return_value = AIMessage(content="Como posso ajudar?")
    result = lab["graph"].build_graph(llm).invoke({
        "messages": [HumanMessage(content="Preciso de ajuda")],
    })

    assert result["agent_name"] == "suporte"
    assert result["motivo"] == "Pedido pouco claro"
    assert result["resposta"] == "Como posso ajudar?"
    assert len(result["messages"]) == 2
    assert result["messages"][0].content == "Preciso de ajuda"
    assert result["messages"][-1].content == result["resposta"]


def test_router_schema_rejects_unknown_area(lab):
    with pytest.raises(ValidationError):
        lab["state"].RouterResult(agent_name="unknown", motivo="Rota inválida")


def test_model_creation_fails_clearly_without_model_name(lab, monkeypatch):
    monkeypatch.setattr(lab["main"], "load_dotenv", lambda: False)
    with pytest.raises(ValueError, match="Defina LLM_MODEL"):
        lab["main"].create_model()
