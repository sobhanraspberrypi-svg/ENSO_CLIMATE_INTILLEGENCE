import sys, os, i0

# ── Path setup: works locally AND on Streamlit Cloud ─────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ─────────────────────────────────────────────────────────────────
# pages/3_📈_Forecast.py  –  ENSO 9-month forecast + uncertainty
# ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data_fetch  import load_all_data
from enso_engine import get_current_state, classify_enso_phase
from forecast    import train_model, forecast_nino34, spb_skill_data

st.set_page_config(page_title="Forecast", page_icon="📈", layout="wide")

@st.cache_data(ttl=3*3600, show_spinner="Fetching data…")
def get_data():
    return load_all_data()

@st.cache_resource(ttl=6*3600, show_spinner="Training forecast model on historical ENSO data…")
def get_model(nino_json):
    nino_df = pd.read_json(io.StringIO(nino_json))
    nino_df["date"] = pd.to_datetime(nino_df["date"])
    return train_model(nino_df)

data  = get_data()
state = get_current_state(data["nino"], data["oni"])

# Serialise for caching
nino_json = data["nino"].to_json()
model_art = get_model(nino_json)

# ── Header ────────────────────────────────────────────────────────
st.title("📈 ENSO Forecast — Next 9 Months")
st.markdown(f"**Current phase:** {state['phase']} &nbsp;|&nbsp; "
            f"**Model skill (r):** {model_art['corr']:.2f} &nbsp;|&nbsp; "
            f"**RMSE:** {model_art['rmse']:.2f}°C")

# ── Spring Predictability Barrier callout ─────────────────────────
spb = state["spb_skill"]
if spb < 0.55:
    st.warning(f"""
⚠️ **Spring Predictability Barrier (SPB) — Reduced Forecast Confidence**

We are currently in the **{state['spb_month']}** initialization window.
ENSO models lose skill significantly in **March–May** every year because the tropical Pacific
is in its weakest coupled state — small random atmospheric disturbances dominate.
Forecast skill: **{spb:.0%}** (vs ~78% in Oct–Jan).

👉 **Widen your planning scenarios. Do not make irreversible decisions based on a single forecast.**
    """)

# ── Forecast chart ────────────────────────────────────────────────
fc = forecast_nino34(model_art, lead_months=9)

# Historical last 24 months
hist = data["nino"].sort_values("date").tail(24)[["date", "nino34_anom"]].dropna()

fig = go.Figure()

# Historical line
fig.add_trace(go.Scatter(
    x=hist["date"], y=hist["nino34_anom"],
    mode="lines", name="Observed Niño 3.4",
    line=dict(color="#1565c0", width=2.5),
))

# Uncertainty band
fig.add_trace(go.Scatter(
    x=pd.concat([fc["date"], fc["date"][::-1]]),
    y=pd.concat([fc["upper_90"], fc["lower_90"][::-1]]),
    fill="toself",
    fillcolor="rgba(244,143,45,0.2)",
    line=dict(color="rgba(255,255,255,0)"),
    name="90% Confidence Interval",
    showlegend=True,
))

# Forecast line
fig.add_trace(go.Scatter(
    x=fc["date"], y=fc["forecast"],
    mode="lines+markers",
    name="Model Forecast",
    line=dict(color="#f57c00", width=2.5, dash="dash"),
    marker=dict(size=8, color="#f57c00"),
    hovertemplate="<b>%{x|%b %Y}</b><br>Forecast: %{y:.2f}°C<extra></extra>",
))

# Threshold lines
for val, col, label in [(1.5, "#d32f2f", "Strong El Niño"),
                         (0.5, "#fbc02d", "El Niño threshold"),
                         (-0.5, "#1565c0", "La Niña threshold"),
                         (-1.5, "#0d47a1", "Strong La Niña")]:
    fig.add_hline(y=val, line_dash="dot", line_color=col, line_width=1,
                  annotation_text=label, annotation_position="right")

# Today marker — scatter trace workaround (add_vline broken with datetime axes in some Plotly versions)
today_str = state["date"].strftime("%Y-%m-%d")
fig.add_trace(go.Scatter(
    x=[today_str, today_str],
    y=[-2.5, 2.5],
    mode="lines+text",
    line=dict(color="black", width=1.5, dash="solid"),
    text=["", "Today"],
    textposition="top center",
    name="Today",
    showlegend=False,
))

fig.update_layout(
    height=440,
    plot_bgcolor="white", paper_bgcolor="white",
    yaxis_title="Niño 3.4 Anomaly (°C)",
    yaxis=dict(range=[-2.5, 2.5]),
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.15),
    margin=dict(l=10, r=10, t=10, b=60),
)
st.plotly_chart(fig, use_container_width=True)

# ── Forecast table ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("📅 Month-by-Month Forecast")

