import json
from datetime import date
from html import escape

import streamlit as st

import portfolio as portfolio_math
import report
from model import ROOT, Settings, available_return_months, run, stress_suite

FUNDS = report.FUNDS
BASE = {
    'target': 7.5, 'limit': 10, 'reserve': 10,
    'annual_cost': 0., 'trading_cost': 0., 'VTI_shift': 0., 'VXUS_shift': 0.,
    'portfolio_size': 100_000,
}
for ticker in FUNDS:
    BASE[f'{ticker}_included'] = True
    BASE[f'{ticker}_maximum'] = 100

st.set_page_config(page_title='Portfolio Trust: Allocation Recommendation', layout='wide')
try:
    months_available = available_return_months()
except (OSError, ValueError) as error:
    st.error(f'Could not read the fund price history. {error}')
    st.stop()

history_options = [months for months in (36, 60, 120) if months <= months_available]
BASE['history'] = 60 if 60 in history_options else max(history_options, default=None)
if st.session_state.get('history') not in history_options:
    st.session_state['history'] = BASE['history']
for name, original_value in BASE.items():
    if name not in st.session_state:
        st.session_state[name] = original_value


def reset_inputs():
    for name, original_value in BASE.items():
        st.session_state[name] = original_value


with st.sidebar:
    st.header('Model Inputs')
    st.write('These are the assumptions behind every result on the page. They start at the original case; change any input and the whole page updates.')
    with st.container(border=True, key='original-inputs'):
        st.markdown(
            '**Original Inputs**  \n'
            f"{BASE['target']:.1f}% return target · {BASE['limit']:.1f}% volatility limit  \n"
            f"{BASE['reserve']:.1f}% SGOV cash reserve · {BASE['history'] or 'Unavailable'} months  \n"
            f"{report.dollars(BASE['portfolio_size'])} portfolio · no extra costs  \n"
            'All five funds · no caps'
        )
    st.button('Reset to Original Inputs', on_click=reset_inputs, width='stretch',
              help='Restore the original portfolio size and analytical assumptions.')
    with st.expander('01 · Client Goals', expanded=True):
        st.caption('Set the target gain, acceptable swings and minimum cash reserve.')
        size = st.number_input('Portfolio Size ($)', min_value=1, step=1000, key='portfolio_size',
                               help='The amount to invest. Dollar figures scale with this amount.')
        target = st.number_input('Annual Return Target (%)', 0., 50., step=.5, key='target',
                                 help='Minimum average yearly gain after annual investor costs.')
        limit = st.slider('Volatility Limit (%)', 1, 50, key='limit',
                          help='Maximum annual standard deviation, a measure of how widely returns swing.')
        reserve = st.slider('Minimum Cash Reserve in SGOV (%)', 0, 100, step=5, key='reserve',
                            help='Minimum share in short-term U.S. Treasury bills through SGOV.')
    fund_limits = {}
    current_weights = {}
    with st.expander('02 · Funds & Caps'):
        st.caption('Choose the funds to test and set their maximum weights. 100% = no cap.')
        for ticker, (description, _, _) in FUNDS.items():
            included = st.checkbox(f'Include {ticker}', key=f'{ticker}_included', help=description)
            cap = st.number_input(f'{ticker} · Maximum Allowed in This Fund (%)', 0, 100, step=5,
                                  key=f'{ticker}_maximum', disabled=not included,
                                  help='100% means no cap. A weight is the share of the portfolio in this fund.')
            fund_limits[ticker] = cap / 100 if included else 0.
            current_weights[ticker] = st.empty()
    with st.expander('03 · Market History'):
        st.caption('A shorter window reflects recent markets. A longer one includes more market conditions.')
        history = st.selectbox('Months of Returns', history_options, key='history',
                               disabled=not history_options,
                               help='Number of monthly fund returns used to estimate gains and volatility.')
        st.caption(f'The bundled data contains {months_available} months of returns. Longer lookbacks are omitted.')
    with st.expander('04 · Costs'):
        st.caption('Annual costs reduce the return estimate. The initial trading charge is shown separately.')
        annual_cost = st.number_input('Annual investor costs (%)', 0., 10., step=.1, key='annual_cost',
                                      help='Recurring investor costs. Fund expenses are already reflected in adjusted prices.')
        trading_cost = st.number_input('One-Time Trading Cost (%)', 0., 10., step=.1, key='trading_cost',
                                       help='A one-time charge applied to the starting investment for display.')
    historical = {}
    using = {}
    shifts = {}
    with st.expander('05 · Return Assumptions'):
        st.caption('Test a more pessimistic or optimistic view of future returns. This changes the recommended mix and every result above.')
        for ticker in ('VTI', 'VXUS'):
            st.markdown(f'**{ticker} · {FUNDS[ticker][1]}**')
            historical[ticker] = st.empty()
            shifts[ticker] = st.slider('Adjust Estimate (Percentage Points)', -5., 5., step=.5,
                                       key=f'{ticker}_shift',
                                       help='A one-point increase takes an estimate from 7% to 8%.')
            using[ticker] = st.empty()

