import json

import pandas as pd
import streamlit as st

from model import ROOT, Settings, research_prompt, run, sensitivity_grid, stress_suite

FUNDS = {
    'SGOV': 'Short-term U.S. Treasury bills',
    'IEF': 'U.S. Treasury bonds',
    'LQD': 'Higher-rated company bonds',
    'VTI': 'U.S. stocks',
    'VXUS': 'Stocks outside the U.S.',
}
BASE = {
    'target': 7.5, 'limit': 10, 'reserve': 10, 'history': 60,
    'annual_cost': 0., 'trading_cost': 0., 'VTI_shift': 0., 'VXUS_shift': 0.,
    'portfolio_size': 100_000,
}
for ticker in FUNDS:
    BASE[f'{ticker}_included'] = True
    BASE[f'{ticker}_maximum'] = 100


def reset_inputs():
    for name, value in BASE.items():
        st.session_state[name] = value


def money(amount):
    return f'${amount:,.2f}'


st.set_page_config(page_title='Portfolio Trust | Project 2', layout='wide')
st.html("""
<style>
.block-container {max-width: 1050px; padding-top: 2.7rem; padding-bottom: 4rem;}
[data-testid="stMain"] h2 {border-top: 1px solid #d8e4e3; margin-top: 1.3rem; padding-top: 1.5rem;}
</style>
""")
for name, value in BASE.items():
    if name not in st.session_state:
        st.session_state[name] = value

with st.sidebar:
    st.header('Inputs')
    st.button('Reset to base case', on_click=reset_inputs)

    st.subheader('Goals')
    st.caption('Set the yearly gain you want, how much returns may swing, and what to keep in short-term U.S. Treasury bills.')
    target = st.number_input('Annual return target (%)', 0., 50., step=.5, key='target')
    limit = st.slider('Proposed volatility ceiling (%)', 1, 50, key='limit')
    reserve = st.slider('Minimum SGOV reserve (%)', 0, 100, step=5, key='reserve')

    st.subheader('History used')
    st.caption('Choose how many past monthly changes in fund prices go into the estimates.')
    history = st.selectbox('Months of returns', [36, 60, 120], key='history')
    if history == 120:
        st.caption('The bundled series contains 60 months of returns. A 120-month estimate is unavailable.')

    st.subheader('Funds')
    st.caption('Include each fund you want to test. A maximum weight is the most you can put in that fund.')
    fund_limits = {}
    with st.expander('Choose funds and maximum weights'):
        for ticker, description in FUNDS.items():
            included = st.checkbox(f'Include {ticker} · {description}', key=f'{ticker}_included')
            cap = st.number_input(f'{ticker} maximum weight (%)', 0, 100, step=5,
                                  key=f'{ticker}_maximum', disabled=not included)
            fund_limits[ticker] = cap / 100 if included else 0.

    st.subheader('Costs')
    st.caption('Annual costs repeat each year. The trading estimate is a separate, one-time bill on the initial investment.')
    annual_cost = st.number_input('Annual investor costs (%)', 0., 10., step=.1, key='annual_cost')
    trading_cost = st.number_input('One-time trading cost (%)', 0., 10., step=.1, key='trading_cost')

    st.subheader('What-ifs')
    st.caption('Change the estimated return for either stock fund. One percentage point takes 7% to 8%.')
    vti = st.slider('VTI return estimate change (percentage points)', -5., 5., step=.5, key='VTI_shift')
    vxus = st.slider('VXUS return estimate change (percentage points)', -5., 5., step=.5, key='VXUS_shift')

    st.subheader('Portfolio size')
    st.caption('Set the dollar amount used to translate each percentage into dollars.')
    size = st.number_input('Portfolio size ($)', min_value=1, step=1000, key='portfolio_size')

settings = Settings(target/100, reserve/100, annual_cost/100, limit/100)
limits = fund_limits if any(cap < 1 for cap in fund_limits.values()) else None
snapshot = None
input_error = None
try:
    snapshot = run(settings, vti_shift=vti/100, vxus_shift=vxus/100,
                   history_months=history, fund_limits=limits)
