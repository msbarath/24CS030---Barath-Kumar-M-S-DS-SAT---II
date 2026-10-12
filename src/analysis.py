"""Phase D – Exploratory Data Analysis."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

FIGURES = Path("reports/figures")
REPORTS = Path("reports")
PROCESSED = Path("data/processed")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "figure.figsize": (10, 5)})


def _save(fig, name: str):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}.png")


def load_integrated() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "electricity_integrated.csv", parse_dates=["timestamp", "date"])
    return df


def overall_stats(df: pd.DataFrame) -> dict:
    c = df["consumption"].dropna()
    return {
        "total_consumption": round(float(c.sum()), 2),
        "mean": round(float(c.mean()), 4),
        "median": round(float(c.median()), 4),
        "std": round(float(c.std()), 4),
        "min": round(float(c.min()), 4),
        "max": round(float(c.max()), 4),
        "p25": round(float(c.quantile(0.25)), 4),
        "p75": round(float(c.quantile(0.75)), 4),
        "p95": round(float(c.quantile(0.95)), 4),
        "valid_observations": int(c.count()),
        "null_consumption": int(df["consumption"].isnull().sum()),
    }


def hourly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate total consumption per timestamp, then average by hour."""
    agg = df.dropna(subset=["consumption"]).groupby("timestamp")["consumption"].sum().reset_index()
    agg["hour"] = agg["timestamp"].dt.hour
    hourly = agg.groupby("hour")["consumption"].mean().reset_index()
    hourly.columns = ["hour", "avg_aggregate_demand"]

    fig, ax = plt.subplots()
    ax.plot(hourly["hour"], hourly["avg_aggregate_demand"], marker="o", linewidth=2)
    ax.set_title("Average Aggregate Hourly Demand")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Avg Total Consumption (kWh)")
    ax.set_xticks(range(0, 24))
    _save(fig, "hourly_demand")
    return hourly