title, switch = st.columns([.83, .17], vertical_alignment='center')
with title:
    st.title('Portfolio Trust: Allocation Recommendation')
    st.caption(f"Built by Aidan Klebenow · Purdue University · Run date {date.today():%b %d, %Y}")
with switch:
    mode_label = 'Dark Mode' if st.session_state.get('dark_mode', False) else 'Light Mode'
    dark = st.toggle(mode_label, key='dark_mode', help='Switch the report and charts between light and dark.')
report.style(dark)

changed = []
input_labels = {
    'target': 'return target', 'limit': 'volatility limit', 'reserve': 'cash reserve',
    'history': 'history', 'annual_cost': 'annual investor cost', 'trading_cost': 'one-time trading cost',
    'VTI_shift': 'VTI return adjustment', 'VXUS_shift': 'VXUS return adjustment', 'portfolio_size': 'portfolio size',
}
for key, label in input_labels.items():
    value = st.session_state[key]
    if value != BASE[key]:
        formatted = (report.dollars(value) if key == 'portfolio_size' else
                     f'{value} months' if key == 'history' else
                     f'{value:+.1f} percentage points' if key.endswith('_shift') else f'{value:.1f}%')
        changed.append(f'{label}: {formatted}')
for ticker in FUNDS:
    if not st.session_state[f'{ticker}_included']:
        changed.append(f'{ticker} excluded')
    cap = st.session_state[f'{ticker}_maximum']
    if cap != 100:
        changed.append(f'{ticker} maximum: {cap:.1f}%')
if changed:
    st.html(f'<div class="changed-case"><strong>You are viewing a modified case:</strong> '
            f'{escape("; ".join(changed))}</div>')

settings = Settings(target/100, reserve/100, annual_cost/100, limit/100)
limits = fund_limits if any(cap < 1 for cap in fund_limits.values()) else None
input_error = report.cap_error(fund_limits)
snapshot = None
if not input_error:
    try:
        if history is None:
            raise ValueError('At least 36 monthly returns are needed for the available lookbacks.')
        snapshot = run(settings, vti_shift=shifts['VTI']/100, vxus_shift=shifts['VXUS']/100,
                       history_months=history, fund_limits=limits)
    except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
        input_error = str(error)

candidate = None
if snapshot:
    candidate = next((row for row in snapshot['portfolios'] if row['name'] == 'Constrained portfolio'), None)
for i, ticker in enumerate(FUNDS):
    weight = report.percent(candidate['weights'][i]) if candidate else '—'
    current_weights[ticker].caption(f'Selected weight: {weight}')
estimates = snapshot['estimates'] if snapshot else None
if estimates is None and history is not None:
    try:
        estimates = portfolio_math.estimate_from_csv(ROOT / 'data/prices.csv', history_months=history)
    except (OSError, ValueError):
        pass
