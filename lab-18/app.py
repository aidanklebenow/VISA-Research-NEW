"""Run from repository root: python3 -m streamlit run lab-18/app.py."""
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

st.set_page_config(page_title='Buffett Business Review', layout='wide')
st.title('Buffett Business Review')
st.caption('Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
st.write('Review earning power and cash generation using annual filings. “Own the business” is a business-quality verdict. This lab excludes stock prices, so the app cannot determine whether the shares are a good buy at today’s price.')
ticker = st.text_input('Ticker', 'COST').strip().upper()
email = st.text_input('SEC contact email (used only for downloads)', value=os.getenv('SEC_EMAIL', ''), type='password')
if st.button('Download latest SEC facts'):
    try:
        with st.spinner('Downloading annual SEC facts…'):
            sec.download(ticker, email, EVIDENCE)
        st.success('Downloaded and calculated. Ask Codex to use the Buffett skill to write or refresh the memo.')
    except (OSError, ValueError) as error:
        st.error(str(error))

# Never form a filesystem path from an unvalidated ticker.
if not sec.re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', ticker):
    st.warning('Enter a valid ticker such as COST or JPM.')
    st.stop()
report_path = EVIDENCE / f'{ticker}-report.json'
if not report_path.exists():
    st.info('Download SEC facts to begin. No example figures are substituted for live data.')
    st.stop()
try:
    report = json.loads(report_path.read_text())
except (OSError, ValueError) as error:
    st.error(f'Cannot read saved report: {error}')
    st.stop()
st.subheader(report['company'])
st.caption('USD millions; ROE uses year-end equity. Owner earnings = operating cash flow − capital spending.')
chart = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                       'Owner earnings': r['owner_earnings']['value'] / 1e6 if r['owner_earnings']['value'] is not None else None,
                       'Net income': r['net_income']['value'] / 1e6 if r['net_income']['value'] is not None else None}
                      for r in report['rows']]).set_index('Fiscal year end')
st.line_chart(chart, y_label='USD millions')
st.dataframe(sec.table_rows(report), hide_index=True, width='stretch')
for label, status in report['checks'].items():
    st.write(f'**{label}: {status}**')
with st.expander('XBRL tags and filing provenance'):
    st.markdown(sec.render_report(report).split('## XBRL provenance')[1])
if 'source' in report:
    st.caption(f"Downloaded UTC: {report['source']['downloaded_utc']}")
    st.link_button('SEC company facts source', report['source']['url'])
st.subheader('Buffett-inspired memo')
memo_path = MEMOS / f'{ticker}.md'
saved = memo_path.read_text() if memo_path.exists() else ''
if not saved:
    st.info('Memo pending: ask Codex to use $buffett-business on this ticker after downloading.')
with st.expander('Edit memo or test an unsupported number'):
    memo = st.text_area('Memo text', value=saved, height=220, key=f'memo-{ticker}')
if memo:
    st.markdown(memo)
    flags = sec.unsupported_numbers(memo, report)
    if flags:
        st.error('Numbers not printed in the financial table: ' + ', '.join(flags))
    else:
        st.success('Every numerical token matches the printed table. Check the metric and year yourself.')
    st.caption('The checker compares exact displayed numbers; it cannot verify that a supported number is attached to the right claim.')
    if st.button('Save memo'):
        MEMOS.mkdir(parents=True, exist_ok=True)
        memo_path.write_text(memo)
        st.success('Saved Markdown memo locally.')
    st.download_button('Download memo (.md)', memo, file_name=f'{ticker}.md')
