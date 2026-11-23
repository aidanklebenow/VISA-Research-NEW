# Validation and AI use

## Claim and checks

The main claim is that the selected mix has the lowest estimated volatility among the tested mixes that meet the return and SGOV reserve requirements. The search tests portfolio weights in steps of five percentage points. The volatility ceiling is checked after selection. The model displays the least-volatile candidate and stops if it breaches the ceiling. If no mix meets return and reserve, the two comparators remain available.

Annual investor cost is subtracted once from the estimated gross return. The search uses the net return target plus annual investor cost as its gross hurdle. The displayed return is an arithmetic historical estimate, with no guarantee of compounded growth. The full client mandate requires benchmark, issuer, risk, and withdrawal decisions.

The snapshot is dated October 30, 2026. Prices end September 30 and were retrieved October 22. The bundled data and source records are listed in the [data card](data-card.md) and [price source file](../data/price-sources.json). The October 29 CPI vintage is first eligible October 30. The CPI monitor leaves the weights unchanged.

Ten model tests cover the known portfolio, a breached risk ceiling, infeasibility, annual cost arithmetic, vintage timing, missing or empty source evidence, empty CPI, the sensitivity grid, explicit history windows, and fund limits. Two report tests check the frontier, sensitivity and cap validation. The automated app check verifies the report sections, original result, both themes, dollar displays, stop messages and reset. The live sensitivity grid uses the report’s active inputs; the archived stress and sensitivity outputs retain their original definitions. The base results and six existing stress cases reproduce without changing the committed JSON. [Executed results](../output/results.json) include estimate, lookback, cost, reserve, and risk stresses and the centered two-input grid.

## Material AI contributions

| Tool and date | Contribution | Check and disposition |
|---|---|---|
| OpenAI Codex, Nov. 10 and 17, 2026 | Reused the Lab 15 engine; integrated the Streamlit app, CPI monitor and historical checks | Retained after known-answer and vintage tests. The proposed volatility limit is a reference assumption. |
| OpenAI Codex, Nov. 23, 2026 | Redesigned app, added the grid and input-failure checks, and revised setup and evidence documentation | Retained after model and app checks. Andrew’s Windows finding is recorded in the [correction log](where-i-caught-the-ai.md). |
| OpenAI Codex, Nov. 17, 2026 | Ran the substitute Lab 20 startup check | The [substitute record](../../lab-20/partner_cold_run.md) documents the scope and browser limitation. |

Exact backend model versions were not captured in the technical records.

## Locked changed-input record · Aidan

- Original prediction, timestamp, and pre-run GitHub commit: ___
- Before and after outputs and run timestamp: ___
- Actual result, effect on the decision, and diagnosis: ___

## Personal check of a material AI output · Aidan

- Claim, check performed, and what you accepted or corrected: ___
