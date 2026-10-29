# Lab 17 — Point-in-Time Audit: CPIAUCSL

Prepared October 29, 2026 with AI assistance. Technical results below come from live FRED and ALFRED downloads. Personal verification and partner exercises are recorded separately and remain pending unless confirmed by the student.

## Question and economic connection

Was each number knowable on the day a strategy would have traded on it, and may Project 2 use this series? CPI measures consumer prices. Changes in inflation can affect purchasing power, business costs and interest-rate expectations, making CPI a candidate macroeconomic input; relevance to a specific Project 2 universe still needs a stated investment hypothesis. This audit establishes data eligibility, not predictive power.

## Run the dashboard

From the repository root:

```bash
python3 -m pip install -r lab-17/requirements.txt
python3 -m streamlit run lab-17/asof_app.py
```

The app starts with four required rates and CPIAUCSL. Change the custom ID to PAYEMS for the revision probe. Current observations and historical vintages are downloaded separately, cached for one hour, and timestamped. The chart start date affects presentation only; counts cover the full downloaded history. Missing observations (`.`) are excluded rather than filled. No API key is required or stored.

Reproduce the saved evidence with `python3 lab-17/verify_lab.py`; exercise the UI with `python3 lab-17/check_app.py`. These commands use live data and can change the current observations and revision counts.

## Known-answer validation

The actual downloaded ALFRED vintage for October 5, 2026 matched every assigned value:

| Series | Last measured date known then | Actual value | Result |
| --- | --- | ---: | --- |
| BAA | September 2026 | 6.47 | Pass |
| FEDFUNDS | September 2026 | 3.75 | Pass |
| DGS10 | October 2, 2026 | 5.28 | Pass |
| MORTGAGE30US | October 1, 2026 | 7.28 | Pass |

PAYEMS at January 15, 2025 ends with December 2024 at **159,536 thousand jobs**. The current download reports **158,316** for that same month, a decrease of **1,220 thousand jobs**. There are **381 revised common observations** across the downloaded history. The historical and current downloads therefore do not contain identical data.

See [machine-readable results](evidence/verification.json), [download URLs and UTC timestamps](evidence/download_manifest.json), and the adjacent CSV snapshots. The snapshots preserve parsed, nonmissing observations from the public downloads; they are not raw HTTP-response archives. Benchmark values appear only in validation code, never in the dashboard's data path.

## CPIAUCSL data card

| Field | Evidence and interpretation |
| --- | --- |
| Series and source | [CPIAUCSL on FRED](https://fred.stlouisfed.org/series/CPIAUCSL), produced by the U.S. Bureau of Labor Statistics; historical vintages from [ALFRED](https://alfred.stlouisfed.org/series?seid=CPIAUCSL). |
| Measure | Consumer Price Index for All Urban Consumers, all items, U.S. city average: a consumer price level. |
| Units | Index, 1982–1984 = 100; seasonally adjusted; monthly. A value of 336.298 is an index level, not 336.298% inflation. |
| Publication lag | Released in the following month, typically around midmonth; use actual releases rather than a fixed lag. FRED shows September 2026 data updated October 14, 2026. This is 14 calendar days after September 30; the CSV's September 1 observation label is not its publication date. Consult the [BLS release schedule](https://www.bls.gov/schedule/news_release/cpi.htm) for exact timing. |
| Revision policy | Seasonally adjusted history can change as seasonal factors are updated. [BLS seasonal-adjustment FAQ](https://www.bls.gov/cpi/seasonal-adjustment/questions-and-answers.htm) describes annual factor updates with January data released in February. Zero revisions over one short comparison is not evidence of a permanent no-revision policy. |
| Download date | October 29, 2026; exact UTC download times and URLs are in the manifest. |
| Point-in-time constraint | Retrieve the ALFRED vintage eligible at each decision date. When intraday availability is uncertain, allow use only from the next trading session after that vintage date. Do not backfill today's observations into earlier trades. |

### Last month versus today

| As known on | Last measured month | Value | Later observations in current data | Revised shared dates |
| --- | --- | ---: | ---: | ---: |
| September 30, 2026 | August 2026 | 334.131 | 1 | 0 |
| October 29, 2026 | September 2026 | 336.298 | 0 | 0 |

September CPI disappears when the vintage date moves back to September 30: it had not yet been published. The two selected vintages show publication delay but no revisions on their shared dates. Revision risk is still documented by BLS.

### Three-value source comparison

AI compared these downloaded observations with the visible FRED page on October 29, 2026:

| Measured month | Downloaded value | FRED page value | AI comparison |
| --- | ---: | ---: | --- |
| July 2026 | 332.813 | 332.813 | Match |
| August 2026 | 334.131 | 334.131 | Match |
| September 2026 | 336.298 | 336.298 | Match |

**Student's own manual check: pending confirmation.** The assignment specifically requires the student to read three values against FRED personally; the AI comparison does not replace it.

## Fresh eyes

**Actual partner challenge and no-AI code explanation: pending.** No partner participation is claimed.

Prepared self-check challenge: “Why trust the revisions field if the app reports zero?”

Prepared response: The app reports zero changed shared values between September 30 and October 29, 2026, while September is an additional observation rather than a revision. BLS describes annual seasonal-factor updates, so eligibility must rely on historical vintages even when this particular comparison shows no revisions.

This is an AI-prepared self-check, not a substitute for the required real partner attack. Record the partner's actual question and an evidence-based two-sentence answer after the exercise.

## Project 2 decision

**Quarantine CPIAUCSL until Project 2 implements point-in-time access.** Admit only when each decision uses an eligible historical vintage, retains its vintage/download metadata, and executes after information availability; use the next trading session if intraday timing cannot be established. If Project 2 can only obtain today's revised history, reject that input for historical trading decisions.

For an inflation feature, calculate `100 * (CPI_t / CPI_(t-12) - 1)` using both index observations from the same eligible vintage. Never mix a historical numerator with a subsequently revised denominator. Passing this data gate permits testing; it does not prove forecasting value.

## Understand and explain the code

`download_asof()` validates the series ID, parses the requested date, and rejects a future date. It places that date in ALFRED's `vintage_date` query, which requests the historical information set. `download()` checks the HTTP response, parses the two CSV columns, converts dates/numbers, removes missing observations, and returns sorted values plus a UTC retrieval timestamp. The final date guard excludes future-dated observations; it is the ALFRED request, not that guard, that enforces historical publication eligibility. The decorator caches separately for each series/date argument.

Practice question: Why is filtering today's CSV to observation dates before the trade insufficient? Because an old observation date can carry a value published or revised after the trade; only the historical vintage addresses that leak.

A data card identifies meaning, units, source, publication lag, revisions, retrieval date and eligibility rules. Saying “cleaned the data” does not establish when any value could have been known.

## Reflection preparation and remaining checkout

Using September CPI for a September 30 trade would leak information released in October. Using today's revised history may also give the strategy later statistical revisions. Either can make historical results misleading; the direction and size of the performance distortion require an actual backtest and cannot be asserted from this audit alone.

- Student: personally confirm the three FRED observations above.
- Student: explain the historical-download function without AI and answer a real partner's question.
- Student: record the real partner attack and evidence-based answer, and explain publication lag/backtest leakage in their own words.
- Student: complete the Brightspace Lab 17 quiz and submit the GitHub file links as instructed. Neither quiz completion nor Brightspace submission is claimed here.

Assignment: [Lab 17 — Point-in-Time Audit](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-17-point-in-time.md).