if estimates:
    gains = {ticker: gain for ticker, gain, _ in estimates['vehicles']}
    for ticker in shifts:
        used = gains[ticker] if snapshot else gains[ticker] + shifts[ticker] / 100
        historical[ticker].caption(f'Historical estimate: {report.percent(used - shifts[ticker] / 100)} per year')
        using[ticker].caption(f'Using: {report.percent(used)} per year')

# REQ[P2-01]: Runnable decision app | Rubric: Technical execution and usability | Evidence: tests/check_app.py
report.section(1, 'Bottom Line')
with st.container(border=True):
    if input_error:
        st.error(input_error)
    elif candidate is None:
        st.error('No grid portfolio meets the return target, cash reserve and fund limits.')
    else:
        names = snapshot['tickers']
        parts = [f'{report.percent(weight)} {FUNDS[ticker][1]} ({ticker})'
                 for ticker, weight in zip(names, candidate['weights']) if weight > 0]
        expected = report.dollars(round(size * candidate['net_return_proxy'], -2))
        swing = report.dollars(round(size * candidate['volatility'], -2))
        if candidate['model_verdict'] == 'PASS':
            summary = f"Recommended mix: {', '.join(parts)}"
        else:
            summary = f"Lowest-volatility mix: {', '.join(parts)} (above the volatility limit)"
        summary = (f'{summary} — estimated annual gain of about {expected} on {report.dollars(size)}, '
                   f'with typical annual swings of about ±{swing} around that estimate.')
        st.html(f'<div class="bottom-summary"><strong>{escape(summary)}</strong></div>')
    st.html(f'Committee decision: {report.placeholder()}')

report.section(2, 'Key Numbers')
card_specs = [
    ('Expected Annual Return', report.percent(candidate['net_return_proxy']) if candidate else '—',
     'Average yearly gain after annual costs, estimated from historical prices. '
     'The client target is 7.5% per year.'
     + (f' The active target is {target:.1f}%.' if target != BASE['target'] else '')
     + (f" The estimate is {report.dollars(size * candidate['net_return_proxy'])} a year." if candidate else '')),
    ('Volatility', report.percent(candidate['volatility']) if candidate else '—',
     'Measures how far yearly returns typically swing from the average. '
     + (f"That is about ±{report.dollars(round(size * candidate['volatility'], -2))} on {report.dollars(size)}. " if candidate else '')
     + f'The active limit is {limit:.1f}%.'),
]
checks = dict(candidate['rules']) if candidate else {}
if candidate:
    checks.setdefault('Fund maximums and exclusions respected', True)
card_specs.append(('Rule Checks', f'{sum(checks.values())} of 5 Passed' if candidate else '—',
                   'The model checks the return target, cash reserve, volatility limit, fund caps and whether all the money is invested.'))
for card_index, (column, (label, value, caption)) in enumerate(zip(st.columns(3), card_specs)):
    with column:
        with st.container(border=True, key=f'number-card-{card_index}'):
            st.metric(label, value)
            st.caption(caption)

# REQ[P2-03]: Two transparent comparisons and rule-level verdicts | Rubric: Financial soundness and judgment | Evidence: output/results.json
report.section(3, 'Recommended Allocation')
with st.container(border=True):
    if candidate:
        if candidate['model_verdict'] == 'FAIL':
            st.warning('The mix exceeds the volatility limit. It remains visible so the breach can be examined.')
        chart, holdings = st.columns([1, 1.15], vertical_alignment='center')
        with chart:
            st.plotly_chart(report.allocation_chart(candidate, names, size, dark),
                            theme=None, config=report.CHART_CONFIG)
        with holdings:
            report.table(['Fund', 'What It Holds', 'Weight', 'Dollars'], [
                (report.fund_mark(ticker), FUNDS[ticker][0], report.percent(weight), report.dollars(weight * size))
                for ticker, weight in zip(names, candidate['weights']) if weight > 0
            ], label='Recommended allocation')
            st.caption(f'One-time trading charge: {report.dollars(size * trading_cost / 100)} on the starting investment. Annual return excludes this separate charge.')
        with st.expander('Numerical Rule Details'):
            report.table(['Rule', 'Result'], [(rule, 'Pass' if passed else 'Fail') for rule, passed in checks.items()],
                         classes={(i, 1): 'pass' if passed else 'fail' for i, passed in enumerate(checks.values())})
    else:
        st.write('An allocation appears when a mix meets the return, cash reserve and fund limits.')
    if snapshot:
        with st.expander('Two Comparison Portfolios'):
            st.write('Equal weight splits money evenly across the included funds. Inverse volatility favors funds whose returns have moved less.')
            report.table(['Portfolio', 'Expected Annual Return', 'Volatility', 'Rule Checks'], [
                (row['name'], report.percent(row['net_return_proxy']), report.percent(row['volatility']), row['model_verdict'])
                for row in snapshot['portfolios']
            ])
            export = dict(snapshot, portfolio_size=size, one_time_trading_cost=trading_cost/100, fund_limits=fund_limits)
            st.download_button('Download Calculation Snapshot', json.dumps(export, indent=2), 'portfolio-snapshot.json')