fc_display = fc.copy()
fc_display["Month"] = fc_display["date"].dt.strftime("%B %Y")
fc_display["Forecast (°C)"] = fc_display["forecast"].apply(lambda x: f"{x:+.2f}")
fc_display["Lower (90% CI)"] = fc_display["lower_90"].apply(lambda x: f"{x:+.2f}")
fc_display["Upper (90% CI)"] = fc_display["upper_90"].apply(lambda x: f"{x:+.2f}")
fc_display["Expected Phase"] = fc_display["phase"]
fc_display["Lead (months)"] = fc_display["lead"]

phase_colours = {
    "Strong El Niño": "background-color:#ffcdd2",
    "Moderate El Niño": "background-color:#ffe0b2",
    "Weak El Niño": "background-color:#fff9c4",
    "Neutral": "background-color:#f5f5f5",
    "Weak La Niña": "background-color:#e3f2fd",
    "Moderate La Niña": "background-color:#c8e6c9",  # actually blue theme
    "Strong La Niña": "background-color:#bbdefb",
}

styled_fc = (fc_display[["Month","Lead (months)","Forecast (°C)","Lower (90% CI)","Upper (90% CI)","Expected Phase"]]
             .style.map(lambda v: phase_colours.get(v, ""), subset=["Expected Phase"]))
st.dataframe(styled_fc, use_container_width=True, height=320)

# ── Spring Predictability Barrier Chart ───────────────────────────
st.markdown("---")
st.subheader("🌸 Spring Predictability Barrier — Why Forecasts Lose Skill in March–May")

spb_df = spb_skill_data()

fig_spb = go.Figure()
fig_spb.add_trace(go.Bar(
    x=spb_df["month"], y=spb_df["skill"],
    marker_color=["#d32f2f" if b else "#42a5f5" for b in spb_df["is_barrier"]],
    text=[f"{v:.0%}" for v in spb_df["skill"]],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Forecast skill: %{y:.0%}<extra></extra>",
))
fig_spb.add_hrect(y0=0, y1=0.6, fillcolor="rgba(211,47,47,0.08)", line_width=0,
                  annotation_text="Low skill zone", annotation_position="top left")
fig_spb.add_annotation(x="Apr", y=0.42, text="⚠️ SPB<br>Season",
                        showarrow=True, arrowhead=2, font=dict(color="#d32f2f", size=12))
fig_spb.update_layout(
    height=300, plot_bgcolor="white", paper_bgcolor="white",
    yaxis_title="Correlation Skill (r)", yaxis=dict(range=[0, 1]),
    xaxis_title="Initialization Month",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_spb, use_container_width=True)

with st.expander("ℹ️ What is the Spring Predictability Barrier and why does it exist?"):
    st.markdown("""
**The Spring Predictability Barrier (SPB)** is a well-documented phenomenon where ENSO forecast skill
drops sharply when models are initialized in March–May.

**Physical reason:**
- In boreal spring, SST gradients across the tropical Pacific are at their seasonal minimum
- The ocean-atmosphere coupling is weakest (thermocline closest to surface in central Pacific)
- Random atmospheric "noise" (weather variability) has its largest relative impact on the ocean
- Small disturbances can either trigger or kill a developing El Niño / La Niña

**What this means practically:**
- A March forecast for the coming winter has ~38% skill (barely better than climatology)
- A June forecast for the same winter has ~60% skill
- An October forecast has ~78% skill

**How your dashboard handles it:**
- Confidence intervals automatically widen for forecasts issued in SPB months
- A warning banner activates when you're in the barrier season
- Users are advised to consult multiple model ensembles (IRI plume, ECMWF, NCEP) in spring
    """)

# ── Model transparency box ─────────────────────────────────────────
st.markdown("---")
with st.expander("🔬 Model Architecture & Limitations (for technical users)"):
    st.markdown(f"""
**Model type:** Gradient Boosting Ensemble (20 bootstrap models) with autoregressive lag features

**Input features:**
- 12 monthly lags of Niño 3.4 SST anomaly
- Seasonal encoding (sin/cos of month)

**Training data:** {len(data['nino'])} months of NOAA ERSSTv5 Niño indices

**Performance:**
- In-sample Pearson r: **{model_art['corr']:.3f}**
- RMSE: **{model_art['rmse']:.3f}°C**
- Useful skill at 6-month lead: ~0.6–0.7 (outside SPB season)

**Uncertainty quantification:**
Bootstrap ensemble uncertainty ± skill degradation factor by lead time (90% CI shown)

**What this model does NOT do:**
- Does not ingest spatial SST fields (would need CNN/LSTM on NetCDF)
- Does not include wind or OHC inputs (feature roadmap)
- Not a dynamical model — purely statistical/ML
- Not validated against full CMIP6 ensemble

**For operational forecasting, also consult:**
- [IRI ENSO Forecast Plume](https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/)
- [NOAA CPC ENSO Outlook](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/)
    """)
