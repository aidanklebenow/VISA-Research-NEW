AI use: OpenAI Codex assisted with software, validation, and documentation; Claude (Anthropic) assisted with reviewing wording and planning. All decisions and the locked prediction are Aidan's. Education, not investment advice.

# Portfolio Trust

Portfolio Trust helps a portfolio analyst and an investment committee decide whether a way of splitting money across five funds is worth using. It compares three mixes, estimates how much each might earn and how much its value might swing, and shows which rules each mix passes. The October 30, 2026 example passes its numerical checks for one mix. Aidan’s recommendation and client policies are recorded in the committee memo.

## Start Here

Install Python 3.14 and Git. Clone and open this project:

```sh
git clone --branch lab-20-readiness https://github.com/aidanklebenow/VISA-Research-NEW.git
cd VISA-Research-NEW/Project-2
```

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe model.py
.\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false
```

### Mac or Linux

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python model.py
.venv/bin/python -m streamlit run app.py --browser.gatherUsageStats false
```

Open the Local URL printed in Terminal. Try the volatility limit and read the verdict in **Bottom Line**. The lookback menu shows only windows supported by the bundled prices. The current snapshot offers 36 and 60 months. The example starts at a hypothetical $100,000, and the one-time trading cost is shown separately from the annual return. The bundled data work offline after dependencies are installed. No account or credentials are required.

To run the checks, use the Python executable above with `-m unittest discover -s tests -v`, then with `tests/check_app.py`.

## Executed Result

| Mix | Estimated yearly return after entered costs | Estimated yearly volatility | Numerical checks |
|---|---:|---:|---|
| Equal weight | 4.87% | 8.80% | Fail |
| Inverse volatility | 3.64% | 1.67% | Fail |
| Lowest-risk candidate | 7.50% | 6.80% | Pass |
| 60/40 policy benchmark | 7.17% | 11.51% | Fail |

Volatility measures how much returns tend to swing. The selected mix is 55% SGOV, 30% VTI and 15% VXUS, with 0% each for IEF and LQD. Inputs were a 7.5% return target, 10% minimum SGOV reserve, 10% volatility limit and zero entered annual costs. The portfolio uses adjusted monthly prices through September 30, 2026. The [data card](docs/data-card.md) explains the inflation release available on the October 30 decision date. The original estimate is $7,501 a year on the $100,000 example. All five weights are within Aidan’s [allocation bands](docs/decision-memo.md#11-allocation-range). The 60/40 benchmark uses 60% VTI and 40% IEF. Annual rebalancing is its policy convention, while this table reports fixed-weight estimates. Historical estimates are uncertain and monthly prices can miss losses within a month.

## Repository Map

- [App](app.py), [decision and scenario logic](model.py), [allocation engine](portfolio.py)
- [Input files](data/), [executed output](output/results.json), [tests](tests/)
- [Committee memo](docs/decision-memo.md), [validation and AI-use details](docs/validation-and-ai-use.md), [comparators](docs/comparator-policy.md)
- [Requirement map](docs/requirements-map.md), [submission manifest](docs/manifest.md)
