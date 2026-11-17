import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import Settings, cpi_signal, run


class ModelTests(unittest.TestCase):
    def test_known_lab15_answer_and_no_false_approval(self):
        result = run()
        selected = result['portfolios'][-1]
        self.assertEqual(selected['weights'], [.55, 0, 0, .30, .15])
        self.assertAlmostEqual(selected['volatility'], .0680, places=4)
        self.assertEqual(selected['model_verdict'], 'PASS')
        self.assertTrue(all(r['full_mandate_verdict'].startswith('FAIL') for r in result['portfolios']))

    def test_risk_failure_not_hidden(self):
        selected = run(Settings(volatility_limit=.05))['portfolios'][-1]
        self.assertEqual(selected['model_verdict'], 'FAIL')
        self.assertFalse(selected['rules']['Estimated volatility within proposed limit'])

    def test_infeasible_does_not_invent_portfolio(self):
        result = run(Settings(target=.50))
        self.assertFalse(result['feasible'])
        self.assertEqual(len(result['portfolios']), 2)

    def test_costs_reduce_net_and_raise_required_gross(self):
        settings = Settings(annual_cost=.005)
        selected = run(settings)['portfolios'][-1]
        self.assertAlmostEqual(selected['expected_return']-selected['net_return_proxy'], .005)
        self.assertGreaterEqual(selected['net_return_proxy']+1e-12, settings.target)

    def test_vintage_gate_and_same_vintage_calculation(self):
        with self.assertRaises(ValueError):
            cpi_signal('2026-10-29')
        signal = cpi_signal()
        self.assertEqual(signal['measured'], '2026-09-01')
        self.assertAlmostEqual(signal['inflation_yoy'], 336.298/324.245-1)


if __name__ == '__main__':
    unittest.main()
