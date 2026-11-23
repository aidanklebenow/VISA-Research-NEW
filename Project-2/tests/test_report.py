import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model import Settings, run
from report import cap_error, grid_results, tested_mixes


class ReportTests(unittest.TestCase):
    def test_cap_shortfall_shows_an_error(self):
        self.assertIsNone(cap_error({'A': .40, 'B': .60}))
        self.assertIn('less than 100.0%', cap_error({'A': .40, 'B': .59}))

    def test_original_frontier_and_sensitivity_match_selected_mix(self):
        snapshot = run()
        estimates = snapshot['estimates']
        points = tested_mixes(estimates['vehicles'], estimates['correlations'], None, 0)
        self.assertEqual(len(points), 10626)
        candidate = snapshot['portfolios'][-1]
        self.assertIn((candidate['volatility'], candidate['net_return_proxy'], candidate['reserve_weight']), points)
        self.assertEqual(grid_results(points, Settings.reserve)[2], candidate['volatility'])
