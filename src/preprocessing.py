"""Phase B & C – Preprocessing and Dataset Integration."""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
REPORTS = Path("reports")


# ── Phase B: Clean individual datasets ──────────────────────────────────────

def clean_meter_readings(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    audit["rows_input"] = len(df)

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Remove exact duplicate rows
    n_before = len(df)
    df = df.drop_duplicates()
    audit["exact_dupes_removed"] = n_before - len(df)

    # Conflicting customer+timestamp: keep the one with higher consumption (non-null preferred)
    n_before = len(df)
    df = df.sort_values("consumption", ascending=False, na_position="last")
    df = df.drop_duplicates(subset=["customer", "timestamp"], keep="first")
    audit["conflicting_key_dupes_removed"] = n_before - len(df)

    # Invalid timestamps
    n_before = len(df)
    df = df.dropna(subset=["timestamp"])
    audit["invalid_timestamps_removed"] = n_before - len(df)

    # Negative consumption — flag and remove (synthetic errors per notes)
    audit["negative_consumption_found"] = int((df["consumption"] < 0).sum())
    df = df[~(df["consumption"] < 0)]

    # Null consumption — keep rows but flag count (excluded from supervised training)
    audit["null_consumption_rows"] = int(df["consumption"].isnull().sum())

    # IQR outlier flag (retain, just flag)
    q1 = df["consumption"].quantile(0.25)
    q3 = df["consumption"].quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 3 * iqr
    audit["iqr_flagged_high"] = int((df["consumption"] > upper).sum())
    df["consumption_outlier_flag"] = df["consumption"] > upper

    audit["rows_output"] = len(df)
    return df.sort_values(["customer", "timestamp"]).reset_index(drop=True), audit


def clean_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    audit["rows_input"] = len(df)
    df = df.copy()

    # Standardize segment labels
    df["segment"] = df["segment"].str.strip().str.title()
    audit["segments_after_norm"] = df["segment"].unique().tolist()

    # Check for duplicate customer IDs
    audit["duplicate_customer_ids"] = int(df.duplicated("customer").sum())
    df = df.drop_duplicates("customer")

    audit["rows_output"] = len(df)
    return df.reset_index(drop=True), audit


def clean_weather(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    audit["rows_input"] = len(df)
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    n_before = len(df)
    df = df.dropna(subset=["timestamp"])
    audit["invalid_timestamps_removed"] = n_before - len(df)

    df = df.drop_duplicates("timestamp")
    audit["missing_temperature"] = int(df["temperature"].isnull().sum())
    audit["missing_humidity"] = int(df["humidity"].isnull().sum())
    audit["missing_rain"] = int(df["rain"].isnull().sum())

    # Forward-fill then back-fill missing weather measurements
    df = df.sort_values("timestamp")
    for col in ["temperature", "humidity", "rain"]:
        df[col] = df[col].ffill().bfill()

    audit["rows_output"] = len(df)
    return df.reset_index(drop=True), audit


def clean_calendar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["weekday"] = df["weekday"].str.strip().str.title()
    df["season"] = df["season"].str.strip().str.title()
    audit["rows_output"] = len(df)
    return df.reset_index(drop=True), audit


def clean_tariff(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    df = df.copy()
    df["tariff_category"] = df["tariff_category"].str.strip().str.upper()
    df["peak_period"] = df["peak_period"].str.strip().str.title()
    audit["rows_output"] = len(df)
    return df.reset_index(drop=True), audit


# ── Phase C: Integration ─────────────────────────────────────────────────────

def integrate(mr: pd.DataFrame, cu: pd.DataFrame, we: pd.DataFrame,
              ca: pd.DataFrame, ta: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    audit = {}
    audit["meter_rows_before_join"] = len(mr)

    # 1. meter → customers (many-to-one)
    assert cu.duplicated("customer").sum() == 0, "customers table has duplicate IDs"
    df = mr.merge(cu, on="customer", how="left", validate="many_to_one", indicator=True)
    audit["meter_unmatched_customers"] = int((df["_merge"] == "left_only").sum())
    df = df.drop(columns="_merge")
    audit["rows_after_customer_join"] = len(df)

    # 2. meter → weather (many-to-one on timestamp)
    assert we.duplicated("timestamp").sum() == 0, "weather has duplicate timestamps"
    df = df.merge(we, on="timestamp", how="left", validate="many_to_one", indicator=True)
    audit["meter_unmatched_weather"] = int((df["_merge"] == "left_only").sum())
    df = df.drop(columns="_merge")
    audit["rows_after_weather_join"] = len(df)

    # 3. meter → calendar (on date)
    df["date"] = df["timestamp"].dt.normalize()
    ca_join = ca.copy()
    ca_join["date"] = pd.to_datetime(ca_join["date"])
    df = df.merge(ca_join, on="date", how="left", validate="many_to_one", indicator=True)
    audit["meter_unmatched_calendar"] = int((df["_merge"] == "left_only").sum())
    df = df.drop(columns="_merge")
    audit["rows_after_calendar_join"] = len(df)

    # 4. meter → tariff (tariff_category + hour)
    df["hour"] = df["timestamp"].dt.hour
    ta_join = ta.copy()
    ta_join["tariff_category"] = ta_join["tariff_category"].str.strip().str.upper()
    df["tariff_category"] = df["tariff_category"].str.strip().str.upper()
    df = df.merge(ta_join, on=["tariff_category", "hour"], how="left", validate="many_to_one", indicator=True)
    audit["meter_unmatched_tariff"] = int((df["_merge"] == "left_only").sum())
    df = df.drop(columns="_merge")
    audit["rows_after_tariff_join"] = len(df)

    assert len(df) == audit["meter_rows_before_join"], \
        f"Row count changed after joins: {audit['meter_rows_before_join']} → {len(df)}"

    return df.reset_index(drop=True), audit


def run_preprocessing():
    from src.data_inspection import load_raw
    dfs = load_raw()

    mr_clean, mr_audit = clean_meter_readings(dfs["meter_readings"])
    cu_clean, cu_audit = clean_customers(dfs["customers"])
    we_clean, we_audit = clean_weather(dfs["weather"])
    ca_clean, ca_audit = clean_calendar(dfs["calendar"])
    ta_clean, ta_audit = clean_tariff(dfs["tariff"])

    integrated, int_audit = integrate(mr_clean, cu_clean, we_clean, ca_clean, ta_clean)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    mr_clean.to_csv(PROCESSED / "meter_readings_clean.csv", index=False)
    cu_clean.to_csv(PROCESSED / "customers_clean.csv", index=False)
    we_clean.to_csv(PROCESSED / "weather_clean.csv", index=False)
    integrated.to_csv(PROCESSED / "electricity_integrated.csv", index=False)

    # Write audit report
    REPORTS.mkdir(exist_ok=True)
    lines = ["# Preprocessing Audit\n\n_Synthetic data — not official GridSense data._\n"]
    for label, audit in [("meter_readings", mr_audit), ("customers", cu_audit),
                          ("weather", we_audit), ("calendar", ca_audit),
                          ("tariff", ta_audit), ("integration", int_audit)]:
        lines.append(f"\n## {label}\n")
        for k, v in audit.items():
            lines.append(f"- {k}: {v}\n")
    (REPORTS / "preprocessing_audit.md").write_text("".join(lines), encoding="utf-8")

    print("Preprocessing complete.")
    print(f"  Integrated dataset: {integrated.shape}")
    print(f"  Columns: {list(integrated.columns)}")
    return integrated, {
        "mr_audit": mr_audit, "cu_audit": cu_audit,
        "we_audit": we_audit, "int_audit": int_audit
    }


if __name__ == "__main__":
    run_preprocessing()
