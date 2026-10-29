"""Exercise the real Streamlit UI against live public endpoints."""
from pathlib import Path
import json
from datetime import date
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent


def main():
    app = AppTest.from_file(str(ROOT / "asof_app.py"), default_timeout=180).run()
    checks = []
    def record(name, passed):
        checks.append({"check": name, "passed": bool(passed)})
        assert passed, name
    record("Default: four rates plus CPI, no exceptions/errors", not app.exception and not app.error and len(app.dataframe) == 1 and len(app.dataframe[0].value) == 5)
    app.sidebar.date_input[1].set_value(date(2026, 10, 5)).run()
    record("Benchmark renders without errors", not app.exception and not app.error)
    table = app.dataframe[0].value
    for sid, expected in {"BAA": 6.47, "FEDFUNDS": 3.75, "DGS10": 5.28, "MORTGAGE30US": 7.28}.items():
        row = table[table.Series.str.endswith('/' + sid)].iloc[0]
        record(sid + " known value", abs(row["Value known then"] - expected) < 1e-9)
    app.sidebar.text_input[0].set_value("PAYEMS")
    app.sidebar.date_input[1].set_value(date(2025, 1, 15)).run()
    row = app.dataframe[0].value.iloc[-1]
    record("PAYEMS known answer and positive revisions", row["Value known then"] == 159536 and row["Revised common observations"] > 0)
    app.sidebar.text_input[0].set_value("THIS_SERIES_DOES_NOT_EXIST_17").run()
    record("Unknown ID: error displayed and four valid rows survive", bool(app.error) and not app.exception and len(app.dataframe[0].value) == 4)
    (ROOT / "evidence" / "app_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
