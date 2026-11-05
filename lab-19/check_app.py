"""Exercise real saved reports and interactive controls without network calls."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

HERE = Path(__file__).resolve().parent
app = AppTest.from_file(str(HERE / 'app.py')).run(timeout=30)
assert not app.exception, app.exception
assert len(app.tabs) == 6
assert len(app.dataframe) == 3
assert any('Nasdaq observation' == t.label for t in app.tabs)
assert any('What counts as passing?' in m.value for m in app.markdown)
assert any('SEC company facts documentation' in m.value for m in app.markdown)
assert any('All investor memos checked' in x.value for x in app.success)
assert list(app.dataframe[0].value['Investor'].unique()) == ['Buffett', 'Graham', 'Burry']
for index in range(3):
    original = app.text_area[index].value
    app.text_area[index].set_value(original + ' Unsupported 40.0%.').run()
    assert any('40.0%' in x.value for x in app.error)
    app.text_area[index].set_value(original).run()
app.number_input[0].set_value(1.0).run()
app.number_input[1].set_value(5.0).run()
probe = app.dataframe[2].value
assert probe.iloc[0]['Probe'] == 'pass'
assert probe.iloc[3]['Probe'] == 'pass'
assert probe.iloc[4]['Probe'] == 'not known'
app.radio[0].set_value('Additional view · Cathie Wood').run()
assert 'Cathie Wood' in list(app.dataframe[0].value['Investor'])
app.text_area[1].set_value(app.text_area[1].value + ' Unsupported 40.0%.').run()
assert any('Cathie Wood: unprinted numbers' in x.value for x in app.error)
next(x for x in app.selectbox if x.label == 'Choose a company').set_value('NVDA · NVIDIA').run()
assert app.text_input[0].value == 'NVDA'
assert not app.exception
assert 'Does not clear screen' in ' '.join(x.value for x in app.markdown)
next(x for x in app.selectbox if x.label == 'Choose a company').set_value('JPM · JPMorgan Chase').run()
assert app.text_input[0].value == 'JPM'
assert not app.exception
next(x for x in app.selectbox if x.label == 'Choose a company').set_value('Other ticker').run()
app.text_input[0].set_value('ZZZZZZ').run()
assert any('No saved company report' in x.value for x in app.info)
app.text_input[0].set_value('../../bad').run()
assert app.warning and not app.exception
print('UI passed: two panel views, all memo injections, live threshold controls, NVDA/JPM, missing and invalid tickers.')
