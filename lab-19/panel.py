"""Shared SEC snapshot, deterministic investor screens, and memo evidence checks."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('lab18_sec', ROOT / '.agents/skills/buffett-business/scripts/sec_facts.py')
sec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sec)
EXTRA_TAGS = {
    'liabilities': 'Liabilities', 'research_and_development': 'ResearchAndDevelopmentExpense',
    'current_assets': 'AssetsCurrent', 'current_liabilities': 'LiabilitiesCurrent',
}
LABELS = {
    'fiscal_year_end': 'Fiscal year end', 'revenue': 'Revenue', 'net_income': 'Net income',
    'operating_cash_flow': 'Operating cash flow', 'capital_spending': 'Capital spending',
    'equity': 'Year-end equity', 'roe': 'ROE', 'owner_earnings': 'Owner earnings',
    'liabilities': 'Liabilities', 'research_and_development': 'R&D',
    'current_assets': 'Current assets', 'current_liabilities': 'Current liabilities',
    'current_ratio': 'Current ratio', 'liabilities_equity': 'Liabilities / equity',
    'rd_revenue': 'R&D / revenue',
}
DEFAULTS = {'graham_current_ratio': 2.0, 'wood_growth_pct': 15.0}


def select_extra(facts, field, end):
    tag = EXTRA_TAGS[field]
    candidates = [f for f in sec.observations(facts, tag)
                  if f.get('form') == '10-K' and f.get('end') == end
                  and (field != 'research_and_development' or sec.annual(f))]
    if not candidates:
        return {'value': None, 'tag': 'not found'}
    chosen = max(candidates, key=lambda f: (f.get('filed', ''), f.get('accn', '')))
    return {'value': chosen['val'], 'tag': tag, 'filed': chosen.get('filed'),
            'accession': chosen.get('accn'), 'start': chosen.get('start'), 'end': end}


def ratio(row, numerator, denominator, percent=False):
    top, bottom = row[numerator]['value'], row[denominator]['value']
    value = top / bottom * (100 if percent else 1) if top is not None and bottom is not None and bottom > 0 else None
    # Missing R&D remains visibly not found; invalid denominators remain not known.
    missing = 'not found' if numerator == 'research_and_development' and top is None else 'not known'
    return {'value': value, 'tag': f'{numerator} / {denominator}', 'missing': missing}


def analyze(facts, ticker):
    report = sec.analyze(facts, ticker)
    for row in report['rows']:
        row.update({field: select_extra(facts, field, row['fiscal_year_end']) for field in EXTRA_TAGS})
        row['current_ratio'] = ratio(row, 'current_assets', 'current_liabilities')
        row['liabilities_equity'] = ratio(row, 'liabilities', 'equity')
        row['rd_revenue'] = ratio(row, 'research_and_development', 'revenue', percent=True)
    rows = report['rows']
    revenues = [r['revenue']['value'] for r in rows]
    # Exactly five consecutive annual observations: four compounding intervals.
    consecutive = len(rows) == 5 and all(350 <= (sec.date.fromisoformat(b['fiscal_year_end']) - sec.date.fromisoformat(a['fiscal_year_end'])).days <= 380 for a, b in zip(rows, rows[1:]))
    growth = ((revenues[-1] / revenues[0]) ** (1 / 4) - 1) * 100 if consecutive and all(v is not None and v > 0 for v in revenues) else None
    report['revenue_growth_pct'] = growth
    report['thresholds'] = dict(DEFAULTS)
    report['panel'] = evaluate(report)
    return report


def status(value, predicate):
    return 'not known' if value is None else 'pass' if predicate(value) else 'fail'


def graham_checks(rows, threshold=2.0):
    """Unknown inputs stay unknown; comparisons use unrounded source values."""
    income = [r['net_income']['value'] for r in rows]
    return {
        f'Latest current ratio ≥ {threshold:.2f}': status(rows[-1]['current_ratio']['value'], lambda x: x >= threshold),
        'Net income positive every year': sec.check(income, lambda xs: all(x > 0 for x in xs)),
        'Net income grew first to last': sec.check(income, lambda xs: xs[-1] > xs[0]),
    }


def evaluate(report, graham_current_ratio=2.0, wood_growth_pct=15.0):
    if graham_current_ratio < 0 or wood_growth_pct < 0:
        raise ValueError('Screen thresholds must be nonnegative.')
    rows = report['rows']
    cash_pairs = [(r['operating_cash_flow']['value'], r['net_income']['value']) for r in rows]
    cash = 'not known' if len(rows) != 5 or any(a is None or b is None for a, b in cash_pairs) else ('pass' if all(a >= b for a, b in cash_pairs) else 'fail')
    return {
        'Buffett': dict(report['checks']),
        'Graham': graham_checks(rows, graham_current_ratio),
        'Burry': {'Operating cash flow ≥ net income every year': cash,
                  'Latest liabilities / equity ≤ 2.00': status(rows[-1]['liabilities_equity']['value'], lambda x: x <= 2)},
        'Cathie Wood': {f'Annual revenue growth ≥ {wood_growth_pct:.2f}%': status(report['revenue_growth_pct'], lambda x: x >= wood_growth_pct),
                        'Latest R&D / revenue ≥ 5.00%': status(rows[-1]['rd_revenue']['value'], lambda x: x >= 5)},
    }


def verdict(checks):
    values = list(checks.values())
    if 'fail' in values:
        return 'Does not clear screen'
    if 'not known' in values:
        return 'Incomplete evidence'
    return 'Clears screen'


def display(field, cell):
    value = cell['value']
    if value is None:
        return cell.get('missing', 'not found')
    if field in ('current_ratio', 'liabilities_equity'):
        return f'{value:.2f}'
    if field == 'rd_revenue':
        return f'{value:.2f}%'
    return sec.display_value(field, cell)


def table_rows(report):
    return [{LABELS[field]: (value if field == 'fiscal_year_end' else display(field, value))
             for field, value in row.items()} for row in report['rows']]


def growth_display(report):
    value = report['revenue_growth_pct']
    return 'not known' if value is None else f'{value:.2f}%'


def unsupported_numbers(memo, report):
    printed = '\n'.join(' '.join(r.values()) for r in table_rows(report)) + '\n' + growth_display(report)
    return sorted(sec.numeric_tokens(memo) - sec.numeric_tokens(printed))


def memo_flags(memos, report):
    return {investor: unsupported_numbers(memo, report) for investor, memo in memos.items()}


def markdown_table(rows):
    headers = list(rows[0])
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(str(row[h]) for h in headers) + ' |' for row in rows])


def panel_rows(panel):
    return [{'Investor': investor, 'Check': name, 'Status': result} for investor, checks in panel.items() for name, result in checks.items()]


def render(report):
    source = report.get('source', {})
    text = f"# {report['ticker']} — {report['company']}\n\nUSD millions; ROE and R&D in percent; balance-sheet ratios in times.\n\n"
    text += markdown_table(table_rows(report))
    text += f"\n\nAnnual revenue growth (five fiscal years / four intervals): {growth_display(report)}\n\n"
    text += markdown_table(panel_rows(report['panel'])) + '\n\n'
    text += '\n'.join(f'- {i}: {verdict(c)}' for i, c in report['panel'].items())
    text += f"\n\n## SEC source\n\n{source.get('url', 'not downloaded')}\n\nRetrieved UTC: {source.get('downloaded_utc', 'not recorded')}\n\nSHA-256: {source.get('sha256', 'not recorded')}\n\n## Filing provenance\n"
    for row in report['rows']:
        text += f"\n### Fiscal year end {row['fiscal_year_end']}\n"
        for field, cell in row.items():
            if field != 'fiscal_year_end':
                accession = cell.get('accession')
                link = f"https://www.sec.gov/Archives/edgar/data/{int(source['cik'])}/{accession.replace('-', '')}/" if accession and source.get('cik') else ''
                text += f"- {LABELS[field]}: {cell['tag']}" + (f"; filed {cell['filed']}; accession [{accession}]({link})" if accession else '') + '\n'
    return text


def load_email():
    email = os.getenv('SEC_EMAIL', '')
    config = Path(__file__).parent / '.env'
    if not email and config.exists():
        email = next((line.partition('=')[2].strip() for line in config.read_text().splitlines() if line.startswith('SEC_EMAIL=')), '')
    return email


def save(report, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{report['ticker']}-report.json").write_text(json.dumps(report, indent=2))
    (output / f"{report['ticker']}-report.md").write_text(render(report))


def download(ticker, email, output):
    ticker = ticker.strip().upper()
    if not sec.re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', ticker):
        raise ValueError('Enter a valid ticker.')
    companies = sec.fetch_json('https://www.sec.gov/files/company_tickers.json', email)
    company = next((c for c in companies.values() if c['ticker'] == ticker), None)
    if company is None:
        raise ValueError('Ticker absent from SEC map; no data substituted.')
    cik = int(company['cik_str'])
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'
    facts = sec.fetch_json(url, email)
    report = analyze(facts, ticker)
    report['source'] = {'url': url, 'cik': cik, 'downloaded_utc': datetime.now(timezone.utc).isoformat(),
                        'sha256': hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()}
    output.mkdir(parents=True, exist_ok=True)
    (output / f'{ticker}-companyfacts.json').write_text(json.dumps(facts))
    save(report, output)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'evidence')
    args = parser.parse_args()
    try:
        print(render(download(args.ticker, load_email(), args.output)))
    except (ValueError, OSError) as error:
        parser.exit(1, f'SEC download failed: {error}\n')
