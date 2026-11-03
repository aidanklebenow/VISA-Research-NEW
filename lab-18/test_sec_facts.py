"""Synthetic edge-case tests; these are not SEC verification evidence."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('sec', Path(__file__).resolve().parents[1] / '.agents/skills/buffett-business/scripts/sec_facts.py')
sec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sec)


def fixture():
    facts = {'facts': {'us-gaap': {}}}
    for field, tags in sec.TAGS.items():
        facts['facts']['us-gaap'][tags[0]] = {'units': {'USD': [
            {'form': '10-K', 'fp': 'FY', 'fy': year, 'filed': f'{year+1}-02-01',
             'start': f'{year}-01-01', 'end': f'{year}-12-31', 'val': 100_000_000,
             'accn': f'{year}-original'} for year in range(2020, 2025)]}}
    return facts


class ExtractionTests(unittest.TestCase):
    def test_latest_annual_value_wins_not_quarter(self):
        facts = fixture()
        values = facts['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
        original = values[-1]
        values += [dict(original, filed='2026-02-01', val=25_000_000),
                   dict(original, filed='2026-03-01', start='2024-10-01', val=900_000_000),
                   dict(original, filed='2026-04-01', form='10-Q', val=800_000_000)]
        row = sec.year_row(facts, '2024-12-31')
        self.assertEqual(row['net_income']['value'], 25_000_000)
        self.assertEqual(row['roe']['value'], 25)

    def test_missing_capex_propagates_and_fallback_works(self):
        facts = fixture()
        primary, fallback = sec.TAGS['capital_spending']
        del facts['facts']['us-gaap'][primary]
        report = sec.analyze(facts, 'TEST')
        self.assertIsNone(report['rows'][0]['owner_earnings']['value'])
        self.assertEqual(report['checks']['Owner earnings grew first to last'], 'not known')
        facts['facts']['us-gaap'][fallback] = {'units': {'USD': [
            {'form': '10-K', 'start': '2024-01-01', 'end': '2024-12-31', 'val': 20_000_000}]}}
        self.assertEqual(sec.year_row(facts, '2024-12-31')['owner_earnings']['value'], 80_000_000)

    def test_nonpositive_equity(self):
        facts = fixture()
        for value in (0, -1):
            facts['facts']['us-gaap']['StockholdersEquity']['units']['USD'][-1]['val'] = value
            report = sec.analyze(facts, 'TEST')
            self.assertIsNone(report['rows'][-1]['roe']['value'])
            self.assertEqual(report['checks']['ROE ≥ 15% every year'], 'not known')

    def test_short_history_is_unknown(self):
        facts = fixture()
        for field in facts['facts']['us-gaap'].values():
            field['units']['USD'] = field['units']['USD'][-2:]
        self.assertEqual(set(sec.analyze(facts, 'TEST')['checks'].values()), {'not known'})

    def test_memo_flags_unsupported_percentage(self):
        report = sec.analyze(fixture(), 'TEST')
        self.assertEqual(sec.unsupported_numbers('ROE was 100.0%.', report), [])
        self.assertEqual(sec.unsupported_numbers('ROE was 40.0%.', report), ['40.0%'])
        self.assertEqual(sec.unsupported_numbers('ROE was 100%.', report), ['100%'])

    def test_fifty_three_week_year_is_annual(self):
        self.assertTrue(sec.annual({'start': '2022-08-29', 'end': '2023-09-03'}))
        self.assertFalse(sec.annual({'start': '2023-06-01', 'end': '2023-09-03'}))


if __name__ == '__main__':
    unittest.main()
