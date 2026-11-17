### CPI data card

Source: [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL), produced by BLS; historical vintage from [ALFRED](https://alfred.stlouisfed.org/series?seid=CPIAUCSL). Saved download metadata: `data/macro-download-manifest.json`, recovered from Lab 17. Source inspection belongs to the October 29 Lab 17 evidence, not a new November source verification.

Measure: all-items U.S. city-average CPI, seasonally adjusted; monthly index, 1982–84 = 100. Inflation signal is `(September 2026 index / September 2025 index - 1) × 100`, using both observations from the same October 29, 2026 vintage. An index level is not a percentage rate.

Publication occurs after the measured month. Revisions to seasonal factors can change history. [BLS seasonal adjustment policy](https://www.bls.gov/cpi/seasonal-adjustment/questions-and-answers.htm) and [release calendar](https://www.bls.gov/schedule/news_release/cpi.htm) are source pointers, previously inspected in Lab 17. Do not interpret an observation date as its release date.

Eligibility: this particular frozen vintage is allowed from the next trading session, October 30, 2026. Earlier dates are rejected. It is not a general historical-vintage retrieval engine. No missing observation is filled; the year-over-year endpoints must exist. Missing intervening months prevent analyses requiring consecutive monthly observations.

Role: informational purchasing-power monitor. No fitted prediction, tactical allocation or backtest depends on this series. A CPI increase alone does not establish which fund will outperform. Stop historical strategy use unless every decision has an eligible historical vintage and execution timing.
