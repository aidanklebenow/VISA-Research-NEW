# Lab 18 — Decision, comparison, and checkout

Aidan Klebenow · Updated November 3, 2026 with AI assistance.

## Student decision

Aidan said he trusts the COST verdict because Costco seems successful and its strong results over time make sense. He also questioned how the app could judge investment attractiveness without an attractive purchase price. His decision is recorded under [the COST memo](memos/COST.md).

Clarification: the assignment judges the business and explicitly excludes price data. The verdict therefore concerns recorded business performance, not whether the shares are a bargain. A strong business can be too expensive at a particular price.

## Fresh chat without the skill

Aidan supplied a separate browser-AI response to the assigned Costco question. It described Costco favorably and supplied approximate ROE ranges, attributing differences to ending versus average equity. No source links accompanied the pasted response. Its claims about Buffett, Munger, Berkshire holdings, competitive advantages and retail comparisons have not been independently verified here.

| Fiscal year | Fresh-chat ROE range as supplied | Script ROE using year-end equity |
| --- | --- | --- |
| FY2022 | approximately 28.3% to 30.6% | 28.3% |
| FY2023 | approximately 25.1% to 27.5% | 25.1% |
| FY2024 | approximately 31.2% to 30.3% | 31.2% |
| FY2025 | approximately 27.8% to 30.7% | 27.8% |
| FY2026 | approximately 25.8% to 28.4% | 25.8% |

The FY2024 range is reproduced in the order supplied, although its endpoints descend. Each range contains the script's rounded year-end-equity answer, but a range does not identify a single reproducible calculation. The response gave no filing identifiers or input values to establish where its alternative figures came from. This lab specifically requires net income divided by year-end equity; average equity is a different denominator. The skill-backed output records the tags, fiscal-year ends, filing dates and accessions, making its calculation traceable. Agreement with one endpoint alone does not verify the other claims.

## Partner exercise: incomplete

Aidan reported that his partner was absent and elected to submit before the deadline with the written reflection below. The partner exercise was not completed; no partner interaction, no-AI performance, or instructor-approved waiver is claimed.

## Written reflection — student draft edited with AI assistance

**What is a skill?** A skill is a folder containing reusable instructions and optional scripts that help the AI complete a particular task consistently.

**How does it work?** The AI first sees the name and description of each available skill. When a skill matches my request, it loads the detailed instructions. This avoids filling the context with instructions it does not need.

**Why do the numbers belong in code?** Python selects the filing values and calculates the results so the inputs and arithmetic can be inspected and reproduced. The model explains and judges the evidence rather than inventing numbers or performing unchecked arithmetic. Code still needs testing because incorrect logic produces incorrect results.

**What stays consistent, and what remains judgment?** My skill specifies the SEC data sources, financial formulas, missing-data handling and required checks. The script applies those rules consistently. The model decides whether the evidence supports owning the business, watching it or passing, and explains why. Its wording and judgment need not be identical on every run.

**Why is “not found” better than an estimate here?** This lab requires reported filing values. An estimate would conceal a missing input. “Not found” keeps the gap visible and prevents unsupported calculations.

## Code-explanation preparation — AI assisted

A “yearly row” is simply one line of the app's financial table for one fiscal year. The function named `year_row()` builds it:

- Start with the fiscal-year-end date.
- Find the reported revenue, net income, operating cash flow, capital spending and equity for that date.
- Calculate ROE when income exists and equity is positive.
- Calculate owner earnings when operating cash flow and capital spending both exist.
- Return that year's values for the table.

Where does “not found” come from? `select_fact()` searches the allowed XBRL tags for an eligible fact. If none exists, it returns `None`, meaning no value was found. `display_value()` displays that as “not found.” The script never replaces missing data with zero or an estimate. Missing or nonpositive equity instead makes ROE “not known”; a check missing required inputs is also “not known.”

What stays consistent? The skill instructs the AI to use the same data rules, formulas, missing-value handling and memo scope each time. Code applies those rules; downloads may change when new filings arrive. What remains judgment? Whether that evidence merits “own the business,” “watch it,” or “pass,” and how strongly to trust that conclusion. The AI's exact wording and qualitative verdict need not be identical on every run.

Why keep numbers in code? The arithmetic and input selection can be inspected and reproduced. The model interprets that evidence rather than inventing financial values. Missing data honestly shows the limit of the evidence.

Practice question: If JPM has operating cash flow but no eligible capital-spending value, why can't the app calculate owner earnings?

## Submission status

- Complete: skill, app, live COST known-answer match, JPM missing-data probe, unsupported-number check, Markdown memos, Aidan's trust decision, and documented fresh-chat comparison.
- Complete: written reflection based on Aidan's own draft, edited with AI assistance.
- Not completed: live partner/no-AI explanation and discussion, because the partner was absent. No waiver is assumed.
- Pending Aidan: Brightspace quiz and submission of GitHub links. Aidan plans to submit after the GitHub files and results are finalized.

Assignment: [Lab 18 — Legend Investor as Skill](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md).
