"""Compare saved SEC-derived reports to professor's targets, never overwrite data."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = [
    ('2022-08-28', 226954, 5844, 7392, 3891, 20642, 28.3, 3501),
    ('2023-09-03', 242290, 6292, 11068, 4323, 25058, 25.1, 6745),
    ('2024-09-01', 254453, 7367, 11339, 4710, 23622, 31.2, 6629),
    ('2025-08-31', 275235, 8099, 13335, 5498, 29164, 27.8, 7837),
    ('2026-08-30', 303154, 9226, 15817, 6435, 35803, 25.8, 9382),
]
FIELDS = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'roe', 'owner_earnings']


def main():
    failures = []
    for ticker in ('COST', 'JPM'):
        path = HERE / f'evidence/{ticker}-report.json'
        if not path.exists():
            failures.append(f'{ticker}: live report not downloaded')
            continue
        report = json.loads(path.read_text())
        if ticker == 'COST':
            by_end = {r['fiscal_year_end']: r for r in report['rows']}
            for end, *expected in EXPECTED:
                if end not in by_end:
                    failures.append(f'COST {end}: fiscal year not found')
                    continue
                for field, target in zip(FIELDS, expected):
                    actual = by_end[end][field]['value']
                    actual = None if actual is None else round(actual, 1) if field == 'roe' else actual / 1e6
                    if actual != target:
                        failures.append(f'COST {end} {field}: SEC={actual}; assignment={target}')
            if set(report['checks'].values()) != {'pass'}:
                failures.append(f"COST checks: {report['checks']}")
        else:
            for row in report['rows']:
                for field in ('capital_spending', 'owner_earnings'):
                    if row[field]['value'] is not None:
                        failures.append(f"JPM {row['fiscal_year_end']} {field}: unexpectedly present; inspect source")
            for name, status in report['checks'].items():
                if name.startswith('Owner earnings') and status != 'not known':
                    failures.append(f'JPM {name}: {status}')
    if failures:
        print('\n'.join(failures))
        raise SystemExit(1)
    print('All COST known-answer values and checks match; JPM missing-data probes pass.')


if __name__ == '__main__':
    main()
