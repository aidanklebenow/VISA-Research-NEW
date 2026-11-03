# Lab 18 — Legend Investor as Skill

Aidan Klebenow · FIN 43900 · Fall 2026

This Streamlit app reviews a business using five fiscal years of SEC EDGAR 10-K facts. Its finished layout separates the financial overview, business memo, and source methodology into tabs, with latest-year metric cards and a sidebar for choosing the ticker and refreshing SEC data. Code computes the numbers and three Buffett checks. Codex uses the bundled skill to write a separate Buffett-inspired memo. No API key, paid financial data, price feed, or model API is needed.

## Open without commands

Double-click **Double-click here to open Warren Buffett app for Lab 18.command** in the repository root. It starts the app if needed and opens your browser; repeated clicks reuse the running app. Your SEC contact email is stored only in ignored `lab-18/.env`. While running, open http://localhost:8518.

## Run

Open the `VISA-Research-NEW` repository root, then:

```bash
python3 -m venv lab-18/.venv
lab-18/.venv/bin/python -m pip install -r lab-18/requirements.txt
lab-18/.venv/bin/python -m streamlit run lab-18/app.py
```

Enter your real contact email in the app and download COST, then JPM. It is used in the SEC User-Agent with Aidan Klebenow's name; it is not written into reports or source. Download errors remain visible rather than substituting sample data.

Alternatively, set `SEC_EMAIL` locally (never commit it), then run:

```bash
python3 .agents/skills/buffett-business/scripts/sec_facts.py COST
python3 .agents/skills/buffett-business/scripts/sec_facts.py JPM
```

Reports are saved under `lab-18/evidence/` as JSON and Markdown; raw downloaded facts are ignored by Git. Reports include source URL, UTC retrieval time, hash, XBRL tags, filing dates and accession identifiers. Hashes use sorted-key JSON serialization of the source facts.

Launch Codex from this repository so it discovers [the skill](../.agents/skills/buffett-business/SKILL.md) in `.agents/skills`. Ask: “Use $buffett-business on COST and JPM; write their memos using only the script's printed table.” The memo is AI judgment, not a programmed verdict. The app can show and save the Markdown memo; it does not call a model itself.

## Data rules

Only USD facts in 10-K filings are eligible. Annual flows must span 350–380 elapsed days, accommodating fiscal calendars with an extra week while excluding quarters. Annual net-income facts identify fiscal-year ends; the last five are selected. Within each requested period and tag, the latest filing wins, including later comparative restatements. The ordered revenue and capital-spending fallbacks follow the assignment. ROE divides net income by year-end equity; owner earnings subtracts total capital spending from operating cash flow. This is the assigned simplified proxy, not a maintenance-capex estimate.

Missing source values print “not found.” ROE with missing or nonpositive equity prints “not known.” Any check lacking five complete inputs prints “not known.” The chart leaves missing values blank. No company-specific financial answers appear in the extractor or app.

The memo checker compares exact numerical tokens against the financial table's displayed values. For example, type an unsupported `40.0%` into the memo to see it flagged. It is a presence check: a supported number can still be attached to the wrong year or metric, so review the claims yourself. Filing accession numbers are not admitted as financial evidence.

## Verify and complete

```bash
python3 -m unittest discover -s lab-18 -p 'test_*.py' -v
lab-18/.venv/bin/python lab-18/check_app.py
python3 lab-18/verify_known_answers.py
```

The unit and UI checks use synthetic inputs, clearly separate from live verification. Only `verify_known_answers.py` contains the professor's reference values; it compares saved live reports and cannot populate the app.

Verified November 3, 2026: live SEC COST values match every assigned value and all checks pass. JPM capital spending and owner earnings remain “not found”; both owner-earnings checks are “not known.” Both AI-written memos pass the numerical-token check; an injected `40.0%` is flagged. Six extraction tests and the Streamlit UI checks passed. Aidan supplied his trust decision and the fresh-chat response; see [checkout notes](checkout.md). The partner exercise remains incomplete because his partner was absent. No answers were substituted for downloaded values.

Submission files are finalized; see [submission links](SUBMISSION.md). Aidan supplied a written reflection, edited with AI assistance. His partner was absent, so the live partner/no-AI exercise was not completed. Brightspace quiz completion and submission remain Aidan's tasks; no waiver or submission is claimed.

## Explain simply

A skill is a reusable instruction folder. Codex first reads its name and description, then loads the detailed instructions when relevant. Here it repeats the data-selection rules and calculations; the model still judges whether the evidence warrants owning, watching or passing. Missing data is more honest than inventing a convincing number.

In `year_row()`, the script selects each input for one fiscal-year end. It calculates ROE only with available income and positive equity, and calculates owner earnings only when both cash-flow inputs exist. Otherwise the value remains missing. The formatting function turns those missing values into the assignment's required words.

## Sources

- [Current Lab 18, rebuilt November 1](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md)
- [Buffett reference: read only, not installed](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md)
- [SEC EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [Official Codex skill documentation](https://developers.openai.com/codex/skills)
- [Streamlit chart documentation](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart)

Built with AI help for an educational demonstration; not investment advice.
