"""Phase E & F – Feature Engineering and Machine Learning."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

PROCESSED = Path("data/processed")
MODELS = Path("models")
FIGURES = Path("reports/figures")
REPORTS = Path("reports")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["is_weekend"] = (df["timestamp"].dt.dayofweek >= 5).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Season to numeric ordinal via existing column if present
    if "season" in df.columns:
        df["season"] = df["season"].str.strip().str.title()

    # Holiday to int
    if "holiday" in df.columns:
        df["holiday"] = pd.to_numeric(df["holiday"], errors="coerce").fillna(0).astype(int)

    return df


NUMERIC_FEATURES = [
    "hour", "day_of_week", "month", "is_weekend",
    "hour_sin", "hour_cos", "month_sin", "month_cos",
    "temperature", "humidity", "rain",
]
CATEGORICAL_FEATURES = ["segment", "area", "connection_type", "tariff_category", "peak_period"]
OPTIONAL_FEATURES = ["holiday", "tariff_rate"]
TARGET = "consumption"
ID_COLS = ["timestamp", "customer"]


def select_features(df: pd.DataFrame) -> tuple[list, list]:
    num = [f for f in NUMERIC_FEATURES if f in df.columns]
    cat = [f for f in CATEGORICAL_FEATURES if f in df.columns]
    for f in OPTIONAL_FEATURES:
        if f in df.columns:
            num.append(f)
    return num, cat


def chronological_split(df: pd.DataFrame, test_frac: float = 0.2):
    """Split by timestamp boundary — all readings at a timestamp go to same side."""
    df = df.sort_values("timestamp")
    timestamps = df["timestamp"].unique()
    split_idx = int(len(timestamps) * (1 - test_frac))
    split_ts = timestamps[split_idx]
    train = df[df["timestamp"] < split_ts]
    test = df[df["timestamp"] >= split_ts]
    return train, test, split_ts


def build_pipeline(num_features: list, cat_features: list) -> Pipeline:
    num_transformer = SimpleImputer(strategy="median")
    cat_transformer = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])
    preprocessor = ColumnTransformer([
        ("num", num_transformer, num_features),
        ("cat", cat_transformer, cat_features),
    ])
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)),
    ])


def evaluate(y_true, y_pred, label: str) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"  [{label}] MAE={mae:.4f}  RMSE={rmse:.4f}  R²={r2:.4f}")
    return {"label": label, "MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}


def plot_predictions(y_true, y_pred, split_ts):
    FIGURES.mkdir(parents=True, exist_ok=True)

    # Actual vs Predicted
    fig, ax = plt.subplots()
    ax.scatter(y_true, y_pred, alpha=0.2, s=8)
    lims = [min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())]
    ax.plot(lims, lims, "r--", linewidth=1)
    ax.set_title("Actual vs Predicted Consumption")
    ax.set_xlabel("Actual (kWh)")
    ax.set_ylabel("Predicted (kWh)")
    fig.savefig(FIGURES / "actual_vs_predicted.png", bbox_inches="tight")
    plt.close(fig)

    # Residuals distribution
    residuals = y_true - y_pred
    fig, ax = plt.subplots()
    ax.hist(residuals, bins=60, edgecolor="none")
    ax.axvline(0, color="red", linestyle="--")
    ax.set_title("Residual Distribution")
    ax.set_xlabel("Residual (kWh)")
    ax.set_ylabel("Count")
    fig.savefig(FIGURES / "residual_distribution.png", bbox_inches="tight")
    plt.close(fig)

    # Residuals vs Predicted
    fig, ax = plt.subplots()
    ax.scatter(y_pred, residuals, alpha=0.2, s=8)
    ax.axhline(0, color="red", linestyle="--")
    ax.set_title("Residuals vs Predicted")
    ax.set_xlabel("Predicted (kWh)")
    ax.set_ylabel("Residual (kWh)")
    fig.savefig(FIGURES / "residuals_vs_predicted.png", bbox_inches="tight")
    plt.close(fig)
    print("  Saved prediction plots.")


def plot_feature_importance(pipeline: Pipeline, num_features: list, cat_features: list):
    model = pipeline.named_steps["model"]
    feature_names = num_features + cat_features
    importances = model.feature_importances_
    idx = np.argsort(importances)[::-1][:15]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([feature_names[i] for i in idx[::-1]], importances[idx[::-1]])
    ax.set_title("Top Feature Importances (Random Forest)")
    ax.set_xlabel("Importance")
    fig.savefig(FIGURES / "feature_importance.png", bbox_inches="tight")
    plt.close(fig)
    print("  Saved feature_importance.png")


def run_modeling() -> dict:
    df = pd.read_csv(PROCESSED / "electricity_integrated.csv", parse_dates=["timestamp"])
    df = engineer_features(df)

    # Drop rows with missing target
    df_model = df.dropna(subset=[TARGET]).copy()
    print(f"Rows available for modeling: {len(df_model):,}")

    num_features, cat_features = select_features(df_model)
    print(f"  Numeric features: {num_features}")
    print(f"  Categorical features: {cat_features}")

    train, test, split_ts = chronological_split(df_model)
    print(f"  Train: {len(train):,} rows (up to {split_ts})")
    print(f"  Test:  {len(test):,} rows")
    assert len(test) > 0, "Test set is empty"

    X_train = train[num_features + cat_features]
    y_train = train[TARGET]
    X_test = test[num_features + cat_features]
    y_test = test[TARGET]

    # Baseline
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_train, y_train)
    baseline_metrics = evaluate(y_test, dummy.predict(X_test), "Baseline (Mean)")

    # Random Forest pipeline
    pipeline = build_pipeline(num_features, cat_features)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    rf_metrics = evaluate(y_test, y_pred, "RandomForest")

    plot_predictions(y_test.values, y_pred, split_ts)
    plot_feature_importance(pipeline, num_features, cat_features)

    # Save predictions
    PROCESSED.mkdir(exist_ok=True)
    pred_df = test[ID_COLS].copy()
    pred_df["actual"] = y_test.values
    pred_df["predicted"] = y_pred
    pred_df["residual"] = pred_df["actual"] - pred_df["predicted"]
    pred_df.to_csv(PROCESSED / "test_predictions.csv", index=False)

    metrics_df = pd.DataFrame([baseline_metrics, rf_metrics])
    metrics_df.to_csv(PROCESSED / "model_metrics.csv", index=False)

    # Save pipeline
    MODELS.mkdir(exist_ok=True)
    model_path = MODELS / "rf_pipeline.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    # Verify reload
    with open(model_path, "rb") as f:
        loaded = pickle.load(f)
    assert loaded.predict(X_test[:5]).shape == (5,), "Pipeline reload failed"
    print(f"  Pipeline saved and verified: {model_path}")

    print("Modeling complete.")
    return {
        "baseline": baseline_metrics,
        "rf": rf_metrics,
        "num_features": num_features,
        "cat_features": cat_features,
        "train_rows": len(train),
        "test_rows": len(test),
        "split_ts": str(split_ts),
    }


if __name__ == "__main__":
    run_modeling()
