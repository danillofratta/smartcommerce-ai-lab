"""Offline software tests with simulated responses; not LLM quality evaluations."""

import importlib.util
import socket
import sys
from pathlib import Path
from threading import Barrier
from unittest.mock import Mock

import dotenv
import langchain_groq
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


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
    for name in ("state", "data", "agents", "graph", "main"):
        spec = importlib.util.spec_from_file_location(name, LAB_DIR / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def simulated_response(messages):
    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    return AIMessage(content=messages[1].content)


@pytest.mark.parametrize("order_id,expected", [
    (1024, "CONFIRMADO"), (1025, "RETIDO"), (1026, "RETIDO"),
])
def test_graph_collects_all_reviews_before_one_consolidation(lab, order_id, expected):
    llm = Mock()
    llm.invoke.side_effect = simulated_response
    pedido = lab["data"].PEDIDOS_SIMULADOS[order_id]
    result = lab["graph"].build_graph(llm).invoke({"pedido": pedido, "avaliacoes": []})

    assert result["pedido"] == pedido
    assert result["status_pedido"] == expected
    assert len(result["avaliacoes"]) == 3
    assert {review.split(":", 1)[0] for review in result["avaliacoes"]} == {
        "[ESTOQUE]", "[FINANCEIRO]", "[LOGISTICA]",
    }
    assert llm.invoke.call_count == 4
    consolidation = llm.invoke.call_args.args[0][1].content
    assert expected in consolidation
    for review in result["avaliacoes"]:
        assert review in consolidation
    assert result["parecer_final"] == consolidation


def test_specialists_really_run_concurrently(lab):
    barrier = Barrier(3)

    def respond(messages):
        if "Consolidador" not in messages[0].content:
            # Sequential execution would time out here before reaching all three calls.
            barrier.wait(timeout=10)
        return simulated_response(messages)

    llm = Mock()
    llm.invoke.side_effect = respond
    app = lab["graph"].build_graph(llm)
    updates = list(app.stream({
        "pedido": lab["data"].PEDIDOS_SIMULADOS[1024], "avaliacoes": [],
    }, stream_mode="updates"))

    names = [next(iter(step)) for step in updates]
    assert set(names[:3]) == {"estoque", "financeiro", "logistica"}
    assert names[3:] == ["consolidador"]


@pytest.mark.parametrize("changes", [
    {"payment_status": "declined"},
    {"stock_available": 0},
    {"delivery_available": False},
])
def test_llm_cannot_change_order_status(lab, changes):
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="CONFIRMADO")
    pedido = {**lab["data"].PEDIDOS_SIMULADOS[1024], **changes}
    result = lab["graph"].build_graph(llm).invoke({"pedido": pedido, "avaliacoes": []})
    assert result["status_pedido"] == "RETIDO"


def test_specialist_failure_prevents_consolidation(lab):
    def respond(messages):
        assert "Consolidador" not in messages[0].content
        if "Financeiro" in messages[0].content:
            raise RuntimeError("Simulated provider failure")
        return simulated_response(messages)

    llm = Mock()
    llm.invoke.side_effect = respond
    with pytest.raises(RuntimeError, match="Simulated provider failure"):
        lab["graph"].build_graph(llm).invoke({
            "pedido": lab["data"].PEDIDOS_SIMULADOS[1024], "avaliacoes": [],
        })


def test_console_reuses_graph_without_mixing_orders(lab, capsys):
    llm = Mock()
    llm.invoke.side_effect = simulated_response
    app = lab["graph"].build_graph(llm)
    lab["main"].analisar_pedido(app, 1024)
    lab["main"].analisar_pedido(app, 1025)
    output = capsys.readouterr().out
    assert "Status do pedido: CONFIRMADO" in output
    assert "Status do pedido: RETIDO" in output
    assert llm.invoke.call_count == 8
    prompt = llm.invoke.call_args.args[0][1].content
    assert "Maria" not in prompt
    assert "Notebook Dell" not in prompt


def test_unknown_order_fails_before_model_call(lab):
    app = Mock()
    with pytest.raises(ValueError, match="não encontrado"):
        lab["main"].analisar_pedido(app, 9999)
    app.stream.assert_not_called()


def test_missing_model_configuration(lab, monkeypatch):
    monkeypatch.setattr(lab["main"], "load_dotenv", lambda: False)
    with pytest.raises(ValueError, match="Defina LLM_MODEL"):
        lab["main"].create_model()
