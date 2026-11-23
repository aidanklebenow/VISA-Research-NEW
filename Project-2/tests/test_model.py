import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import Settings, cpi_signal, run, sensitivity_grid


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

    def test_sensitivity_grid_center_and_invalid_cells(self):
        grid = sensitivity_grid()
        self.assertEqual(grid[1]['target'], Settings.target)
        self.assertEqual(grid[1]['cells'][1]['limit'], Settings.volatility_limit)
        self.assertEqual(grid[1]['cells'][1]['verdict'], 'Pass')
        self.assertEqual(grid[1]['cells'][0]['verdict'], 'Above limit')
        self.assertTrue(all(cell['verdict'] == 'No mix' for cell in grid[-1]['cells']))

    def test_missing_and_invalid_provenance_stop_model(self):
        with TemporaryDirectory() as directory, patch('model.ROOT', Path(directory)):
            with self.assertRaises(FileNotFoundError):
                run()
            data = Path(directory) / 'data'
            data.mkdir()
            (data / 'price-sources.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Empty source record'):
                run()

    def test_empty_cpi_is_rejected(self):
        with TemporaryDirectory() as directory, patch('model.ROOT', Path(directory)):
            data = Path(directory) / 'data'
            data.mkdir()
            (data / 'cpi-vintage-2026-10-29.csv').write_text('date,value\n')
            with self.assertRaisesRegex(ValueError, 'vintage is empty'):
                cpi_signal()

    def test_explicit_history_matches_legacy_paths(self):
        self.assertEqual(run(history_months=60), run())
        self.assertEqual(run(history_months=36), run(last_36=True))
        with self.assertRaisesRegex(ValueError, 'bundled data contain 60'):
            run(history_months=120)

    def test_exclusions_caps_and_stock_adjustments(self):
        result = run(fund_limits={'VXUS': 0, 'SGOV': .50}, vxus_shift=.02)
        expected = run()['estimates']['vehicles'][-1][1]
        self.assertAlmostEqual(result['estimates']['vehicles'][-1][1], expected + .02)
        self.assertTrue(result['feasible'])
        for row in result['portfolios']:
            self.assertEqual(row['weights'][-1], 0)
        candidate = result['portfolios'][-1]
        self.assertLessEqual(candidate['weights'][0], .50)
        self.assertTrue(candidate['rules']['Fund maximums and exclusions respected'])
        self.assertFalse(run(fund_limits={'SGOV': 0})['feasible'])


if __name__ == '__main__':
    unittest.main()