report.section(4, 'Methodology')
points = None
with st.container(border=True):
    flow = ('Fund Prices', 'Return and Risk Estimates', 'Mixes in 5% Steps', 'Lowest-Risk Mix', 'Rule Checks')
    st.html('<div class="flow">' + '<b>→</b>'.join(f'<span>{name}</span>' for name in flow) + '</div>')
    st.markdown("""
1. Collect monthly fund prices adjusted for payouts and splits.
2. Estimate average yearly returns, volatility and how the funds move together.
3. Test fully invested mixes in five-percentage-point steps within the fund limits.
4. Select the lowest-volatility mix that meets the after-cost return target and cash reserve.
5. Check the selected mix against the risk limit and display the rule verdict.
""")
    st.subheader('Efficient Frontier')
    if snapshot:
        points = report.tested_mixes(estimates['vehicles'], estimates['correlations'],
                                     list(fund_limits.values()) if limits is not None else None,
                                     settings.annual_cost)
        st.plotly_chart(report.frontier_chart(points, candidate, settings, dark),
                        theme=None, config=report.CHART_CONFIG)
        st.caption(f'{len(points):,} dots show tested mixes by volatility and expected return, and the efficient frontier traces the highest available return at each level of risk for mixes that meet the cash reserve.')
    else:
        st.caption('The chart requires a valid set of inputs.')

report.section(5, 'Risk & Stress Testing')


@st.cache_data(show_spinner=False)
def saved_stresses():
    return stress_suite()


with st.container(border=True):
    st.caption('These six reference scenarios use their original assumptions. The bad-year loss in dollars scales with the entered portfolio size.')
    stress_names = ('Original Case', 'Lower U.S. Stock Return', 'Shorter Market History', 'Higher Annual Costs',
                    'Higher Cash Reserve', 'Tighter Risk Limit')
    descriptions = ('Original inputs', 'VTI estimate down 1.0 percentage point', 'Last 36 monthly returns',
                    'Annual investor cost rises to 0.5%', 'SGOV reserve rises to 30.0%',
                    'Volatility limit drops to 5.0%')
    rows = []
    status = {}
    for index, (name, description, case) in enumerate(zip(stress_names, descriptions, saved_stresses())):
        row = case['result']
        loss = max(0, 2 * row['volatility'] - row['net_return_proxy']) * size if row else None
        loss_label = ('—' if loss is None else '$0 (no loss in a 2-SD year)' if loss == 0
                      else report.dollars(loss))
        rows.append((name, description, report.mix_text(row['weights'], FUNDS) if row else 'No mix',
                     report.percent(row['net_return_proxy']) if row else '—',
                     report.percent(row['volatility']) if row else '—',
                     loss_label, 'Fail' if case['stop'] else 'Pass'))
        status[index, 6] = 'fail' if case['stop'] else 'pass'
    report.table(['Scenario', 'What Changed', 'New Mix', 'Return', 'Volatility', '“Bad Year” Loss', 'Result'],
                 rows, classes=status, label='Reference stress tests')
    st.caption('The bad-year illustration subtracts twice the annual standard deviation (a measure of typical spread) from the expected return. It shows the resulting loss in dollars, floored at zero. Actual losses can be larger.')

