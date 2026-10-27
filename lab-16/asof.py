"""Lab 16: publication-date gate. Run with python3 Class_Notes/Lab_16/asof.py."""

from datetime import date

# Editable inputs: row number, ticker, measured month, publication date, index.
DECISION_DATE = "2026-03-31"
TABLE = [
    (1, "AAA", "2026-01", "2026-02-10", 101.0),
    (2, "AAA", "2026-02", "2026-03-10", 104.0),
    (3, "AAA", "2026-03", "2026-04-10", 109.0),
    (4, "AAA", "2026-02", "2026-03-25", 103.0),
    (5, "BBB", "2026-01", "2026-02-10", 98.0),
    (6, "BBB", "2026-02", "2026-03-10", 97.0),
    (7, "BBB", "2026-02", "2026-03-10", 97.0),
    (8, "BBB", "2026-03", "2026-04-10", 92.0),
    (9, "CCC", "2026-01", "2026-02-10", 110.0),
    (10, "CCC", "2026-02", "2026-04-05", 112.0),
    (11, "", "2026-02", "2026-03-10", 99.0),
    (12, "CCC", "2026-02", "2026-03-10", 111.0),
]


def latest_publications(rows):
    """Rule 4: choose the latest publication for each ticker and month."""
    latest = {}
    for row in rows:
        key = (row[1], row[2])
        if key not in latest or row[3] > latest[key][3]:
            latest[key] = row
        elif row[3] == latest[key][3] and row[4] != latest[key][4]:
            raise ValueError(f"Conflicting values on the same publication date: {key}")
    panel = sorted(latest.values(), key=lambda row: row[0])
    kept = {row[0] for row in panel}
    return panel, [row[0] for row in rows if row[0] not in kept]


def filter_asof(rows, decision_date):
    cutoff = date.fromisoformat(decision_date)
    funnel = []
    clean = [row for row in rows if row[1].strip()]
    funnel.append(("Quarantined: no ticker", [row[0] for row in rows if not row[1].strip()]))
    unique, duplicates, seen = [], [], set()
    for row in clean:
        # Row number is an identifier, not part of the observed data.
        fingerprint = row[1:]
        if fingerprint in seen:
            duplicates.append(row[0])
        else:
            seen.add(fingerprint)
            unique.append(row)
    funnel.append(("Exact duplicate", duplicates))
    eligible = [row for row in unique if date.fromisoformat(row[3]) <= cutoff]
    funnel.append(("Published after decision date", [
        row[0] for row in unique if date.fromisoformat(row[3]) > cutoff
    ]))
    panel, replaced = latest_publications(eligible)
    funnel.append(("Older vintage replaced by a revision", replaced))
    naive, _ = latest_publications(unique)
    return panel, naive, funnel


def signals(panel):
    result = {}
    for ticker in sorted({row[1] for row in panel}):
        history = sorted((row for row in panel if row[1] == ticker), key=lambda row: row[2])
        latest = history[-1]
        year, month = map(int, latest[2].split("-"))
        previous_month = f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"
        previous = next((row for row in history if row[2] == previous_month), None)
        change = None if previous is None or previous[4] == 0 else (latest[4] / previous[4] - 1) * 100
        result[ticker] = (latest[2], change)
    return result


def format_signal(signal):
    month, change = signal
    return f"{change:+.2f}% ({month})" if change is not None else f"unavailable ({month}; missing prior month or zero base)"


def main():
    panel, naive, funnel = filter_asof(TABLE, DECISION_DATE)
    print(f"Decision date: {DECISION_DATE}\nInput rows: {len(TABLE)}")
    for label, removed in funnel:
        print(f"{label}: removed {len(removed)}; rows {', '.join(map(str, removed)) or 'none'}")
    print(f"\nAs-of panel: {len(panel)} rows")
    print("Row | Ticker | Month measured | Published on | Index")
    for row in panel:
        print(" | ".join(map(str, row)))
    print("\nTicker | As-of signal | Naive signal (ignores publication cutoff)")
    asof_signals, naive_signals = signals(panel), signals(naive)
    for ticker in sorted(naive_signals):
        asof = format_signal(asof_signals[ticker]) if ticker in asof_signals else "unavailable"
        print(f"{ticker} | {asof} | {format_signal(naive_signals[ticker])}")


if __name__ == "__main__":
    main()
