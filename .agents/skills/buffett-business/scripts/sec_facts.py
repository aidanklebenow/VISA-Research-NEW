"""Keyless EDGAR extraction and Buffett checks. Money is stored in USD."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import time
from urllib.request import Request, urlopen

TAGS = {
    'revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
    'net_income': ['NetIncomeLoss'],
    'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities'],
    'capital_spending': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets'],
    'equity': ['StockholdersEquity'],
}
FLOWS = set(TAGS) - {'equity'}
NUMBER = re.compile(r'(?<![\w.])[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?!\w|\.\d)')


def annual(fact):
    """Allow 52/53-week years but exclude quarterly and multi-year flows."""
    try:
        days = (date.fromisoformat(fact['end']) - date.fromisoformat(fact['start'])).days
        return 350 <= days <= 380
    except (KeyError, ValueError):
        return False


def observations(facts, tag):
    return facts.get('facts', {}).get('us-gaap', {}).get(tag, {}).get('units', {}).get('USD', [])


def select_fact(facts, field, end):
    for tag in TAGS[field]:
        eligible = [f for f in observations(facts, tag)
                    if f.get('form') == '10-K' and f.get('end') == end
                    and (field not in FLOWS or annual(f))]
        if eligible:
            chosen = max(eligible, key=lambda f: (f.get('filed', ''), f.get('accn', '')))
            return {'value': chosen['val'], 'tag': tag, 'filed': chosen.get('filed'),
                    'accession': chosen.get('accn'), 'start': chosen.get('start'), 'end': end}
    return {'value': None, 'tag': 'not found'}


def year_row(facts, end):
    row = {'fiscal_year_end': end}
    row.update({field: select_fact(facts, field, end) for field in TAGS})
    income, equity = row['net_income']['value'], row['equity']['value']
    ocf, capex = row['operating_cash_flow']['value'], row['capital_spending']['value']
    row['roe'] = {'value': income / equity * 100 if income is not None and equity is not None and equity > 0 else None,
                  'tag': 'NetIncomeLoss / StockholdersEquity × 100', 'missing': 'not known'}
    row['owner_earnings'] = {'value': ocf - capex if ocf is not None and capex is not None else None,
                             'tag': f"{row['operating_cash_flow']['tag']} − {row['capital_spending']['tag']}"}
    return row


def check(values, predicate):
    if len(values) != 5 or any(v is None for v in values):
        return 'not known'
    return 'pass' if predicate(values) else 'fail'


def analyze(facts, ticker):
    # A fiscal-year anchor must be the current annual period in an annual filing.
    # Comparative years in a newer filing still supply the latest values below.
    ends = sorted({f['end'] for tag in TAGS['net_income'] for f in observations(facts, tag)
                   if f.get('form') == '10-K' and f.get('fp') == 'FY' and annual(f)
                   and f['end'][:4] == str(f.get('fy'))})[-5:]
    if not ends:
        raise ValueError('No annual 10-K fiscal years found; no data will be estimated.')
    rows = [year_row(facts, end) for end in ends]
    roe = [r['roe']['value'] for r in rows]
    owner = [r['owner_earnings']['value'] for r in rows]
    return {'ticker': ticker, 'company': facts.get('entityName', ticker), 'rows': rows,
            'checks': {'ROE ≥ 15% every year': check(roe, lambda v: all(x >= 15 for x in v)),
                       'Owner earnings positive every year': check(owner, lambda v: all(x > 0 for x in v)),
                       'Owner earnings grew first to last': check(owner, lambda v: v[-1] > v[0])}}


def display_value(field, cell):
    if cell['value'] is None:
        return cell.get('missing', 'not found')
    return f"{cell['value']:.1f}%" if field == 'roe' else f"{cell['value'] / 1_000_000:,.0f}"


def table_rows(report):
    return [{'Fiscal year end': row['fiscal_year_end'],
             **{field: display_value(field, cell) for field, cell in row.items() if field != 'fiscal_year_end'}}
            for row in report['rows']]


def render_report(report):
    table = table_rows(report)
    headers = list(table[0])
    lines = [f"# {report['ticker']} — {report['company']}", '', 'USD millions; ROE in percent.', '',
             '| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines.extend('| ' + ' | '.join(row[h] for h in headers) + ' |' for row in table)
    lines.extend(['', '## Computed checks', *[f'- {k}: {v}' for k, v in report['checks'].items()], '', '## XBRL provenance'])
    for row in report['rows']:
        lines.append(f"\nFiscal year end {row['fiscal_year_end']}")
        for field, cell in row.items():
            if field != 'fiscal_year_end':
                lines.append(f"- {field}: {cell['tag']}" + (f"; filed {cell['filed']}; accession {cell['accession']}" if cell.get('filed') else ''))
    return '\n'.join(lines) + '\n'


def numeric_tokens(text):
    return {m.group() for m in NUMBER.finditer(text)}


def unsupported_numbers(memo, report):
    # Exact displayed tokens: 40.0% cannot pass because an unrelated 40 exists.
    # Exclude provenance identifiers, which are metadata rather than financial outputs.
    allowed_text = '\n'.join(' '.join(row.values()) for row in table_rows(report))
    return sorted(numeric_tokens(memo) - numeric_tokens(allowed_text))


def fetch_json(url, email):
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ValueError('Set SEC_EMAIL to your real contact email before downloading.')
    request = Request(url, headers={'User-Agent': f'Aidan Klebenow {email}', 'Accept': 'application/json'})
    time.sleep(0.2)
    # Python.org macOS installs may lack system certificate configuration.
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    with urlopen(request, timeout=45, context=context) as response:
        return json.load(response)


def download(ticker, email, output):
    ticker = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', ticker):
        raise ValueError('Enter a valid ticker such as COST or JPM.')
    companies = fetch_json('https://www.sec.gov/files/company_tickers.json', email)
    company = next((c for c in companies.values() if c['ticker'] == ticker), None)
    if company is None:
        raise ValueError(f'Ticker {ticker} not found in the SEC ticker map.')
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(company['cik_str']):010d}.json"
    facts = fetch_json(url, email)
    report = analyze(facts, ticker)
    report['source'] = {'url': url, 'downloaded_utc': datetime.now(timezone.utc).isoformat(),
                        'sha256': hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()}
    output.mkdir(parents=True, exist_ok=True)
    (output / f'{ticker}-companyfacts.json').write_text(json.dumps(facts))
    (output / f'{ticker}-report.json').write_text(json.dumps(report, indent=2))
    (output / f'{ticker}-report.md').write_text(render_report(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--output', type=Path, default=Path('lab-18/evidence'))
    args = parser.parse_args()
    try:
        report = download(args.ticker, os.getenv('SEC_EMAIL', ''), args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Download failed: {error}\n')
    print(render_report(report))


if __name__ == '__main__':
    main()
