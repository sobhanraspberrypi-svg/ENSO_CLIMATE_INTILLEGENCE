import sys, os

# ── Path setup: works locally AND on Streamlit Cloud ─────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in [_ROOT, os.path.join(_ROOT, "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ─────────────────────────────────────────────────────────────────
# app.py  –  ENSO Climate Intelligence Dashboard  (Home Page)
# ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from data_fetch  import load_all_data
from enso_engine import get_current_state, compute_oni_rolling, historical_enso_events, pdo_phase, iod_state

st.set_page_config(
    page_title="ENSO Climate Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24701-nature-natural-beauty.jpg/320px-24701-nature-natural-beauty.jpg", use_container_width=True)
    st.title("🌊 ENSO Intelligence")
    st.markdown("""
**What is ENSO?**
El Niño–Southern Oscillation (ENSO) is a coupled ocean-atmosphere cycle in the tropical Pacific
that disrupts rainfall, temperature, and extreme events **worldwide**.

**Who uses this?**
- 🌾 Farmers & Agri-businesses
- 💧 Water / Irrigation Boards
- ⚡ Power & Energy utilities
- 🏦 Banks & Insurers
- 🌲 Forestry Departments
- 🏛️ Government planners

---
**Data Sources (all free)**
- NOAA CPC ONI / Niño indices
- NOAA OISST / ERSSTv5
- NOAA CPC SOI
- NOAA NCEI PDO
- NOAA CPC NAO
    """)
    st.markdown("---")
    st.caption("Data refreshed every 3 days from NOAA public servers.")

# ── Load data ─────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner="Fetching latest NOAA climate data…")
def get_data():
    return load_all_data()

data = get_data()
# ── Auto-fix stale cache: if data is pre-2025, clear memory and refetch ──────
# NEW — only tries once per session, stops the loop
data = get_data()
if pd.Timestamp(data["nino"]["date"].max()).year < 2025:
    if not st.session_state.get("_cache_cleared"):
        st.session_state["_cache_cleared"] = True
        st.cache_data.clear()
        st.rerun()
state  = get_current_state(data["nino"], data["oni"])
iod    = iod_state(data["iod"])
pdo_s  = pdo_phase(data["pdo"])

# ── Hero Status Banner ────────────────────────────────────────────
st.markdown(f"""
<div style="background:{state['colour']};padding:24px 32px;border-radius:12px;margin-bottom:16px;">
  <h1 style="color:white;margin:0;font-size:2.2rem;">🌊 {state['phase']}</h1>
  <p style="color:rgba(255,255,255,0.9);margin:8px 0 0 0;font-size:1.1rem;">
    Niño 3.4 Anomaly: <b>{state['nino34_anom']:+.2f}°C</b> &nbsp;|&nbsp;
    Updated: <b>{state['date'].strftime('%B %Y')}</b> &nbsp;|&nbsp;
    Type: <b>{state['ep_cp'] if state['ep_cp'] != 'N/A' else 'Not applicable'}</b>
  </p>
</div>
""", unsafe_allow_html=True)

# ── Four KPI Cards ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_colour = "normal" if abs(state['nino34_anom']) < 0.5 else ("inverse" if state['nino34_anom'] > 0 else "normal")
    st.metric("🌡️ Niño 3.4 Anomaly", f"{state['nino34_anom']:+.2f}°C",
              help="Sea surface temperature deviation from 30-year average in Niño 3.4 region (170°W–120°W, 5°N–5°S).")

with c2:
    nao_val = data["nao"].sort_values("date").iloc[-1]["nao"] if len(data["nao"]) else 0.0
    st.metric("🌬️ SOI (Latest)",
              f"{data['soi'].sort_values('date').iloc[-1]['soi']:+.1f}" if len(data["soi"]) else "N/A",
              help="Southern Oscillation Index: Tahiti minus Darwin pressure. Negative = El Niño tendency.")

with c3:
    st.metric("🌊 IOD Phase", iod["phase"],
              help="Indian Ocean Dipole. Modifies ENSO impact on India monsoon.")

