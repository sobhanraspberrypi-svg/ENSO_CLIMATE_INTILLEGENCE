# 🌊 ENSO Climate Intelligence Dashboard

> **First open-source end-to-end pipeline: ENSO monitoring → Global teleconnection analysis → India district-level agricultural, water, and energy risk — with ML forecasting and audience-specific decision intelligence.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: NOAA](https://img.shields.io/badge/Data-NOAA%20CPC-blue)](https://www.cpc.ncep.noaa.gov)

---

## 🎯 What This Is

El Niño–Southern Oscillation (ENSO) is the most powerful year-to-year climate driver on Earth. It disrupts monsoons, triggers droughts, floods, wildfires, and heatwaves — affecting agriculture, water, energy, and economies globally.

**The problem:** Existing dashboards (NOAA, WMO, IRI) are scientifically excellent but:
- Stop at "El Niño probability = X%" — no actionable local intelligence
- Built for scientists, not for farmers, water managers, or banks
- No open-source India-specific agricultural/water risk layer
- No physics-aware EP vs CP El Niño distinction for India impact

**This project fills that gap.**

---

## 🖥️ Dashboard Pages

| Page | What It Shows |
|---|---|
| 🏠 **Home** | Live ENSO status banner, ONI time series, teleconnection snapshot (IOD, PDO, NAO) |
| 🌍 **Global Monitor** | Interactive 3D globe — drought/flood risk by country, EP vs CP El Niño explained |
| 🇮🇳 **India Impact** | State-level monsoon deficit map, crop risk, reservoir stress, historical analog table |
| 📈 **Forecast** | 9-month ML forecast with 90% confidence intervals, Spring Predictability Barrier chart |
| 🏭 **Sector Intelligence** | Audience-specific risk cards: Farmers, Government, Energy, Banks, Forestry |

---

## 🧠 Science Implemented

### ENSO Detection
- **Niño 1+2, 3, 3.4, 4** SST anomaly indices from NOAA ERSSTv5
- **Oceanic Niño Index (ONI)** — 3-month rolling mean classification
- **Southern Oscillation Index (SOI)** — Tahiti–Darwin pressure difference
- **EP vs CP El Niño classification** using El Niño Modoki Index (EMI)

### Teleconnections
- **IOD (Indian Ocean Dipole)** — modifies India monsoon impact (critical: 2019 case)
- **PDO (Pacific Decadal Oscillation)** — decadal modulation, flagged not forecasted
- **NAO (North Atlantic Oscillation)** — Europe signal

### Forecasting
- Gradient Boosting ensemble (20 bootstrap models) on 12-month lag features
- Seasonal encoding (sin/cos) to capture annual cycle
- Bootstrap uncertainty quantification → 90% confidence interval
- **Spring Predictability Barrier (SPB)** visualised with skill degradation by initialization month

### Impact Modeling
- Teleconnection impact map for 16 countries across 6 regions
- India state-level monsoon deficit estimation (scaled by ENSO anomaly intensity)
- Sector risk scoring: agriculture, water, energy, banking, forestry
- Historical El Niño analog table for India (1982–2023)

---

## 📦 Tech Stack

| Component | Technology | Why |
|---|---|---|
| Dashboard | Streamlit | Fast, free hosting, Python-native |
| Visualisation | Plotly | Interactive 3D globe, charts |
| Data | NOAA CPC public APIs | 100% free, no API key |
| ML Model | Scikit-learn GBM | CPU-only, no GPU needed |
| Data processing | Pandas + NumPy | Standard |

**Platform requirements:**
- ✅ **GitHub** — code hosting
- ✅ **Streamlit Community Cloud** — free dashboard hosting (connect your repo)
- ❌ **Hugging Face** — not needed for v1 (add later for model weights if desired)
- ❌ **Google Earth Engine** — not needed (we use pre-gridded NOAA data)
- ❌ **Paid compute** — runs entirely on free tier

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/yourusername/enso-climate-intelligence.git
cd enso-climate-intelligence

# Install (no GPU required)
pip install -r requirements.txt

# Run
streamlit run app.py
```

Data downloads automatically from NOAA on first run and caches locally for 3 days.

---

## 📁 Project Structure

```
enso-climate-intelligence/
│
├── app.py                          # Home page
├── requirements.txt
├── config.py                       # All constants, thresholds, impact maps
│
├── src/
│   ├── data_fetch.py               # NOAA data download + caching
│   ├── enso_engine.py              # ENSO classification, EP/CP, teleconnections
│   ├── forecast.py                 # ML forecast model + SPB
│   └── impacts.py                  # Regional & sector risk scoring
│
├── pages/
│   ├── 1_🌍_Global_Monitor.py
│   ├── 2_🇮🇳_India_Impact.py
│   ├── 3_📈_Forecast.py
│   └── 4_🏭_Sector_Intelligence.py
│
└── data/cache/                     # Auto-populated on first run
```

---

## 🗺️ Data Sources (All Free)

| Dataset | Source | Used For |
|---|---|---|
| ONI | NOAA CPC | Primary ENSO classification |
| Niño indices (1+2, 3, 3.4, 4) | NOAA CPC ERSSTv5 | EP vs CP classification |
| SOI | NOAA CPC | Atmospheric ENSO confirmation |
| PDO | NOAA NCEI | Decadal modulation flag |
| NAO | NOAA CPC | Europe teleconnection |

---

## 🔭 Roadmap

**Phase 2 — Enhanced ML:**
- [ ] CNN-LSTM on full ERA5 spatial fields (needs Colab GPU for training)
- [ ] SHAP feature importance (XAI layer)
- [ ] Real DMI download from JAMSTEC/NOAA PSL

**Phase 3 — India Geospatial:**
- [ ] District-level choropleth using actual IMD gridded rainfall
- [ ] Reservoir storage integration (India-WRIS API)
- [ ] MODIS NDVI crop stress overlay (via GEE or pre-downloaded)

**Phase 4 — Sector APIs:**
- [ ] REST API for programmatic sector risk access
- [ ] Email/webhook alerts when ENSO phase changes

---

## 🧑‍🔬 Target Audiences

| Who | What They Get |
|---|---|
| 🌾 **Farmers & Agri-business** | Crop suitability scores, sowing calendar advisories, drought-resilient alternatives |
| 💧 **Water / Irrigation Boards** | Reservoir fill projections, groundwater recharge outlook, conservation orders timing |
| ⚡ **Energy Utilities** | Hydro generation risk, cooling demand forecast, thermal backup planning |
| 🏦 **Banks & Insurers** | Agricultural NPA risk by district, commodity price pressure, PMFBY uptake signal |
| 🌲 **Forest Departments** | Fire risk calendar, pre-positioning checklist, FIRMS hotspot guidance |
| 🏛️ **Government / Policy** | State-level risk matrix, cross-sector cascade analysis, early warning triggers |

---

## 🤝 Contributing

Pull requests welcome. Priority areas:
- Add more countries to `GLOBAL_IMPACTS` in `config.py`
- Improve India district-level data with shapefile + IMD integration
- Add SHAP explainability to the forecast model
- Translate sector advisories for regional languages

---

## 📄 License

MIT License — use freely, cite the project.

---

## 🙏 Acknowledgements

- NOAA Climate Prediction Center for publicly accessible climate indices
- IRI Columbia for ENSO science education resources
- IITM Pune for India monsoon research
