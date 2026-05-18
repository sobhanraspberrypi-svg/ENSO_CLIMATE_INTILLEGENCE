# ─────────────────────────────────────────────────────────────────
# src/enso_engine.py  –  ENSO detection, classification, and state summary
# ─────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from config import ENSO_THRESHOLDS, EMI_THRESHOLD, SPB_SKILL


def classify_enso_phase(nino34_anom: float) -> str:
    """Classify ENSO phase from Niño 3.4 anomaly (°C)."""
    t = ENSO_THRESHOLDS
    if nino34_anom >= t["el_nino_strong"]:   return "Strong El Niño"
    if nino34_anom >= t["el_nino_moderate"]: return "Moderate El Niño"
    if nino34_anom >= t["el_nino_weak"]:     return "Weak El Niño"
    if nino34_anom <= t["la_nina_strong"]:   return "Strong La Niña"
    if nino34_anom <= t["la_nina_moderate"]: return "Moderate La Niña"
    if nino34_anom <= t["la_nina_weak"]:     return "Weak La Niña"
    return "Neutral"


def classify_ep_cp(nino3_anom: float, nino4_anom: float, nino12_anom: float) -> str:
    """
    Classify El Niño flavor using El Niño Modoki Index (EMI).
    EMI = Niño4 − 0.5×Niño3 − 0.5×Niño1+2
    EMI > 0.5 → Central Pacific (Modoki)
    EMI < 0.3 → Eastern Pacific (Classic)
    """
    nino34_anom = (nino3_anom + nino4_anom) / 2   # approx
    if nino34_anom < 0.5:
        return "N/A"   # Not El Niño
    emi = nino4_anom - 0.5 * nino3_anom - 0.5 * nino12_anom
    if emi >= EMI_THRESHOLD:
        return "Central Pacific (Modoki)"
    else:
        return "Eastern Pacific (Classic)"


def get_current_state(nino_df: pd.DataFrame, oni_df: pd.DataFrame) -> dict:
    """
    Extract the latest ENSO state from the data.
    Returns a dict with all current indicators.
    """
    # Latest Niño values
    latest = nino_df.dropna(subset=["nino34_anom"]).iloc[-1]
    nino34_anom  = latest["nino34_anom"]
    nino3_anom   = latest.get("nino3_anom",  0.0)
    nino4_anom   = latest.get("nino4_anom",  0.0)
    nino12_anom  = latest.get("nino12_anom", 0.0)
    current_date = pd.Timestamp(latest["date"])

    phase    = classify_enso_phase(nino34_anom)
    ep_cp    = classify_ep_cp(nino3_anom, nino4_anom, nino12_anom)
    is_elnino = "El Niño" in phase

    # 3-month running mean for ONI confirmation
    oni_recent = oni_df.sort_values("date").tail(5)["anom"].mean() if len(oni_df) > 5 else nino34_anom

    # Spring Predictability Barrier
    current_month = current_date.strftime("%b")
    spb_skill = SPB_SKILL.get(current_month, 0.65)

    # Phase colour for UI
    colour_map = {
        "Strong El Niño": "#d32f2f",
        "Moderate El Niño": "#f57c00",
        "Weak El Niño": "#fbc02d",
        "Neutral": "#388e3c",
        "Weak La Niña": "#1565c0",
        "Moderate La Niña": "#0d47a1",
        "Strong La Niña": "#1a237e",
    }
    colour = colour_map.get(phase, "#616161")

    return {
        "date":          current_date,
        "nino34_anom":   round(nino34_anom, 2),
        "nino3_anom":    round(nino3_anom, 2),
        "nino4_anom":    round(nino4_anom, 2),
        "nino12_anom":   round(nino12_anom, 2),
        "oni_mean":      round(oni_recent, 2),
        "phase":         phase,
        "ep_cp":         ep_cp,
        "is_elnino":     is_elnino,
        "is_lanina":     "La Niña" in phase,
        "colour":        colour,
        "spb_skill":     spb_skill,
        "spb_month":     current_month,
        # Map key for impact lookup
        "impact_key":    (
            "modoki"  if ep_cp == "Central Pacific (Modoki)" else
            "el_nino" if is_elnino else
            "la_nina" if "La Niña" in phase else
            "neutral"
        ),
    }


def compute_oni_rolling(oni_df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Add 3-month rolling mean (the ONI metric) to the dataframe."""
    df = oni_df.sort_values("date").copy()
    df["oni_rolling"] = df["anom"].rolling(window, center=True, min_periods=1).mean()
    return df


def historical_enso_events(oni_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract historical El Niño and La Niña events from ONI time series.
    An event is ≥5 consecutive overlapping 3-month periods with |ONI| ≥ 0.5°C.
    """
    df = compute_oni_rolling(oni_df)
    df["event"] = np.where(df["oni_rolling"] >= 0.5, "El Niño",
                  np.where(df["oni_rolling"] <= -0.5, "La Niña", "Neutral"))
    return df


def enso_phase_distribution(oni_df: pd.DataFrame) -> dict:
    """Percentage of months in each phase (historical)."""
    df = compute_oni_rolling(oni_df)
    total = len(df)
    el_n  = (df["oni_rolling"] >= 0.5).sum()
    la_n  = (df["oni_rolling"] <= -0.5).sum()
    neut  = total - el_n - la_n
    return {
        "El Niño": round(100*el_n/total, 1),
        "La Niña": round(100*la_n/total, 1),
        "Neutral":  round(100*neut/total, 1),
    }


def pdo_phase(pdo_df: pd.DataFrame) -> str:
    """Return current PDO phase (Warm / Cool / Neutral)."""
    recent = pdo_df.sort_values("date").tail(12)["pdo"].mean()
    if recent > 0.3:  return f"Warm PDO (+{recent:.2f}) — Amplifies El Niño probability"
    if recent < -0.3: return f"Cool PDO ({recent:.2f}) — Dampens El Niño, supports La Niña"
    return f"Neutral PDO ({recent:.2f}) — Minimal decadal modulation"


def iod_state(iod_df: pd.DataFrame) -> dict:
    """Return current IOD state and its India monsoon modifier."""
    recent = iod_df.sort_values("date").tail(3)["iod"].mean()
    if recent >= 0.4:
        phase  = "Positive IOD"
        effect = "⚠️ Positive IOD can partially OFFSET El Niño's monsoon suppression (as in 2019)."
        colour = "#f57c00"
    elif recent <= -0.4:
        phase  = "Negative IOD"
        effect = "🔴 Negative IOD AMPLIFIES El Niño drought impact on India monsoon."
        colour = "#d32f2f"
    else:
        phase  = "Neutral IOD"
        effect = "IOD not significantly modifying ENSO teleconnection this season."
        colour = "#388e3c"
    return {"value": round(recent, 2), "phase": phase, "effect": effect, "colour": colour}
