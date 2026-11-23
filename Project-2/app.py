import json

import pandas as pd
import streamlit as st

from model import ROOT, Settings, research_prompt, run, stress_suite

st.set_page_config(page_title='Portfolio Trust | Project 2', layout='wide')
st.title('Portfolio Trust')
st.caption('DECISION SNAPSHOT  /  OCTOBER 30, 2026')

with st.sidebar:
    st.header('Try different assumptions')
    target = st.number_input('Annual return target (%)', 0., 50., 7.5, .5,
                             help='The yearly gain you want after the costs entered here.')
    reserve = st.slider('Minimum SGOV reserve (%)', 0, 100, 10, 5,
                        help='The smallest share kept in SGOV, a fund holding short-term U.S. Treasury bills.')
    limit = st.slider('Proposed volatility ceiling (%)', 1, 50, 10,
                      help='Volatility measures how much returns tend to move around. The ceiling is the largest amount allowed by this check.')
    cost = st.number_input('Annual investor costs (%)', 0., 10., 0., .1)
    st.caption('Enter yearly trading or advice costs. Fund expenses already affect the price data. Taxes are excluded.')
    short = st.checkbox('Use last 36 monthly returns')
    shift = st.slider('VTI return estimate change (percentage points)', -5., 5., 0., .5,
                      help='VTI is a broad U.S. stock fund. One percentage point changes 7% to 8%, for example.')

settings = Settings(target/100, reserve/100, cost/100, limit/100)
try:
    snapshot = run(settings, short, shift/100)
except (OSError, ValueError, KeyError, ZeroDivisionError) as error:
    st.error(f'Stop. The model could not verify its inputs. {error}')
    st.stop()

candidate = next((row for row in snapshot['portfolios'] if row['name'] == 'Constrained portfolio'), None)
if candidate is None:
    st.error('Stop. No grid portfolio meets the return target and minimum reserve.')
elif candidate['model_verdict'] == 'FAIL':
    st.error('Stop. Even the least volatile mix that meets the return and reserve targets exceeds the risk limit.')
else:
    st.info('Research only. This mix passes the numerical checks. Client money stays on hold until the investment rules are settled.')

st.markdown('**What this app does**')
st.write('Compare ways to split money across five funds. The app uses historical prices to estimate annual return (how much money might grow in a year after entered costs) and volatility (how much returns tend to swing). It checks whether a mix meets your targets. A technical pass alone does not establish that the mix fits a client’s needs.')

return_card, risk_card, check_card = st.columns(3)
return_card.metric('Estimated annual return', f"{candidate['net_return_proxy']:.2%}" if candidate else '—',
                   help=f'Current target: {target:g}% after entered costs.', border=True)
risk_card.metric(f'Volatility vs. {limit:g}% limit', f"{candidate['volatility']:.2%}" if candidate else '—',
                 help='An annual estimate of how much returns typically fluctuate.', border=True)
check_card.metric('Numerical checks', candidate['model_verdict'] if candidate else 'NO MIX', border=True)

# REQ[P2-01]: Runnable decision app | Rubric: Technical execution and usability | Evidence: tests/check_app.py
overview, portfolio, risk, data, committee = st.tabs(
    ['Overview', 'Portfolio', 'Risk & Stress Tests', 'Data & Sources', 'Committee Decision'])

with overview:
    st.subheader('How to read the result')
    st.write('A pass means the mix clears the return target, holds enough in reserve, and stays within the volatility limit. The client decision also depends on the full mandate, meaning the rules for investing the client’s money.')
    with st.expander('Facts behind this'):
        st.write(f'The return target is {target:g}%, the minimum SGOV reserve is {reserve:g}%, the volatility limit is {limit:g}%, and entered annual costs are {cost:g}%. Pricing ends September 30, 2026.')
        st.write('The search finds the lowest estimated volatility among mixes that meet return and reserve requirements. The app checks the volatility limit afterward. It shows a failing candidate when even the lowest-risk mix exceeds that limit.')
    st.download_button('Download calculation snapshot', json.dumps(snapshot, indent=2), 'portfolio-snapshot.json', 'application/json')

