# pages/2_India_Impact.py
import sys, os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import json, requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data_fetch  import load_all_data
from enso_engine import get_current_state, iod_state
from impacts     import india_impact_df
from config      import (INDIA_STATE_TEMP_ELNINO, INDIA_CITY_ELNINO,
                          GEOJSON_NAME1_TO_CONFIG)

st.set_page_config(page_title="India Impact", page_icon="\U0001f1ee\U0001f1f3", layout="wide")

# ── Load GeoJSON (local file first, then fallback download) ────────
@st.cache_data(ttl=None, show_spinner="Loading India map...")
def load_geojson():
    geo_path = os.path.join(_ROOT, "data", "india_states.geojson")
    gj = None
    # Local file (committed to repo or generated locally)
    if os.path.exists(geo_path):
        try:
            with open(geo_path, "r", encoding="utf-8") as f:
                gj = json.load(f)
        except Exception:
            gj = None
    # Fallback download (Streamlit Cloud when file not committed)
    if gj is None:
        for url in [
            "https://raw.githubusercontent.com/Aftaab25/India-State-wise-GeoJSON/main/india_states.geojson",
            "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
        ]:
            try:
                r = requests.get(url, timeout=20)
                if r.status_code == 200:
                    gj = r.json()
                    break
            except Exception:
                continue
    if gj is None:
        return None
    # Add ST_NAME field using GEOJSON_NAME1_TO_CONFIG mapping
    # Works for NAME_1 field (simplemaps / geohacker)
    for feat in gj["features"]:
        props = feat["properties"]
        raw = props.get("NAME_1") or props.get("name") or props.get("ST_NM") or ""
        props["ST_NAME"] = GEOJSON_NAME1_TO_CONFIG.get(raw, raw)
    return gj

@st.cache_data(ttl=3*3600, show_spinner="Fetching latest NOAA climate data...")
def get_data():
    return load_all_data()

data    = get_data()
state   = get_current_state(data["nino"], data["oni"])
iod     = iod_state(data["iod"])
rain    = india_impact_df(state["phase"], state["nino34_anom"])
geojson = load_geojson()

def build_state_df(phase, nino34_anom):
    intensity = min(abs(nino34_anom) / 1.0, 2.0)
    rows = []
    for _, row in rain.iterrows():
        s, rd = row["state"], row["deficit_pct"]
        td = INDIA_STATE_TEMP_ELNINO.get(s, {})
        if "El" in phase and "Ni" in phase:
            temp_a  = round(td.get("temp_anom", 1.0) * intensity, 2)
            hw_days = int(td.get("heatwave_days", 5) * intensity)
            t_risk  = td.get("risk", "Moderate")
        elif "La" in phase:
            temp_a, hw_days, t_risk = round(-0.3 * intensity, 2), 0, "Low"
        else:
            temp_a, hw_days, t_risk = 0.4, 3, "Low"
        rows.append({
            "state": s, "rain_def": rd,
            "temp_anom": temp_a, "heatwave_days": hw_days, "temp_risk": t_risk,
            "crop_risk": row["crop_risk"], "reservoir": row["reservoir"],
        })
    return pd.DataFrame(rows)

sdf = build_state_df(state["phase"], state["nino34_anom"])
sdf["combined_risk"] = (sdf["rain_def"].abs()*2 + sdf["temp_anom"]*10).clip(0,100).astype(int)

# ── Header ─────────────────────────────────────────────────────────
st.title("\U0001f1ee\U0001f1f3 India ENSO Impact Dashboard")
latest_date = pd.Timestamp(data["nino"]["date"].max())
st.markdown(
    f"**ENSO Phase:** {state['phase']} &nbsp;|&nbsp; "
    f"**IOD:** {iod['phase']} &nbsp;|&nbsp; "
    f"**Data:** {latest_date.strftime('%B %Y')} &nbsp;|&nbsp; "
    + ("⬇️ Deficit likely" if state["is_elnino"]
       else "⬆️ Surplus likely" if state["is_lanina"]
       else "➡️ Near-normal monsoon")
)
if latest_date.year < 2025:
    st.warning(
        f"⚠️ Showing {latest_date.strftime('%B %Y')} data. "
        "Delete **data/cache/** folder, then restart Streamlit to get 2026 data."
    )