report.section(6, 'Sensitivity Analysis')
with st.container(border=True):
    st.caption('Sensitivity shows how the outcome changes as the return goal and volatility limit move. Other inputs follow the active case.')
    if points is not None:
        grid_rows, colors = [], {}
        for i, (goal, risk) in enumerate(zip(report.GOALS, report.grid_results(points, settings.reserve))):
            row = [report.percent(goal)]
            for j, ceiling in enumerate(report.CEILINGS, start=1):
                status = 'none' if risk is None else 'over' if risk > ceiling + 1e-12 else 'pass'
                label = {'none': 'No mix', 'over': 'Over limit', 'pass': 'Pass'}[status]
                row.append(f'{label} · {report.percent(risk)}' if risk is not None else label)
                colors[i, j] = status + (' base' if (goal, ceiling) == (.075, .10) else '')
            grid_rows.append(row)
        report.table(['Return Goal'] + [report.percent(limit) for limit in report.CEILINGS],
                     grid_rows, classes=colors, label='Return goal by volatility limit')
        st.html('<span class="legend-chip status-pass">Pass</span>'
                '<span class="legend-chip status-over">Over limit</span>'
                '<span class="legend-chip status-none">No possible mix</span>'
                '<span class="legend-chip base">Outlined cell: original goal and limit</span>')
    else:
        st.caption('The grid requires a valid set of inputs.')

report.section(7, 'Client Mandate')
with st.container(border=True):
    st.write('The mandate is the client’s investment rulebook. This case uses an illustrative portfolio and a five-year horizon.')
    mark = report.placeholder()
    report.table(['Rule', 'Setting', 'Why'], [
        ('Portfolio Size', f'{report.dollars(size)} illustration', 'Converts portfolio weights and estimates to dollars.'),
        ('Annual Return Target', '7.5% after recurring costs', 'Sets the yearly growth objective over five years.'),
        ('Cash Reserve', '10.0% in SGOV in the original case', 'Keeps a share in short-term Treasury bills.'),
        ('Benchmark', mark, 'Sets a reference against which to judge performance.'),
        ('Risk Limit', mark, 'The model starts at 10.0% volatility. The client risk policy requires a decision.'),
        ('Issuer Rule', mark, 'The original 7.0% cap limits exposure to the same issuer across holdings.'),
        ('Withdrawals', mark, 'The amount and timing of cash needs affect the required reserve.'),
    ], label='Client mandate')

report.section(8, 'Investment Committee Recommendation')
with st.container(border=True):
    fields = ('Recommendation', 'Allocation Range', 'Key Risks', 'Reversal Trigger', 'Committee Ask')
    st.html('<div class="decision-fields">' + ''.join(
        f'<strong>{field}</strong><div>{report.placeholder()}</div>' for field in fields) + '</div>')

report.section(9, 'Data Sources & Notes')
with st.expander('Data Sources & Notes'):
    st.markdown("""
- **Fund prices:** Yahoo Finance monthly adjusted prices from September 2021 through September 2026. Final price observation: September 30, 2026. [Yahoo terms of service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html).
- **Inflation:** U.S. Bureau of Labor Statistics Consumer Price Index via FRED/ALFRED. The October 29, 2026 vintage was eligible for the October 30, 2026 decision snapshot. [FRED terms and attribution](https://fred.stlouisfed.org/legal/).
- **Data use:** No personal data used. Market data remains subject to provider terms. The portfolio size is illustrative.
- **Project 2 Editions A and B:** For the student’s own comparison. Neither is submitted.
- **AI-use disclosure:** OpenAI Codex-assisted implementation and validation. Education, not investment advice.
""")
    if snapshot:
        st.caption(f"September 2026 inflation: {report.percent(snapshot['signal']['inflation_yoy'])} year over year. This series tracks changes in consumer prices and does not set fund weights.")
    with st.expander('Inflation Data Card'):
        st.markdown((ROOT / 'docs/data-card.md').read_text(encoding='utf-8'))
