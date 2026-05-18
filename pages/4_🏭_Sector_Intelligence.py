import sys, os

# ── Path setup: works locally AND on Streamlit Cloud ─────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ─────────────────────────────────────────────────────────────────
# pages/4_🏭_Sector_Intelligence.py  –  Audience-specific advisories
# ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data_fetch  import load_all_data
from enso_engine import get_current_state
from impacts     import sector_impact, risk_gauge_colour

st.set_page_config(page_title="Sector Intelligence", page_icon="🏭", layout="wide")

@st.cache_data(ttl=3*3600, show_spinner="Loading data…")
def get_data():
    return load_all_data()

data  = get_data()
state = get_current_state(data["nino"], data["oni"])

# ── Header ────────────────────────────────────────────────────────
st.title("🏭 Sector Intelligence — Who Needs to Act?")
st.markdown(f"""
ENSO Phase: **{state['phase']}** &nbsp;|&nbsp;
Niño 3.4: **{state['nino34_anom']:+.2f}°C** &nbsp;|&nbsp;
Select your sector below to see tailored risk analysis and action steps.
""")

st.markdown("---")

# ── Sector Tabs ───────────────────────────────────────────────────
tabs = st.tabs([
    "🌾 Agriculture",
    "💧 Water / Government",
    "⚡ Energy",
    "🏦 Banks & Insurance",
    "🌲 Forestry",
])


