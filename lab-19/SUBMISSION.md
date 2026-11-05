# Lab 19 — Legend Panel

**Student:** Aidan Klebenow

**Selected company:** NVIDIA (NVDA), selected from VTI using dated Vanguard holdings evidence.

## Review these files

- [README](README.md): application overview, local launch and validation.
- [Results](RESULTS.md): COST reference and NVIDIA panel findings.
- [Personal checkout](MY_CHECKOUT.md): Aidan's chosen cutoff, research purpose and remaining personal responses.
- [App](app.py), [screen calculations](panel.py), and [presentation explanations](presentation.py).
- [COST report](evidence/COST-report.md) and [NVIDIA report](evidence/NVDA-report.md): printed facts, checks and original filing links.
- [Investor memos](memos/): separate professional AI-written interpretations, with final-thought bullets.
- [Company-selection evidence](sources/fund-selection.md).
- Skills: [Buffett](../.agents/skills/buffett-business/SKILL.md), [Graham](../.agents/skills/graham-financial-strength/SKILL.md), [Burry](../.agents/skills/burry-cash-quality/SKILL.md). Cathie Wood is an optional additional view.
- [Financial verification](verify_panel.py), [unit tests](test_panel.py), and [app interaction checks](check_app.py).

## Findings

**COST baseline:** Buffett passes all checks, Graham fails only the current-ratio check, and Burry passes both checks. Latest current ratio is 1.06 and liabilities/equity is 1.49. The saved baseline matches the assignment.

**Threshold choice:** Aidan chose a current-ratio cutoff of 1.0 to include Costco in further research. The app preserves the assignment baseline and displays the chosen cutoff in the threshold comparison.

**NVIDIA:** Buffett and Graham pass all their checks. Burry's leverage check passes but his operating-cash-flow check fails. This disagreement identifies a cash-conversion question for further research; it does not prove manipulation or mispricing.

**Research purpose stated by Aidan:** use the panel as a starting point for research and identify questions or possible irregularities for analysis. A specific final follow-up condition is still an AI-assisted draft in the personal checkout, not a separately confirmed personal answer.

## Honest activity and AI-use record

Code, explanatory text and investor memos were prepared with AI assistance. Numerical memo checks and saved financial reference checks pass. The app includes the required baseline panel, missing-data handling, memo-number flag, threshold controls, a company picker, Nasdaq observation links and clickable primary-source references. No live price feed is claimed.

Aidan reports his teammate is absent. No partner exchange, swap, no-AI explanation, instructor waiver, quiz completion or Brightspace submission is claimed. Personal agreement/disagreement reflection and threshold reflection remain pending in MY_CHECKOUT.md. Publishing this repository documents the current work; it does not certify all personal/class activities complete.
