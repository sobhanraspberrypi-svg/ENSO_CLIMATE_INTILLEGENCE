import sys, os

# ── Path setup: works locally AND on Streamlit Cloud ─────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ─────────────────────────────────────────────────────────────────
# pages/5_🏙️_City_Risk.py  –  City-level ENSO risk (India + World)
# ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data_fetch  import load_all_data
from enso_engine import get_current_state
from config      import (INDIA_ALL_CITIES, INDIA_STATE_TEMP_ELNINO,
                          INDIA_STATE_ELNINO, GLOBAL_IMPACTS, WORLD_CITIES)

st.set_page_config(page_title="City Risk", page_icon="🏙️", layout="wide")

@st.cache_data(ttl=3*3600, show_spinner="Loading data...")
def get_data():
    return load_all_data()

data  = get_data()
state = get_current_state(data["nino"], data["oni"])
phase = state["phase"]
imp_key = state["impact_key"]
nino34  = state["nino34_anom"]
intensity = min(abs(nino34) / 1.0, 2.0)

# ── Helpers ───────────────────────────────────────────────────────
WS_COLOUR = {
    "Critical": "#b71c1c", "Severe": "#d32f2f",
    "High": "#f57c00", "Moderate": "#fbc02d", "Low": "#c8e6c9"
}
RISK_LABEL = {
    "Extreme": "🔴 Extreme", "Very High": "🔴 Very High",
    "High": "🟠 High", "Moderate": "🟡 Moderate", "Low": "🟢 Low"
}

def derive_city_impact_india(city_name: str, cdata: dict) -> dict:
    s = cdata["state"]
    state_rain = INDIA_STATE_ELNINO.get(s, {})
    state_temp = INDIA_STATE_TEMP_ELNINO.get(s, {})
    if "El Nino" in phase or "El Niño" in phase:
        base_def  = state_rain.get("deficit", 12) * intensity
        base_temp = state_temp.get("temp_anom", 1.5) * intensity
        base_hw   = int(state_temp.get("heatwave_days", 8) * intensity)
        base_ws   = state_rain.get("reservoir", "Moderate")
        base_crop = state_rain.get("crop_risk", "Medium")
    elif "La Nina" in phase or "La Niña" in phase:
        base_def  = -state_rain.get("deficit", 12) * 0.4
        base_temp = -0.3
        base_hw   = 0
        base_ws   = "Good"
        base_crop = "Low"
    else:
        base_def  = state_rain.get("deficit", 12) * 0.2
        base_temp = 0.3
        base_hw   = 2
        base_ws   = "Normal"
        base_crop = "Low"
    rain_def  = round(base_def  + cdata.get("rain_mod", 0), 1)
    temp_anom = round(base_temp + cdata.get("temp_mod", 0.3), 2)
    risk_score = min(100, int(abs(rain_def) * 2.5 + temp_anom * 10))
    risk_label = ("Extreme" if risk_score >= 75 else "Very High" if risk_score >= 60
                  else "High" if risk_score >= 40 else "Moderate" if risk_score >= 20 else "Low")
    return {
        "rain_def": rain_def, "temp_anom": temp_anom,
        "heatwave_days": base_hw, "water_stress": base_ws,
        "crop_risk": base_crop, "risk_score": risk_score,
        "risk_label": risk_label, "tier": cdata.get("tier", 3),
        "pop_m": cdata.get("pop_m", 0.5),
        "state": cdata["state"], "lat": cdata["lat"], "lon": cdata["lon"],
    }

def derive_city_impact_world(city_name: str, cdata: dict) -> dict:
    iso3 = cdata["country"]
    country_impact = GLOBAL_IMPACTS.get(iso3, {}).get(imp_key,
                     GLOBAL_IMPACTS.get(iso3, {}).get("neutral", {}))
    rain  = country_impact.get("rain", 0)
    temp  = country_impact.get("temp", 0)
    drought = country_impact.get("drought", 0)
    flood   = country_impact.get("flood", 0)
    label   = country_impact.get("label", "Near-Normal")
    detail  = cdata.get("local_note", country_impact.get("detail", ""))
    rain_def_pct = rain * intensity * 8   # convert -2..+2 scale to approximate %
    temp_anom    = round(temp * intensity * 0.8, 1)
    risk_score   = min(100, int((abs(drought) + abs(flood)) * intensity * 20 + abs(temp_anom) * 5))
    risk_label   = ("Extreme" if risk_score >= 75 else "Very High" if risk_score >= 60
                    else "High" if risk_score >= 40 else "Moderate" if risk_score >= 20 else "Low")
    return {
        "rain_def": round(rain_def_pct, 1), "temp_anom": temp_anom,
        "drought_risk": drought, "flood_risk": flood,
        "label": label, "local_note": detail,
        "risk_score": risk_score, "risk_label": risk_label,
        "pop_m": cdata.get("pop_m", 1.0),
        "lat": cdata["lat"], "lon": cdata["lon"],
        "country_iso3": iso3,
    }

