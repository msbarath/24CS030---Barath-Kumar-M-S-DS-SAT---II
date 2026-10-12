"""Phase A – Data Understanding and Quality Assessment."""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
REPORTS = Path("reports")


def load_raw() -> dict[str, pd.DataFrame]:
    files = {
        "meter_readings": "meter_readings.csv",
        "customers": "customers.csv",
        "weather": "weather.csv",
        "calendar": "calendar.csv",
        "tariff": "tariff.csv",
    }
    return {name: pd.read_csv(RAW / fname) for name, fname in files.items()}


def inspect_df(name: str, df: pd.DataFrame) -> dict:
    result = {
        "name": name,
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "exact_duplicates": int(df.duplicated().sum()),
    }
    # numeric stats
    num = df.select_dtypes(include="number")
    if not num.empty:
        result["numeric_stats"] = num.describe().round(4).to_dict()
    return result


def inspect_meter(df: pd.DataFrame) -> dict:
    info = inspect_df("meter_readings", df)
    info["dup_customer_timestamp"] = int(df.duplicated(["customer", "timestamp"]).sum())
    info["negative_consumption"] = int((df["consumption"] < 0).sum())
    info["null_consumption"] = int(df["consumption"].isnull().sum())
    ts = pd.to_datetime(df["timestamp"], errors="coerce")
    info["invalid_timestamps"] = int(ts.isnull().sum())
    info["date_range"] = [str(ts.min()), str(ts.max())]
    info["unique_customers"] = int(df["customer"].nunique())
    return info


def inspect_customers(df: pd.DataFrame) -> dict:
    info = inspect_df("customers", df)
    info["unique_customers"] = int(df["customer"].nunique())
    info["segments_raw"] = df["segment"].unique().tolist()
    info["areas"] = df["area"].unique().tolist()
    info["connection_types"] = df["connection_type"].unique().tolist()
    info["tariff_categories"] = df["tariff_category"].unique().tolist()
    return info


def inspect_weather(df: pd.DataFrame) -> dict:
    info = inspect_df("weather", df)
    ts = pd.to_datetime(df["timestamp"], errors="coerce")
    info["invalid_timestamps"] = int(ts.isnull().sum())
    info["date_range"] = [str(ts.min()), str(ts.max())]
    return info


def inspect_calendar(df: pd.DataFrame) -> dict:
    info = inspect_df("calendar", df)
    info["unique_dates"] = int(df["date"].nunique())
    info["seasons"] = df["season"].unique().tolist()
    info["holiday_count"] = int(df["holiday"].sum()) if df["holiday"].dtype != object else None
    return info


def inspect_tariff(df: pd.DataFrame) -> dict:
    info = inspect_df("tariff", df)
    info["tariff_categories"] = df["tariff_category"].unique().tolist()
    info["peak_periods"] = df["peak_period"].unique().tolist()
    info["hours_covered"] = sorted(df["hour"].unique().tolist())
    return info


def run_inspection() -> dict:
    dfs = load_raw()
    results = {
        "meter_readings": inspect_meter(dfs["meter_readings"]),
        "customers": inspect_customers(dfs["customers"]),
        "weather": inspect_weather(dfs["weather"]),
        "calendar": inspect_calendar(dfs["calendar"]),
        "tariff": inspect_tariff(dfs["tariff"]),
    }
    return results, dfs


def write_inspection_report(results: dict):
    REPORTS.mkdir(exist_ok=True)
    lines = ["# Dataset Inspection Report\n", "_Synthetic practice data — not official GridSense data._\n"]
    for name, info in results.items():
        lines.append(f"\n## {name}\n")
        lines.append(f"- Shape: {info['shape'][0]:,} rows × {info['shape'][1]} columns\n")
        lines.append(f"- Columns: {info['columns']}\n")
        lines.append(f"- Exact duplicate rows: {info['exact_duplicates']}\n")
        for col, cnt in info["missing"].items():
            if cnt > 0:
                lines.append(f"- Missing `{col}`: {cnt:,} ({info['missing_pct'][col]:.2f}%)\n")
        # dataset-specific extras
        for key in ["dup_customer_timestamp", "negative_consumption", "null_consumption",
                    "invalid_timestamps", "unique_customers", "segments_raw", "areas",
                    "connection_types", "tariff_categories", "peak_periods", "date_range",
                    "unique_dates", "holiday_count"]:
            if key in info:
                lines.append(f"- {key}: {info[key]}\n")
    (REPORTS / "dataset_inspection.md").write_text("".join(lines), encoding="utf-8")
    print("Wrote reports/dataset_inspection.md")


if __name__ == "__main__":
    results, _ = run_inspection()
    write_inspection_report(results)
    for name, info in results.items():
        print(f"\n=== {name} ===")
        print(f"  Shape: {info['shape']}")
        print(f"  Missing: {info['missing']}")
        print(f"  Exact dupes: {info['exact_duplicates']}")
        for k in ["dup_customer_timestamp", "negative_consumption", "null_consumption",
                  "segments_raw", "date_range"]:
            if k in info:
                print(f"  {k}: {info[k]}")
