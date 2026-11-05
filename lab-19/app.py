"""Lab 19: one SEC snapshot, distinct investor lenses, honest evidence gaps."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import panel
import presentation

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
INVESTORS = {'Buffett': 'buffett', 'Graham': 'graham', 'Burry': 'burry', 'Cathie Wood': 'wood'}
st.set_page_config(page_title='Legend Panel · Lab 19', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {padding-top:2rem;max-width:1550px}
[data-testid="stMetric"] {border:1px solid #77889940;border-radius:12px;padding:18px}
h1 {letter-spacing:-.04em} [data-testid="stSidebar"] {border-right:1px solid #77889930}
[data-testid="stTabs"] h3 {margin-top:1.4rem}
[data-testid="stMarkdownContainer"] li {margin-bottom:.5rem}
.result-table {width:100%;border-collapse:collapse;font-size:.94rem;margin:1rem 0 2rem}
.result-table th {text-align:left;background:#172c47;color:#fff;padding:14px}
.result-table td {padding:14px;border-bottom:1px solid #77889940;vertical-align:top}
.result-table .pass {color:#14866a;font-weight:800;white-space:nowrap}
.result-table .fail {color:#cf554f;font-weight:800;white-space:nowrap}
.result-table .unknown {color:#ab7c22;font-weight:800;white-space:nowrap}
</style>''', unsafe_allow_html=True)
st.caption('PURDUE UNIVERSITY   /   FIN 43900   /   AIDAN KLEBENOW')
st.title('One business. Different lenses.')
st.write('The Legend Panel · Compare earning power, financial strength, and cash quality on the same SEC facts.')
st.caption('AI-written investor-inspired interpretations for education. These are not the investors’ actual opinions or stock-price recommendations.')
if 'ticker' not in st.session_state:
    st.session_state.ticker = 'COST'
if 'pending_ticker' in st.session_state:
    st.session_state.ticker = st.session_state.pop('pending_ticker')
with st.sidebar:
    st.header('Legend Panel')
    company = st.selectbox('Choose a company', ['COST · Costco', 'NVDA · NVIDIA', 'JPM · JPMorgan Chase', 'Other ticker'])
    ticker = st.text_input('Company ticker', key='ticker').strip().upper()
    chosen = company.split(' · ')[0]
    if company != st.session_state.get('last_company'):
        st.session_state.last_company = company
        if company != 'Other ticker' and ticker != chosen:
            st.session_state.pending_ticker = chosen
            st.rerun()
    mode = st.radio('Panel', ['Current assignment · Graham', 'Additional view · Cathie Wood'])
    st.caption('Saved companies: COST · NVDA · JPM. VTI’s largest holding is NVIDIA; see source evidence.')
    with st.expander('SEC download settings'):
        email = st.text_input('SEC contact email', panel.load_email(), type='password')
        refresh = st.button('Refresh from SEC', width='stretch')
    st.divider()
    st.caption('Same facts. Different questions. Agreement is evidence to inspect, not an independent vote.')
    st.link_button('Open preserved Lab 18', 'http://localhost:8518')
if not panel.sec.re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', ticker):
    st.warning('Enter a valid company ticker.'); st.stop()
if refresh:
    try:
        with st.spinner('Downloading annual SEC facts…'):
            panel.download(ticker, email, EVIDENCE)
        st.success('Refreshed. Saved memos must be reviewed against the new snapshot.')
    except (OSError, ValueError) as error:
        st.error(f'SEC download failed: {error}')
path = EVIDENCE / f'{ticker}-report.json'
if not path.exists():
    st.info('No saved company report. Use SEC download settings to retrieve its annual facts.'); st.stop()
try:
    report = json.loads(path.read_text())
except (OSError, ValueError) as error:
    st.error(f'Cannot read report: {error}'); st.stop()
rows = report['rows']
selected = ['Buffett', 'Graham' if 'Graham' in mode else 'Cathie Wood', 'Burry']
st.subheader(f"{ticker} / {report['company']}")
st.caption(f"{rows[0]['fiscal_year_end']} → {rows[-1]['fiscal_year_end']} · Annual 10-K facts · USD millions; ratios in times")
for column, field in zip(st.columns(4), ['revenue', 'owner_earnings', 'current_ratio', 'liabilities_equity']):
    column.metric(panel.LABELS[field], panel.display(field, rows[-1][field]))
main, financials, probe, market, sources, learning = st.tabs(['Investor panel', 'Financial facts', 'Threshold lab', 'Nasdaq observation', 'Sources & references', 'My checkout'])
with main:
    st.markdown('### What is this test?')
    st.write('The panel applies several financial checks to the same annual SEC facts. Each investor lens asks a different question. Passing means the company meets that specific rule; a complete passing screen makes it a candidate for further research.')
    st.markdown('**PASS** — the required facts meet the rule.  ·  **FAIL** — the available facts do not meet the rule.  ·  **NOT KNOWN** — required facts are missing or a ratio cannot be calculated.')
    active = {name: report['panel'][name] for name in selected}
    for column, (name, checks) in zip(st.columns(3), active.items()):
        with column:
            with st.container(border=True):
                st.subheader(name)
                st.caption(presentation.LENSES[name][0])
                st.write(presentation.LENSES[name][1])
                st.write('**Final result: ' + panel.verdict(checks) + '**')
                st.caption(f"{list(checks.values()).count('pass')} of {len(checks)} checks pass · {list(checks.values()).count('not known')} unknown")
    st.dataframe(panel.panel_rows(active), hide_index=True, width='stretch', column_config={'Check': st.column_config.TextColumn(width='large')})
    st.markdown('### Understand every check')
    st.caption('Annual cash and profit amounts below are USD millions. Ratios use unrounded inputs. “Every period” requires a complete annual history. The table and memos preserve the assignment baseline; your chosen Graham threshold appears in Threshold lab.')
    from html import escape
    details = presentation.explained_checks(report, selected)
    for name in selected:
        st.markdown(f'#### {name} · {presentation.LENSES[name][0]}')
        html = '<table class="result-table"><thead><tr><th>Test & purpose</th><th>What counts as passing?</th><th>What the facts show</th><th>Final result</th></tr></thead><tbody>'
        for item in (d for d in details if d['Investor'] == name):
            status_class = {'PASS': 'pass', 'FAIL': 'fail', 'NOT KNOWN': 'unknown'}[item['Result']]
            html += f'<tr><td><strong>{escape(item["Test"])}</strong><br>{escape(item["What it means"])}</td><td>{escape(item["Passing rule"])}</td><td>{escape(item["Evidence from saved report"])}</td><td class="{status_class}"><strong>{item["Result"]}</strong></td></tr>'
        st.markdown(html + '</tbody></table>', unsafe_allow_html=True)
    st.subheader('Read the interpretations')
    all_memos = {}
    metadata = json.loads((HERE / 'memos/manifest.json').read_text()) if (HERE / 'memos/manifest.json').exists() else {}
    for name, slug in INVESTORS.items():
        memo_path = HERE / f'memos/{ticker}-{slug}.md'
        all_memos[name] = memo_path.read_text() if memo_path.exists() else ''
    snapshot = report.get('source', {}).get('sha256')
    stale = metadata.get(ticker, {}).get('source_sha256') != snapshot
    if stale:
        st.warning('Memo snapshot has not been confirmed against this report. Review the memos before relying on them.')
    for column, name in zip(st.columns(3), selected):
        with column:
            with st.container(border=True):
                st.markdown(f'#### {name} lens')
                memo = all_memos[name]
                if memo:
                    st.markdown(memo)
                else:
                    st.info('AI-written memo pending. Ask Codex to use this investor’s skill on the printed report.')
                if name == 'Graham':
                    st.caption('Aidan keeps a 1.0 cutoff to include Costco in further research. This memo preserves the assignment baseline of 2.0; see Threshold lab for the comparison.')
                elif name == 'Cathie Wood':
                    st.caption('Optional Wood threshold choice remains pending. Baseline memo uses the original threshold.')
    with st.expander('Validate or experiment with memo text'):
        st.caption('Try an unsupported 40.0%. Edits here are session-only; original memos remain preserved.')
        for name in selected:
            all_memos[name] = st.text_area(f'{name} memo', all_memos[name], key=f'{ticker}-{name}', height=180)
    flags = panel.memo_flags(all_memos, report)
    for name, found in flags.items():
        if found:
            st.error(f'{name}: unprinted numbers — ' + ', '.join(found))
    if not any(flags.values()) and all(all_memos.values()):
        st.success('All investor memos checked: every numerical token appears in the printed financial facts.')
    st.caption('This check covers every saved investor memo, including the other panel view. It checks token presence, not whether a number is attached to the correct metric or year.')
with financials:
    st.subheader('Annual financial facts')
    st.dataframe(panel.table_rows(report), hide_index=True, width='stretch')
    st.metric('Annual revenue growth · four intervals', panel.growth_display(report))
    st.caption('“Not found”: no eligible reported input. “Not known”: a ratio or check cannot be determined. Missing R&D / revenue remains “not found”; its screen remains “not known.”')
    chart = pd.DataFrame([{ 'Fiscal year end': r['fiscal_year_end'], **{panel.LABELS[f]: r[f]['value']/1e6 if r[f]['value'] is not None else None for f in ('net_income', 'owner_earnings')}} for r in rows]).set_index('Fiscal year end')
    st.line_chart(chart, y_label='USD millions', color=['#648bda', '#20b29b'])
    st.download_button('Download full source report', panel.render(report), file_name=f'{ticker}-panel.md', mime='text/markdown')
with probe:
    st.subheader('Change a rule. Keep the facts.')
    st.write('Thresholds are screening choices. Moving a cutoff changes the answer without changing the company.')
    a, b = st.columns(2)
    graham = a.number_input('Graham minimum current ratio', min_value=0.0, value=1.0, step=0.1)
    wood = b.number_input('Wood minimum annual growth (%)', min_value=0.0, value=15.0, step=1.0)
    changed = panel.evaluate(report, graham_current_ratio=graham, wood_growth_pct=wood)
    comparison = []
    for name in ('Graham', 'Cathie Wood'):
        for (old_label, old_status), (new_label, new_status) in zip(report['panel'][name].items(), changed[name].items()):
            comparison.append({'Investor': name, 'Active check': new_label, 'Baseline': old_status, 'Probe': new_status, 'Changed': 'yes' if old_status != new_status else 'no'})
    st.dataframe(comparison, hide_index=True, width='stretch')
    st.info('COST probes: Graham 2.0 → 1.0; Wood 15% → 5%. These controls recalculate checks using unrounded values. They do not rewrite the baseline memos or record your final choice.')
    st.markdown('**Aidan’s retained Graham cutoff: 1.0.** The screen is a starting point for research, including questions about liquidity and unusual financial patterns.')
with market:
    st.subheader(f'{ticker} · Nasdaq observation desk')
    st.write('Connect the financial screen to what the market is doing. Use the Nasdaq pages below to observe the stock price, trading activity, news and upcoming earnings, then ask whether the financial facts help explain what you see.')
    st.info('Current quotes are not loaded in this app. Nasdaq returned no quote values during verification on November 5, 2026. The annual SEC figures elsewhere in the app are saved financial history, not live market data.')
    base = f'https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}'
    for col, (label, suffix) in zip(st.columns(3), [('Quote & overview', ''), ('News', '/news-headlines'), ('Historical prices', '/historical')]):
        col.link_button(f'{ticker} · {label}', base + suffix, width='stretch')
    st.markdown('### What to look for')
    st.markdown('''- **Price and timing:** Record the quote, its timestamp, and whether it is delayed. Compare equivalent periods when judging a move.
- **Trading activity:** Is volume unusually high compared with the stock’s normal trading activity? Look for an earnings release or other dated announcement.
- **Financial explanation:** Does the cash-flow or earnings history support the story behind the price move? A disagreement is a research question, not proof of mispricing.
- **Next question:** What filing, earnings release or company disclosure would help you test the explanation?''')
    st.text_area('My market observations and follow-up questions', key=f'market-note-{ticker}', placeholder='Observation and timestamp → source → possible explanation → evidence still needed')
    st.caption('Notes are session-only. Nasdaq hosts market pages for companies listed on different exchanges; this tab does not imply every company is Nasdaq-listed.')
with sources:
    st.subheader('Reliable sources · follow the evidence')
    st.write('SEC filings support the accounting facts. Vanguard supports the dated fund-holding selection. Nasdaq provides market observations. GitHub documents the classroom rules and investor-inspired frameworks.')
    for title, url, explanation in presentation.SOURCE_LINKS:
        st.markdown(f'**[{title}]({url})** — {explanation}')
    st.markdown(f'**[{ticker} on Nasdaq](https://www.nasdaq.com/market-activity/stocks/{ticker.lower()})** — Quote, news and market context; check the page’s timestamp and data availability.')
    st.subheader('One source of facts for every investor')
    source = report.get('source', {})
    st.link_button('SEC companyfacts', source.get('url', 'https://www.sec.gov'))
    st.caption('Retrieved UTC: ' + source.get('downloaded_utc', 'not recorded'))
    st.code(source.get('sha256', 'not recorded'), language=None)
    st.write('Lab 19 reuses the unchanged Lab 18 downloader and extraction rules. Only annual USD 10-K facts are eligible; flows cover 350–380 elapsed days. Latest filing wins within each permitted tag. Five fiscal-year ends are anchored by annual net income. Ordered revenue and capital-spending tag fallbacks remain unchanged.')
    st.markdown('''- ROE = net income / year-end equity; nonpositive equity stays unknown.
- Owner earnings = operating cash flow − capital spending, a simplified lab proxy.
- Current ratio = current assets / current liabilities; denominator must be positive.
- Liabilities / equity uses total liabilities, not debt; equity must be positive.
- R&D / revenue uses reported R&D; missing expense is never assumed zero.
- Revenue growth = (last / first) ** (1/4) − 1, requiring five consecutive annual observations and positive revenue.
- Every-year and first-to-last screens require five complete inputs. Any missing input leaves that check unknown. Checks use full precision.''')
    with st.expander('Tags, filing dates, and accession links'):
        st.markdown(panel.render(report).split('## Filing provenance')[1])
    st.markdown((HERE / 'sources/fund-selection.md').read_text() if (HERE / 'sources/fund-selection.md').exists() else 'Fund evidence pending.')
    st.link_button('Current Lab 19 assignment', 'https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-19-legend-panel.md')
with learning:
    st.subheader('Prepare your own answer')
    st.markdown((HERE / 'LEARNING.md').read_text() if (HERE / 'LEARNING.md').exists() else 'Study guide pending.')
    decision = st.selectbox('My final screening decision', ['Not answered', 'Yes', 'No', 'Only with a condition'])
    reason = st.text_area('My reason or condition', key='reason')
    thresholds = st.text_area('My retained threshold(s) and why', key='choice')
    st.download_button('Download my personal answers', f'# My Lab 19 answers\n\nDecision: {decision}\n\nReason / condition: {reason}\n\nThresholds: {thresholds}\n', file_name='Lab19-my-answers.md', mime='text/markdown')
    st.caption('Your entries are session-only until downloaded. Partner work, no-AI explanation, quiz, and Brightspace submission must be completed personally.')
st.divider()
st.caption('SEC EDGAR facts · Code computes the screens · AI interprets the evidence · You make the decision')
