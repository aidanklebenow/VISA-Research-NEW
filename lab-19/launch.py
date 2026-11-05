"""Launch the separate Lab 19 app; normal use requires no terminal."""
from pathlib import Path
import os
import subprocess
import time
from urllib.request import urlopen
import webbrowser

HERE = Path(__file__).resolve().parent
URL = 'http://localhost:8519'


def ready():
    try:
        with urlopen(URL + '/_stcore/health', timeout=1) as response:
            return response.read() == b'ok'
    except OSError:
        return False


def main():
    if not ready():
        python = HERE / '.venv/bin/python'
        if not python.exists():
            raise SystemExit('Lab 19 environment missing. Ask Codex to restore it using lab-19/requirements.txt.')
        with (HERE / 'app.log').open('a') as log:
            subprocess.Popen([str(python), '-m', 'streamlit', 'run', str(HERE / 'app.py'),
                              '--server.port', '8519', '--server.address', '127.0.0.1',
                              '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
                             cwd=HERE.parent, env=os.environ.copy(), stdout=log, stderr=log, start_new_session=True)
        for _ in range(60):
            if ready():
                break
            time.sleep(.5)
        else:
            raise SystemExit('Lab 19 did not start. Ask Codex to inspect lab-19/app.log.')
    webbrowser.open(URL)


if __name__ == '__main__':
    main()
