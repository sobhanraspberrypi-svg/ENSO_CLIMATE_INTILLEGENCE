import sys, os

# ── Path setup: works locally AND on Streamlit Cloud ─────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ─────────────────────────────────────────────────────────────────
# pages/1_🌍_Global_Monitor.py  –  Interactive globe + impact map
# ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data_fetch  import load_all_data
from enso_engine import get_current_state
from impacts     import global_impact_scores

st.set_page_config(page_title="Global Monitor", page_icon="🌍", layout="wide")

@st.cache_data(ttl=3*3600, show_spinner="Loading climate data…")
def get_data():
    return load_all_data()

data  = get_data()
state = get_current_state(data["nino"], data["oni"])

# ── Page header ───────────────────────────────────────────────────
st.title("🌍 Global ENSO Impact Monitor")
st.markdown(f"""
Current ENSO phase: **{state['phase']}** &nbsp;|&nbsp;
Niño 3.4 Anomaly: **{state['nino34_anom']:+.2f}°C** &nbsp;|&nbsp;
Type: **{state['ep_cp'] if state['ep_cp'] != 'N/A' else '—'}**
""")

# ── Globe controls ────────────────────────────────────────────────
col_ctrl, col_info = st.columns([3, 1])
with col_ctrl:
    view_var = st.radio(
        "Show on globe:",
        ["Drought Risk", "Flood Risk", "Rainfall Change", "Temperature Change"],
        horizontal=True,
    )
with col_info:
    st.info("Rotate the globe by dragging. Hover over countries for details.")

VAR_MAP = {
    "Drought Risk":        ("drought_risk", "YlOrRd",  "Drought Risk",   "Higher = more drought risk"),
    "Flood Risk":          ("flood_risk",   "Blues",    "Flood Risk",     "Higher = more flood risk"),
    "Rainfall Change":     ("rain_change",  "RdBu",     "Rainfall Signal","Blue = more rain, Red = less rain"),
    "Temperature Change":  ("temp_change",  "RdYlBu_r", "Heat Signal",    "Red = warmer than normal"),
}
col, cscale, ctitle, chelp = VAR_MAP[view_var]

impact_df = global_impact_scores(state["impact_key"], state["nino34_anom"])

# ── Full country name lookup (ISO3 → common name) ─────────────────
COUNTRY_NAMES = {
    "IND": "India",   "PAK": "Pakistan", "BGD": "Bangladesh",
    "IDN": "Indonesia","PHL": "Philippines","THA": "Thailand",
    "AUS": "Australia","KEN": "Kenya",   "ETH": "Ethiopia",
    "ZAF": "South Africa","ZWE": "Zimbabwe","PER": "Peru",
    "BRA": "Brazil",  "USA": "United States","GBR": "United Kingdom","CHN": "China",
}
impact_df["country"] = impact_df["iso3"].map(COUNTRY_NAMES).fillna(impact_df["iso3"])
impact_df["hover"] = impact_df.apply(
    lambda r: f"<b>{r['country']}</b><br>"
              f"Status: {r['label']}<br>"
              f"Drought Risk: {'▲'*max(0,r['drought_risk'])} {'▼'*max(0,-r['drought_risk'])}<br>"
              f"Flood Risk: {'▲'*max(0,r['flood_risk'])}<br>"
              + (f"<i>{r['detail'][:120]}</i>" if r['detail'] else ""),
    axis=1
)

# ── Globe Figure ──────────────────────────────────────────────────
fig_globe = go.Figure()

fig_globe.add_trace(go.Choropleth(
    locations        = impact_df["iso3"],
    z                = impact_df[col],
    colorscale       = cscale,
    zmin             = -2, zmax = 2,
    colorbar_title   = ctitle,
    hovertext        = impact_df["hover"],
    hoverinfo        = "text",
    marker_line_color= "rgba(255,255,255,0.4)",
    marker_line_width= 0.5,
))

fig_globe.update_layout(
    geo=dict(
        projection_type       = "orthographic",
        showland              = True,
        landcolor             = "rgb(240,240,235)",
        showocean             = True,
        oceancolor            = "rgb(180,210,235)",
        showlakes             = True,
        lakecolor             = "rgb(200,220,240)",
        showcountries         = True,
        countrycolor          = "rgba(150,150,150,0.5)",
        showcoastlines        = True,
        coastlinecolor        = "rgba(100,100,100,0.6)",
        projection_rotation   = dict(lon=80, lat=10, roll=0),
    ),
    height        = 560,
    margin        = dict(l=0, r=0, t=0, b=0),
    paper_bgcolor = "#0a1628",
)