with c4:
    spb = state["spb_skill"]
    spb_label = "⚠️ SPB Season" if spb < 0.55 else "Normal"
    st.metric("📊 Forecast Skill", f"{spb:.0%}", delta=spb_label,
              help="Model prediction skill for current initialization month. Low in Mar–May (Spring Predictability Barrier).")

st.markdown("---")

# ── ONI Time Series ───────────────────────────────────────────────
st.subheader("📈 ENSO History — Oceanic Niño Index (1990–Present)")
st.caption("The ONI is the primary metric used to classify El Niño and La Niña events. "
           "Values above +0.5°C = El Niño, below −0.5°C = La Niña.")

oni_plot = compute_oni_rolling(data["oni"]).sort_values("date")
oni_plot = oni_plot[oni_plot["date"] >= "1990-01-01"]

fig_oni = go.Figure()

# Shaded bands
fig_oni.add_hrect(y0=0.5,  y1=4,  fillcolor="rgba(211,47,47,0.15)",  line_width=0)
fig_oni.add_hrect(y0=-4,   y1=-0.5, fillcolor="rgba(13,71,161,0.15)",line_width=0)

# ONI line
fig_oni.add_trace(go.Scatter(
    x=oni_plot["date"], y=oni_plot["oni_rolling"],
    mode="lines", name="ONI (3-month mean)",
    line=dict(color="#1565c0", width=2),
    fill="tozeroy",
    fillcolor="rgba(21,101,192,0.1)",
))

# Threshold lines
for val, col, label in [(0.5, "#d32f2f", "El Niño threshold"),
                         (-0.5, "#1565c0", "La Niña threshold")]:
    fig_oni.add_hline(y=val, line_dash="dash", line_color=col,
                      annotation_text=label, annotation_position="top right")

fig_oni.update_layout(
    height=320, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", paper_bgcolor="white",
    xaxis_title="", yaxis_title="Anomaly (°C)",
    legend=dict(orientation="h"),
    hovermode="x unified",
)
st.plotly_chart(fig_oni, use_container_width=True)

# ── Teleconnection Snapshot ───────────────────────────────────────
st.markdown("---")
st.subheader("🔗 Key Teleconnections — Modifying Signals Right Now")
st.caption("Teleconnections are climate links between remote ocean areas and regional weather. "
           "They can amplify or reduce El Niño's impact.")

tc1, tc2, tc3 = st.columns(3)

with tc1:
    st.markdown(f"""
    <div style="background:{iod['colour']};padding:16px;border-radius:8px;color:white;">
    <b>🌊 Indian Ocean Dipole (IOD)</b><br>
    Phase: <b>{iod['phase']}</b> ({iod['value']:+.2f})<br><br>
    {iod['effect']}
    </div>
    """, unsafe_allow_html=True)

with tc2:
    pdo_colour = "#f57c00" if "Warm" in pdo_s else "#1565c0" if "Cool" in pdo_s else "#616161"
    st.markdown(f"""
    <div style="background:{pdo_colour};padding:16px;border-radius:8px;color:white;">
    <b>🌀 Pacific Decadal Oscillation (PDO)</b><br><br>
    {pdo_s}<br><br>
    <small>Decadal background signal — cannot be predicted, only monitored.</small>
    </div>
    """, unsafe_allow_html=True)

with tc3:
    nao_recent = data["nao"].sort_values("date").tail(3)["nao"].mean() if len(data["nao"]) else 0
    nao_phase  = "Positive NAO" if nao_recent > 0.5 else "Negative NAO" if nao_recent < -0.5 else "Neutral NAO"
    nao_effect = ("Milder, wetter winters in Europe. Storm tracks shift north."
                  if nao_recent > 0.5 else
                  "Colder, drier conditions in Europe. Blocked circulation." if nao_recent < -0.5
                  else "Minimal NAO modulation on European winter climate.")
    nao_col = "#388e3c" if nao_recent > 0.5 else "#5c6bc0"
    st.markdown(f"""
    <div style="background:{nao_col};padding:16px;border-radius:8px;color:white;">
    <b>🌬️ North Atlantic Oscillation (NAO)</b><br>
    Phase: <b>{nao_phase}</b> ({nao_recent:+.2f})<br><br>
    {nao_effect}
    </div>
    """, unsafe_allow_html=True)

