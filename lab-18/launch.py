"""Start the local dashboard without requiring terminal commands."""
import os
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen
import webbrowser

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
URL = 'http://localhost:8518'
env = os.environ.copy()
config = HERE / '.env'
if config.exists():
    for line in config.read_text().splitlines():
        key, separator, value = line.partition('=')
        if separator and key == 'SEC_EMAIL':
            env[key] = value.strip()


def ready():
    try:
        with urlopen(URL + '/_stcore/health', timeout=1) as response:
            return response.read() == b'ok'
    except OSError:
        return False


if not ready():
    python = HERE / '.venv/bin/python'
    if not python.exists():
        raise SystemExit('The app environment is missing. Ask Codex to set up Lab 18.')
    with (HERE / 'app.log').open('a') as log:
        subprocess.Popen([str(python), '-m', 'streamlit', 'run', str(HERE / 'app.py'),
                          '--server.port', '8518', '--server.address', '127.0.0.1',
                          '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
                         cwd=ROOT, env=env, stdout=log, stderr=log, start_new_session=True)
    for _ in range(60):
        if ready():
            break
        time.sleep(0.5)
    else:
        raise SystemExit('App did not start. Ask Codex to inspect lab-18/app.log.')
webbrowser.open(URL)
print('Lab 18 is open at ' + URL)
