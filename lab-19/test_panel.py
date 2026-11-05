"""Synthetic financial-logic tests; no company reference values in production."""
import sys
from pathlib import Path
import unittest
from copy import deepcopy
import panel
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lab-18'))
from test_sec_facts import fixture


def panel_fixture():
    facts = fixture()
    for field, tag in panel.EXTRA_TAGS.items():
        facts['facts']['us-gaap'][tag] = deepcopy(facts['facts']['us-gaap']['NetIncomeLoss'])
    for idx in range(5):
        facts['facts']['us-gaap'][panel.sec.TAGS['revenue'][0]]['units']['USD'][idx]['val'] = 100e6 * 1.1 ** idx
        facts['facts']['us-gaap']['AssetsCurrent']['units']['USD'][idx]['val'] = 150e6
        facts['facts']['us-gaap']['ResearchAndDevelopmentExpense']['units']['USD'][idx]['val'] = 10e6
    return facts


class PanelTests(unittest.TestCase):
    def test_growth_and_real_thresholds(self):
        report = panel.analyze(panel_fixture(), 'TEST')
        self.assertAlmostEqual(report['revenue_growth_pct'], 10)
        self.assertEqual(list(report['panel']['Cathie Wood'].values()), ['fail', 'pass'])
        changed = panel.evaluate(report, wood_growth_pct=5, graham_current_ratio=1)
        self.assertEqual(list(changed['Cathie Wood'].values()), ['pass', 'pass'])
        self.assertEqual(next(iter(report['panel']['Graham'].values())), 'fail')
        self.assertEqual(next(iter(changed['Graham'].values())), 'pass')

    def test_missing_rd_and_equity(self):
        facts = panel_fixture()
        del facts['facts']['us-gaap']['ResearchAndDevelopmentExpense']
        for equity in (0, -1):
            facts['facts']['us-gaap']['StockholdersEquity']['units']['USD'][-1]['val'] = equity
            report = panel.analyze(facts, 'TEST')
            self.assertEqual(panel.display('rd_revenue', report['rows'][-1]['rd_revenue']), 'not found')
            self.assertIsNone(report['rows'][-1]['liabilities_equity']['value'])
            self.assertEqual(list(report['panel']['Burry'].values())[-1], 'not known')
            self.assertEqual(list(report['panel']['Cathie Wood'].values())[-1], 'not known')

    def test_missing_flow_and_short_history(self):
        facts = panel_fixture()
        del facts['facts']['us-gaap']['NetCashProvidedByUsedInOperatingActivities']
        report = panel.analyze(facts, 'TEST')
        self.assertEqual(list(report['panel']['Burry'].values())[0], 'not known')
        for tag in facts['facts']['us-gaap'].values():
            tag['units']['USD'] = tag['units']['USD'][-2:]
        report = panel.analyze(facts, 'TEST')
        self.assertIsNone(report['revenue_growth_pct'])
        self.assertEqual(list(report['panel']['Graham'].values())[1:], ['not known', 'not known'])

    def test_extra_tag_selection_and_latest_filing(self):
        facts = panel_fixture()
        rd = facts['facts']['us-gaap']['ResearchAndDevelopmentExpense']['units']['USD']
        rd += [dict(rd[-1], filed='2026-01-01', val=12e6), dict(rd[-1], filed='2027-01-01', start='2024-10-01', val=999e6)]
        self.assertEqual(panel.analyze(facts, 'TEST')['rows'][-1]['research_and_development']['value'], 12e6)

    def test_denominators_and_boundaries(self):
        report = panel.analyze(panel_fixture(), 'TEST')
        row = report['rows'][-1]
        for field in ('current_liabilities', 'revenue'):
            row[field]['value'] = 0
        self.assertIsNone(panel.ratio(row, 'current_assets', 'current_liabilities')['value'])
        self.assertIsNone(panel.ratio(row, 'research_and_development', 'revenue')['value'])
        row['current_ratio']['value'] = 2
        row['liabilities_equity']['value'] = 2
        self.assertEqual(next(iter(panel.evaluate(report)['Graham'].values())), 'pass')
        self.assertEqual(list(panel.evaluate(report)['Burry'].values())[-1], 'pass')

    def test_all_memos_number_validation(self):
        report = panel.analyze(panel_fixture(), 'TEST')
        for name in ('Buffett', 'Graham', 'Burry', 'Cathie Wood'):
            memos = {n: 'Current ratio 1.50.' for n in report['panel']}
            memos[name] += ' Unsupported 40.0% and -987.65.'
            flags = panel.memo_flags(memos, report)
            self.assertEqual(flags[name], ['-987.65', '40.0%'])
            self.assertTrue(all(not f for n, f in flags.items() if n != name))
        self.assertEqual(panel.verdict({'a': 'pass', 'b': 'not known'}), 'Incomplete evidence')


if __name__ == '__main__':
    unittest.main()