# ── Header ────────────────────────────────────────────────────────
st.title("🏙️ City-Level ENSO Risk")
st.markdown(f"**Phase:** {phase} &nbsp;|&nbsp; **Niño 3.4:** {nino34:+.2f}°C")

tab_india, tab_world = st.tabs(["🇮🇳 India Cities", "🌍 World Cities"])

# ═══════════════════════════════════════════════════════════════════
# INDIA CITIES TAB
# ═══════════════════════════════════════════════════════════════════
with tab_india:
    st.subheader("India City Risk Explorer")
    st.caption(f"81 cities covered. Risk derived from state-level ENSO analog data + urban heat island adjustment.")

    col_search, col_filter = st.columns([2, 2])
    with col_search:
        all_india_cities = sorted(INDIA_ALL_CITIES.keys())
        selected_city = st.selectbox(
            "🔍 Search or select any Indian city:",
            options=["— Browse all cities —"] + all_india_cities,
            key="india_city_select"
        )
    with col_filter:
        state_options = ["All States"] + sorted(set(v["state"] for v in INDIA_ALL_CITIES.values()))
        filter_state  = st.selectbox("Filter by State:", state_options, key="india_state_filter")

    # ── Single city detail card ───────────────────────────────────
    if selected_city != "— Browse all cities —":
        cdata  = INDIA_ALL_CITIES[selected_city]
        impact = derive_city_impact_india(selected_city, cdata)
        rc     = WS_COLOUR.get(impact["water_stress"], "#fbc02d")
        riskc  = ("#d32f2f" if impact["risk_score"] >= 60 else
                  "#f57c00" if impact["risk_score"] >= 40 else
                  "#fbc02d" if impact["risk_score"] >= 20 else "#388e3c")

        st.markdown(f"""
        <div style="background:{riskc};padding:20px 28px;border-radius:12px;margin:16px 0;color:white;">
          <h2 style="margin:0;">🏙️ {selected_city}</h2>
          <p style="margin:4px 0;opacity:0.9;">{cdata['state']} &nbsp;|&nbsp;
             Tier {cdata['tier']} city &nbsp;|&nbsp; Pop: {cdata['pop_m']:.1f}M</p>
          <p style="margin:8px 0 0 0;font-size:1.1rem;">
             Risk Score: <b>{impact['risk_score']}/100</b> &nbsp;|&nbsp;
             {RISK_LABEL.get(impact['risk_label'], impact['risk_label'])}
          </p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("🌧️ Rain Deficit", f"{impact['rain_def']:+.0f}%")
        m2.metric("🌡️ Temp Anomaly", f"+{impact['temp_anom']:.1f}°C")
        m3.metric("☀️ Heatwave Days", f"+{impact['heatwave_days']} days")
        m4.metric("💧 Water Stress", impact["water_stress"])
        m5.metric("🌾 Crop Risk", impact["crop_risk"])

        st.markdown("---")

    # ── City table (filtered) ─────────────────────────────────────
    rows = []
    for city, cdata in INDIA_ALL_CITIES.items():
        if filter_state != "All States" and cdata["state"] != filter_state:
            continue
        imp = derive_city_impact_india(city, cdata)
        rows.append({
            "City": city, "State": cdata["state"], "Tier": cdata["tier"],
            "Pop (M)": cdata["pop_m"],
            "Rain Def %": imp["rain_def"],
            "Temp +°C": imp["temp_anom"],
            "HW Days": imp["heatwave_days"],
            "Water Stress": imp["water_stress"],
            "Crop Risk": imp["crop_risk"],
            "Risk Score": imp["risk_score"],
            "lat": cdata["lat"], "lon": cdata["lon"],
        })
    city_df = pd.DataFrame(rows).sort_values("Risk Score", ascending=False)

    # City map — scatter on India
    st.subheader("City Risk Map")
    colour_list = [WS_COLOUR.get(r, "#fbc02d") for r in city_df["Water Stress"]]
    fig_map = go.Figure()
    fig_map.add_trace(go.Scattergeo(
        lat=city_df["lat"], lon=city_df["lon"],
        mode="markers+text",
        marker=dict(
            size=city_df["Pop (M)"].clip(0.3, 15) * 3 + 6,
            color=city_df["Risk Score"],
            colorscale="RdYlGn_r",
            cmin=0, cmax=100,
            colorbar=dict(title="Risk Score", len=0.5),
            opacity=0.85,
            line=dict(color="white", width=1),
        ),
        text=city_df["City"],
        textposition="top center",
        textfont=dict(size=9, color="black"),
        customdata=city_df[["State","Rain Def %","Temp +°C","Water Stress"]].values,
        hovertemplate=(
            "<b>%{text}</b><br>State: %{customdata[0]}<br>"
            "Rain Deficit: %{customdata[1]:+.0f}%<br>"
            "Temp Anomaly: +%{customdata[2]:.1f}°C<br>"
            "Water Stress: %{customdata[3]}<extra></extra>"
        ),
    ))
    fig_map.update_layout(
        geo=dict(
            scope="asia",
            projection_type="mercator",
            showland=True, landcolor="rgb(240,240,235)",
            showocean=True, oceancolor="rgb(200,225,245)",
            showcountries=True, countrycolor="gray",
            center=dict(lat=22, lon=82),
            lataxis_range=[6, 37], lonaxis_range=[68, 98],
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_map, use_container_width=True, key="india_city_map")

    # Table
    st.subheader(f"All India Cities — Ranked by Risk ({len(city_df)} cities)")
    display_cols = ["City","State","Tier","Pop (M)","Rain Def %",
                    "Temp +°C","HW Days","Water Stress","Crop Risk","Risk Score"]

    def ws_style(val):
        return f"background-color:{WS_COLOUR.get(val,'#f5f5f5')};color:{'white' if val in ['Critical','Severe'] else 'black'}"

    styled = (city_df[display_cols].style
              .map(ws_style, subset=["Water Stress"])
              .background_gradient(subset=["Risk Score"], cmap="RdYlGn_r")
              .background_gradient(subset=["Rain Def %"], cmap="RdYlGn_r")
              .background_gradient(subset=["Temp +°C"], cmap="YlOrRd"))
    st.dataframe(styled, use_container_width=True, height=500, key="india_city_table")

# ═══════════════════════════════════════════════════════════════════
# WORLD CITIES TAB
# ═══════════════════════════════════════════════════════════════════
with tab_world:
    st.subheader("World City Risk Explorer")
    st.caption(f"59 major world cities covered. Impact derived from country-level ENSO teleconnection data.")

    col_ws, col_wf = st.columns([2, 2])
    with col_ws:
        all_world_cities = sorted(WORLD_CITIES.keys())
        selected_world   = st.selectbox(
            "🔍 Search or select any world city:",
            options=["— Browse all cities —"] + all_world_cities,
            key="world_city_select"
        )
    with col_wf:
        country_iso_options = ["All Countries"] + sorted(set(v["country"] for v in WORLD_CITIES.values()))
        country_names_map = {
            "AUS":"Australia","IDN":"Indonesia","PHL":"Philippines",
            "CHN":"China","USA":"United States","PER":"Peru",
            "BRA":"Brazil","KEN":"Kenya","ETH":"Ethiopia",
            "ZAF":"South Africa","ZWE":"Zimbabwe","GBR":"United Kingdom",
            "THA":"Thailand","PAK":"Pakistan","BGD":"Bangladesh","IND":"India",
        }
        country_display = ["All Countries"] + [
            f"{country_names_map.get(iso, iso)} ({iso})"
            for iso in sorted(set(v["country"] for v in WORLD_CITIES.values()))
        ]
        filter_country_disp = st.selectbox("Filter by Country:", country_display, key="world_country_filter")
        filter_country = "All Countries" if filter_country_disp == "All Countries" else filter_country_disp.split("(")[-1].rstrip(")")

    # ── Single world city card ────────────────────────────────────
    if selected_world != "— Browse all cities —":
        wdata  = WORLD_CITIES[selected_world]
        impact = derive_city_impact_world(selected_world, wdata)
        riskc  = ("#d32f2f" if impact["risk_score"] >= 60 else
                  "#f57c00" if impact["risk_score"] >= 40 else
                  "#fbc02d" if impact["risk_score"] >= 20 else "#388e3c")
        country_name = country_names_map.get(wdata["country"], wdata["country"])

        st.markdown(f"""
        <div style="background:{riskc};padding:20px 28px;border-radius:12px;margin:16px 0;color:white;">
          <h2 style="margin:0;">🌍 {selected_world}</h2>
          <p style="margin:4px 0;opacity:0.9;">{country_name} &nbsp;|&nbsp;
             Pop: {wdata['pop_m']:.1f}M</p>
          <p style="margin:8px 0 0 0;font-size:1.05rem;">
             <b>{impact['label']}</b><br>
             {impact['local_note']}
          </p>
        </div>
        """, unsafe_allow_html=True)

        wm1, wm2, wm3, wm4 = st.columns(4)
        wm1.metric("🌧️ Rainfall Signal", f"{impact['rain_def']:+.0f}%",
                   help="Positive = deficit, Negative = surplus vs normal")
        wm2.metric("🌡️ Temp Anomaly", f"{impact['temp_anom']:+.1f}°C")
        wm3.metric("🏜️ Drought Risk", f"{impact['drought_risk']:+d} / 2")
        wm4.metric("🌊 Flood Risk", f"{impact['flood_risk']:+d} / 2")
        st.markdown("---")

    # ── World cities table ────────────────────────────────────────
    world_rows = []
    for city, cdata in WORLD_CITIES.items():
        if filter_country != "All Countries" and cdata["country"] != filter_country:
            continue
        imp = derive_city_impact_world(city, cdata)
        world_rows.append({
            "City": city,
            "Country": country_names_map.get(cdata["country"], cdata["country"]),
            "Pop (M)": cdata["pop_m"],
            "ENSO Condition": imp["label"],
            "Rain Signal %": imp["rain_def"],
            "Temp +°C": imp["temp_anom"],
            "Drought Risk": imp["drought_risk"],
            "Flood Risk": imp["flood_risk"],
            "Risk Score": imp["risk_score"],
            "Local Note": imp["local_note"],
            "lat": cdata["lat"], "lon": cdata["lon"],
        })
    world_df = pd.DataFrame(world_rows).sort_values("Risk Score", ascending=False)

    # World city map
    st.subheader("World City Risk Map")
    fig_wmap = go.Figure(go.Scattergeo(
        lat=world_df["lat"], lon=world_df["lon"],
        mode="markers+text",
        marker=dict(
            size=world_df["Pop (M)"].clip(0.3, 25).apply(lambda x: x**0.5 * 5 + 6),
            color=world_df["Risk Score"],
            colorscale="RdYlGn_r",
            cmin=0, cmax=100,
            colorbar=dict(title="Risk Score", len=0.5),
            opacity=0.85,
            line=dict(color="white", width=1),
        ),
        text=world_df["City"],
        textposition="top center",
        textfont=dict(size=8),
        customdata=world_df[["Country","ENSO Condition","Rain Signal %","Temp +°C","Local Note"]].values,
        hovertemplate=(
            "<b>%{text}</b> (%{customdata[0]})<br>"
            "%{customdata[1]}<br>"
            "Rain Signal: %{customdata[2]:+.0f}%<br>"
            "Temp: %{customdata[3]:+.1f}°C<br>"
            "<i>%{customdata[4]}</i><extra></extra>"
        ),
    ))
    fig_wmap.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="rgb(240,240,235)",
            showocean=True, oceancolor="rgb(200,225,245)",
            showcountries=True, countrycolor="rgba(150,150,150,0.5)",
            showcoastlines=True,
        ),
        height=460,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_wmap, use_container_width=True, key="world_city_map")

    # Table
    st.subheader(f"All World Cities — Ranked by Risk ({len(world_df)} cities)")
    display_cols_w = ["City","Country","Pop (M)","ENSO Condition",
                      "Rain Signal %","Temp +°C","Drought Risk","Flood Risk","Risk Score","Local Note"]

    styled_w = (world_df[display_cols_w].style
                .background_gradient(subset=["Risk Score"], cmap="RdYlGn_r")
                .background_gradient(subset=["Drought Risk"], cmap="YlOrRd")
                .background_gradient(subset=["Flood Risk"], cmap="Blues"))
    st.dataframe(styled_w, use_container_width=True, height=500, key="world_city_table")

    st.info("💡 Don't see your city? Select its country from the filter — "
            "country-level ENSO teleconnection applies to all cities within it. "
            "More cities are added with each update.")
