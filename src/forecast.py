# ─────────────────────────────────────────────────────────────────
# src/forecast.py  –  ENSO Prediction (AR + Gradient Boosting ensemble)
# Runs entirely on CPU.  No TensorFlow or GPU required.
# ─────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore")


# ── Feature engineering ───────────────────────────────────────────
def _make_features(series: np.ndarray, lags: int = 12) -> tuple:
    """
    Build lag feature matrix from a time series.
    X shape: (n_samples, lags)
    y shape: (n_samples,)  — 1-step ahead target
    """
    X, y = [], []
    for i in range(lags, len(series)):
        X.append(series[i-lags:i])
        y.append(series[i])
    return np.array(X), np.array(y)


def _seasonal_features(dates: pd.DatetimeIndex, lags: int = 12) -> np.ndarray:
    """Add sine/cosine month encoding to capture annual cycle."""
    months = np.array([d.month for d in dates[lags:]])
    sin_m  = np.sin(2 * np.pi * months / 12)
    cos_m  = np.cos(2 * np.pi * months / 12)
    return sin_m, cos_m


# ── Model training ────────────────────────────────────────────────
def train_model(nino_df: pd.DataFrame, lags: int = 12) -> dict:
    """
    Train an ensemble of Gradient Boosting models on Niño 3.4 anomaly.
    Returns model artefact dict.
    """
    df      = nino_df.sort_values("date").dropna(subset=["nino34_anom"])
    series  = df["nino34_anom"].values.astype(float)
    dates   = pd.DatetimeIndex(df["date"].values)

    X, y      = _make_features(series, lags)
    sin_m, cos_m = _seasonal_features(dates, lags)
    X_full    = np.column_stack([X, sin_m, cos_m])

    scaler    = StandardScaler()
    X_scaled  = scaler.fit_transform(X_full)

    # Train 20 bootstrap models for uncertainty quantification
    n_boot = 20
    models = []
    rng    = np.random.default_rng(42)
    n      = len(X_scaled)

    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        m   = GradientBoostingRegressor(
            n_estimators=80, max_depth=3, learning_rate=0.08,
            subsample=0.8, random_state=int(rng.integers(0, 9999))
        )
        m.fit(X_scaled[idx], y[idx])
        models.append(m)

    # Compute in-sample skill score
    preds_all = np.array([m.predict(X_scaled) for m in models])
    pred_mean = preds_all.mean(axis=0)
    rmse      = np.sqrt(mean_squared_error(y, pred_mean))
    corr      = np.corrcoef(y, pred_mean)[0, 1]

    return {
        "models": models, "scaler": scaler,
        "series": series, "dates": dates,
        "lags": lags, "rmse": round(rmse, 3), "corr": round(corr, 3),
        "last_window": series[-lags:],
        "last_date": dates[-1],
    }


# ── Multi-step forecast ───────────────────────────────────────────
def forecast_nino34(model_art: dict, lead_months: int = 9) -> pd.DataFrame:
    """
    Generate Niño 3.4 anomaly forecast for the next `lead_months`.
    Returns DataFrame with date, forecast mean, lower/upper 90% CI.
    """
    scaler  = model_art["scaler"]
    models  = model_art["models"]
    lags    = model_art["lags"]
    window  = model_art["last_window"].copy()
    start   = model_art["last_date"]

    forecast_dates = pd.date_range(
        start + pd.DateOffset(months=1), periods=lead_months, freq="MS"
    )

    all_preds = np.zeros((len(models), lead_months))

    for m_idx, model in enumerate(models):
        w = window.copy()
        for step in range(lead_months):
            fut_month = (start + pd.DateOffset(months=step+1)).month
            sin_m = np.sin(2 * np.pi * fut_month / 12)
            cos_m = np.cos(2 * np.pi * fut_month / 12)
            feat  = np.append(w[-lags:], [sin_m, cos_m]).reshape(1, -1)
            feat_s = scaler.transform(feat)
            pred  = model.predict(feat_s)[0]
            all_preds[m_idx, step] = pred
            w     = np.append(w, pred)

    mean_f  = all_preds.mean(axis=0)
    lower_f = np.percentile(all_preds, 5,  axis=0)
    upper_f = np.percentile(all_preds, 95, axis=0)

    # Skill degrades with lead time — widen CI proportionally
    skill_weights = np.linspace(1.0, 1.8, lead_months)
    half_range    = (upper_f - lower_f) / 2
    lower_adj     = mean_f - half_range * skill_weights
    upper_adj     = mean_f + half_range * skill_weights

    df = pd.DataFrame({
        "date":  forecast_dates,
        "lead":  range(1, lead_months+1),
        "forecast":   np.round(mean_f,  2),
        "lower_90":   np.round(lower_adj, 2),
        "upper_90":   np.round(upper_adj, 2),
    })

    # Add plain-language phase label for each forecast month
    df["phase"] = df["forecast"].apply(_forecast_phase_label)
    return df


def _forecast_phase_label(val: float) -> str:
    if val >= 1.5:   return "Strong El Niño"
    if val >= 1.0:   return "Moderate El Niño"
    if val >= 0.5:   return "Weak El Niño"
    if val <= -1.5:  return "Strong La Niña"
    if val <= -1.0:  return "Moderate La Niña"
    if val <= -0.5:  return "Weak La Niña"
    return "Neutral"


# ── Spring Predictability Barrier visualisation data ──────────────
def spb_skill_data() -> pd.DataFrame:
    """
    Returns a DataFrame showing model prediction skill by initialization month.
    Visualises the Spring Predictability Barrier (March–May skill drop).
    """
    from config import SPB_SKILL
    months = list(SPB_SKILL.keys())
    skills = list(SPB_SKILL.values())
    return pd.DataFrame({
        "month": months,
        "skill": skills,
        "month_num": range(1, 13),
        "is_barrier": [m in ["Mar","Apr","May"] for m in months],
    })
