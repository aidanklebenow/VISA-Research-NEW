# Lab 16 — Provenance Gate Checkout

Aidan Klebenow | October 27, 2026

Status: code and AI-assisted numerical verification complete; student quiz, partner activities, student review of the reflection pending. Individual submission remains student-operated.

## Question and interpretation

On the day I would have traded, what did the data actually say, and how much of what I see now came later?

Decision date: March 31, 2026. In class, the groups were discussed as bond-fund observations by rating. The linked written assignment describes fictional retailer card-spend indexes and labels the groups as tickers. The calculations below use the supplied index values and publication rules under either interpretation. A negative index change is not, by itself, evidence of a negative bond yield.

## Run the code

From the GitHub repository root:

```bash
python3 lab-16/asof.py
```

The script uses the standard library only. Its editable table and decision date are at the top. It calculates both signal columns from the observations; expected answers are not embedded in the calculation.

## Verified funnel

| Rule | Number removed | Row IDs |
|---|---:|---|
| Quarantine missing identifier | 1 | 11 |
| Remove exact duplicate | 1 | 7 |
| Exclude publications after March 31 | 3 | 3, 8, 10 |
| Replace earlier eligible vintage | 1 | 2 |
| Remaining panel | 6 | 1, 4, 5, 6, 9, 12 |

Row 7 duplicates row 6 even though its row ID differs. Row 4 replaces row 2 because its March 25 publication was already available. Row 10 cannot replace row 12 because April 5 is after the cutoff.

## Verified signals

Signal = (latest month's index / previous calendar month's index - 1) × 100.

| Group | As-of signal | Naive signal |
|---|---|---|
| AAA | +1.98% (February) | +5.83% (March) |
| BBB | -1.02% (February) | -5.15% (March) |
| CCC | +0.91% (February) | +1.82% (February) |

The naive calculation keeps the latest publication for each group/month without applying the publication cutoff. It still removes missing identifiers and duplicates.

At April 15, the as-of signals equal the naive signals for all three groups. This was technically checked by AI, and the source file's default remains March 31. See [verification.txt](verification.txt). The required independent partner exercise remains pending.

## Study before the no-AI code explanation

The rule-4 function is `latest_publications()` in [asof.py](asof.py).

```python
latest = {}
for row in rows:
    key = (row[1], row[2])
    if key not in latest or row[3] > latest[key][3]:
        latest[key] = row
```

- `latest = {}` creates storage for the selected observation for each group/month.
- The loop examines each input observation.
- The key combines the group and measured month; January and February stay separate.
- The condition accepts the first observation for a key or a later publication for that same key. The dates use the sortable YYYY-MM-DD format.
- Assignment saves the selected row, replacing an older version when appropriate.

The as-of branch removes future publications before calling this function. This order prevents an unavailable revision from replacing a knowable observation. The remaining function checks for conflicting same-date values and identifies the replaced row IDs.

## Quiz — student response pending

Question: February was reported as 104 on March 10, revised to 103 on March 25, and revised to 105 on April 5. Which value is available for a March 31 decision, and why?

My answer: **[student to complete]**

## Partner exercise — pending

Partner: **[complete in class]**

Partner's question about my code: **[complete in class]**

My answer from the code: **[complete personally]**

Result of running my partner's script at March 31: **[record actual result]**

Result after changing their date to April 15: **[record actual result]**

Date restored to March 31: **[confirm after restoring]**

## Reflection

Look-ahead bias occurs when a historical analysis uses information that was not available on the decision date. The month measured tells us when the activity happened, while the publication date tells us when the number became available. A revision updates an earlier observation and can only be used once that revision has been published.

The publication-date rule mattered most because it removed rows 3, 8, and 10, preventing later information from entering the March 31 analysis. For AAA, March's index of 109 was not published until April 10. Using it produces the naive March signal of +5.83%, while the latest signal actually available on March 31 was February's +1.98%. The revision rule also matters: row 4 replaces row 2 because the revised February value of 103 was published by March 31.

A backtest using the naive column would act as though future publications and revisions were already known. It could claim a stronger AAA growth signal and a steeper BBB decline than the available information supported. That would make the historical test misleading. These signals describe changes in the index; they do not, by themselves, establish bond yields or investment profits.

## Individual GitHub checkout

Files for individual checkout: [asof.py](asof.py), [this write-up](README.md), and [verification.txt](verification.txt). Submit the GitHub links as directed by the instructor. Partner activities and quiz remain pending; publication does not establish completion of those exercises.

Assignment: https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-16-provenance-gate.md

AI assistance: code generation, technical verification, and study/checkout drafting. Student and partner activities remain separately identified above.
