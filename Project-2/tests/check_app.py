from pathlib import Path

from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=60)
assert not app.exception, app.exception
assert [tab.label for tab in app.tabs] == [
    'Overview', 'Portfolio', 'Risk & Stress Tests', 'Data & Sources', 'Committee Decision']
assert [metric.value for metric in app.metric[:3]] == ['7.50%', '6.80%', 'PASS']
assert 'Withheld' in str(app.dataframe[0].value)
app.slider[0].set_value(100).run(timeout=60)
assert not app.exception, app.exception
assert any('No grid portfolio' in item.value for item in app.error)
app.slider[0].set_value(10).run(timeout=60)
app.slider[1].set_value(5).run(timeout=60)
assert not app.exception, app.exception
assert app.metric[2].value == 'FAIL'
assert any('exceeds the risk limit' in item.value for item in app.error)
print('PASS: app renders, and both stop conditions are visible.')