def render_sector(tab, sector_key: str, icon: str, title: str):
    impact = sector_impact(sector_key, state["impact_key"])
    risk   = impact.get("risk_level", 35)
    colour = risk_gauge_colour(risk)

    with tab:
        # ── Risk Gauge ─────────────────────────────────────────────
        col_gauge, col_headline = st.columns([1, 3])

        with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode  = "gauge+number",
                value = risk,
                title = {"text": "Risk Score", "font": {"size": 14}},
                number= {"suffix": "/100", "font": {"size": 24}},
                gauge = {
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar":  {"color": colour},
                    "steps": [
                        {"range": [0, 30],   "color": "#e8f5e9"},
                        {"range": [30, 55],  "color": "#fff9c4"},
                        {"range": [55, 75],  "color": "#ffe0b2"},
                        {"range": [75, 100], "color": "#ffcdd2"},
                    ],
                    "threshold": {
                        "line": {"color": "#333", "width": 3},
                        "thickness": 0.8, "value": risk,
                    },
                },
            ))
            fig_gauge.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10),
                                    paper_bgcolor="white")
            st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{sector_key}")

        with col_headline:
            hl_bg = "#ffcdd2" if risk >= 70 else "#ffe0b2" if risk >= 45 else "#fff9c4" if risk >= 25 else "#e8f5e9"
            st.markdown(f"""
            <div style="background:{hl_bg};padding:20px 24px;border-radius:10px;height:180px;display:flex;align-items:center;">
              <div>
                <h3 style="margin:0 0 8px 0;">{icon} {title}</h3>
                <p style="margin:0;font-size:1.1rem;">{impact.get('headline','')}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── KPIs ───────────────────────────────────────────────────
        kpis = impact.get("kpis", {})
        if kpis:
            st.subheader("📊 Key Indicators")
            kpi_cols = st.columns(min(len(kpis), 4))
            for idx, (kpi_name, kpi_val) in enumerate(kpis.items()):
                with kpi_cols[idx % 4]:
                    st.metric(kpi_name, kpi_val)
            st.markdown("---")

        # ── Action Steps ───────────────────────────────────────────
        actions = impact.get("actions", [])
        if actions:
            st.subheader("✅ Recommended Actions — Right Now")
            for i, action in enumerate(actions, 1):
                urgency = "🔴" if risk >= 70 else "🟠" if risk >= 45 else "🟡"
                st.markdown(f"{urgency} **{i}.** {action}")

        st.markdown("---")

        # ── Sector-specific deep content ───────────────────────────
        _sector_deep_content(sector_key, state, tab)


def _sector_deep_content(sector: str, state: dict, tab):
    """Render sector-specific deeper content below actions."""

    if sector == "agriculture":
        st.subheader("🗓️ Season Planning Calendar")
        col_kh, col_rb = st.columns(2)
        with col_kh:
            st.markdown("**Kharif Season (Jun–Oct)**")
            if state["is_elnino"]:
                st.markdown("""
| Month | Advisory |
|---|---|
| May | Pre-purchase drought-tolerant seeds. Micro-irrigation inspection. |
| June | Delay transplanting 10–14 days if onset delayed. |
| July | Watch soil moisture weekly. Activate contingency crops if < 50% LPA |
| August | Foliar spray against pest surge (El Niño → less rain → pest pressure) |
| October | Rabi planning: carry-over soil moisture likely below normal |
                """)
            else:
                st.markdown("""
| Month | Advisory |
|---|---|
| May | Standard sowing preparation. Good season expected. |
| June | Proceed with normal sowing schedule. |
| July–Sep | Monitor for waterlogging in low-lying areas. |
| October | Good Rabi prospects — adequate soil moisture. |
                """)

        with col_rb:
            st.markdown("**Crop Diversification Recommendation**")
            crops = {
                "Bajra (Pearl Millet)": 95,
                "Sorghum (Jowar)": 90,
                "Pulses (Tur/Moong)": 85,
                "Cotton": 55,
                "Maize": 60,
                "Kharif Rice": 30 if state["is_elnino"] else 80,
                "Sugarcane": 20 if state["is_elnino"] else 75,
            }
            colour_fn = lambda v: "#388e3c" if v >= 75 else "#f57c00" if v >= 50 else "#d32f2f"
            fig_crops = go.Figure(go.Bar(
                x=list(crops.values()), y=list(crops.keys()),
                orientation="h",
                marker_color=[colour_fn(v) for v in crops.values()],
                text=[f"{v}%" for v in crops.values()], textposition="outside",
            ))
            fig_crops.update_layout(
                height=280, plot_bgcolor="white", paper_bgcolor="white",
                xaxis_title="Suitability Score (El Niño Year)",
                margin=dict(l=10, r=60, t=10, b=10),
            )
            st.plotly_chart(fig_crops, use_container_width=True, key=f"crops_{sector}")

    elif sector == "water":
        st.subheader("💧 Reservoir Stress Projection")
        if state["is_elnino"]:
            months  = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
            normal  = [45, 65, 85, 92, 88, 75]
            elnino  = [30, 48, 62, 68, 58, 45]
            fig_res = go.Figure()
            fig_res.add_trace(go.Scatter(x=months, y=normal, mode="lines+markers",
                                         name="Normal Year", line=dict(color="#1565c0")))
            fig_res.add_trace(go.Scatter(x=months, y=elnino, mode="lines+markers",
                                         name="El Niño Year", line=dict(color="#d32f2f", dash="dash")))
            fig_res.add_hline(y=40, line_dash="dot", line_color="#d32f2f",
                              annotation_text="Critical threshold (40%)")
            fig_res.update_layout(
                height=300, plot_bgcolor="white", paper_bgcolor="white",
                yaxis_title="Reservoir Filling (%)", yaxis=dict(range=[0, 100]),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_res, use_container_width=True, key=f"reservoir_{sector}")
            st.caption("Indicative projection based on median El Niño analog years. Actual levels depend on catchment rainfall.")
        else:
            st.success("✅ Above-normal reservoir filling expected. Maintain flood-control protocols for major reservoirs.")

    elif sector == "energy":
        st.subheader("⚡ Generation Risk Matrix")
        sources = ["Hydro", "Solar", "Wind", "Thermal (Coal)", "Gas"]
        if state["is_elnino"]:
            impacts = [-30, +5, -5, +25, +15]   # % change from normal
            colours = ["#d32f2f", "#66bb6a", "#fbc02d", "#f57c00", "#f57c00"]
        elif state["is_lanina"]:
            impacts = [+20, -5, +5, -15, -10]
            colours = ["#66bb6a", "#fbc02d", "#66bb6a", "#1565c0", "#1565c0"]
        else:
            impacts = [0, 0, 0, 0, 0]
            colours = ["#616161"] * 5

        fig_en = go.Figure(go.Bar(
            x=sources, y=impacts,
            marker_color=colours,
            text=[f"{v:+d}%" for v in impacts], textposition="outside",
        ))
        fig_en.add_hline(y=0, line_color="black", line_width=1)
        fig_en.update_layout(
            height=280, plot_bgcolor="white", paper_bgcolor="white",
            yaxis_title="Deviation from Normal (%)",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_en, use_container_width=True, key=f"energy_{sector}")
        st.caption("Positive = above normal generation / demand. Negative = below normal.")

    elif sector == "banking":
        st.subheader("🏦 Portfolio Risk Exposure")

        st.markdown("**Agricultural Loan Book — District Risk Classification**")
        risk_buckets = {
            "🔴 High Risk Districts (deficit > 20%)": 28 if state["is_elnino"] else 5,
            "🟠 Elevated Risk (deficit 12–20%)":      35 if state["is_elnino"] else 12,
            "🟡 Moderate Risk (deficit 5–12%)":       22 if state["is_elnino"] else 25,
            "🟢 Low Risk (deficit < 5%)":             15 if state["is_elnino"] else 58,
        }
        colours_b = ["#d32f2f", "#f57c00", "#fbc02d", "#388e3c"]
        fig_pie = go.Figure(go.Pie(
            labels=list(risk_buckets.keys()),
            values=list(risk_buckets.values()),
            marker_colors=colours_b,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}% of districts<extra></extra>",
        ))
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="white", showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{sector}")

        st.markdown("**Commodity Price Risk (Historical El Niño Pattern)**")
        commodities = pd.DataFrame({
            "Commodity": ["Rice", "Wheat", "Pulses", "Edible Oils", "Sugar", "Cotton", "Maize"],
            "Price Pressure": ["+12–18%", "+5–10%", "+18–25%", "+10–15%", "+15–20%", "+8–14%", "+10–16%"],
            "Timeline": ["Sep–Dec", "Dec–Mar", "Sep–Feb", "Oct–Mar", "Oct–Jan", "Nov–Feb", "Sep–Nov"],
            "Risk Level": ["High", "Medium", "Very High", "High", "High", "Medium", "High"],
        })
        st.dataframe(commodities, use_container_width=True, hide_index=True)

    elif sector == "forestry":
        st.subheader("🔥 Forest Fire Risk Calendar")
        if state["is_elnino"]:
            months   = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            risk_val = [20, 30, 45, 55, 70, 85, 90, 75, 35]
            rcolours = ["#388e3c" if v < 40 else "#f57c00" if v < 65 else "#d32f2f" for v in risk_val]
        else:
            months   = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            risk_val = [10, 15, 25, 30, 40, 55, 60, 45, 20]
            rcolours = ["#388e3c"] * 4 + ["#fbc02d"] * 2 + ["#f57c00"] * 2 + ["#388e3c"]

        fig_fire = go.Figure(go.Bar(x=months, y=risk_val, marker_color=rcolours,
                                    text=[f"{v}%" for v in risk_val], textposition="outside"))
        fig_fire.add_hline(y=60, line_dash="dot", line_color="#d32f2f",
                           annotation_text="High-alert threshold")
        fig_fire.update_layout(
            height=260, plot_bgcolor="white", paper_bgcolor="white",
            yaxis_title="Forest Fire Risk Index (0–100)",
            yaxis=dict(range=[0, 100]),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_fire, use_container_width=True, key=f"fire_{sector}")

        st.markdown("""
**Pre-positioning checklist for Forest Departments:**
- [ ] FIRMS/MODIS hotspot monitoring activated (free: [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov))
- [ ] Fire watchtowers staffed in dry deciduous zones from February
- [ ] Community fire prevention brigades briefed
- [ ] Water tanker deployment plan ready for Madhya Pradesh, Chhattisgarh, Odisha
- [ ] Firebreak maintenance completed before dry season
        """)


# ── Render all sector tabs ────────────────────────────────────────
render_sector(tabs[0], "agriculture", "🌾", "Agriculture & Farming")
render_sector(tabs[1], "water",       "💧", "Water Resources & Government")
render_sector(tabs[2], "energy",      "⚡", "Power & Energy")
render_sector(tabs[3], "banking",     "🏦", "Banking & Insurance")
render_sector(tabs[4], "forestry",    "🌲", "Forestry & Wildlife")

# ── Footer cross-sector note ──────────────────────────────────────
st.markdown("---")
st.info("""
**ℹ️ Cross-Sector Cascade Note**

ENSO impacts are not isolated. A single El Niño event creates a cascade:

Monsoon Deficit → Reservoir Below 40% → Hydropower Falls → Grid Stress → Industry Slowdown
→ Rural Income Falls → Agri NPA Rise → Bank Stress → Rural Demand Contraction → Food Inflation

Early coordinated action across sectors reduces cascade severity significantly.
""")
