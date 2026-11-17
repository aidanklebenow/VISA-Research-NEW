from pathlib import Path
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=60)
assert not app.exception, app.exception
assert len(app.dataframe) == 2
assert 'FAIL' in str(app.dataframe[0].value)
app.slider[0].set_value(100).run(timeout=60)
assert not app.exception, app.exception
assert any('No grid portfolio' in item.value for item in app.error)
app.text_area[0].set_value('Would a diversified fund reduce concentration risk?').run(timeout=60)
assert not app.exception, app.exception
assert any('Not connected' in item.value for item in app.warning)
print('PASS: app renders, infeasibility is visible, question box remains clearly disconnected.')