st.plotly_chart(fig_globe, use_container_width=True)

# ── Country impact table ───────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Country-Level Impact Summary")
st.caption(f"Showing expected impacts during **{state['phase']}** conditions. "
           "Scores range from −2 (severe negative) to +2 (beneficial).")

col_filter = st.multiselect(
    "Filter by region:",
    ["South Asia", "Southeast Asia", "Africa", "Australia/Pacific", "Americas", "Europe/China"],
    default=["South Asia", "Southeast Asia", "Africa", "Australia/Pacific"],
)

REGION_MAP = {
    "South Asia":        ["IND","PAK","BGD"],
    "Southeast Asia":    ["IDN","PHL","THA"],
    "Africa":            ["KEN","ETH","ZAF","ZWE"],
    "Australia/Pacific": ["AUS"],
    "Americas":          ["PER","BRA","USA"],
    "Europe/China":      ["GBR","CHN"],
}

show_isos = []
for reg in col_filter:
    show_isos.extend(REGION_MAP.get(reg, []))

display_df = impact_df[impact_df["iso3"].isin(show_isos)].copy()

def colour_cell(val):
    if isinstance(val, (int, float)):
        if val >= 1.5:  return "background-color:#ffcdd2"
        if val >= 0.5:  return "background-color:#fff9c4"
        if val <= -1.5: return "background-color:#c8e6c9"
        if val <= -0.5: return "background-color:#e3f2fd"
    return ""

table_cols = ["country", "label", "rain_change", "temp_change", "drought_risk", "flood_risk"]
rename_map = {
    "country": "Country", "label": "Condition",
    "rain_change": "Rain Signal", "temp_change": "Heat Signal",
    "drought_risk": "Drought Risk", "flood_risk": "Flood Risk",
}

styled = (display_df[table_cols]
          .rename(columns=rename_map)
          .style
          .map(colour_cell, subset=["Rain Signal","Heat Signal","Drought Risk","Flood Risk"]))

st.dataframe(styled, use_container_width=True, height=350)

# ── ENSO Flavor Explainer ─────────────────────────────────────────
st.markdown("---")
st.subheader("🔀 Eastern vs Central Pacific El Niño — Why it matters")

ec1, ec2 = st.columns(2)
with ec1:
    st.markdown("""
    **🔴 Eastern Pacific (Classic) El Niño**
    - Warm anomaly centred off Peru coast
    - Walker Circulation collapses fully
    - Very strong India monsoon suppression (−15 to −30%)
    - Australia, Southern Africa severe drought
    - 1997–98, 2015–16 are the textbook examples
    - Detected by: **Niño 3 anomaly > Niño 4 anomaly**
    """)

with ec2:
    st.markdown("""
    **🟠 Central Pacific (Modoki) El Niño**
    - Warm anomaly in central Pacific; cool anomalies on either side
    - Walker Circulation weakens partially, doesn't collapse
    - India monsoon: **weaker suppression** — some years near-normal
    - Indonesia / Australia still affected but less severely
    - 2002–03, 2004–05, 2009–10 were Modoki events
    - Detected by: **EMI = Niño4 − 0.5×Niño3 − 0.5×Niño1+2 > 0.5**
    """)

# ── Nino index comparison chart ───────────────────────────────────
nino_plot = data["nino"].sort_values("date").tail(60)

fig_nino = go.Figure()
for col_name, label, colour in [
    ("nino34_anom", "Niño 3.4 (Primary)", "#1565c0"),
    ("nino3_anom",  "Niño 3 (E. Pacific)", "#d32f2f"),
    ("nino4_anom",  "Niño 4 (C. Pacific)", "#f57c00"),
    ("nino12_anom", "Niño 1+2 (Extreme E.)", "#7b1fa2"),
]:
    if col_name in nino_plot.columns:
        fig_nino.add_trace(go.Scatter(
            x=nino_plot["date"], y=nino_plot[col_name],
            mode="lines", name=label, line=dict(color=colour, width=2),
        ))

fig_nino.add_hline(y=0.5,  line_dash="dot", line_color="gray")
fig_nino.add_hline(y=-0.5, line_dash="dot", line_color="gray")
fig_nino.update_layout(
    title="Niño Index Comparison — Last 5 Years",
    height=340, plot_bgcolor="white", paper_bgcolor="white",
    yaxis_title="SST Anomaly (°C)", hovermode="x unified",
    margin=dict(l=10, r=10, t=40, b=10),
)
st.plotly_chart(fig_nino, use_container_width=True)