with portfolio:
    # REQ[P2-03]: Two transparent comparisons and rule-level verdicts | Rubric: Financial soundness and judgment | Evidence: output/results.json
    st.subheader('Compare three ways to split the money')
    st.write('Equal weight splits money evenly. Inverse volatility favors funds whose returns have swung less. The constrained portfolio is the lowest-risk mix the search finds under the return and reserve rules.')
    rows = [
        {'Portfolio': row['name'], **{name: f'{weight:.1%}' for name, weight in zip(snapshot['tickers'], row['weights'])},
         'Annual return': f"{row['net_return_proxy']:.2%}", 'Volatility': f"{row['volatility']:.2%}",
         'Numerical checks': row['model_verdict'], 'Client approval': 'Withheld'}
        for row in snapshot['portfolios']
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
    with st.expander('Facts behind this'):
        st.write('Weights are percentages of the total investment. The model searches long-only mixes (no bets on prices falling) in steps of five percentage points, with all the money assigned. The risk calculation uses how much each fund swings and how closely funds move together.')
        for row in snapshot['portfolios']:
            st.markdown(f"**{row['name']}**")
            for rule, passed in row['rules'].items():
                st.write(f"{'PASS' if passed else 'FAIL'} · {rule}")

with risk:
    st.subheader('Could a change in assumptions stop the process?')
    st.write('Stress tests ask what happens when one assumption changes. Stop if the search finds no mix, if the lowest-risk mix breaks the risk limit, or if the source data cannot be verified.')

    @st.cache_data
    def fixed_stresses():
        return stress_suite()

    rows = []
    for case in fixed_stresses():
        row = case['result']
        rows.append({'Scenario': case['scenario'], 'Annual return': f"{row['net_return_proxy']:.2%}" if row else '—',
                     'Volatility': f"{row['volatility']:.2%}" if row else '—',
                     'Model action': 'Stop' if case['stop'] else 'Research checks pass'})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
    with st.expander('Facts behind this'):
        st.write('These examples start from the saved base settings. The shorter price history changes which market periods are counted. Higher costs reduce the estimated gain and can require a different mix. A tighter risk limit can reject the same mix even when its estimated return stays the same.')
        for case in fixed_stresses():
            if case['result']:
                weights = ', '.join(f'{name} {weight:.0%}' for name, weight in zip(snapshot['tickers'], case['result']['weights']))
                st.write(f"{case['scenario']} · {weights}")

with data:
    st.subheader('Historical prices and inflation')
    st.write('Inflation is the rise in prices over time. The Consumer Price Index (CPI) tracks a basket of household goods and services.')
    signal = snapshot['signal']
    st.metric('September 2026 inflation vs. a year earlier', f"{signal['inflation_yoy']:.2%}")
    with st.expander('Facts behind this'):
        st.write('A vintage is a saved version of a data release. This calculation uses the same October 29 vintage for both months. The first eligible decision date is October 30. The signal helps monitor purchasing power and leaves portfolio weights unchanged.')
        st.write('Price estimates use bundled monthly adjusted prices. Adjusted prices account for changes such as distributions and splits. Historical averages can change with the sample and cannot guarantee a future return.')
        st.markdown((ROOT / 'docs/data-card.md').read_text(encoding='utf-8'))

with committee:
    st.subheader('Client approval is withheld')
    st.write('Before committing client money, settle how to judge performance, how much risk is acceptable, how much can be invested with one issuer, and when the client needs cash.')
    with st.expander('Facts behind this'):
        st.write('A benchmark is the reference used to judge performance. An issuer is the organization behind a stock or bond. An issuer limit may have to count holdings across multiple funds.')
        st.markdown('**Human-owned decisions and evidence**')
        st.write('Benchmark: ___  ·  Risk limit: ___  ·  Issuer rule: ___  ·  Withdrawals: ___')
        st.write('Committee action, allocation range, and reversal trigger: ___')
        st.write('AI-off prediction commit, run, and diagnosis: ___')
    with st.expander('Prepare a research question'):
        st.caption('Creates a downloadable prompt. No AI service is connected.')
        question = st.text_area('Your investment question')
        if question.strip():
            st.download_button('Download research prompt', research_prompt(question, snapshot),
                               'research-question.txt', 'text/plain')
