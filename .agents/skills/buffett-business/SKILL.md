---
name: buffett-business
description: Evaluate a business using five years of SEC 10-K facts and Buffett-style qualitative judgment for FIN 43900 Lab 18. Use for a ticker business review, not a stock-price recommendation.
---

Run `python3 .agents/skills/buffett-business/scripts/sec_facts.py TICKER` from the repository root. The downloader requires `SEC_EMAIL` containing the student's real email; requests identify Aidan Klebenow. Do not hardcode or commit contact configuration. Use SEC EDGAR only, without API keys.

Read the printed table and checks before judging. The script selects annual 10-K flows, latest-filed values for duplicate periods, and last five fiscal years. Revenue and capital spending use the assignment's ordered tag fallbacks. ROE uses year-end equity; owner earnings is operating cash flow minus total capital spending. This is the lab's simplified proxy, not an estimate of maintenance spending. Missing inputs remain missing; missing checks remain not known.

Write `lab-18/memos/TICKER.md`: a short Buffett-inspired educational memo choosing **own the business**, **watch it**, or **pass**. Do not claim to be Buffett or represent his actual opinion. Judge earning power and consistency using only the printed financial numbers. Discuss the limits: these checks alone do not establish a durable moat or management quality. No prices, intrinsic values, targets, paid data, forecasts, or invented statistics. If owner earnings are missing, explicitly say they cannot be judged.

Use numerical tokens exactly as printed in the financial table (USD millions, ROE to one decimal). Do not calculate additional numbers in prose. Run the app's unsupported-number check on the memo and fix unsupported tokens. This check verifies token presence, not semantic correctness: review each number against the correct metric and year. Leave the student's own trust decision pending until they provide it.

Philosophy reference: https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md — read only; never install FAskills or use its paid sources. Follow this lab's simpler formula and scope over the reference's valuation and forecasting sections.