# ── IOD Explainer ─────────────────────────────────────────────────
with st.expander("ℹ️ Why do teleconnections matter? (click to expand)"):
    st.markdown("""
**El Niño is not the only player.** Several other ocean-atmosphere patterns modify its impact:

| Signal | What it is | Key impact on India |
|---|---|---|
| **IOD (Indian Ocean Dipole)** | West vs East Indian Ocean SST difference | Positive IOD can SAVE monsoon during El Niño years (e.g., 2019) |
| **PDO (Pacific Decadal Oscillation)** | Decadal North Pacific SST pattern | Warm PDO amplifies El Niño; Cool PDO suppresses it |
| **NAO (North Atlantic Oscillation)** | Pressure difference, Azores–Iceland | Affects Europe/Mediterranean, weak India signal |
| **AMO (Atlantic Multidecadal Oscillation)** | Multi-decadal Atlantic SST | Modulates global monsoon on 60-80 year cycles |

**Practical takeaway:** A strong El Niño + Positive IOD = potentially a near-normal India monsoon.
A moderate El Niño + Negative IOD = worse drought than the ONI alone would suggest.
    """)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🌊 ENSO Climate Intelligence | Open Source | Data: NOAA CPC | "
           "[GitHub](https://github.com/your-repo/enso-climate-intelligence)")

# ── Walker Circulation Mechanism Diagram ─────────────────────────
st.markdown("---")
st.subheader("⚙️ How El Niño Works — Walker Circulation")
st.caption("The mechanism that connects Pacific Ocean warming to Indian monsoon failure.")

mode = st.radio("Show:", ["Normal Year", "El Niño Year"], horizontal=True, key="walker_mode")