def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    daily = df.dropna(subset=["consumption"]).groupby("date")["consumption"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(daily["date"], daily["consumption"], linewidth=1)
    ax.set_title("Daily Total Consumption Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Consumption (kWh)")
    fig.autofmt_xdate()
    _save(fig, "daily_trend")
    return daily


def weather_relationships(df: pd.DataFrame) -> dict:
    """Use one system-level demand per timestamp to avoid duplicated weather values."""
    agg = df.dropna(subset=["consumption"]).groupby("timestamp").agg(
        total_consumption=("consumption", "sum"),
        temperature=("temperature", "first"),
        humidity=("humidity", "first"),
        rain=("rain", "first"),
    ).reset_index()

    corr = {}
    for col in ["temperature", "humidity", "rain"]:
        valid = agg[["total_consumption", col]].dropna()
        if len(valid) > 1:
            corr[col] = round(float(valid.corr().iloc[0, 1]), 4)

    # Temperature scatter
    fig, ax = plt.subplots()
    ax.scatter(agg["temperature"], agg["total_consumption"], alpha=0.3, s=10)
    ax.set_title(f"Temperature vs Aggregate Demand (r={corr.get('temperature','N/A')})")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Total Consumption (kWh)")
    _save(fig, "temperature_consumption")

    # Humidity scatter
    fig, ax = plt.subplots()
    ax.scatter(agg["humidity"], agg["total_consumption"], alpha=0.3, s=10, color="steelblue")
    ax.set_title(f"Humidity vs Aggregate Demand (r={corr.get('humidity','N/A')})")
    ax.set_xlabel("Humidity (%)")
    ax.set_ylabel("Total Consumption (kWh)")
    _save(fig, "humidity_consumption")

    # Correlation heatmap
    num_cols = agg[["total_consumption", "temperature", "humidity", "rain"]].dropna()
    if len(num_cols) > 1:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(num_cols.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap (System-Level)")
        _save(fig, "correlation_heatmap")

    return corr


def segment_analysis(df: pd.DataFrame) -> pd.DataFrame:
    seg = df.dropna(subset=["consumption"]).groupby("segment")["consumption"].agg(
        mean="mean", median="median", total="sum", std="std", count="count"
    ).round(4).reset_index()

    fig, ax = plt.subplots()
    ax.bar(seg["segment"], seg["mean"], color=sns.color_palette("muted", len(seg)))
    ax.set_title("Mean Consumption by Customer Segment")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Mean Consumption (kWh)")
    _save(fig, "segment_comparison")
    return seg


def weekday_weekend(df: pd.DataFrame) -> dict:
    d = df.dropna(subset=["consumption"]).copy()
    d["is_weekend"] = d["timestamp"].dt.dayofweek >= 5
    summary = d.groupby("is_weekend")["consumption"].agg(
        mean="mean", median="median", total="sum", count="count"
    ).round(4).reset_index()  # is_weekend stays as a column
    summary["type"] = summary["is_weekend"].map({False: "Weekday", True: "Weekend"})

    # Hourly pattern by weekday/weekend
    d["hour"] = d["timestamp"].dt.hour
    hourly = d.groupby(["is_weekend", "hour"])["consumption"].mean().reset_index()
    hourly["type"] = hourly["is_weekend"].map({False: "Weekday", True: "Weekend"})

    fig, ax = plt.subplots()
    for label, grp in hourly.groupby("type"):
        ax.plot(grp["hour"], grp["consumption"], marker="o", label=label, linewidth=2)
    ax.set_title("Average Consumption: Weekday vs Weekend by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Mean Consumption (kWh)")
    ax.legend()
    ax.set_xticks(range(0, 24))
    _save(fig, "weekday_weekend_hourly")

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(summary["type"], summary["mean"].values, color=["#4C72B0", "#DD8452"])
    ax.set_title("Mean Consumption: Weekday vs Weekend")
    ax.set_ylabel("Mean Consumption (kWh)")
    _save(fig, "weekday_weekend_comparison")

    return {"summary": summary.to_dict("records"), "hourly": hourly}


def area_analysis(df: pd.DataFrame) -> pd.DataFrame:
    area = df.dropna(subset=["consumption"]).groupby("area")["consumption"].agg(
        mean="mean", median="median", std="std", total="sum", count="count"
    ).round(4).reset_index()
    area["cv"] = (area["std"] / area["mean"]).round(4)

    fig, ax = plt.subplots(figsize=(10, 5))
    df.dropna(subset=["consumption"]).boxplot(column="consumption", by="area", ax=ax,
                                               flierprops=dict(marker=".", markersize=2))
    ax.set_title("Consumption Distribution by Area")
    ax.set_xlabel("Area")
    ax.set_ylabel("Consumption (kWh)")
    plt.suptitle("")
    _save(fig, "area_boxplot")
    return area


def tariff_analysis(df: pd.DataFrame) -> pd.DataFrame:
    if "peak_period" not in df.columns:
        print("  peak_period column not found, skipping tariff analysis")
        return pd.DataFrame()
    tariff = df.dropna(subset=["consumption"]).groupby("peak_period")["consumption"].agg(
        mean="mean", median="median", total="sum", count="count"
    ).round(4).reset_index()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(tariff["peak_period"], tariff["mean"],
           color=sns.color_palette("Set2", len(tariff)))
    ax.set_title("Mean Consumption by Tariff Period")
    ax.set_xlabel("Tariff Period")
    ax.set_ylabel("Mean Consumption (kWh)")
    _save(fig, "tariff_period_comparison")
    return tariff


def run_eda() -> dict:
    df = load_integrated()
    print(f"Integrated dataset loaded: {df.shape}")

    stats = overall_stats(df)
    print(f"  Total consumption: {stats['total_consumption']:,.2f} kWh")
    print(f"  Mean per reading: {stats['mean']} | Median: {stats['median']}")

    hourly = hourly_demand(df)
    peak_hour = int(hourly.loc[hourly["avg_aggregate_demand"].idxmax(), "hour"])
    low_hour = int(hourly.loc[hourly["avg_aggregate_demand"].idxmin(), "hour"])
    print(f"  Peak demand hour: {peak_hour}:00 | Low demand hour: {low_hour}:00")

    daily = daily_trend(df)
    corr = weather_relationships(df)
    print(f"  Weather correlations: {corr}")

    seg = segment_analysis(df)
    ww = weekday_weekend(df)
    area = area_analysis(df)
    tariff = tariff_analysis(df)

    # Write EDA findings report
    ww_summary = pd.DataFrame(ww["summary"])
    # summary rows have 'type' key after to_dict("records")
    wd_rows = [r for r in ww["summary"] if r.get("type") == "Weekday" or r.get("is_weekend") == False]
    we_rows = [r for r in ww["summary"] if r.get("type") == "Weekend" or r.get("is_weekend") == True]
    wd_val = float(wd_rows[0]["mean"]) if wd_rows else 0.0
    we_val = float(we_rows[0]["mean"]) if we_rows else 0.0

    top_seg = seg.loc[seg["mean"].idxmax(), "segment"]
    top_seg_mean = seg.loc[seg["mean"].idxmax(), "mean"]

    lines = [
        "# EDA Findings\n\n_Synthetic data — not official GridSense data._\n",
        f"\n## Overall Statistics\n",
        f"- Total consumption: {stats['total_consumption']:,.2f} kWh\n",
        f"- Valid observations: {stats['valid_observations']:,}\n",
        f"- Mean: {stats['mean']} | Median: {stats['median']} | Std: {stats['std']}\n",
        f"- Min: {stats['min']} | Max: {stats['max']} | P95: {stats['p95']}\n",
        f"\n## Finding 1 — Peak Demand Hour\n",
        f"- Peak aggregate demand occurs at **{peak_hour}:00**.\n",
        f"- Low demand occurs at **{low_hour}:00**.\n",
        f"- Peak avg aggregate demand: {hourly['avg_aggregate_demand'].max():.2f} kWh\n",
        f"- Low avg aggregate demand: {hourly['avg_aggregate_demand'].min():.2f} kWh\n",
        f"\n## Finding 2 — Customer Segment Differences\n",
        f"- Highest mean consumption segment: **{top_seg}** ({top_seg_mean:.4f} kWh/reading)\n",
        f"- Segment summary:\n{seg.to_string(index=False)}\n",
        f"\n## Weather Correlations (system-level)\n",
    ]
    for k, v in corr.items():
        lines.append(f"- {k}: r = {v}\n")
    lines += [
        f"\n## Weekday vs Weekend\n",
        f"- Weekday mean: {wd_val:.4f} kWh | Weekend mean: {we_val:.4f} kWh\n",
        f"\n## Tariff Period\n",
    ]
    if not tariff.empty:
        lines.append(tariff.to_string(index=False) + "\n")

    (REPORTS / "eda_findings.md").write_text("".join(lines), encoding="utf-8")
    print("Wrote reports/eda_findings.md")

    return {
        "stats": stats, "hourly": hourly, "peak_hour": peak_hour, "low_hour": low_hour,
        "corr": corr, "segment": seg, "weekday_weekend": ww,
        "area": area, "tariff": tariff,
    }


if __name__ == "__main__":
    run_eda()
