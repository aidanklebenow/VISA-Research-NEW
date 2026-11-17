import json
import pandas as pd
import streamlit as st
from model import ROOT, Settings, run, stress_suite, research_prompt

st.set_page_config(page_title='Portfolio Trust | Project 2', page_icon='◈', layout='wide')
st.caption('Built with OpenAI Codex for code, research organization and validation. Aidan must review and own the final analysis and decision. Education, not investment advice.')
st.title('Portfolio Trust')
st.write('**Can this process earn a committee’s trust?** Compare the evidence, challenge the assumptions, and know when to stop.')
st.info('Historical research snapshot · decision date October 30, 2026 · prices end September 30, 2026 · no live account or quotes. Working mandate awaits Aidan’s approval.')
with st.sidebar:
    st.header('Research assumptions')
    target = st.number_input('Annual return target (%)', 0., 50., 7.5, .5)
    reserve = st.slider('Minimum SGOV reserve (%)', 0, 100, 10, 5)
    limit = st.slider('Proposed volatility ceiling (%)', 1, 50, 10)
    cost = st.number_input('Annual investor costs (%)', 0., 10., 0., .1)
    st.caption('Trading/advisory cost scenario. Fund expenses already affect adjusted prices; do not subtract them again. Taxes are excluded.')
    short = st.checkbox('Use last 36 monthly returns')
    shift = st.slider('VTI return estimate change (percentage points)', -5., 5., 0., .5)
settings = Settings(target/100, reserve/100, cost/100, limit/100)
try:
    snapshot = run(settings, short, shift/100)
except ValueError as error:
    st.error(str(error))
    st.stop()
overview, stresses, signal, assistant, evidence = st.tabs(['Portfolio decision', 'Stress & stop', 'Point-in-time signal', 'Ask a research question', 'Evidence & ownership'])
with overview:
    st.subheader('Research use only; client allocation is not approved')
    st.write('The five-year draft targets 7.5% annually with a 10% Treasury reserve. No final client risk mandate or withdrawal schedule has been verified. The original 7% issuer rule needs fund look-through and Treasury definitions.')
    table = []
    for r in snapshot['portfolios']:
        table.append({'Portfolio':r['name'], **{n:f'{w:.1%}' for n,w in zip(snapshot['tickers'],r['weights'])},
                      'Return proxy':f"{r['net_return_proxy']:.2%}", 'Volatility':f"{r['volatility']:.2%}",
                      'Model checks':r['model_verdict'], 'Full mandate':r['full_mandate_verdict']})
    st.dataframe(pd.DataFrame(table), hide_index=True, width='stretch')
    if not snapshot['feasible']:
        st.error('STOP: No grid portfolio meets the return-estimate target and reserve rule. Do not relax them silently.')
    for r in snapshot['portfolios']:
        with st.expander(r['name']+' — rule-by-rule verdict'):
            for rule, passed in r['rules'].items():
                st.write(('✅ PASS: ' if passed else '❌ FAIL: ')+rule)
            st.write('**Full mandate FAIL: unresolved requirements prevent approval.**')
            for item in r['unresolved']:
                st.write('• '+item)
    st.caption('Equal weight = 20% per fund. Inverse volatility weights are proportional to 1 / estimated volatility; this is transparent, not a forecast. Search uses 5-percentage-point steps. Risk is annualized monthly sample standard deviation, not a worst-loss limit.')
    st.download_button('Download this calculation snapshot', json.dumps(snapshot,indent=2), 'portfolio-snapshot.json', 'application/json')
with stresses:
    st.write('**These are AI-assisted development checks. They are not your Locked Changed-Input Record.** Fixed scenarios below use the original draft settings, independently of sidebar edits.')
    @st.cache_data
    def fixed_stresses():
        return stress_suite()
    rows = []
    for case in fixed_stresses():
        r=case['result']
        rows.append({'Scenario':case['scenario'], 'Weights SGOV / IEF / LQD / VTI / VXUS':str([round(w*100,1) for w in r['weights']]) if r else 'Infeasible',
                     'Return proxy':f"{r['net_return_proxy']:.2%}" if r else 'Unavailable',
                     'Volatility':f"{r['volatility']:.2%}" if r else 'Unavailable',
                     'Model action':'STOP' if case['stop'] else 'Research check passes'})
    st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
    st.warning('Stop client use while mandate rules remain unresolved. Stop the model if no feasible allocation exists, a proposed risk limit fails, data provenance is missing, or point-in-time eligibility cannot be established. A large weight change triggers review; it does not automatically authorize trading.')
with signal:
    s=snapshot['signal']
    st.metric('September 2026 CPI inflation, year over year', f"{s['inflation_yoy']:.2%}")
    st.write(f"Calculation: ({s['value']} / {s['prior_value']} − 1) × 100. Both values come from the October 29 vintage. First permitted decision session: October 30, 2026.")
    st.write('**Use:** monitor purchasing-power risk. This signal does not change the optimizer’s weights; no forecasting edge or historical trading performance is claimed.')
    st.markdown((ROOT/'docs/data-card.md').read_text())
with assistant:
    st.subheader('Prepare a question for an AI research assistant')
    st.warning('Not connected to an AI service. This box generates a prompt containing the local calculation and research safeguards; it does not generate an AI answer.')
    question=st.text_area('Your investment question',placeholder='What should I investigate before replacing a concentrated stock position with diversified funds?')
    if question.strip():
        prompt=research_prompt(question,snapshot)
        st.download_button('Download research prompt',prompt,'research-question.txt','text/plain')
        with st.expander('Preview the prompt'):
            st.text(prompt)
    st.write('Live Q&A requires a provider/credential decision. Actual holdings, taxes, account type and risk preferences must be verified before portfolio-specific alternatives are assessed.')
    st.markdown('[Investor.gov: diversification](https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds-and-exchange-traded-funds) · [SEC company filings](https://www.sec.gov/edgar/search/)')
with evidence:
    st.write('OpenAI Codex prepared the implementation and drafts on November 10, 2026. No partner cold run, student AI-off prediction, recording, final investment decision or submission is claimed.')
    st.markdown('[Project requirements](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md) · [Week 12 studio](https://github.com/CinderZhang/FIN43900-Fall2026/tree/main/lessons/week-12)')
    st.markdown((ROOT/'docs/data-card.md').read_text())
    st.caption('Historical price evidence: data/price-sources.json. Visible executed output: output/results.json. See docs/validation-and-ai-use.md for scope and limitations.')
