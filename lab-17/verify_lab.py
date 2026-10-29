"""Download reproducible audit evidence; expected answers never enter the app."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import json
from pathlib import Path
import requests
from asof_app import download, compare

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evidence"
BENCHMARK = {"BAA": ("2026-09-01", 6.47), "FEDFUNDS": ("2026-09-01", 3.75), "DGS10": ("2026-10-02", 5.28), "MORTGAGE30US": ("2026-10-01", 7.28)}


def main():
    OUT.mkdir(exist_ok=True)
    today = date.today().isoformat()
    jobs = [(s, None) for s in [*BENCHMARK, "PAYEMS", "CPIAUCSL"]]
    jobs += [(s, "2026-10-05") for s in BENCHMARK]
    jobs += [("PAYEMS", "2025-01-15"), ("CPIAUCSL", "2026-09-30"), ("CPIAUCSL", today)]
    manifest, data, errors = [], {}, []

    def fetch(job):
        sid, vintage = job
        url = (f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={sid}&vintage_date={vintage}" if vintage else f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        try:
            values, timestamp = download(url)
            filename = f"{sid}_{vintage or 'current'}.csv"
            values.rename("value").to_csv(OUT / filename)
            return job, values, {"file": filename, "url": url, "downloaded_utc": timestamp, "observations": len(values)}
        except Exception as exc:
            return job, None, {"url": url, "error": str(exc)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        for job, values, record in pool.map(fetch, jobs):
            manifest.append(record)
            if values is None:
                errors.append(record)
            else:
                data[job] = values
    results = {"run_utc": datetime.now(timezone.utc).isoformat(), "errors": errors, "benchmark": [], "comparisons": []}
    for sid, (expected_date, expected_value) in BENCHMARK.items():
        if (sid, "2026-10-05") not in data:
            continue
        values = data[sid, "2026-10-05"]
        actual_date, actual_value = str(values.index[-1].date()), float(values.iloc[-1])
        results["benchmark"].append({"series": sid, "expected_date": expected_date, "expected_value": expected_value, "actual_date": actual_date, "actual_value": actual_value, "passed": actual_date == expected_date and abs(actual_value - expected_value) < 1e-9})
    for sid, vintage in [(s, "2026-10-05") for s in BENCHMARK] + [("PAYEMS", "2025-01-15"), ("CPIAUCSL", "2026-09-30"), ("CPIAUCSL", today)]:
        if (sid, None) in data and (sid, vintage) in data:
            results["comparisons"].append({"asof": vintage, **compare(sid, data[sid, None], data[sid, vintage])})
    if ("PAYEMS", "2025-01-15") in data and ("PAYEMS", None) in data:
        old = float(data["PAYEMS", "2025-01-15"].loc["2024-12-01"])
        new = float(data["PAYEMS", None].loc["2024-12-01"])
        results["payems_probe"] = {"December_2024_asof": old, "December_2024_today": new, "passed": old == 159536 and new < old}
    (OUT / "download_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "verification.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
