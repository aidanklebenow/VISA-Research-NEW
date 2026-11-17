# Validation and AI use — working record

Prepared with OpenAI Codex on November 10, 2026. This file separates technical evidence from student ownership. No final student adoption, partner activity or submission is claimed.

## Scope and highest-risk claim

The model finds the lowest estimated volatility on a 5-point long-only grid subject to a return-estimate floor and SGOV reserve floor. Its integrated verdict adds a proposed volatility ceiling. The riskiest claim would be that passing these numerical checks establishes a suitable, mandate-compliant portfolio. It does not: issuer definitions, loss expectations, benchmark and net compounded objective remain unresolved. Full mandate approval is withheld.

Conceptual soundness: arithmetic historical returns are a transparent research input, not a forecast of net compounded return. Outcome analysis: reproduce the Lab 15 known allocation, challenge it with estimation/window/cost/constraint changes and test missing/ineligible data. Monitoring: review whenever assumptions, client constraints or data change; stop on missing provenance, unavailable historical vintage, infeasibility or failed risk checks. These use the Week 12 local model-risk reference; no claim of legal compliance or generative-AI validation under Federal Reserve guidance is made.

## Data boundary

Historical snapshot at October 30, 2026. Prices end September 30 and were downloaded October 22. CPI vintage October 29 is first used October 30. Saved adjusted price history can be revised by the vendor and is not suitable for an unaudited historical backtest. See `data/price-sources.json`, `data/macro-download-manifest.json`, and `docs/data-card.md`. Current market facts were not refreshed.

## Material AI uses and dispositions

Tool: OpenAI Codex; exact backend version is not independently captured. Interaction date: November 10, 2026.

| AI contribution | Disposition / check |
|---|---|
| Reuse Lab 15 five-fund engine | Preserved source copy; known-answer regression checks |
| Suggest 10% annual volatility research ceiling | Unadopted assumption; clearly editable and labeled |
| Integrate app, rule verdicts and stress report | Technical tests and Streamlit AppTest; details in local test output |
| Treat accounting screens as research support | No stock selection or market mispricing conclusion inferred |
| Prepare AI Q&A interface | Disconnected prompt preparer; no generated answer or credential claimed |
| Draft recommendation and video outlines | Student review and adoption pending |

Development stresses are AI-assisted and ineligible as the Locked Changed-Input Record. Prior Lab 15 exposure includes a one-point VTI return stress and full/36-month window comparison. Do not represent either as an unexposed AI-off prediction.

## Locked Changed-Input Record — NOT COMPLETED

Do not ask AI to write or suggest this prediction. Choose a material input you can explain. With AI closed, write the following before execution and commit it to GitHub before the run. Write the prediction in `../../lab-20/prediction.md`.

- Student author / timestamp: **pending**
- Exact input, units, old value and new value: **student to enter without AI**
- Expected output direction and finance reason: **student to enter without AI**
- Expected decision effect: **student to enter without AI**
- Pre-run GitHub commit URL and hash: **pending**
- AI-off execution command and timestamp: **pending**
- Preserved before/after output paths: **pending**
- Actual output direction and decision effect: **pending**
- Student reconciliation / diagnosis, including unchanged action: **pending**

Keep the prediction unchanged after running; append results and reconciliation. If AI is accidentally used, disclose it and seek instructor direction rather than relabeling the record.

## Verification and independent review

Executed development results belong in `output/results.json`. Technical verification logs belong in `output/verification.txt`. Automated UI checks do not establish an independent partner run or visual browser inspection.

Partner cold run: **pending**. Record README URL given, exact command, elapsed time, first failure, result location and fixes. Skeptical committee question and student response: **pending**. Final student decision and limits: **pending**. Video upload and final Brightspace submission: **pending**.
