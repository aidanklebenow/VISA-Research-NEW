# CPI Data Card

Source: [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL), produced by BLS; historical vintage from [ALFRED](https://alfred.stlouisfed.org/series?seid=CPIAUCSL). Saved download metadata: `data/macro-download-manifest.json`, recovered from Lab 17. Source inspection belongs to the October 29 Lab 17 evidence, not a new November source verification.

Measure: all-items U.S. city-average CPI, seasonally adjusted; monthly index, 1982–84 = 100. Inflation signal is `(September 2026 index / September 2025 index - 1) × 100`, using both observations from the same October 29, 2026 vintage. An index level is not a percentage rate.

Publication occurs after the measured month. Revisions to seasonal factors can change history. [BLS seasonal adjustment policy](https://www.bls.gov/cpi/seasonal-adjustment/questions-and-answers.htm) and [release calendar](https://www.bls.gov/schedule/news_release/cpi.htm) are source pointers, previously inspected in Lab 17. Do not interpret an observation date as its release date.

Eligibility: this particular frozen vintage is allowed from the next trading session, October 30, 2026. Earlier dates are rejected. It is not a general historical-vintage retrieval engine. No missing observation is filled; the year-over-year endpoints must exist. Missing intervening months prevent analyses requiring consecutive monthly observations.

Role: informational purchasing-power monitor. No fitted prediction, tactical allocation or backtest depends on this series. A CPI increase alone does not establish which fund will outperform. Stop historical strategy use unless every decision has an eligible historical vintage and execution timing.

## ETF Issuer Profiles

[Saved ETF profiles](../data/etf_profiles.json) hold the fund names, issuer, strategy descriptions, dated holdings counts and exposures, and prospectus expense ratios. Each record stores the source URL, access date (November 23, 2026), and provider observation dates where supplied. These facts are shown for context only. The allocation continues to use the same historical price-based estimates. The expense ratios describe fund-level fees already reflected in adjusted price history.

| Fund | Official source | Dates and counting basis |
|---|---|---|
| SGOV | [iShares fund page](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf) and [issuer holdings table](https://www.ishares.com/us/products/314116/sgov) | Holdings table count is 24 listed entries on October 20, 2026, including cash-classified Treasury bills. The November 20 snapshot supplies sector weights and separately reports 0 in the summary holdings-count field. The profile uses the dated position-table count and shows both reporting contexts. |
| IEF | [iShares fund page](https://www.ishares.com/us/products/239456/ishares-710-year-treasury-bond-etf) | Holdings and sector weights are dated November 20, 2026. |
| LQD | [iShares fund page](https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf) | Holdings and top sector weights are dated November 20, 2026. |
| VTI | [Vanguard fund page](https://advisors.vanguard.com/investments/products/vti/vanguard-total-stock-market-etf?source=autosugg) | Stock count and top sector weights are dated July 31, 2026. The expense ratio is dated April 28, 2026. |
| VXUS | [Vanguard fund page](https://workplace.vanguard.com/investments/product-details/fund/3369) | Stock count and top equity holdings are dated July 31, 2026. The expense ratio is dated February 27, 2026. |

The iShares expense ratios were visible on the pages at access. A separate effective date was not provided there. Issuer sector tables for SGOV and IEF listed two categories each. The cards display both categories. These issuer observations are dated independently from the model's October 30 decision snapshot.