if state["is_elnino"]:
    if iod["phase"] == "Positive IOD":
        st.warning("⚠️ Positive IOD partially offsetting El Niño monsoon suppression (2019 precedent).")
    else:
        st.error("🔴 El Niño active — monsoon deficit + heat stress across central & peninsular India.")

st.markdown("---")

tab_map, tab_rain, tab_temp, tab_city, tab_hist = st.tabs([
    "🗺️ India Impact Map", "🌧️ Monsoon Deficit",
    "🌡️ Temperature Impact", "🏙️ City-Level Risk", "📅 Historical Record",
])

# ══════════════════════════════════════════════════════════════════
with tab_map:
    st.subheader("India State-Level Impact Map")
    st.caption(
        "36 states & UTs | J&K and Ladakh shown separately | "
        "Boundary: simplemaps.com India layer | "
        "Map courtesy: simplemaps.com (free non-commercial use)."
    )

    if geojson is None:
        st.error(
            "GeoJSON not loaded. For local use: export your QGIS simplemaps layer "
            "as GeoJSON to data/india_states.geojson. "
            "For Streamlit Cloud: it will download automatically."
        )
    else:
        geo_states = set(f["properties"]["ST_NAME"] for f in geojson["features"])
        sdf["in_geo"] = sdf["state"].isin(geo_states)
        unmatched = sdf[~sdf["in_geo"]]["state"].tolist()

        map_var = st.radio(
            "Show on map:",
            ["🌧️ Monsoon Deficit %", "🌡️ Temperature Anomaly", "⚠️ Combined Risk Score"],
            horizontal=True, key="map_var"
        )
        if "Monsoon"  in map_var: z_col, title, cscale, zmin, zmax = "rain_def",      "Deficit %",  "RdBu",     -25, 25
        elif "Temp"   in map_var: z_col, title, cscale, zmin, zmax = "temp_anom",     "Temp (°C)",  "YlOrRd",     0,  3
        else:                     z_col, title, cscale, zmin, zmax = "combined_risk", "Risk 0-100", "RdYlGn_r",   0,100

        sdf_geo = sdf[sdf["in_geo"]].copy()
        fig_map = px.choropleth(
            sdf_geo, geojson=geojson,
            locations="state", featureidkey="properties.ST_NAME",
            color=z_col, color_continuous_scale=cscale, range_color=[zmin, zmax],
            hover_name="state",
            hover_data={"state": False, z_col: True,
                        "crop_risk": True, "reservoir": True, "heatwave_days": True},
            labels={z_col: title, "crop_risk":"Crop Risk",
                    "reservoir":"Reservoir","heatwave_days":"HW Days"},
        )
        fig_map.update_geos(fitbounds="locations", visible=False,
                            showcountries=True, countrycolor="gray")
        fig_map.update_layout(height=580, margin=dict(l=0,r=0,t=0,b=0),
                               coloraxis_colorbar=dict(title=title, len=0.6),
                               paper_bgcolor="white")
        st.plotly_chart(fig_map, use_container_width=True, key="india_map")
        st.caption(
            f"✅ {len(sdf_geo)}/{len(sdf)} states matched."
            + (f" | ℹ️ Not shown: {', '.join(unmatched)}" if unmatched else "")
        )

        # City quick-view
        ws_dot = {"Critical":"🔴","Severe":"🔴","High":"🟠","Moderate":"🟡","Low":"🟢"}
        cols = st.columns(4)
        for i, (city, cd) in enumerate(INDIA_CITY_ELNINO.items()):
            with cols[i % 4]:
                st.markdown(
                    f"**{city}** {ws_dot.get(cd['water_stress'],'🟡')}<br>"
                    f"Def {cd['rain_def']}% | +{cd['temp_anom']:.1f}°C",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════
with tab_rain:
    st.subheader("State-Level Monsoon Deficit Risk")
    sdf_s = sdf.sort_values("rain_def", ascending=True)
    colours = [
        "#d32f2f" if v>=20 else "#f57c00" if v>=12 else
        "#fbc02d" if v>=5  else "#66bb6a" if v>=0  else "#1565c0"
        for v in sdf_s["rain_def"]
    ]
    fig_r = go.Figure(go.Bar(
        x=sdf_s["rain_def"], y=sdf_s["state"], orientation="h",
        marker_color=colours,
        text=[f"{v:+.0f}%" for v in sdf_s["rain_def"]], textposition="outside",
    ))
    fig_r.add_vline(x=0, line_color="black", line_width=1)
    fig_r.update_layout(height=700, plot_bgcolor="white", paper_bgcolor="white",
                         xaxis_title="Monsoon Deficit / Surplus (%)",
                         margin=dict(l=10,r=80,t=10,b=10))
    st.plotly_chart(fig_r, use_container_width=True, key="rain_bar")
    st.dataframe(
        sdf.sort_values("rain_def", ascending=False)
           [["state","rain_def","crop_risk","reservoir"]]
           .rename(columns={"state":"State","rain_def":"Deficit %",
                             "crop_risk":"Crop Risk","reservoir":"Reservoir"})
           .style.background_gradient(subset=["Deficit %"], cmap="RdYlGn_r"),
        use_container_width=True, key="rain_table"
    )

# ══════════════════════════════════════════════════════════════════
with tab_temp:
    st.subheader("\U0001f321\ufe0f Temperature Anomaly — El Niño Heat Stress")
    sdf_t = sdf.sort_values("temp_anom", ascending=False)
    t_col = [
        "#b71c1c" if v>=2.2 else "#d32f2f" if v>=1.8 else
        "#f57c00" if v>=1.4 else "#fbc02d" if v>=1.0 else "#66bb6a"
        for v in sdf_t["temp_anom"]
    ]
    c1, c2 = st.columns(2)
    with c1:
        fig_t = go.Figure(go.Bar(
            x=sdf_t["temp_anom"], y=sdf_t["state"], orientation="h",
            marker_color=t_col,
            text=[f"+{v:.1f}°C" for v in sdf_t["temp_anom"]], textposition="outside",
        ))
        fig_t.update_layout(height=700, plot_bgcolor="white", paper_bgcolor="white",
                             xaxis_title="°C above normal", xaxis=dict(range=[0,3.2]),
                             title="Temperature Anomaly (°C)",
                             margin=dict(l=10,r=80,t=40,b=10))
        st.plotly_chart(fig_t, use_container_width=True, key="temp_bar")
    with c2:
        fig_hw = go.Figure(go.Bar(
            x=sdf_t["heatwave_days"], y=sdf_t["state"], orientation="h",
            marker_color=t_col,
            text=[f"{v}d" for v in sdf_t["heatwave_days"]], textposition="outside",
        ))
        fig_hw.update_layout(height=700, plot_bgcolor="white", paper_bgcolor="white",
                              xaxis_title="Extra Heatwave Days",
                              title="Additional Heatwave Days vs Normal Year",
                              margin=dict(l=10,r=60,t=40,b=10))
        st.plotly_chart(fig_hw, use_container_width=True, key="hw_bar")
    rc_t = {"Extreme":"#b71c1c","Very High":"#d32f2f","High":"#f57c00","Moderate":"#fbc02d","Low":"#c8e6c9"}
    st.dataframe(
        sdf_t[["state","temp_anom","heatwave_days","temp_risk"]]
            .rename(columns={"state":"State","temp_anom":"Temp (°C)",
                              "heatwave_days":"HW Days","temp_risk":"Risk"})
            .style.map(
                lambda v: f"background-color:{rc_t.get(v,'#f5f5f5')};color:{'white' if v in ['Extreme','Very High'] else 'black'}",
                subset=["Risk"])
            .background_gradient(subset=["Temp (°C)"], cmap="YlOrRd"),
        use_container_width=True, height=560, key="temp_table"
    )

# ══════════════════════════════════════════════════════════════════
with tab_city:
    st.subheader("\U0001f3d9\ufe0f Major Cities — El Niño Risk")
    wsc = {"Critical":"#b71c1c","Severe":"#d32f2f","High":"#f57c00","Moderate":"#fbc02d","Low":"#c8e6c9"}
    rows = [{
        "City":c, "State":d["state"], "Pop (M)":d["pop_m"],
        "Temp":f"+{d['temp_anom']:.1f}°C", "Rain Def":f"{d['rain_def']}%",
        "Water Stress":d["water_stress"], "Agri Zone":d["agri_zone"],
    } for c,d in INDIA_CITY_ELNINO.items()]
    st.dataframe(
        pd.DataFrame(rows).style.map(
            lambda v: f"background-color:{wsc.get(v,'')};color:{'white' if v in ['Critical','Severe'] else 'black'}",
            subset=["Water Stress"]),
        use_container_width=True, height=400, key="city_tbl"
    )
    st.info("For all 81 Indian cities + 59 world cities → **🏙️ City Risk** page.")

# ══════════════════════════════════════════════════════════════════
with tab_hist:
    st.subheader("📅 Historical El Niño — India Record")
    hist = pd.DataFrame({
        "Year":             [1982,1987,1991,1994,1997,2002,2004,2009,2014,2015,2018,2023],
        "ONI Peak (°C)":    [2.1, 1.6, 1.7, 1.0, 2.3, 0.8, 0.7, 1.0, 0.6, 2.3, 0.8, 2.0],
        "ISMR Anomaly (%)": [-14,-19,-10,-11, +2,-19,-13,-22,-12,-14, -9,  -4],
        "Temp Anom (°C)":   [1.6, 2.1, 1.4, 1.2, 1.0, 1.8, 1.3, 1.9, 1.1, 2.2, 0.9, 1.7],
        "IOD Phase":        ["Neg","Neu","Neu","Pos","Pos","Neu","Neu","Neg","Neu","Neu","Neu","Pos"],
        "Event":            ["Severe drought","Worst since 1918","Partial","Moderate",
                             "IOD offset","Severe drought","Modoki partial","Worst since 1972",
                             "Moderate","2500 deaths AP/TG","Near-normal","IOD offset"],
    })
    st.dataframe(
        hist.style
            .background_gradient(subset=["ISMR Anomaly (%)"], cmap="RdYlGn")
            .background_gradient(subset=["Temp Anom (°C)"],   cmap="YlOrRd")
            .background_gradient(subset=["ONI Peak (°C)"],    cmap="RdYlBu_r"),
        use_container_width=True, height=360, key="hist_tbl"
    )
    iod_c = {"Pos":"#f57c00","Neg":"#d32f2f","Neu":"#1565c0"}
    fig_sc = go.Figure()
    for ph in ["Pos","Neg","Neu"]:
        sub = hist[hist["IOD Phase"]==ph]
        fig_sc.add_trace(go.Scatter(
            x=sub["ONI Peak (°C)"], y=sub["ISMR Anomaly (%)"],
            mode="markers+text", name=f"IOD {ph}",
            marker=dict(size=14, color=iod_c[ph]),
            text=sub["Year"].astype(str), textposition="top center",
        ))
    fig_sc.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_sc.update_layout(
        height=320, plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title="ONI Peak (°C)", yaxis_title="Monsoon Anomaly (%)",
        title="El Niño Strength vs India Monsoon — IOD matters as much as ONI",
        margin=dict(l=10,r=10,t=50,b=10)
    )
    st.plotly_chart(fig_sc, use_container_width=True, key="hist_sc")
    st.caption("1997 (ONI 2.3°C) → +2% ISMR (Positive IOD). 2009 (ONI 1.0°C) → −22% (Negative IOD).")
