from pathlib import Path

from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=60)
assert not app.exception, app.exception
assert [heading.value for heading in app.header if heading.value != 'Inputs'] == [
    'The client and the rules', 'How it works', 'The result', 'What could go wrong', 'The decision']
assert [metric.value for metric in app.metric[:3]] == ['7.50%', '6.80%', 'PASS']
assert any('$55,000.00' in str(table.value) for table in app.table)

app.number_input(key='portfolio_size').set_value(200_000).run(timeout=60)
assert not app.exception, app.exception
assert any('$110,000.00' in str(table.value) for table in app.table)

app.number_input(key='trading_cost').set_value(1.).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[0].value == '7.50%'
assert any('One-time trading charge on the initial investment: $2,000.00' in caption.value
           for caption in app.caption)

app.slider(key='reserve').set_value(100).run(timeout=60)
assert not app.exception, app.exception
assert any('No grid portfolio' in item.value for item in app.error)
app.slider(key='reserve').set_value(10).run(timeout=60)
app.slider(key='limit').set_value(5).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[2].value == 'FAIL'
assert any('exceeds the risk limit' in item.value for item in app.error)

app.selectbox(key='history').set_value(120).run(timeout=60)
assert not app.exception, app.exception
assert any('bundled data contain 60' in item.value for item in app.error)
assert not app.metric
app.button[0].click().run(timeout=60)
assert not app.exception, app.exception
assert app.selectbox(key='history').value == 60
assert app.number_input(key='portfolio_size').value == 100_000
assert app.number_input(key='annual_cost').value == 0.
assert app.metric[2].value == 'PASS'
print('PASS: one-page app, dollar outputs, separate trading costs, stop conditions and reset.')
