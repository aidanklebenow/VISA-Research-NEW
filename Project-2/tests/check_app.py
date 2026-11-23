from pathlib import Path

from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=60)
assert not app.exception, app.exception
sections = [heading.value for heading in app.header if heading.value != 'Model Inputs']
assert sections == [
    'Bottom Line', 'Key Numbers', 'Recommended Allocation', "What's Inside Each ETF", 'Methodology',
    'Risk & Stress Testing', 'Sensitivity Analysis', 'Client Mandate',
    'Investment Committee Recommendation', 'Data Sources & Notes',
]
assert [metric.value for metric in app.metric[:3]] == ['7.5%', '6.8%', '5 of 5 Passed']
assert len(app.get('plotly_chart')) == 2
assert any('**Original Inputs**' in item.value and '7.5% return target' in item.value
           and 'All five funds · no caps' in item.value for item in app.markdown)
assert not any('active target is 7.5%' in item.value for item in app.caption)
assert any('$0 (no loss in a 2-SD year)' in item.proto.body for item in app.get('html'))
profiles = next(item.proto.body for item in app.get('html') if 'class="etf-grid"' in item.proto.body)
assert profiles.count('class="etf-profile"') == 5
assert profiles.count('issuer page</a>, as of') == 5
assert '55.0% · $55,000' in profiles
stress = next(item.proto.body for item in app.get('html') if 'aria-label="Reference stress tests"' in item.proto.body)
for ticker in ('SGOV', 'IEF', 'LQD', 'VTI', 'VXUS'):
    assert f'</span>{ticker}</th>' in stress
assert '55.0%<small>$55,000</small>' in stress
assert 'stress-weight muted-weight">0.0%<small>$0</small>' in stress
assert app.toggle(key='dark_mode').value
assert app.toggle(key='dark_mode').label == 'Dark Mode'

app.toggle(key='dark_mode').set_value(False).run(timeout=60)
assert not app.exception, app.exception
assert not app.toggle(key='dark_mode').value
assert app.toggle(key='dark_mode').label == 'Light Mode'
assert len(app.get('plotly_chart')) == 2
assert app.metric[0].value == '7.5%'
app.toggle(key='dark_mode').set_value(True).run(timeout=60)
assert not app.exception, app.exception
assert app.toggle(key='dark_mode').label == 'Dark Mode'

app.number_input(key='portfolio_size').set_value(200_000).run(timeout=60)
assert not app.exception, app.exception
assert any('$200,000' in html.proto.body for html in app.get('html'))
assert any('55.0% · $110,000' in html.proto.body for html in app.get('html'))
assert any('55.0%<small>$110,000</small>' in html.proto.body for html in app.get('html'))
app.number_input(key='trading_cost').set_value(1.).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[0].value == '7.5%'
assert any('One-time trading charge: $2,000' in caption.value for caption in app.caption)

app.slider(key='reserve').set_value(100).run(timeout=60)
assert not app.exception, app.exception
assert any('No grid portfolio' in item.value for item in app.error)
app.slider(key='reserve').set_value(10).run(timeout=60)
app.slider(key='limit').set_value(5).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[2].value == '4 of 5 Passed'
assert any('exceeds the volatility limit' in item.value for item in app.warning)

assert app.selectbox(key='history').options == ['36', '60']
app.selectbox(key='history').set_value(36).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[0].value == '7.6%'
app.button[0].click().run(timeout=60)
assert not app.exception, app.exception
assert app.selectbox(key='history').value == 60
assert app.number_input(key='portfolio_size').value == 100_000
assert app.number_input(key='target').value == 7.5
assert app.slider(key='limit').value == 10
assert app.slider(key='reserve').value == 10
assert app.number_input(key='annual_cost').value == 0.
assert app.number_input(key='trading_cost').value == 0.
assert app.slider(key='VTI_shift').value == 0.
assert app.slider(key='VXUS_shift').value == 0.
for ticker in ('SGOV', 'IEF', 'LQD', 'VTI', 'VXUS'):
    assert app.checkbox(key=f'{ticker}_included').value
    assert app.number_input(key=f'{ticker}_maximum').value == 100
assert not any('You are viewing a modified case' in html.proto.body for html in app.get('html'))
assert app.metric[2].value == '5 of 5 Passed'
print('PASS: report, both themes, dollar outputs, risk stops, supported lookbacks and original-input reset.')
