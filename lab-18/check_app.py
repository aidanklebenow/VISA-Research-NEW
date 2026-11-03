"""Exercise app UI with synthetic inputs in a temporary repository."""
import json
from pathlib import Path
import shutil
import tempfile

from streamlit.testing.v1 import AppTest
from test_sec_facts import fixture, sec

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    (root / 'lab-18/evidence').mkdir(parents=True)
    (root / 'lab-18/memos').mkdir()
    target = root / '.agents/skills/buffett-business/scripts'
    target.mkdir(parents=True)
    shutil.copy(ROOT / 'lab-18/app.py', root / 'lab-18/app.py')
    shutil.copy(ROOT / '.agents/skills/buffett-business/scripts/sec_facts.py', target)
    report = sec.analyze(fixture(), 'COST')
    (root / 'lab-18/evidence/COST-report.json').write_text(json.dumps(report))
    (root / 'lab-18/memos/COST.md').write_text('Watch it. ROE was 100.0%.')
    app = AppTest.from_file(str(root / 'lab-18/app.py')).run(timeout=30)
    assert not app.exception, app.exception
    assert len(app.dataframe) == 1
    assert any('Every numerical token matches' in x.value for x in app.success)
    app.text_area[0].set_value('Unsupported ROE: 40.0%.').run()
    assert any('40.0%' in x.value for x in app.error)
    app.text_input[0].set_value('JPM').run()
    assert any('Download SEC facts to begin' in x.value for x in app.info)
    app.text_input[0].set_value('../../invalid').run()
    assert app.warning and not app.exception
print('App checks passed: table, valid memo, injected percentage, absent ticker, invalid ticker.')