def walker_diagram(elnino: bool):
    fig = go.Figure()
    bg  = "#0a1628" if elnino else "#0d2137"
    fig.update_layout(
        width=900, height=400,
        plot_bgcolor=bg, paper_bgcolor=bg,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(range=[0,10], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0,5],  showgrid=False, zeroline=False, visible=False),
    )

    # Ocean surface
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=1.2,
                  fillcolor="#1565c0", line_width=0, opacity=0.7)

    # Land masses
    for x0,x1,label in [(0,1.2,"India / S. Asia"),(8.5,10,"S. America")]:
        fig.add_shape(type="rect", x0=x0, y0=1.2, x1=x1, y1=2.0,
                      fillcolor="#5d4037", line_color="#8d6e63", line_width=1)
        fig.add_annotation(x=(x0+x1)/2, y=1.6, text=label,
                           font=dict(color="white", size=11), showarrow=False)

    # Warm pool
    warm_x0 = 5.0 if elnino else 1.0
    warm_x1 = warm_x0 + 3.5
    warm_label = "Warm Pool\n(Central Pacific)" if elnino else "Warm Pool\n(Western Pacific)"
    fig.add_shape(type="rect", x0=warm_x0, y0=0, x1=warm_x1, y1=1.2,
                  fillcolor="#e53935", line_width=0, opacity=0.6)
    fig.add_annotation(x=(warm_x0+warm_x1)/2, y=0.6, text=warm_label,
                       font=dict(color="white", size=10, family="Arial"),
                       showarrow=False, align="center")

    # Cold upwelling
    cu_x = 0.5 if not elnino else 9.5
    fig.add_annotation(x=cu_x, y=0.5, text="Cold Water\nUpwelling",
                       font=dict(color="#90caf9", size=9), showarrow=False)

    # Trade wind arrows
    if elnino:
        # Weakened — fewer, shorter arrows going right
        for xi in [2.5, 4.5, 6.5]:
            fig.add_annotation(x=xi, y=1.5, ax=xi-0.8, ay=1.5,
                               arrowhead=2, arrowsize=1.2, arrowwidth=2,
                               arrowcolor="#ffeb3b", showarrow=True)
        fig.add_annotation(x=5.0, y=1.9, text="⚠️ Trade winds WEAKENED",
                           font=dict(color="#ffeb3b", size=12, family="Arial Bold"),
                           showarrow=False)
    else:
        # Strong — arrows going left (west)
        for xi in [3.0, 5.0, 7.0]:
            fig.add_annotation(x=xi, y=1.5, ax=xi+0.8, ay=1.5,
                               arrowhead=2, arrowsize=1.2, arrowwidth=2,
                               arrowcolor="#4fc3f7", showarrow=True)
        fig.add_annotation(x=5.0, y=1.9, text="Strong Trade Winds →  West",
                           font=dict(color="#4fc3f7", size=12), showarrow=False)

    # Convection / Walker Cell
    if not elnino:
        # Rising air over warm pool (west)
        fig.add_shape(type="line", x0=2.0, y0=2.0, x1=2.0, y1=4.2,
                      line=dict(color="#ef5350", width=2, dash="dot"))
        fig.add_annotation(x=2.0, y=4.4, text="🔴 Rising Warm Air\n(Monsoon Driver)",
                           font=dict(color="#ef5350", size=10), showarrow=False)
        # Descending over east / India
        fig.add_shape(type="line", x0=8.5, y0=2.0, x1=8.5, y1=4.0,
                      line=dict(color="#90caf9", width=2, dash="dot"))
        fig.add_annotation(x=8.5, y=4.2, text="🔵 Sinking Air\n(S. America dry)",
                           font=dict(color="#90caf9", size=10), showarrow=False)
        # Circulation arc at top
        fig.add_shape(type="path",
                      path="M 2,4.0 Q 5,4.8 8.5,4.0",
                      line=dict(color="white", width=1.5, dash="dot"))
        # India monsoon label
        fig.add_annotation(x=0.6, y=3.0, text="✅ India\nMonsoon\nNormal",
                           font=dict(color="#66bb6a", size=11, family="Arial Bold"),
                           showarrow=False, bgcolor="rgba(0,0,0,0.4)", borderpad=4)
    else:
        # Rising over central/east Pacific
        fig.add_shape(type="line", x0=6.5, y0=2.0, x1=6.5, y1=4.2,
                      line=dict(color="#ef5350", width=2, dash="dot"))
        fig.add_annotation(x=6.5, y=4.4, text="🔴 Rising Air\nShifts East",
                           font=dict(color="#ef5350", size=10), showarrow=False)
        # Subsidence over India
        fig.add_shape(type="line", x0=0.6, y0=2.0, x1=0.6, y1=4.0,
                      line=dict(color="#90caf9", width=2, dash="dot"))
        fig.add_annotation(x=0.6, y=4.2, text="🔵 Sinking Air\nOver India",
                           font=dict(color="#90caf9", size=10), showarrow=False)
        # Arc at top (reversed cell)
        fig.add_shape(type="path",
                      path="M 6.5,4.0 Q 3.5,4.8 0.6,4.0",
                      line=dict(color="white", width=1.5, dash="dot"))
        # India impact label
        fig.add_annotation(x=0.6, y=3.0, text="❌ India Monsoon\nSuppressed\n−10 to −25%",
                           font=dict(color="#ef5350", size=11, family="Arial Bold"),
                           showarrow=False, bgcolor="rgba(0,0,0,0.5)", borderpad=4)
        # Peru label
        fig.add_annotation(x=9.2, y=2.5, text="⛈️ Peru\nFlooding",
                           font=dict(color="#ffeb3b", size=10), showarrow=False)

    # Labels
    fig.add_annotation(x=0.5, y=0.15, text="Indian Ocean", font=dict(color="#90caf9",size=9), showarrow=False)
    fig.add_annotation(x=5.0, y=0.15, text="Pacific Ocean", font=dict(color="#90caf9",size=9), showarrow=False)
    title_text = "🔴 EL NIÑO YEAR — Walker Circulation Weakens" if elnino else "🔵 NORMAL YEAR — Walker Circulation Active"
    fig.add_annotation(x=5, y=4.85, text=title_text,
                       font=dict(color="white", size=14, family="Arial Bold"),
                       showarrow=False)
    return fig

st.plotly_chart(walker_diagram(mode == "El Niño Year"),
                use_container_width=True, key="walker_diagram")
st.caption("Toggle between Normal and El Niño year to see how the Walker Circulation shifts "
           "and why India's monsoon weakens.")
