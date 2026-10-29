"""Lab 17: FRED current observations versus actual ALFRED vintages."""
from datetime import date, datetime, timezone
from io import StringIO
import re

import pandas as pd
import requests
import streamlit as st

SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}


def download(url):
    response = requests.get(url, timeout=45)
    response.raise_for_status()
    frame = pd.read_csv(StringIO(response.text), na_values=["."])
    if len(frame.columns) != 2:
        raise ValueError("Expected one date column and one series column.")
    frame.columns = ["date", "value"]
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame["value"] = pd.to_numeric(frame["value"], errors="raise")
    values = frame.dropna().set_index("date")["value"].sort_index()
    if values.empty or values.index.has_duplicates:
        raise ValueError("No usable observations, or duplicate dates.")
    return values, datetime.now(timezone.utc).isoformat()


def validate_id(series_id):
    if not re.fullmatch(r"[A-Z0-9_]+", series_id):
        raise ValueError("Use a FRED series ID containing letters, numbers or underscores.")


@st.cache_data(ttl=3600, show_spinner=False)
def download_today(series_id):
    """One public CSV request; timestamp travels with the cached data."""
    validate_id(series_id)
    return download(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}")


@st.cache_data(ttl=3600, show_spinner=False)
def download_asof(series_id, asof):
    """Request the actual historical vintage, not today's data truncated."""
    validate_id(series_id)
    vintage = date.fromisoformat(str(asof))
    if vintage > date.today():
        raise ValueError("A future vintage is not yet knowable.")
    values, downloaded = download(
        f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={series_id}"
        f"&vintage_date={vintage.isoformat()}"
    )
    # Observation dates and publication dates differ; the vintage request above
    # handles publication eligibility. This guard also excludes future forecasts.
    return values.loc[values.index <= pd.Timestamp(vintage)], downloaded


def compare(series_id, current, historical):
    """Counts use all downloaded history; chart start does not change the audit."""
    common = current.index.intersection(historical.index)
    revised = int(((current.loc[common] - historical.loc[common]).abs() > 1e-9).sum())
    last = historical.index.max() if not historical.empty else None
    return {
        "Series": f"https://fred.stlouisfed.org/series/{series_id}",
        "Last measured date known then": last.date().isoformat() if last is not None else None,
        "Value known then": float(historical.iloc[-1]) if last is not None else None,
        "Last measured date today": current.index[-1].date().isoformat(),
        "Value today": float(current.iloc[-1]),
        "Later observations": int((current.index > last).sum()) if last is not None else len(current),
        "Revised common observations": revised,
    }


def main():
    st.set_page_config(page_title="Point-in-time rates audit", layout="wide")
    st.title("Point-in-time rates audit")
    st.caption(f"Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded {date.today()}; built with AI help, a learning demonstration, not investment advice.")
    selected = st.sidebar.multiselect("Series", list(SERIES), default=list(SERIES), format_func=lambda key: f"{key} — {SERIES[key]}")
    extra = st.sidebar.text_input("Add a FRED series ID", value="CPIAUCSL").strip().upper()
    start = st.sidebar.date_input("Chart start date", date(2020, 1, 1))
    asof = st.sidebar.date_input("As known on", date.today(), max_value=date.today())
    st.sidebar.caption("Try 2026-10-05 for the benchmark; PAYEMS at 2025-01-15 for revisions.")
    if st.sidebar.button("Refresh downloads"):
        st.cache_data.clear()
    if extra and extra not in selected:
        selected.append(extra)
    rows = []
    for series_id in selected:
        st.subheader(f"{series_id} — {SERIES.get(series_id, 'Custom FRED series')}")
        try:
            current, current_time = download_today(series_id)
            historical, historical_time = download_asof(series_id, asof)
            chart = pd.concat({"Today's values": current, f"Known on {asof}": historical}, axis=1)
            st.line_chart(chart.loc[chart.index >= pd.Timestamp(start)])
            row = compare(series_id, current, historical)
            st.write(f"Last measured date known on {asof}: {row['Last measured date known then'] or 'none'}")
            st.caption(f"Retrieved UTC: FRED {current_time}; ALFRED {historical_time}")
            rows.append(row)
        except (requests.RequestException, ValueError, KeyError, pd.errors.ParserError) as exc:
            st.error(f"{series_id}: {exc}")
    if rows:
        st.subheader("Current versus historical vintage")
        st.dataframe(pd.DataFrame(rows), hide_index=True, column_config={"Series": st.column_config.LinkColumn("Series", display_text=r"series/(.*)")})
        st.caption("Later = nonmissing current observations after the historical last date. Revised = different nonmissing values on shared dates, across full history. A vintage date does not certify intraday availability; use the next trading session when release timing is uncertain.")


if __name__ == "__main__":
    main()