except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
    input_error = str(error)

st.title('Portfolio Trust')
st.caption('PROJECT 2  /  HISTORICAL CASE  /  OCTOBER 30, 2026')
st.write('Built by Aidan Klebenow, Purdue finance student. This case is for a hypothetical client who wants to grow their money over five years and keep cash available. The app tests how to split the money across five funds. It shows which mix clears the goals and when I would stop.')

st.header('The client and the rules')
st.write(f'The client has **{money(size)}** to invest in this example. The starting goal is **7.5% a year after annual costs** over **five years**. The starting reserve is **10% in SGOV**, a fund that holds short-term U.S. Treasury bills. A reserve is the part set aside for cash needs.')
st.markdown("""
- **Benchmark [AIDAN TO DECIDE].** A benchmark is the reference I use to judge performance.
- **Risk limit [AIDAN TO DECIDE].** This example uses 10% annual volatility, which measures how much returns tend to swing. The original case also called for zero losses on investments sold during a calendar year.
- **Issuer rule [AIDAN TO DECIDE].** The starting cap is 7% per issuer, the company or government that issued a stock or bond. Decide how to add up holdings across funds and how to treat Treasuries.
- **Withdrawals [AIDAN TO DECIDE].** Set how much cash the client needs and when.
""")

# REQ[P2-01]: Runnable decision app | Rubric: Technical execution and usability | Evidence: tests/check_app.py
st.header('How it works')
st.info('Fund prices → return and risk estimates → mixes in 5% steps → lowest-risk mix that meets the goal → rule checks')
st.markdown("""
1. Start with monthly fund prices that account for payouts and splits.
2. Estimate yearly returns and how much the funds move, both alone and together.
3. Test every split in five-percentage-point steps, subject to the fund maximums.
4. Pick the mix with the smallest swings that meets the return target after annual costs and holds the required reserve.
5. Check the volatility limit and show which rules passed.
""")

# REQ[P2-03]: Two transparent comparisons and rule-level verdicts | Rubric: Financial soundness and judgment | Evidence: output/results.json
st.header('The result')
candidate = None
if snapshot:
    candidate = next((row for row in snapshot['portfolios'] if row['name'] == 'Constrained portfolio'), None)
if input_error:
    st.error(f'Stop. {input_error}')
elif candidate is None:
    st.error('Stop. No grid portfolio meets the return target, reserve, and fund maximums.')
elif candidate['model_verdict'] == 'FAIL':
    st.error('Stop. Even the lowest-risk mix that meets the return and reserve targets exceeds the risk limit.')
else:
    st.success('The mix clears the numerical checks. Client money stays on hold until the investment rules are settled.')

if candidate:
    first, second, third = st.columns(3)
    first.metric(f'Yearly return vs. {target:g}% goal', f"{candidate['net_return_proxy']:.2%}", border=True)
    second.metric(f'Volatility vs. {limit:g}% limit', f"{candidate['volatility']:.2%}", border=True)
    third.metric('Numerical checks', candidate['model_verdict'], border=True)
    st.caption(f"Estimated yearly gain at the entered size: {money(size * candidate['net_return_proxy'])}. "
               f"One-time trading charge on the initial investment: {money(size * trading_cost / 100)}. "
               "The trading charge is shown separately from yearly return.")
    st.subheader('How the money would be split')
    allocation = pd.DataFrame([
        {'Fund': ticker, 'Holding': description, 'Weight (%)': weight * 100, 'Dollars': size * weight}
        for (ticker, description), weight in zip(FUNDS.items(), candidate['weights'])
    ])
    st.bar_chart(allocation, x='Fund', y='Dollars', horizontal=True, sort=False, height=230,
                 alt='Dollar amounts in each of the five funds')
    st.table(allocation.assign(**{'Weight (%)': allocation['Weight (%)'].map('{:.0f}%'.format),
                                  'Dollars': allocation['Dollars'].map(money)}))
    rule_names = ['All money assigned with no bets on falling prices', 'Estimated yearly gain meets target',
                  'SGOV reserve meets minimum', 'Volatility stays within limit', 'Fund maximums and exclusions respected']
    checks = list(candidate['rules'].values())
    if limits is None:
        checks.append(True)
    st.subheader('Rule checks')
    st.table(pd.DataFrame({'Rule': rule_names + ['Client benchmark, risk policy, issuer rule and withdrawals'],
                           'Result': ['PASS' if passed else 'FAIL' for passed in checks] + ['[AIDAN TO DECIDE]']}))

