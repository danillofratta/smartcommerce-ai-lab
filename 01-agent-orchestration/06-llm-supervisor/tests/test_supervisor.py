"""Offline invariant tests with simulated decisions; never an LLM evaluation."""
import importlib.util
import io
import json
import sys
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from pydantic import ValidationError

LAB_DIR = Path(__file__).resolve().parents[1]


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for target in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.create_connection'):
            self.stack.enter_context(patch(target, side_effect=AssertionError('Network forbidden')))
        # Restore only lab modules; removing newly imported dependency modules
        # can invalidate cached type identities (for example uuid.UUID).
        names = ('state', 'data', 'agents', 'graph', 'main')
        saved = {name: sys.modules.get(name) for name in names}
        def restore_modules():
            for name, module in saved.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module
        self.stack.callback(restore_modules)
        self.stack.enter_context(patch('dotenv.load_dotenv', side_effect=AssertionError('No dotenv at import')))
        self.stack.enter_context(patch('langchain_groq.ChatGroq', side_effect=AssertionError('No provider at import')))
        self.modules = {}
        for name in names:
            spec = importlib.util.spec_from_file_location(name, LAB_DIR / f'{name}.py')
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            self.modules[name] = module
        self.llm = Mock()
        self.supervisor = self.llm.with_structured_output.return_value

    def run_graph(self, destinations, order_id='1024'):
        self.supervisor.invoke.side_effect = [
            {'parsed': {'next_agent': d, 'reason': f'Informação necessária: {d}'}, 'parsing_error': None}
            for d in destinations
        ]
        return self.modules['graph'].build_graph(self.llm).invoke(
            {'request': self.modules['data'].SAMPLE_REQUEST, 'order_id': order_id},
            config={'recursion_limit': self.modules['state'].RECURSION_LIMIT},
        )

    def test_variable_order_and_skipping_specialists(self):
        for trajectory in (['logistica', 'FINISH'], ['pagamentos', 'pedidos', 'FINISH'], ['FINISH']):
            with self.subTest(trajectory=trajectory):
                result = self.run_graph(trajectory)
                self.assertEqual([r['agent'] for r in result['agent_results']], trajectory[:-1])
                self.assertEqual(result['steps'], len(trajectory) - 1)
                self.assertEqual(result['final_status'], 'FINISHED')

    def test_results_and_history_reach_next_decision(self):
        result = self.run_graph(['pedidos', 'logistica', 'reembolsos', 'FINISH'])
        context = json.loads(self.supervisor.invoke.call_args.args[0][-1].content)
        self.assertEqual(len(context['agent_results']), 3)
        self.assertEqual(len(context['execution_history']), 3)
        self.assertEqual(context['agent_results'][0]['data']['order_id'], '1024')
        self.assertEqual(len(result['execution_history']), 4)
        self.assertIn('previsão', result['final_response'])
        self.assertIn('Não há aprovação automática', result['final_response'])
        self.llm.with_structured_output.assert_called_once_with(
            self.modules['state'].SupervisorDecision, method='function_calling', include_raw=True,
        )

    def test_repeat_allowed_then_bounded(self):
        result = self.run_graph(['pedidos', 'logistica', 'pedidos', 'FINISH'])
        self.assertEqual(result['steps'], 3)
        result = self.run_graph(['pedidos'] * 3)
        self.assertEqual(result['steps'], 2)
        self.assertEqual(result['final_status'], 'AGENT_LIMIT')
        self.assertEqual(result['execution_history'][-1]['proposed_decision']['next_agent'], 'pedidos')

    def test_total_limit_stops_before_another_llm_call(self):
        result = self.run_graph(['pedidos', 'pagamentos', 'logistica', 'reembolsos'] * 2)
        self.assertEqual(result['steps'], 8)
        self.assertEqual(result['final_status'], 'STEP_LIMIT')
        self.assertEqual(self.supervisor.invoke.call_count, 8)
        self.assertEqual(result['execution_history'][-1]['source'], 'guardrail')

    def test_invalid_decisions_terminate_without_specialist(self):
        for invalid in (
            {'parsed': {'next_agent': 'hacker', 'reason': 'x'}},
            {'parsed': {'next_agent': 'pedidos', 'reason': '  '}},
            {'parsed': {'next_agent': 'pedidos', 'reason': 4}},
            {'parsed': None, 'parsing_error': ValueError('bad JSON')},
            {},
        ):
            with self.subTest(invalid=invalid):
                self.supervisor.invoke.side_effect = None
                self.supervisor.invoke.return_value = invalid
                result = self.modules['graph'].build_graph(self.llm).invoke({'request': 'pedido', 'order_id': '1024'})
                self.assertEqual(result['final_status'], 'INVALID_DECISION')
                self.assertEqual(result['agent_results'], [])
                self.assertIn('revisão manual', result['final_response'])

    def test_schema_rejects_wrong_destination_missing_and_blank_reason(self):
        schema = self.modules['state'].SupervisorDecision
        for payload in ({'next_agent': 'reembolso', 'reason': 'x'}, {'next_agent': 'FINISH'}, {'next_agent': 'FINISH', 'reason': ' '}):
            with self.assertRaises(ValidationError):
                schema.model_validate(payload)

    def test_unknown_order_does_not_invent_data(self):
        result = self.run_graph(['pedidos', 'FINISH'], order_id='9999')
        self.assertEqual(result['agent_results'][0]['data']['status'], 'NOT_FOUND')
        self.assertIn('Confirme o número', result['final_response'])

    def test_provider_error_is_not_disguised_as_success(self):
        self.supervisor.invoke.side_effect = RuntimeError('Provider unavailable')
        with self.assertRaisesRegex(RuntimeError, 'Provider unavailable'):
            self.modules['graph'].build_graph(self.llm).invoke({'request': 'pedido', 'order_id': '1024'})

    def test_blank_input_never_calls_supervisor(self):
        app = self.modules['graph'].build_graph(self.llm)
        for request, order_id in ((' ', '1024'), ('pedido', ' ')):
            with self.assertRaisesRegex(ValueError, 'não vazios'):
                app.invoke({'request': request, 'order_id': order_id})
        self.supervisor.invoke.assert_not_called()

    def test_model_reason_is_not_published_as_customer_fact(self):
        self.supervisor.invoke.return_value = {
            'parsed': {'next_agent': 'FINISH', 'reason': 'Reembolso executado com sucesso.'},
            'parsing_error': None,
        }
        result = self.modules['graph'].build_graph(self.llm).invoke({'request': 'pedido', 'order_id': '1024'})
        self.assertNotIn('Reembolso executado com sucesso.', result['final_response'])
        self.assertIn('Nenhuma consulta foi realizada', result['final_response'])

    def test_policy_boundaries(self):
        data = self.modules['data']
        self.assertEqual(data.refund_policy('9999')['status'], 'NEEDS_INFO')
        self.assertEqual(data.refund_policy('1024')['status'], 'WAIT_FOR_DELIVERY')
        with patch.dict(data.SHIPMENTS['1024'], eta_days=-1):
            self.assertEqual(data.refund_policy('1024')['status'], 'HUMAN_REVIEW')
        with patch.dict(data.SHIPMENTS['1024'], delivered=True):
            self.assertEqual(data.refund_policy('1024')['status'], 'HUMAN_REVIEW')
        with patch.dict(data.ORDERS['1024'], status='PROCESSING'):
            self.assertEqual(data.refund_policy('1024')['status'], 'ELIGIBLE_TO_REQUEST')
        with patch.dict(data.PAYMENTS['1024'], status='PENDING'):
            self.assertEqual(data.refund_policy('1024')['status'], 'NO_APPROVED_PAYMENT')
        self.assertIsInstance(data.PAYMENTS['1024']['amount_cents'], int)

    def test_cli_streams_history_and_final_response(self):
        self.llm.model_name = 'test-model'
        self.supervisor.invoke.side_effect = [
            {'parsed': {'next_agent': destination, 'reason': 'Consultar entrega e finalizar.'}, 'parsing_error': None}
            for destination in ('logistica', 'FINISH')
        ]
        with patch.object(sys, 'argv', ['main.py']), patch.object(
            self.modules['main'], 'create_model', return_value=self.llm,
        ) as create_model, redirect_stdout(io.StringIO()) as output:
            self.modules['main'].main()
        create_model.assert_called_once_with()
        text = output.getvalue()
        self.assertIn('LIVE: Groq / test-model', text)
        self.assertIn('Supervisor', text)
        self.assertIn('Especialista logistica', text)
        self.assertIn('Status: FINISHED', text)
        self.assertIn('Nenhum cancelamento ou reembolso foi executado', text)

    def test_live_requires_configuration(self):
        main = self.modules['main']
        with patch.object(main, 'load_dotenv'), patch.dict('os.environ', {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'LLM_MODEL'):
                main.create_model()
        with patch.object(main, 'load_dotenv'), patch.dict('os.environ', {'LLM_MODEL': 'example'}, clear=True):
            with self.assertRaisesRegex(ValueError, 'GROQ_API_KEY'):
                main.create_model()


if __name__ == '__main__':
    unittest.main()
