Substitute cold run performed by OpenAI Codex, not a human partner. Partner (Andrew) was unable to run it in class; instructor approved a substitute. Aidan observed the run.

# Lab 20 cold run

- Run date: November 17, 2026 (EST).
- Start: 17:32:36 EST, immediately before cloning.
- End: 17:33:39 EST, when Streamlit reported server startup.
- Branch: `lab-20-readiness`.
- Tested commit: `2a716767adc70efe87cd3e90d332a34fac0809ab`.
- First error in the clone, installation, or launch sequence: none. No fix or rerun was needed for server startup.
- Result location: Streamlit printed `http://localhost:8502` and reported that Uvicorn started on port 8502. The separate browser connection failed, so page rendering and interaction were not independently verified by Codex.

From the terminal, the setup and launch commands were:

```bash
mkdir "$HOME/Desktop/aidan_test"
cd "$HOME/Desktop/aidan_test"
date '+%F %T %Z'
git clone --branch lab-20-readiness https://github.com/aidanklebenow/VISA-Research-NEW.git
```

From the new clone root, the app commands came from `Project-2/README.md`:

```bash
cd Project-2
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --browser.gatherUsageStats false
```

Pip reported a successful install, including Streamlit 1.67.0 and pandas 3.1.1.
