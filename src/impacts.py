# ─────────────────────────────────────────────────────────────────
# src/impacts.py  –  Translate ENSO state into regional & sector risk
# ─────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from config import GLOBAL_IMPACTS, INDIA_STATE_ELNINO, SECTOR_IMPACTS


def global_impact_scores(impact_key: str, nino34_anom: float) -> pd.DataFrame:
    """
    Build a country-level impact DataFrame for Plotly Choropleth.
    impact_key: "el_nino" | "la_nina" | "neutral" | "modoki"
    Returns columns: iso3, country, drought_risk, flood_risk, rain_change,
                     temp_change, label, detail, combined_score
    """
    rows = []
    intensity = abs(nino34_anom)          # scale impact with anomaly magnitude

    for iso3, impact_dict in GLOBAL_IMPACTS.items():
        impact = impact_dict.get(impact_key, impact_dict.get("neutral", {}))
        rain    = impact.get("rain", 0)
        temp    = impact.get("temp", 0)
        drought = impact.get("drought", 0)
        flood   = impact.get("flood", 0)
        label   = impact.get("label", "Near-Normal")
        detail  = impact.get("detail", "")

        # Combined score: drought positive → red, flood positive → blue
        # For visualisation: +ve = drought/heat stress, -ve = flood/cool
        combined = (drought - flood) * min(intensity, 2) / 2

        rows.append({
            "iso3":         iso3,
            "drought_risk": drought,
            "flood_risk":   flood,
            "rain_change":  rain,
            "temp_change":  temp,
            "label":        label,
            "detail":       detail,
            "combined":     round(combined, 2),
        })

    return pd.DataFrame(rows)


def india_impact_df(phase: str, nino34_anom: float) -> pd.DataFrame:
    """
    Build India state-level impact DataFrame.
    Scales historical deficit by current ENSO anomaly strength.
    """
    rows = []
    intensity = min(abs(nino34_anom) / 1.0, 2.0)   # scale factor; normalised to moderate El Niño

    for state, data in INDIA_STATE_ELNINO.items():
        if "El Niño" in phase:
            deficit_scaled = data["deficit"] * intensity
            crop_risk      = data["crop_risk"]
            reservoir      = data["reservoir"]
        elif "La Niña" in phase:
            deficit_scaled = -data["deficit"] * 0.5   # surplus rainfall
            crop_risk      = "Low"
            reservoir      = "Good"
        else:
            deficit_scaled = data["deficit"] * 0.2
            crop_risk      = "Low"
            reservoir      = "Normal"

        rows.append({
            "state":         state,
            "state_code":    data["state_code"],
            "deficit_pct":   round(deficit_scaled, 1),
            "crop_risk":     crop_risk,
            "reservoir":     reservoir,
            "risk_score":    _risk_score(deficit_scaled),
        })

    return pd.DataFrame(rows)


def _risk_score(deficit_pct: float) -> int:
    """Convert deficit % to 0–100 risk score."""
    if deficit_pct <= 0:  return max(0, int(10 + deficit_pct))
    return min(100, int(deficit_pct * 4))


def sector_impact(sector: str, impact_key: str) -> dict:
    """
    Return sector-specific impact dict for a given ENSO phase.
    Falls back to neutral if phase not in map.
    """
    sector_data = SECTOR_IMPACTS.get(sector, {})
    # Normalise impact_key to broad 3-state
    key = ("el_nino" if "el_nino" in impact_key or impact_key == "modoki" else
           "la_nina" if impact_key == "la_nina" else "neutral")
    return sector_data.get(key, sector_data.get("neutral", {
        "headline": "Phase data not available",
        "risk_level": 30,
        "actions": [],
        "kpis": {},
    }))


def risk_gauge_colour(risk_level: int) -> str:
    """Return hex colour for risk gauge based on 0–100 score."""
    if risk_level >= 70: return "#d32f2f"
    if risk_level >= 45: return "#f57c00"
    if risk_level >= 25: return "#fbc02d"
    return "#388e3c"