if snapshot:
    with st.expander('Compare this mix with two simpler choices'):
        st.write('Equal weight splits the money evenly across included funds. Inverse volatility gives more money to funds that have moved less.')
        st.table(pd.DataFrame([
            {'Mix': row['name'], 'Yearly return': f"{row['net_return_proxy']:.2%}",
             'Volatility': f"{row['volatility']:.2%}", 'Checks': row['model_verdict']}
            for row in snapshot['portfolios']
        ]))
        export = dict(snapshot, portfolio_size=size, one_time_trading_cost=trading_cost/100, fund_limits=fund_limits)
        st.download_button('Download calculation snapshot', json.dumps(export, indent=2), 'portfolio-snapshot.json')

st.header('What could go wrong')
st.write('Each test changes one input from the starting case. The dollar estimates use the portfolio size you enter.')


@st.cache_data
def fixed_checks():
    return stress_suite(), sensitivity_grid()


stresses, grid = fixed_checks()
causes = [
    'The starting mix sets the comparison',
    'If the U.S. stock fund earns one percentage point less, the mix changes to try to reach the same goal',
    'Using only the latest 36 months changes which market swings count',
    'Higher yearly costs change the mix needed to meet the goal',
    'Raising the reserve floor to 30% leaves the starting mix alone',
    'A 5% risk limit rejects the starting mix',
]
for cause, case in zip(causes, stresses):
    result = case['result']
    if result:
        st.write(f"• {cause} — {money(size * result['net_return_proxy'])} estimated gain per year and "
                 f"{result['volatility']:.2%} volatility.")
    else:
        st.write(f'• {cause} — no mix meets the rules.')

st.subheader('Sensitivity grid')
st.write('The grid shows what happens when the return goal and risk limit change together. The starting case is in the middle.')
grid_rows = []
for case in grid:
    row = {'Yearly return goal': f"{case['target']:.1%}"}
    for cell in case['cells']:
        value = cell['volatility']
        label = cell['verdict']
        row[f"{cell['limit']:.0%} risk limit"] = label if value is None else f'{label} · {value:.2%}'
    grid_rows.append(row)
st.table(pd.DataFrame(grid_rows))

st.header('The decision')
st.info('**[AIDAN TO DECIDE]**\n\nRecommendation and committee ask: ___  \n'
        'Allocation range: ___  \nRisks to watch: ___  \n'
        'Reversal trigger (what would make me change my recommendation): ___')

with st.expander('Data and sources'):
    if snapshot:
        signal = snapshot['signal']
        st.write(f"September 2026 inflation was {signal['inflation_yoy']:.2%} versus a year earlier. Inflation is the rise in prices. "
                 "The Consumer Price Index (CPI) tracks how the price of a basket of goods and services changes.")
    st.write('The bundled monthly fund prices end September 30, 2026. The October 29 version of the inflation release was first usable October 30 and leaves the fund weights alone. Historical results help compare mixes. Future gains and losses can differ.')
    st.markdown((ROOT / 'docs/data-card.md').read_text(encoding='utf-8'))
    if snapshot:
        question = st.text_area('Optional research question')
        if question.strip():
            st.download_button('Download research prompt', research_prompt(question, snapshot),
                               'research-question.txt', 'text/plain')
st.caption('AI use: OpenAI Codex assisted with software and validation. Education, not investment advice.')
