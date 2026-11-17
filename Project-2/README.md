AI use: OpenAI Codex assisted with code, research organization, validation and drafts. Aidan must review and take ownership of the final analysis and decision; that review is pending.

Education, not investment advice.

# Portfolio Trust — Project 2

**Working conclusion: restrict this process to research; do not approve client allocation while mandate requirements remain unresolved.** This Python app helps a student portfolio analyst compare allocations, inspect assumptions and explain why a polished answer may still be unsuitable.

## Reproduce the decision

From the repository root, run this with Python 3:

```bash
python3 Project-2/model.py
```

The command prints the portfolio weights, return proxies, volatility and verdicts, and writes [output/results.json](output/results.json). It uses bundled data and the Python standard library. From inside `Project-2/`, use `python3 model.py`.

| Portfolio | Net annual return proxy | Annual volatility | Model checks | Full mandate |
|---|---:|---:|---|---|
| Equal weight | 4.87% | 8.80% | FAIL | FAIL |
| Inverse volatility | 3.64% | 1.67% | FAIL | FAIL |
| Constrained | 7.50% | 6.80% | PASS | FAIL |

Historical snapshot dated October 30, 2026. The constrained weights are 55% SGOV, 30% VTI, 15% VXUS and 0% each for IEF and LQD. See the [draft memo](docs/decision-memo.md) for the unresolved mandate conditions.

## Start the interactive app

From the repository root on macOS or Linux:

```bash
cd Project-2
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --browser.gatherUsageStats false
```

Use Python 3.14 for the verified setup. Open the Local URL printed in the terminal, move one control and inspect the constrained portfolio verdict or infeasibility message. Use **Download this calculation snapshot** to save the displayed settings and result. Dependency installation requires internet access. The app calculations use bundled data and need no credentials.

On Aidan's Mac, the Desktop launcher `Project 2 Portfolio Trust.command` uses port 8520 and falls back to the existing Lab 19 environment. Its shell syntax has been checked.

## Working mandate — awaiting student approval

Five-year research horizon; 7.5% annual return objective; SGOV, IEF, LQD, VTI and VXUS; long-only; at least 10% in SGOV. Annualized sample volatility is the modeled risk measure. A 10% ceiling is an AI-proposed research assumption, not a verified client limit. Annual investor costs default to zero, an assumption exposed in the app.

Equal weight and inverse volatility are transparent comparators. A policy benchmark is not approved. The original 7% issuer cap needs a look-through definition and Treasury exception. The original zero-realized-loss requirement cannot be guaranteed. **Full mandate verdict is FAIL while those issues remain unresolved**, even when the four numerical model checks pass. The historical arithmetic return proxy is not proof of the draft five-year compounded net objective.

## Dates and sources

Decision snapshot: October 30, 2026, not a current November allocation. Yahoo adjusted monthly prices: September 2021–September 2026, downloaded October 22, 2026. [Data provenance](data/price-sources.json) contains original request URLs and observations; original raw responses remain in the preserved Lab 15 folder. This standalone package includes the parsed prices and provenance, not the raw vendor responses.

CPI: historical ALFRED vintage October 29, 2026, first eligible October 30 under the next-session rule. [Data card](docs/data-card.md). CPI monitors purchasing power and does not drive a trading strategy. Neither the portfolio estimates nor current adjusted prices are represented as a point-in-time backtest.

## Repository map

- `app.py`: interactive presentation; `model.py`: integrated verdicts, scenarios, CPI and report generation.
- `portfolio.py`: preserved Lab 15 estimation and grid-search functions. Its old standalone report is the historical training case; use `model.py` for Project 2.
- `data/`: frozen inputs and provenance; `output/`: executed finance results.
- `docs/decision-memo.md`: unadopted recommendation draft.
- `docs/validation-and-ai-use.md`: evidence and AI boundary.
- `docs/requirements-map.md`: verified requirements and gaps.
- `docs/manifest.md`: unresolved publication/video pointers.
- `docs/video-plan.md`: three distinct recording outlines, not transcripts.

## Limits and remaining ownership

No actual account holdings are verified. Tesla is not a direct security in the modeled universe; indirect fund exposure has not been measured. Fees, taxes, trading liquidity and issuer exposure require further verification. Monthly data miss intramonth drawdowns. No guaranteed return, loss protection or predictive advantage is claimed.

The human AI-off changed-input prediction and run, GitHub pre-run commit, partner cold run, final decision, videos/transcripts and submission remain outstanding. Do not reuse AI-assisted development stresses as the locked record. Project 2 does not require submitted Editions A/B. See [next steps](docs/next-steps.md).
