# Lab 19 — Legend Panel

Use the existing Desktop app **Legend Panel · Lab 19 (AI Finance)**, or run from the repository root:

```bash
lab-19/.venv/bin/python lab-19/launch.py
```

The app opens at http://localhost:8519. Start with COST, then enter NVDA. Use the **Current assignment · Graham** panel for Buffett, Graham and Burry. The Wood view is an optional extension.

## Results and files

- [Results](RESULTS.md): known answer and selected-company findings.
- [Solo worksheet](MY_CHECKOUT.md): personal answers still needed; teammate absence recorded.
- [Learning notes](LEARNING.md): plain-language explanation and AI-drafted practice arguments.
- [Company selection](sources/fund-selection.md): dated VTI holdings evidence supporting NVIDIA.
- [COST report](evidence/COST-report.md) and [NVIDIA report](evidence/NVDA-report.md): printed financial facts, screens and filing provenance.
- `panel.py` calculates checks; `app.py` displays them; `memos/` contains separate AI-written interpretations.

## Validation — November 5, 2026

Six Lab 19 unit tests, saved COST reference comparisons, threshold probes, all twelve memo checks, deliberate unsupported-number injections, and six preserved Lab 18 extraction tests passed. The Lab 19 Streamlit AppTest also passed both panel views, memo edits, threshold controls, NVDA/JPM, and missing/invalid tickers. An earlier UI timeout is superseded by this successful rerun; no visual browser inspection is claimed.

Missing facts remain missing; checks requiring unavailable facts remain not known. The memo checker verifies printed numerical tokens, not the correctness of their interpretation. Screens use simplified classroom rules and do not establish stock value.

Technical validation does not complete personal reflections, partner activities, the no-AI explanation, quiz, or submission. No submission is claimed.

## Presentation update

Added plain-language check explanations, evidence tables with bold results, structured investor memos with final-thought bullets, a COST/NVDA/JPM company picker, a Nasdaq observation tab and a clickable Sources & references tab. Financial reference and all twelve memo validations pass; UI checks pass company switching, threshold controls and the new tabs. Nasdaq live quotes are unavailable in the app; direct market-page links are provided.
