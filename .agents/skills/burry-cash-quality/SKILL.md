---
name: burry-cash-quality
description: Write a Burry-inspired educational SEC business memo for the FIN 43900 Lab 19 panel, using its computed screens and shared financial facts. Excludes price recommendations and valuation forecasts.
---

From the repository root run `python3 lab-19/panel.py TICKER`. Read the printed financial table, growth output, and computed checks. This reuses Lab 18's SEC downloader without changing Lab 18; every investor must use this same snapshot. SEC contact configuration stays in ignored `lab-19/.env` or `SEC_EMAIL`; no API key is needed.

Operating cash flow must be at least net income every year; latest total liabilities must be no more than twice year-end equity. Nonpositive equity makes leverage unknown. Focus on cash backing for earnings and balance-sheet risk; these two checks cannot establish clean accounting. Checks are implemented in `lab-19/panel.py`; do not decide their pass/fail status in prose. All-year checks require five complete inputs. Missing inputs remain missing and unresolved checks remain not known. Compare full precision; round only for display.

Write a short separate memo to `lab-19/memos/TICKER-burry.md`, clearly labeled **AI-written, Burry-inspired educational interpretation; not the investor's actual opinion**. Give a business-screen judgment, its evidence, and a limit. Use numerical tokens exactly as printed in the financial facts or growth output; do not calculate new numbers in prose or quote unprinted thresholds. No stock-price recommendations, valuation figures, investor-holdings claims, forecasts, or invented data. Retain unknowns explicitly.

Run `panel.unsupported_numbers(memo, report)` and review each metric/year manually. Token presence alone cannot prove a statement correct. Record the report source hash in `lab-19/memos/manifest.json` after review so a refreshed report can be identified as needing memo review. Do not fabricate the student's threshold choice, screening decision, partner participation, or checkout.

Reference read for analytical emphasis only: https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md . Do not install FAskills or use its paid sources. The lab's SEC-only checks and educational scope take precedence over the reference's trading, valuation, and persona instructions.
