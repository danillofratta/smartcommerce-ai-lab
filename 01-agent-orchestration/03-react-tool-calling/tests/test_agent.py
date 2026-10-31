"""Offline software tests: scripted model decisions, real graph and tools."""

import importlib.util
import json
import socket
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import dotenv
import langchain_groq
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.errors import GraphRecursionError


LAB_DIR = Path(__file__).resolve().parents[1]


def load_module(name, filename, monkeypatch):
    """Load this lab explicitly; neighboring labs also have a main.py."""
    spec = importlib.util.spec_from_file_location(name, LAB_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("Network access is forbidden in offline tests")

    monkeypatch.setattr(socket.socket, "connect", fail)
    monkeypatch.setattr(socket.socket, "connect_ex", fail)
    monkeypatch.setattr(socket, "create_connection", fail)


@pytest.fixture
def lab(monkeypatch):
    # Patch BEFORE importing main: it creates its model at module scope.
    # Never read the developer's .env or construct a real provider client.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda: False)
    monkeypatch.setenv("LLM_MODEL", "offline-test-model")
    model = Mock(name="scripted_model")
    model.invoke.side_effect = AssertionError("Configure scripted responses first")
    client = Mock(name="provider_client")
    client.bind_tools.return_value = model
    monkeypatch.setattr(langchain_groq, "ChatGroq", Mock(return_value=client))

    data = load_module("data", "data.py", monkeypatch)
    tools = load_module("tools", "tools.py", monkeypatch)
    main = load_module("smartcommerce_react_under_test", "main.py", monkeypatch)
    return main, tools, data, model


def request_tool(name, call_id, order_id="1024"):
    return AIMessage(content="", tool_calls=[{
        "name": name,
        "args": {"order_id": order_id},
        "id": call_id,
        "type": "tool_call",
    }])


@pytest.mark.parametrize("name,order_id,status", [
    ("get_order", "1024", "confirmed"),
    ("get_payment", "1024", "approved"),
    ("get_delivery", "1024", "shipped"),
    ("get_order", "1025", "pending_payment"),
    ("get_payment", "1025", "pending"),
    ("get_delivery", "1025", "pending"),
])
def test_tools_return_distinct_business_statuses(lab, name, order_id, status):
    _, tools, _, _ = lab
    result = getattr(tools, name).invoke({"order_id": order_id})
    assert result["status"] == status
    assert "error" not in result


@pytest.mark.parametrize("name", ["get_order", "get_payment", "get_delivery"])
@pytest.mark.parametrize("order_id", ["9999", "invalid"])
def test_tools_report_missing_or_invalid_order(lab, name, order_id):
    _, tools, _, _ = lab
    result = getattr(tools, name).invoke({"order_id": order_id})
    assert result == {"error": "Pedido não encontrado"}


def test_graph_runs_order_then_payment_and_delivery(lab):
    main, _, _, model = lab
    follow_up = AIMessage(content="", tool_calls=[
        {"name": "get_payment", "args": {"order_id": "1024"}, "id": "payment"},
        {"name": "get_delivery", "args": {"order_id": "1024"}, "id": "delivery"},
    ])
    model.invoke.side_effect = [
        request_tool("get_order", "order"), follow_up,
        AIMessage(content="Pagamento aprovado. Produto enviado."),
    ]
    initial = HumanMessage(content="O pedido 1024 foi pago? Quando será entregue?")

    updates = list(main.app.stream({"messages": [initial]}, stream_mode="updates"))

    assert [next(iter(step)) for step in updates] == [
        "call_agent", "tools", "call_agent", "tools", "call_agent",
    ]
    assert model.invoke.call_count == 3
    # These are the actual histories received by the scripted model.
    second_history = model.invoke.call_args_list[1].args[0]
    assert isinstance(second_history[0], SystemMessage)
    assert second_history[1].content == initial.content
    assert isinstance(second_history[-1], ToolMessage)
    assert second_history[-1].tool_call_id == "order"
    assert json.loads(second_history[-1].content)["status"] == "confirmed"

    final_history = model.invoke.call_args_list[2].args[0]
    results = {
        message.tool_call_id: json.loads(message.content)
        for message in final_history if isinstance(message, ToolMessage)
    }
    assert set(results) == {"order", "payment", "delivery"}
    assert results["payment"]["status"] == "approved"
    assert results["delivery"]["status"] == "shipped"
    final = updates[-1]["call_agent"]["messages"][-1]
    assert final.content == "Pagamento aprovado. Produto enviado."
    assert final.tool_calls == []


def test_graph_ends_without_tools_when_model_answers_directly(lab):
    main, _, _, model = lab
    model.invoke.side_effect = [AIMessage(content="Informe o número do pedido.")]
    result = main.app.invoke({"messages": [HumanMessage(content="Onde está meu pedido?")]})
    assert len(result["messages"]) == 2
    assert result["messages"][-1].content == "Informe o número do pedido."
    assert not any(isinstance(message, ToolMessage) for message in result["messages"])
    assert model.invoke.call_count == 1


def test_graph_passes_lookup_error_back_to_model(lab):
    main, _, _, model = lab
    model.invoke.side_effect = [
        request_tool("get_order", "missing", "9999"),
        AIMessage(content="Pedido não encontrado."),
    ]
    result = main.app.invoke({"messages": [HumanMessage(content="Consulte 9999.")]})
    tool_result = result["messages"][2]
    assert isinstance(tool_result, ToolMessage)
    assert tool_result.tool_call_id == "missing"
    assert json.loads(tool_result.content) == {"error": "Pedido não encontrado"}
    assert result["messages"][-1].content == "Pedido não encontrado."


def test_graph_stops_repeated_calls_at_configured_limit(lab):
    main, _, _, model = lab
    model.invoke.side_effect = lambda messages: request_tool(
        "get_order", f"repeat-{len(messages)}"
    )
    with pytest.raises(GraphRecursionError):
        main.app.invoke(
            {"messages": [HumanMessage(content="Consulte 1024.")]},
            config={"recursion_limit": 4},
        )


def test_console_shows_calls_tool_results_and_final_without_metadata(lab, capsys):
    main, _, _, model = lab
    capsys.readouterr()  # Discard the model name printed during module import.
    model.invoke.side_effect = [
        request_tool("get_order", "order"),
        AIMessage(content="Pedido confirmado."),
    ]
    for step in main.app.stream(
        {"messages": [HumanMessage(content="Consulte 1024.")]}, stream_mode="updates"
    ):
        for update in step.values():
            for message in update.get("messages", []):
                main.print_message(message)

    assert capsys.readouterr().out == (
        "\n[AGENT]\nSolicitando get_order(order_id=1024)\n"
        "\n[TOOL: get_order]\nPedido encontrado: confirmed\n"
        "\n[AGENT - FINAL]\nPedido confirmado.\n"
    )


@pytest.mark.parametrize("content,expected", [
    ('{"error": "Pedido não encontrado"}', "Erro: Pedido não encontrado"),
    ('{"status": "shipped", "estimated_delivery": "05/11/2026"}',
     "Status: shipped\nPrevisão: 05/11/2026"),
    ("Service unavailable", "Service unavailable"),
    ('["unexpected", "list"]', "['unexpected', 'list']"),
])
def test_console_handles_tool_errors_and_payloads(lab, capsys, content, expected):
    main, _, _, _ = lab
    capsys.readouterr()
    main.print_message(ToolMessage(
        content=content, name="get_delivery", tool_call_id="delivery"
    ))
    assert expected in capsys.readouterr().out


def test_order_exposes_customer_for_personalized_greeting(lab):
    _, tools, _, _ = lab
    assert tools.get_order.invoke({"order_id": "1024"}).get("customer") == "Maria"


def test_delivery_exposes_estimated_date(lab):
    _, tools, _, _ = lab
    result = tools.get_delivery.invoke({"order_id": "1024"})
    assert result.get("estimated_delivery") == "05/11/2026"


# Keep this known fixture gap visible; remove the marker after fixing the date.
@pytest.mark.xfail(
    strict=True, raises=ValueError,
    reason="Order 1025 has a date outside DD/MM/YYYY",
)
def test_fixture_dates_use_consistent_day_month_year_format(lab):
    _, _, data, _ = lab
    for order in data.list_orders.values():
        if order.get("estimated_delivery"):
            datetime.strptime(order["estimated_delivery"], "%d/%m/%Y")
