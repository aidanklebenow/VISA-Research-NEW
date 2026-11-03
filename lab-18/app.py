"""Lab 18: SEC data and deterministic checks, with a separate AI-written memo."""
import importlib.util
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('sec_facts', ROOT / '.agents/skills/buffett-business/scripts/sec_facts.py')
sec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sec)
EVIDENCE = ROOT / 'lab-18/evidence'
MEMOS = ROOT / 'lab-18/memos'
LABELS = {
    'Fiscal year end': 'Fiscal year end', 'revenue': 'Revenue',
    'net_income': 'Net income', 'operating_cash_flow': 'Operating cash flow',
    'capital_spending': 'Capital spending', 'equity': 'Year-end equity',
    'roe': 'ROE', 'owner_earnings': 'Owner earnings',
}

st.set_page_config(page_title='Buffett Business Review · Lab 18', page_icon='📊', layout='wide')
st.caption('FIN 43900 · LAB 18 · AIDAN KLEBENOW')
st.title('Buffett Business Review')
st.caption('Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
st.write('Explore a business’s earning power through annual filings, consistent financial checks, and a Buffett-inspired review.')

with st.sidebar:
    st.header('Choose a business')
    ticker = st.text_input('Ticker', 'COST', help='Try COST for Costco or JPM for JPMorgan.').strip().upper()
    st.caption('Saved reports open immediately. Refresh only when you want a new SEC download.')
    with st.expander('SEC download settings'):
        email = st.text_input('SEC contact email', value=os.getenv('SEC_EMAIL', ''), type='password',
                              help='Identifies your requests to SEC. Not saved in reports or committed code.')
    refresh = st.button('Refresh SEC data', type='primary', width='stretch')
    st.divider()
    st.markdown('**Business quality, not stock valuation**')
    st.write('This lab excludes stock prices. A strong business is not automatically a good buy at today’s price.')
    st.caption('Source: annual SEC 10-K facts. No API key required.')

if refresh:
    try:
        with st.spinner('Downloading SEC facts and calculating results…'):
            sec.download(ticker, email, EVIDENCE)
        st.success('SEC data refreshed. Ask Codex to refresh the written memo if the financial results changed.')
    except (OSError, ValueError) as error:
        st.error(f'Download unsuccessful: {error}')

if not sec.re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', ticker):
    st.warning('Enter a valid ticker such as COST or JPM.')
    st.stop()
report_path = EVIDENCE / f'{ticker}-report.json'
if not report_path.exists():
    st.info('Download SEC facts to begin. Enter your SEC contact email in the sidebar settings, then select Refresh SEC data.')
    st.stop()
try:
    report = json.loads(report_path.read_text())
except (OSError, ValueError) as error:
    st.error(f'Cannot read the saved report: {error}')
    st.stop()

rows = report['rows']
st.subheader(f"{ticker} · {report['company']}")
st.caption(f"Fiscal years ending {rows[0]['fiscal_year_end']} through {rows[-1]['fiscal_year_end']} · USD millions except ROE")
latest = rows[-1]
for column, field in zip(st.columns(4), ('revenue', 'net_income', 'owner_earnings', 'roe')):
    column.metric(LABELS[field], sec.display_value(field, latest[field]))
st.caption('Cards show the latest fiscal year. ROE uses year-end equity; owner earnings = operating cash flow − capital spending.')

overview, memo_tab, sources = st.tabs(['Financial overview', 'Business memo', 'Sources & methodology'])
with overview:
    st.subheader('Earnings over time')
    chart = pd.DataFrame([{
        'Fiscal year end': row['fiscal_year_end'],
        **{LABELS[field]: row[field]['value'] / 1e6 if row[field]['value'] is not None else None
           for field in ('owner_earnings', 'net_income')},
    } for row in rows]).set_index('Fiscal year end')
    st.line_chart(chart, y_label='USD millions', color=['#0d9488', '#6366f1'])
    if any(row['owner_earnings']['value'] is None for row in rows):
        st.info('Owner earnings cannot be plotted for years with missing inputs. Missing values are not treated as zero.')
    st.subheader('Buffett checks')
    for column, (label, status) in zip(st.columns(3), report['checks'].items()):
        with column:
            st.markdown(f'**{label}**')
            if status == 'pass':
                st.success('Pass')
            elif status == 'fail':
                st.error('Fail')
            else:
                st.warning('Not known — missing inputs')
    st.subheader('Annual financials')
    table = [{LABELS[key]: value for key, value in row.items()} for row in sec.table_rows(report)]
    st.dataframe(table, hide_index=True, width='stretch')
    st.caption('“Not found” means no eligible reported value was found. “Not known” means a calculation or check lacks the required inputs.')
    st.download_button('Download financial report', sec.render_report(report), file_name=f'{ticker}-report.md', mime='text/markdown')

with memo_tab:
    st.subheader('Buffett-inspired business memo')
    st.caption('An AI-written interpretation of the computed evidence, not Warren Buffett’s actual opinion.')
    memo_path = MEMOS / f'{ticker}.md'
    saved = memo_path.read_text() if memo_path.exists() else ''
    if not saved:
        st.info('Memo pending: ask Codex to use $buffett-business on this ticker after downloading.')
    with st.expander('Edit memo or test an unsupported number'):
        memo = st.text_area('Memo text', value=saved, height=300, key=f'memo-{ticker}')
        st.caption('For the lab probe, add 40.0% to the text and check the warning below. Restore the original memo afterward.')
        if st.button('Save memo changes'):
            MEMOS.mkdir(parents=True, exist_ok=True)
            memo_path.write_text(memo)
            st.success('Markdown memo saved locally.')
    if memo:
        st.markdown(memo)
        st.divider()
        flags = sec.unsupported_numbers(memo, report)
        if flags:
            st.error('Numbers not printed in the financial table: ' + ', '.join(flags))
        else:
            st.success('Every numerical token matches the printed table. Check the metric and year yourself.')
        st.caption('Number validation checks exact displayed values. It cannot establish that a value is used with the correct metric or year.')
        st.download_button('Download business memo', memo, file_name=f'{ticker}-memo.md', mime='text/markdown')

with sources:
    st.subheader('How the numbers are selected')
    st.write('The script uses the latest five fiscal years from annual 10-K filings. Flows must cover an annual period; when a period appears in multiple filings, the latest filing wins. Only the assignment’s permitted XBRL tags and fallbacks are used.')
    st.markdown('**ROE** = net income ÷ year-end equity.\n\n**Owner earnings** = operating cash flow − capital spending. This is the lab’s simplified cash-flow proxy, not an estimate of maintenance spending.')
    st.write('The checks require ROE at or above the assigned threshold every year, positive owner earnings every year, and owner earnings higher in the final year than the first. Missing inputs keep a check unknown.')
    if 'source' in report:
        source = report['source']
        st.caption(f"Downloaded UTC: {source['downloaded_utc']}")
        st.link_button('View SEC company facts', source['url'])
        with st.expander('Snapshot fingerprint'):
            st.code(source['sha256'], language=None)
    with st.expander('XBRL tags and filing provenance'):
        st.markdown(sec.render_report(report).split('## XBRL provenance')[1])
    st.link_button('Lab 18 assignment', 'https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md')

st.divider()
st.caption('FIN 43900 · Purdue University · Fall 2026 · Educational business review')
