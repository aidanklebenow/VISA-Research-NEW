# Project 2 requirement map

[Official brief](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md)

| ID | Requirement | Location | Evidence | Verified |
|---|---|---|---|---|
| P2-01 | Start and operate the Python web app | [app.py:160](../app.py#L160), [README](../README.md) | Automated app test and three setup commands per platform | Yes for automated app |
| P2-02 | Own the investment rules | [Committee memo](decision-memo.md) | Aidan’s mandate fields | No |
| P2-03 | Two comparisons, candidate and verdicts | [app.py:204](../app.py#L204) | [Executed result](../output/results.json) | Yes |
| P2-04 | Date-gated signal and data card | [model.py:29](../model.py#L29), [data card](data-card.md) | Vintage and empty-input tests | Yes |
| P2-05 | Stress estimates, window, costs and constraints; show stop conditions | [model.py:106](../model.py#L106) | [Scenario output](../output/results.json) and automated app test | Yes |
| P2-06 | Locked changed-input evidence | [Validation record](validation-and-ai-use.md) | Aidan’s prediction commit, run and diagnosis | No |
| P2-07 | Recommendation, allocation range, monitoring and reversal rule | [Committee memo](decision-memo.md) | Aidan’s decision | No |
| P2-08 | AI disclosure, ownership and education opening | [README](../README.md), [memo](decision-memo.md), [recording outline](video-plan.md) | Written disclosures present. Aidan confirms ownership and records openings. | No |
| P2-09 | Centered sensitivity grid and invalid cells | [model.py:124](../model.py#L124) | Center, above-limit and no-mix regression test | Yes |
| P2-10 | Failure validation and reproducible output | [Tests](../tests/), [verification](../output/verification.txt) | Known answer, injected source failures and app stop checks | Yes |
| P2-11 | Corrected AI finding and comparator policy | [Correction log](where-i-caught-the-ai.md), [comparator policy](comparator-policy.md) | Andrew’s Windows finding and two comparison methods | Yes |
| P2-12 | Videos, transcripts and frozen bundle | [Manifest](manifest.md) | Three recordings and corrected transcripts | No |
