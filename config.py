# ── J&K Boundary Policy (India Official) ────────────────────────────────────
# All maps in this dashboard use India's claimed boundary for J&K,
# including Aksai Chin and Pakistan-administered Kashmir, per Survey of India.
# Ladakh UT (2019) is merged into J&K polygon. See download_geodata.py.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# config.py  –  Central configuration for ENSO Climate Intelligence
# ─────────────────────────────────────────────────────────────────

# ── NOAA Data URLs (all free, no API key needed) ─────────────────
URLS = {
    "oni":          "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    "nino_monthly": "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii",
    "soi":          "https://www.cpc.ncep.noaa.gov/data/indices/soi",
    "pdo":          "https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/pdo.timeseries.ersstv5.csv",
    "nao":          "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii.table",
}

CACHE_DIR   = "data/cache"
CACHE_DAYS  = 3           # Refresh data every 3 days

# ── ENSO Classification Thresholds ───────────────────────────────
ENSO_THRESHOLDS = {
    "el_nino_strong":   1.5,
    "el_nino_moderate": 1.0,
    "el_nino_weak":     0.5,
    "neutral_low":     -0.5,
    "la_nina_weak":    -0.5,
    "la_nina_moderate":-1.0,
    "la_nina_strong":  -1.5,
}

# El Niño Modoki Index: EMI = Nino4_anom - 0.5*Nino3_anom - 0.5*Nino12_anom
# If EMI > 0.7 and Nino34 > 0.5  → Central Pacific (Modoki) El Niño
# If EMI < 0.3 and Nino34 > 0.5  → Eastern Pacific (Classic) El Niño
EMI_THRESHOLD = 0.5

# ── Global Teleconnection Impact Map ─────────────────────────────
# Structure: country_iso3 → {el_nino: {rain, temp, drought, flood}, la_nina: {...}}
# Scores: -2 (severe negative), -1 (moderate negative), 0 (neutral), +1 (beneficial), +2 (very beneficial)
# rain: rainfall change  | temp: temperature anomaly | drought/flood: risk score

GLOBAL_IMPACTS = {
    # ── South Asia ──────────────────────────────────────────────
    "IND": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -1,
                     "label": "Weak / Deficient Monsoon",
                     "detail": "Indian Summer Monsoon weakens by 10–30%. Reservoirs deplete faster. Kharif crop stress. Heat waves intensify in March–May."},
        "la_nina":  {"rain": +2, "temp": -1, "drought": -2, "flood": +2,
                     "label": "Above-Normal Monsoon / Flood Risk",
                     "detail": "Enhanced monsoon. Flood risk in Indo-Gangetic plain. Good soil moisture for Rabi crops."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0,
                     "label": "Near-Normal Conditions",
                     "detail": "ENSO influence is minimal. Other factors (IOD, MJO) dominate."},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": 0,
                     "label": "Weak Monsoon Suppression",
                     "detail": "Central Pacific El Niño has weaker India teleconnection. Partial monsoon deficit likely."},
    },
    "PAK": {
        "el_nino":  {"rain": -1, "temp": +2, "drought": +2, "flood": -1, "label": "Drought Risk, Heat Amplified", "detail": "Reduced winter rainfall, intensified heat."},
        "la_nina":  {"rain": +1, "temp": 0,  "drought": -1, "flood": +2, "label": "Flood Risk in Indus Basin", "detail": "Enhanced monsoon inflow increases Indus flood risk."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": 0, "label": "Mild Drought Risk", "detail": ""},
    },
    "BGD": {
        "el_nino":  {"rain": -1, "temp": +1, "drought": +1, "flood": -1, "label": "Reduced Monsoon", "detail": ""},
        "la_nina":  {"rain": +2, "temp": 0,  "drought": -1, "flood": +2, "label": "Severe Flood Risk", "detail": "Brahmaputra / Ganges overflow risk."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": 0, "drought": 0, "flood": 0, "label": "Mild Reduction", "detail": ""},
    },
    # ── Southeast Asia ──────────────────────────────────────────
    "IDN": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -2, "label": "Severe Drought / Wildfire Risk", "detail": "Borneo and Sumatra peat fires. Palm oil, rice, cocoa severely impacted."},
        "la_nina":  {"rain": +2, "temp": 0,  "drought": -2, "flood": +1, "label": "Enhanced Rainfall", "detail": "Good conditions for agriculture."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": -1, "label": "Moderate Drought", "detail": ""},
    },
    "PHL": {
        "el_nino":  {"rain": -2, "temp": +1, "drought": +2, "flood": -1, "label": "Drought, Rice Crop Stress", "detail": ""},
        "la_nina":  {"rain": +1, "temp": 0,  "drought": -1, "flood": +2, "label": "Typhoon Enhancement", "detail": "La Niña increases typhoon frequency."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": 0, "drought": +1, "flood": 0, "label": "Moderate Impact", "detail": ""},
    },
    "THA": {
        "el_nino":  {"rain": -1, "temp": +1, "drought": +1, "flood": 0, "label": "Reduced Rainfall", "detail": ""},
        "la_nina":  {"rain": +2, "temp": 0,  "drought": -1, "flood": +2, "label": "Flood Risk", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Minimal Impact", "detail": ""},
    },
    # ── Australia / Pacific ─────────────────────────────────────
    "AUS": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -2, "label": "Severe Drought / Wildfire Season", "detail": "Eastern and southern Australia in drought. Bushfire risk extreme. Murray-Darling basin critically low."},
        "la_nina":  {"rain": +2, "temp": -1, "drought": -2, "flood": +2, "label": "Eastern Australia Flooding", "detail": "QLD, NSW flooding. Good pastoral conditions in west."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": -1, "label": "Moderate Drought Risk", "detail": ""},
    },
    # ── East Africa ─────────────────────────────────────────────
    "KEN": {
        "el_nino":  {"rain": +2, "temp": +1, "drought": -1, "flood": +2, "label": "Flooding / Long Rains Enhanced", "detail": "October–December rains significantly above normal. Flash flood risk."},
        "la_nina":  {"rain": -2, "temp": +1, "drought": +2, "flood": -1, "label": "Drought Risk", "detail": "Long rains failure. Pastoral drought."},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": +1, "temp": 0, "drought": -1, "flood": +1, "label": "Mild Flood Risk", "detail": ""},
    },
    "ETH": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -1, "label": "Drought / Belg Rains Failure", "detail": ""},
        "la_nina":  {"rain": +1, "temp": 0,  "drought": -1, "flood": +1, "label": "Above Normal Kiremt Rains", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": 0, "label": "Mild Drought", "detail": ""},
    },
    # ── Southern Africa ─────────────────────────────────────────
    "ZAF": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -1, "label": "Drought / Heat", "detail": "Summer rainfall season severely suppressed. Maize crop failure risk."},
        "la_nina":  {"rain": +1, "temp": -1, "drought": -1, "flood": +1, "label": "Above Normal Rainfall", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": 0, "label": "Moderate Drought", "detail": ""},
    },
    "ZWE": {
        "el_nino":  {"rain": -2, "temp": +1, "drought": +2, "flood": -1, "label": "Severe Drought", "detail": ""},
        "la_nina":  {"rain": +2, "temp": 0,  "drought": -1, "flood": +2, "label": "Flooding Risk", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": 0, "drought": +1, "flood": 0, "label": "Mild Drought", "detail": ""},
    },
    # ── Americas ────────────────────────────────────────────────
    "PER": {
        "el_nino":  {"rain": +2, "temp": +2, "drought": -1, "flood": +2, "label": "Coastal Flooding / Extreme Heat", "detail": "Humboldt current disruption. Anchovy fishery collapses. Coastal floods in Lima region."},
        "la_nina":  {"rain": -2, "temp": -1, "drought": +2, "flood": -1, "label": "Drought / Fishery Recovery", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": +1, "temp": +1, "drought": 0, "flood": +1, "label": "Moderate Flood Risk", "detail": ""},
    },
    "BRA": {
        "el_nino":  {"rain": -2, "temp": +2, "drought": +2, "flood": -1, "label": "Amazon / NE Brazil Drought", "detail": "Northeast Brazil severe drought. Amazon forest stress. Hydropower output falls."},
        "la_nina":  {"rain": +1, "temp": -1, "drought": -1, "flood": +2, "label": "Southern Brazil Flooding", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": -1, "temp": +1, "drought": +1, "flood": 0, "label": "NE Brazil Stress", "detail": ""},
    },
    "USA": {
        "el_nino":  {"rain": +1, "temp": 0,  "drought": -1, "flood": +1, "label": "Wetter South, Milder North", "detail": "Southern US / California above-normal rainfall. Pacific jetstream strengthens."},
        "la_nina":  {"rain": -1, "temp": +1, "drought": +2, "flood": -1, "label": "Southern US Drought / Active Atlantic Hurricane Season", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Moderate Impact", "detail": ""},
    },
    # ── Europe ──────────────────────────────────────────────────
    "GBR": {
        "el_nino":  {"rain": +1, "temp": +1, "drought": 0, "flood": +1, "label": "Mild Wet Winters", "detail": "NAO positive phase often associated with El Niño. Milder, wetter UK winters."},
        "la_nina":  {"rain": -1, "temp": -1, "drought": 0, "flood": 0, "label": "Colder, Drier Winters", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Weak Signal", "detail": ""},
    },
    # ── China ───────────────────────────────────────────────────
    "CHN": {
        "el_nino":  {"rain": +1, "temp": +1, "drought": -1, "flood": +2, "label": "Yangtze Valley Flooding", "detail": "Summer floods along Yangtze. Northern China drier. Winter warmer than normal."},
        "la_nina":  {"rain": -1, "temp": -1, "drought": +1, "flood": -1, "label": "Drier / Colder North", "detail": ""},
        "neutral":  {"rain": 0, "temp": 0, "drought": 0, "flood": 0, "label": "Near-Normal", "detail": ""},
        "modoki":   {"rain": +1, "temp": 0, "drought": 0, "flood": +1, "label": "Moderate Flood Risk", "detail": ""},
    },
}

# ── India State Impact (for India map) ───────────────────────────
# Monsoon deficit % by state during El Niño (historical average)
INDIA_STATE_ELNINO = {
    "Rajasthan":      {"deficit": 22, "crop_risk": "High",   "reservoir": "Critical", "state_code": "RJ"},
    "Gujarat":        {"deficit": 18, "crop_risk": "High",   "reservoir": "Severe",   "state_code": "GJ"},
    "Maharashtra":    {"deficit": 16, "crop_risk": "High",   "reservoir": "Severe",   "state_code": "MH"},
    "Karnataka":      {"deficit": 14, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "KA"},
    "Telangana":      {"deficit": 15, "crop_risk": "High",   "reservoir": "Severe",   "state_code": "TG"},
    "Andhra Pradesh": {"deficit": 12, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "AP"},
    "Tamil Nadu":     {"deficit":  8, "crop_risk": "Low",    "reservoir": "Moderate", "state_code": "TN"},
    "Kerala":         {"deficit":  5, "crop_risk": "Low",    "reservoir": "Low",      "state_code": "KL"},
    "Madhya Pradesh": {"deficit": 18, "crop_risk": "High",   "reservoir": "Severe",   "state_code": "MP"},
    "Uttar Pradesh":  {"deficit": 15, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "UP"},
    "Bihar":          {"deficit": 10, "crop_risk": "Medium", "reservoir": "Low",      "state_code": "BR"},
    "West Bengal":    {"deficit":  7, "crop_risk": "Low",    "reservoir": "Low",      "state_code": "WB"},
    "Odisha":         {"deficit": 10, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "OD"},
    "Punjab":         {"deficit":  8, "crop_risk": "Low",    "reservoir": "Low",      "state_code": "PB"},
    "Haryana":        {"deficit": 10, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "HR"},
    "Himachal Pradesh":{"deficit": 5, "crop_risk": "Low",   "reservoir": "Low",      "state_code": "HP"},
    "Assam":          {"deficit":  4, "crop_risk": "Low",    "reservoir": "Low",      "state_code": "AS"},
    "Jharkhand":      {"deficit": 12, "crop_risk": "Medium", "reservoir": "Moderate", "state_code": "JH"},
    "Chhattisgarh":   {"deficit": 14, "crop_risk": "High",   "reservoir": "Severe",   "state_code": "CG"},
    # ── J&K NOTE: Western disturbance region, low SW monsoon signal ──────────
    # Using India official claimed boundary (Aksai Chin + PoK included)
    "Jammu and Kashmir": {"deficit":  4, "crop_risk": "Low", "reservoir": "Low",  "state_code": "JK"},
    "Ladakh":             {"deficit":  2, "crop_risk": "Low", "reservoir": "Low",  "state_code": "LA"},
    "Goa":            {"deficit":  6, "crop_risk": "Low",    "reservoir": "Low",      "state_code": "GA"},
}

# ── Sector Risk Profiles ─────────────────────────────────────────
SECTOR_IMPACTS = {
    "agriculture": {
        "el_nino": {
            "headline": "⚠️ HIGH RISK — Kharif Crop Stress Likely",
            "risk_level": 85,
            "actions": [
                "Switch to drought-tolerant varieties (Bajra, Sorghum, Pulses) in deficit-prone districts",
                "Advance sowing calendar by 2–3 weeks if pre-monsoon moisture is adequate",
                "Activate micro-irrigation subsidies — drip/sprinkler demand will spike",
                "Coordinate with NABARD for contingency credit lines before June",
                "Advise farmers to avoid water-intensive crops (Sugarcane, Rice) in red-zone districts",
            ],
            "kpis": {"Crop Loss Risk": "High", "Irrigation Demand": "+30–45%", "Fertilizer Demand": "Stable / Slight Drop",
                     "Food Inflation Risk": "High (3–6 months lag)"},
        },
        "la_nina": {
            "headline": "🟢 FAVOURABLE — Above-Normal Monsoon Expected",
            "risk_level": 20,
            "actions": [
                "Plan for high-yielding varieties needing good moisture (Rice, Maize, Soybean)",
                "Watch for waterlogging risk in low-lying agricultural zones",
                "Rabi sowing outlook positive — good soil moisture carryover",
            ],
            "kpis": {"Crop Loss Risk": "Low", "Irrigation Demand": "Normal / Below", "Food Inflation Risk": "Low"},
        },
        "neutral": {
            "headline": "🟡 NEUTRAL — Monitor IOD and MJO Signals",
            "risk_level": 35,
            "actions": ["Watch for IOD development (June–July) to refine forecast", "Standard advisory applies"],
            "kpis": {"Crop Loss Risk": "Moderate", "Irrigation Demand": "Normal"},
        },
    },
    "water": {
        "el_nino": {
            "headline": "🔴 ALERT — Reservoir and Groundwater Stress",
            "risk_level": 80,
            "actions": [
                "Issue advance reservoir conservation orders — target 85% storage by September",
                "Activate water allocation rationing protocols for Rabi season planning",
                "Review inter-basin transfer capacity (linking rivers, Kaleshwaram etc.)",
                "Groundwater overdraft expected to surge — enforce extraction limits in critical blocks",
                "Urban water boards: plan 15–25% supply shortfall contingency by Nov–Feb",
            ],
            "kpis": {"Reservoir Storage (Sep)": "60–70% of Normal", "Groundwater Recharge": "Below Normal",
                     "River Discharge": "Below Normal", "Drought Probability": "High"},
        },
        "la_nina": {
            "headline": "🟢 POSITIVE — Reservoir Recharge Likely",
            "risk_level": 20,
            "actions": ["Activate flood-control protocols for major dams", "Manage spillway operations"],
            "kpis": {"Reservoir Storage": "Above Normal", "Flood Risk": "Elevated in Low-Lying Areas"},
        },
        "neutral": {
            "headline": "🟡 NEUTRAL — Standard Water Management",
            "risk_level": 35,
            "actions": ["Routine monitoring. Watch IOD and sub-seasonal signals."],
            "kpis": {"Reservoir Storage": "Near Normal"},
        },
    },
    "energy": {
        "el_nino": {
            "headline": "⚡ STRESS — Hydro Shortfall + Cooling Demand Spike",
            "risk_level": 75,
            "actions": [
                "Hydro generation will fall 20–35% — contract thermal and renewable backup capacity NOW",
                "Air-conditioning demand will surge from April–June heat waves — prepare grid for peak load",
                "Coal/gas plant scheduling: activate peaking units earlier in the season",
                "Alert grid operators to reduce planned hydro maintenance during dry months",
                "Wind energy: check if drought correlates with reduced wind in affected regions",
            ],
            "kpis": {"Hydro Output Risk": "-20 to -35%", "Cooling Demand": "+15–25%", "Grid Stress": "High",
                     "Coal Demand": "Above Normal"},
        },
        "la_nina": {
            "headline": "🟢 POSITIVE — Hydro Recovery, Mild Cooling Demand",
            "risk_level": 20,
            "actions": ["Hydro output expected above normal", "Reduced cooling demand in monsoon season"],
            "kpis": {"Hydro Output": "Above Normal", "Cooling Demand": "Below Normal"},
        },
        "neutral": {
            "headline": "🟡 NEUTRAL — Normal Seasonal Patterns",
            "risk_level": 35,
            "actions": ["Standard dispatch planning"],
            "kpis": {"Overall Risk": "Moderate"},
        },
    },
    "banking": {
        "el_nino": {
            "headline": "🏦 RISK — Agricultural Credit & Insurance Exposure",
            "risk_level": 70,
            "actions": [
                "Agricultural loan portfolio: flag districts with deficit >15% for enhanced NPA monitoring",
                "Recommend crop insurance (PMFBY) uptake — increase coverage in red-zone districts",
                "Review collateral valuations for agricultural land in drought-exposed regions",
                "Infrastructure loans: check exposure to hydro projects and irrigation-linked industries",
                "Commodity trading: long position on sugar, edible oils (supply-side pressure expected)",
                "Food & agri NBFCs: increase provisioning by 1.5–2x for Q3/Q4 of current fiscal",
            ],
            "kpis": {"Agri NPA Risk": "Elevated (+30–40%)", "Crop Insurance Claims": "High",
                     "Commodity Price Risk": "Bullish Foodgrains", "Rural FMCG Demand": "Suppressed"},
        },
        "la_nina": {
            "headline": "🟢 POSITIVE — Rural Credit Demand Healthy",
            "risk_level": 20,
            "actions": ["Good monsoon supports rural consumption and agricultural repayment capacity"],
            "kpis": {"Agri NPA Risk": "Low", "Rural Credit Demand": "Strong"},
        },
        "neutral": {
            "headline": "🟡 NEUTRAL — Standard Risk Posture",
            "risk_level": 35,
            "actions": ["Monitor evolving ENSO signal quarterly"],
            "kpis": {"Overall Risk": "Moderate"},
        },
    },
    "forestry": {
        "el_nino": {
            "headline": "🔥 HIGH RISK — Wildfire and Forest Stress",
            "risk_level": 80,
            "actions": [
                "Pre-position firefighting resources in dry deciduous forest zones (MP, CG, Odisha) by March",
                "Activate forest fire early warning via FIRMS/MODIS hotspot monitoring",
                "Reduced canopy moisture — increase fire patrol frequency in fire-prone blocks",
                "Timber harvesting operations: review permits in fire-risk zones",
                "Wildlife: Increased human-animal conflict expected as water bodies dry up — alert forest dept",
            ],
            "kpis": {"Fire Risk Index": "Very High", "Forest Moisture Deficit": "High",
                     "Biodiversity Stress": "Moderate–High", "Carbon Sink Capacity": "Reduced"},
        },
        "la_nina": {
            "headline": "🟢 POSITIVE — Good Forest Moisture",
            "risk_level": 15,
            "actions": ["Good regeneration season. Plan reforestation activities."],
            "kpis": {"Fire Risk": "Low", "Forest Growth": "Above Normal"},
        },
        "neutral": {
            "headline": "🟡 NEUTRAL — Standard Seasonal Monitoring",
            "risk_level": 30,
            "actions": ["Routine fire season preparedness"],
            "kpis": {"Overall Risk": "Moderate"},
        },
    },
}

# ── Spring Predictability Barrier data ───────────────────────────
# Historical model skill (Pearson r) by initialization month at 6-month lead
# Based on CMIP6 multi-model average statistics
SPB_SKILL = {
    "Jan": 0.78, "Feb": 0.72, "Mar": 0.58, "Apr": 0.42,
    "May": 0.38, "Jun": 0.51, "Jul": 0.64, "Aug": 0.73,
    "Sep": 0.76, "Oct": 0.79, "Nov": 0.77, "Dec": 0.75,
}

# ── India State Temperature Anomaly during El Niño (°C above normal) ──────────
# Based on historical IMD data for El Niño analog years (1987, 2002, 2009, 2015)
# Pre-monsoon (Mar–May) and monsoon season (Jun–Sep) combined signal
INDIA_STATE_TEMP_ELNINO = {
    "Rajasthan":        {"temp_anom": 2.6, "heatwave_days": 18, "risk": "Extreme"},
    "Gujarat":          {"temp_anom": 2.2, "heatwave_days": 14, "risk": "Very High"},
    "Madhya Pradesh":   {"temp_anom": 2.1, "heatwave_days": 15, "risk": "Very High"},
    "Maharashtra":      {"temp_anom": 1.9, "heatwave_days": 12, "risk": "High"},
    "Telangana":        {"temp_anom": 1.8, "heatwave_days": 11, "risk": "High"},
    "Andhra Pradesh":   {"temp_anom": 1.7, "heatwave_days": 10, "risk": "High"},
    "Uttar Pradesh":    {"temp_anom": 1.8, "heatwave_days": 13, "risk": "High"},
    "Haryana":          {"temp_anom": 2.0, "heatwave_days": 14, "risk": "Very High"},
    "Punjab":           {"temp_anom": 1.8, "heatwave_days": 11, "risk": "High"},
    "Chhattisgarh":     {"temp_anom": 1.7, "heatwave_days": 10, "risk": "High"},
    "Jharkhand":        {"temp_anom": 1.6, "heatwave_days":  9, "risk": "High"},
    "Odisha":           {"temp_anom": 1.5, "heatwave_days":  8, "risk": "Moderate"},
    "Bihar":            {"temp_anom": 1.6, "heatwave_days":  9, "risk": "High"},
    "West Bengal":      {"temp_anom": 1.2, "heatwave_days":  6, "risk": "Moderate"},
    "Karnataka":        {"temp_anom": 1.4, "heatwave_days":  7, "risk": "Moderate"},
    "Tamil Nadu":       {"temp_anom": 1.1, "heatwave_days":  5, "risk": "Moderate"},
    "Kerala":           {"temp_anom": 0.8, "heatwave_days":  3, "risk": "Low"},
    "Goa":              {"temp_anom": 0.9, "heatwave_days":  3, "risk": "Low"},
    "Himachal Pradesh": {"temp_anom": 1.3, "heatwave_days":  5, "risk": "Moderate"},
    "Assam":            {"temp_anom": 0.9, "heatwave_days":  3, "risk": "Low"},
    # J&K: El Niño warms winters, reduces snowpack — indirect signal
    "Jammu and Kashmir": {"temp_anom": 1.3, "heatwave_days":  4, "risk": "Moderate"},
    "Ladakh":             {"temp_anom": 0.8, "heatwave_days":  1, "risk": "Low"},
    # ── Union Territories & NE states ──────────────────────────────
    "Delhi":                  {"temp_anom": 2.2, "heatwave_days": 16, "risk": "Very High"},
    "Chandigarh":             {"temp_anom": 1.9, "heatwave_days": 12, "risk": "High"},
    "Dadra and Nagar Haveli": {"temp_anom": 1.5, "heatwave_days":  7, "risk": "Moderate"},
    "Lakshadweep":            {"temp_anom": 0.6, "heatwave_days":  1, "risk": "Low"},
    "Puducherry":             {"temp_anom": 0.9, "heatwave_days":  3, "risk": "Low"},
    "Andaman and Nicobar":    {"temp_anom": 0.5, "heatwave_days":  1, "risk": "Low"},
    "Arunachal Pradesh":      {"temp_anom": 0.8, "heatwave_days":  2, "risk": "Low"},
    "Manipur":                {"temp_anom": 0.9, "heatwave_days":  2, "risk": "Low"},
    "Meghalaya":              {"temp_anom": 0.7, "heatwave_days":  1, "risk": "Low"},
    "Mizoram":                {"temp_anom": 0.8, "heatwave_days":  2, "risk": "Low"},
    "Nagaland":               {"temp_anom": 0.9, "heatwave_days":  2, "risk": "Low"},
    "Sikkim":                 {"temp_anom": 0.7, "heatwave_days":  1, "risk": "Low"},
    "Tripura":                {"temp_anom": 1.0, "heatwave_days":  3, "risk": "Low"},
    "Uttarakhand":            {"temp_anom": 1.4, "heatwave_days":  6, "risk": "Moderate"},

}

# ── Major Indian Cities — ENSO El Niño Impact ─────────────────────────────────
INDIA_CITY_ELNINO = {
    # City: {state, lat, lon, temp_anom, rainfall_deficit_pct, sector_risks}
    "Delhi":       {"state":"Haryana",    "lat":28.6,"lon":77.2,"temp_anom":2.3,"rain_def":15,"pop_m":32,"water_stress":"Severe",  "agri_zone":"Haryana-Punjab belt"},
    "Mumbai":      {"state":"Maharashtra","lat":19.1,"lon":72.9,"temp_anom":1.6,"rain_def":14,"pop_m":21,"water_stress":"High",    "agri_zone":"Vidarbha cotton belt"},
    "Bengaluru":   {"state":"Karnataka",  "lat":12.9,"lon":77.6,"temp_anom":1.3,"rain_def":12,"pop_m":13,"water_stress":"Moderate","agri_zone":"Cauvery basin"},
    "Hyderabad":   {"state":"Telangana",  "lat":17.4,"lon":78.5,"temp_anom":1.8,"rain_def":15,"pop_m":10,"water_stress":"High",    "agri_zone":"Godavari basin"},
    "Chennai":     {"state":"Tamil Nadu", "lat":13.1,"lon":80.3,"temp_anom":1.0,"rain_def": 8,"pop_m": 8,"water_stress":"Moderate","agri_zone":"Cauvery delta"},
    "Kolkata":     {"state":"West Bengal","lat":22.6,"lon":88.4,"temp_anom":1.1,"rain_def": 7,"pop_m":15,"water_stress":"Low",     "agri_zone":"West Bengal delta"},
    "Ahmedabad":   {"state":"Gujarat",    "lat":23.0,"lon":72.6,"temp_anom":2.1,"rain_def":18,"pop_m": 8,"water_stress":"Severe",  "agri_zone":"Saurashtra groundnut"},
    "Pune":        {"state":"Maharashtra","lat":18.5,"lon":73.9,"temp_anom":1.7,"rain_def":13,"pop_m": 7,"water_stress":"High",    "agri_zone":"Marathwada sugarcane"},
    "Jaipur":      {"state":"Rajasthan",  "lat":26.9,"lon":75.8,"temp_anom":2.5,"rain_def":22,"pop_m": 4,"water_stress":"Critical","agri_zone":"Rajasthan dryland"},
    "Lucknow":     {"state":"Uttar Pradesh","lat":26.8,"lon":80.9,"temp_anom":1.9,"rain_def":15,"pop_m": 4,"water_stress":"High","agri_zone":"UP wheat-rice belt"},
    "Bhopal":      {"state":"Madhya Pradesh","lat":23.3,"lon":77.4,"temp_anom":2.0,"rain_def":18,"pop_m": 2,"water_stress":"High","agri_zone":"MP soybean belt"},
    "Nagpur":      {"state":"Maharashtra","lat":21.1,"lon":79.1,"temp_anom":2.0,"rain_def":16,"pop_m": 3,"water_stress":"High",   "agri_zone":"Vidarbha cotton"},
    "Patna":       {"state":"Bihar",      "lat":25.6,"lon":85.1,"temp_anom":1.5,"rain_def":10,"pop_m": 3,"water_stress":"Moderate","agri_zone":"Bihar rice belt"},
    "Bhubaneswar": {"state":"Odisha",     "lat":20.3,"lon":85.8,"temp_anom":1.4,"rain_def":10,"pop_m": 1,"water_stress":"Moderate","agri_zone":"Odisha rice belt"},
}

# ── Comprehensive India Cities (all major district HQs + tier-2 cities) ────────
# Format: city_name → {state, lat, lon, tier, pop_m, water_stress, rain_def_modifier, temp_modifier}
# rain_def_modifier: relative to state average (0 = same as state)
# temp_modifier: urban heat island effect above state baseline
INDIA_ALL_CITIES = {
    # Tier 1 metros
    "Delhi":           {"state":"Haryana",         "lat":28.61,"lon":77.21,"tier":1,"pop_m":32.0,"water_stress":"Severe",  "rain_mod":0,    "temp_mod":0.4},
    "Mumbai":          {"state":"Maharashtra",      "lat":19.08,"lon":72.88,"tier":1,"pop_m":21.0,"water_stress":"High",    "rain_mod":2,    "temp_mod":0.3},
    "Bengaluru":       {"state":"Karnataka",        "lat":12.97,"lon":77.59,"tier":1,"pop_m":13.0,"water_stress":"Moderate","rain_mod":0,    "temp_mod":0.5},
    "Hyderabad":       {"state":"Telangana",        "lat":17.39,"lon":78.49,"tier":1,"pop_m":10.0,"water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Chennai":         {"state":"Tamil Nadu",       "lat":13.08,"lon":80.27,"tier":1,"pop_m":8.0, "water_stress":"Moderate","rain_mod":-3,   "temp_mod":0.3},
    "Kolkata":         {"state":"West Bengal",      "lat":22.57,"lon":88.36,"tier":1,"pop_m":15.0,"water_stress":"Low",     "rain_mod":0,    "temp_mod":0.3},
    "Ahmedabad":       {"state":"Gujarat",          "lat":23.03,"lon":72.58,"tier":1,"pop_m":8.0, "water_stress":"Severe",  "rain_mod":0,    "temp_mod":0.4},
    "Pune":            {"state":"Maharashtra",      "lat":18.52,"lon":73.86,"tier":1,"pop_m":7.0, "water_stress":"High",    "rain_mod":1,    "temp_mod":0.3},
    # Tier 2
    "Jaipur":          {"state":"Rajasthan",        "lat":26.91,"lon":75.79,"tier":2,"pop_m":4.0, "water_stress":"Critical","rain_mod":0,    "temp_mod":0.5},
    "Lucknow":         {"state":"Uttar Pradesh",    "lat":26.85,"lon":80.95,"tier":2,"pop_m":4.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Surat":           {"state":"Gujarat",          "lat":21.17,"lon":72.83,"tier":2,"pop_m":7.0, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.3},
    "Kanpur":          {"state":"Uttar Pradesh",    "lat":26.46,"lon":80.33,"tier":2,"pop_m":3.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Nagpur":          {"state":"Maharashtra",      "lat":21.15,"lon":79.09,"tier":2,"pop_m":3.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Bhopal":          {"state":"Madhya Pradesh",   "lat":23.26,"lon":77.41,"tier":2,"pop_m":2.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Patna":           {"state":"Bihar",            "lat":25.61,"lon":85.14,"tier":2,"pop_m":3.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Indore":          {"state":"Madhya Pradesh",   "lat":22.72,"lon":75.86,"tier":2,"pop_m":3.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Thane":           {"state":"Maharashtra",      "lat":19.22,"lon":72.98,"tier":2,"pop_m":2.0, "water_stress":"Moderate","rain_mod":1,    "temp_mod":0.2},
    "Bhubaneswar":     {"state":"Odisha",           "lat":20.30,"lon":85.82,"tier":2,"pop_m":1.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Visakhapatnam":   {"state":"Andhra Pradesh",   "lat":17.69,"lon":83.22,"tier":2,"pop_m":2.0, "water_stress":"Moderate","rain_mod":-3,   "temp_mod":0.2},
    "Vadodara":        {"state":"Gujarat",          "lat":22.31,"lon":73.18,"tier":2,"pop_m":2.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Coimbatore":      {"state":"Tamil Nadu",       "lat":11.02,"lon":76.97,"tier":2,"pop_m":2.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Kochi":           {"state":"Kerala",           "lat":9.93, "lon":76.27,"tier":2,"pop_m":2.0, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Agra":            {"state":"Uttar Pradesh",    "lat":27.18,"lon":78.01,"tier":2,"pop_m":2.0, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.5},
    "Nashik":          {"state":"Maharashtra",      "lat":19.99,"lon":73.79,"tier":2,"pop_m":2.0, "water_stress":"Moderate","rain_mod":-2,   "temp_mod":0.2},
    "Faridabad":       {"state":"Haryana",          "lat":28.41,"lon":77.31,"tier":2,"pop_m":2.0, "water_stress":"Severe",  "rain_mod":0,    "temp_mod":0.4},
    "Meerut":          {"state":"Uttar Pradesh",    "lat":28.98,"lon":77.71,"tier":2,"pop_m":2.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Rajkot":          {"state":"Gujarat",          "lat":22.30,"lon":70.80,"tier":2,"pop_m":2.0, "water_stress":"Severe",  "rain_mod":3,    "temp_mod":0.4},
    "Varanasi":        {"state":"Uttar Pradesh",    "lat":25.32,"lon":83.00,"tier":2,"pop_m":2.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Srinagar":        {"state":"Jammu and Kashmir","lat":34.08,"lon":74.80,"tier":2,"pop_m":1.5, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Amritsar":        {"state":"Punjab",           "lat":31.63,"lon":74.87,"tier":2,"pop_m":1.5, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Allahabad":       {"state":"Uttar Pradesh",    "lat":25.44,"lon":81.84,"tier":2,"pop_m":1.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Ranchi":          {"state":"Jharkhand",        "lat":23.36,"lon":85.33,"tier":2,"pop_m":1.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Howrah":          {"state":"West Bengal",      "lat":22.58,"lon":88.30,"tier":2,"pop_m":1.5, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.3},
    "Jabalpur":        {"state":"Madhya Pradesh",   "lat":23.18,"lon":79.94,"tier":2,"pop_m":1.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Gwalior":         {"state":"Madhya Pradesh",   "lat":26.22,"lon":78.18,"tier":2,"pop_m":1.5, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.4},
    "Vijayawada":      {"state":"Andhra Pradesh",   "lat":16.51,"lon":80.62,"tier":2,"pop_m":1.5, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Jodhpur":         {"state":"Rajasthan",        "lat":26.29,"lon":73.02,"tier":2,"pop_m":1.5, "water_stress":"Critical","rain_mod":4,    "temp_mod":0.5},
    "Madurai":         {"state":"Tamil Nadu",       "lat":9.92, "lon":78.12,"tier":2,"pop_m":1.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Raipur":          {"state":"Chhattisgarh",     "lat":21.25,"lon":81.63,"tier":2,"pop_m":1.2, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Kota":            {"state":"Rajasthan",        "lat":25.18,"lon":75.85,"tier":2,"pop_m":1.2, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.4},
    "Chandigarh":      {"state":"Punjab",           "lat":30.73,"lon":76.79,"tier":2,"pop_m":1.2, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Guwahati":        {"state":"Assam",            "lat":26.14,"lon":91.74,"tier":2,"pop_m":1.0, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Solapur":         {"state":"Maharashtra",      "lat":17.68,"lon":75.90,"tier":2,"pop_m":1.0, "water_stress":"High",    "rain_mod":3,    "temp_mod":0.3},
    "Hubli-Dharwad":   {"state":"Karnataka",        "lat":15.36,"lon":75.12,"tier":2,"pop_m":1.0, "water_stress":"Moderate","rain_mod":2,    "temp_mod":0.3},
    "Bareilly":        {"state":"Uttar Pradesh",    "lat":28.36,"lon":79.41,"tier":2,"pop_m":1.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Moradabad":       {"state":"Uttar Pradesh",    "lat":28.83,"lon":78.77,"tier":2,"pop_m":1.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.3},
    "Mysuru":          {"state":"Karnataka",        "lat":12.30,"lon":76.65,"tier":2,"pop_m":1.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Gurgaon":         {"state":"Haryana",          "lat":28.46,"lon":77.03,"tier":2,"pop_m":1.5, "water_stress":"Severe",  "rain_mod":0,    "temp_mod":0.5},
    "Noida":           {"state":"Uttar Pradesh",    "lat":28.54,"lon":77.39,"tier":2,"pop_m":1.0, "water_stress":"High",    "rain_mod":0,    "temp_mod":0.4},
    "Tiruchirappalli": {"state":"Tamil Nadu",       "lat":10.79,"lon":78.70,"tier":2,"pop_m":1.0, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Thiruvananthapuram":{"state":"Kerala",         "lat":8.52, "lon":76.94,"tier":2,"pop_m":1.0, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Mangaluru":       {"state":"Karnataka",        "lat":12.87,"lon":74.84,"tier":2,"pop_m":0.7, "water_stress":"Low",     "rain_mod":-5,   "temp_mod":0.1},
    "Aurangabad":      {"state":"Maharashtra",      "lat":19.88,"lon":75.34,"tier":2,"pop_m":1.5, "water_stress":"High",    "rain_mod":5,    "temp_mod":0.3},
    "Dehradun":        {"state":"Uttarakhand",      "lat":30.32,"lon":78.03,"tier":2,"pop_m":0.8, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Jodhpur":         {"state":"Rajasthan",        "lat":26.29,"lon":73.02,"tier":2,"pop_m":1.5, "water_stress":"Critical","rain_mod":5,    "temp_mod":0.5},
    "Bikaner":         {"state":"Rajasthan",        "lat":28.02,"lon":73.31,"tier":3,"pop_m":0.7, "water_stress":"Critical","rain_mod":8,    "temp_mod":0.5},
    "Udaipur":         {"state":"Rajasthan",        "lat":24.58,"lon":73.69,"tier":3,"pop_m":0.6, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.3},
    "Ajmer":           {"state":"Rajasthan",        "lat":26.46,"lon":74.64,"tier":3,"pop_m":0.6, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.4},
    "Sikar":           {"state":"Rajasthan",        "lat":27.61,"lon":75.14,"tier":3,"pop_m":0.3, "water_stress":"High",    "rain_mod":3,    "temp_mod":0.4},
    "Latur":           {"state":"Maharashtra",      "lat":18.40,"lon":76.56,"tier":3,"pop_m":0.5, "water_stress":"High",    "rain_mod":5,    "temp_mod":0.3},
    "Amravati":        {"state":"Maharashtra",      "lat":20.93,"lon":77.75,"tier":3,"pop_m":0.7, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.3},
    "Nanded":          {"state":"Maharashtra",      "lat":19.16,"lon":77.31,"tier":3,"pop_m":0.6, "water_stress":"High",    "rain_mod":4,    "temp_mod":0.3},
    "Kolhapur":        {"state":"Maharashtra",      "lat":16.70,"lon":74.24,"tier":3,"pop_m":0.6, "water_stress":"Moderate","rain_mod":-2,   "temp_mod":0.2},
    "Warangal":        {"state":"Telangana",        "lat":18.00,"lon":79.59,"tier":3,"pop_m":0.8, "water_stress":"High",    "rain_mod":2,    "temp_mod":0.3},
    "Khammam":         {"state":"Telangana",        "lat":17.25,"lon":80.15,"tier":3,"pop_m":0.3, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Tirupati":        {"state":"Andhra Pradesh",   "lat":13.63,"lon":79.42,"tier":3,"pop_m":0.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Guntur":          {"state":"Andhra Pradesh",   "lat":16.30,"lon":80.44,"tier":3,"pop_m":0.7, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Salem":           {"state":"Tamil Nadu",       "lat":11.67,"lon":78.15,"tier":3,"pop_m":0.9, "water_stress":"Moderate","rain_mod":2,    "temp_mod":0.3},
    "Vellore":         {"state":"Tamil Nadu",       "lat":12.92,"lon":79.13,"tier":3,"pop_m":0.5, "water_stress":"Moderate","rain_mod":3,    "temp_mod":0.3},
    "Bhilai":          {"state":"Chhattisgarh",     "lat":21.20,"lon":81.43,"tier":3,"pop_m":0.6, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Bilaspur":        {"state":"Chhattisgarh",     "lat":22.09,"lon":82.15,"tier":3,"pop_m":0.5, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.2},
    "Dhanbad":         {"state":"Jharkhand",        "lat":23.80,"lon":86.43,"tier":3,"pop_m":1.2, "water_stress":"Moderate","rain_mod":0,    "temp_mod":0.3},
    "Jamshedpur":      {"state":"Jharkhand",        "lat":22.80,"lon":86.19,"tier":3,"pop_m":1.3, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.3},
    "Bokaro":          {"state":"Jharkhand",        "lat":23.67,"lon":86.15,"tier":3,"pop_m":0.6, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Durgapur":        {"state":"West Bengal",      "lat":23.48,"lon":87.31,"tier":3,"pop_m":0.8, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Asansol":         {"state":"West Bengal",      "lat":23.69,"lon":86.98,"tier":3,"pop_m":1.2, "water_stress":"Low",     "rain_mod":0,    "temp_mod":0.2},
    "Siliguri":        {"state":"West Bengal",      "lat":26.72,"lon":88.39,"tier":3,"pop_m":0.7, "water_stress":"Low",     "rain_mod":-5,   "temp_mod":0.1},
    "Agartala":        {"state":"Tripura",          "lat":23.83,"lon":91.27,"tier":3,"pop_m":0.5, "water_stress":"Low",     "rain_mod":-3,   "temp_mod":0.1},
    "Imphal":          {"state":"Manipur",          "lat":24.81,"lon":93.94,"tier":3,"pop_m":0.4, "water_stress":"Low",     "rain_mod":-2,   "temp_mod":0.1},
    "Shillong":        {"state":"Meghalaya",        "lat":25.57,"lon":91.88,"tier":3,"pop_m":0.4, "water_stress":"Low",     "rain_mod":-8,   "temp_mod":0.0},
    "Dibrugarh":       {"state":"Assam",            "lat":27.48,"lon":94.91,"tier":3,"pop_m":0.3, "water_stress":"Low",     "rain_mod":-2,   "temp_mod":0.1},
    "Silchar":         {"state":"Assam",            "lat":24.83,"lon":92.80,"tier":3,"pop_m":0.3, "water_stress":"Low",     "rain_mod":-3,   "temp_mod":0.1},
}

# ── World Cities — ENSO Impact (200 major cities) ──────────────────────────────
# Each city maps to ISO3 country code (impact pulled from GLOBAL_IMPACTS)
# Additional field: local_note for city-specific El Niño effects
WORLD_CITIES = {
    # Australia
    "Sydney":        {"country":"AUS","lat":-33.9,"lon":151.2,"pop_m":5.3,"local_note":"Catchment drought; Warragamba Dam risk"},
    "Melbourne":     {"country":"AUS","lat":-37.8,"lon":145.0,"pop_m":5.1,"local_note":"Bushfire season extended; Murray-Darling low"},
    "Brisbane":      {"country":"AUS","lat":-27.5,"lon":153.0,"pop_m":2.6,"local_note":"Severe drought; farm losses in Queensland"},
    "Perth":         {"country":"AUS","lat":-31.9,"lon":115.9,"pop_m":2.1,"local_note":"Moderate impact; southwest rainfall less affected"},
    "Adelaide":      {"country":"AUS","lat":-34.9,"lon":138.6,"pop_m":1.4,"local_note":"Drought risk; SA grain crop stress"},
    # Indonesia
    "Jakarta":       {"country":"IDN","lat":-6.2, "lon":106.8,"pop_m":10.5,"local_note":"Severe water shortage; peat fire smoke affects air quality"},
    "Surabaya":      {"country":"IDN","lat":-7.3, "lon":112.7,"pop_m":3.0, "local_note":"Rice crop stress; reservoir near critical"},
    "Medan":         {"country":"IDN","lat":3.6,  "lon":98.7, "pop_m":2.5, "local_note":"Sumatra peat fires; palm oil disruption"},
    "Bandung":       {"country":"IDN","lat":-6.9, "lon":107.6,"pop_m":2.4, "local_note":"Highland drought; vegetable prices spike"},
    "Makassar":      {"country":"IDN","lat":-5.1, "lon":119.4,"pop_m":1.5, "local_note":"Sulawesi drought; cocoa crop failure risk"},
    # Philippines
    "Manila":        {"country":"PHL","lat":14.6, "lon":121.0,"pop_m":13.9,"local_note":"Severe drought; Metro Manila water rationing likely"},
    "Cebu":          {"country":"PHL","lat":10.3, "lon":123.9,"pop_m":0.9, "local_note":"Visayas rice deficit; reservoir below 40%"},
    "Davao":         {"country":"PHL","lat":7.1,  "lon":125.6,"pop_m":1.8, "local_note":"Mindanao drought; banana/pineapple crop stress"},
    # China
    "Shanghai":      {"country":"CHN","lat":31.2, "lon":121.5,"pop_m":24.9,"local_note":"Yangtze flooding risk Jun–Aug; heat dome summer"},
    "Beijing":       {"country":"CHN","lat":39.9, "lon":116.4,"pop_m":21.5,"local_note":"North China drier; dust storms more frequent"},
    "Guangzhou":     {"country":"CHN","lat":23.1, "lon":113.3,"pop_m":15.3,"local_note":"Pearl River high flood risk in El Niño summer"},
    "Wuhan":         {"country":"CHN","lat":30.6, "lon":114.3,"pop_m":8.2, "local_note":"Yangtze flooding; 1998 El Niño caused massive Wuhan floods"},
    "Chongqing":     {"country":"CHN","lat":29.6, "lon":106.6,"pop_m":8.0, "local_note":"Upper Yangtze flooding risk"},
    "Chengdu":       {"country":"CHN","lat":30.7, "lon":104.1,"pop_m":8.0, "local_note":"Sichuan Basin — moderate flood risk"},
    "Shenzhen":      {"country":"CHN","lat":22.5, "lon":114.1,"pop_m":12.5,"local_note":"Heavy rain events; South China coast flooding"},
    # USA
    "Los Angeles":   {"country":"USA","lat":34.1, "lon":-118.2,"pop_m":4.0,"local_note":"Above-normal rainfall El Niño; flood risk in canyons"},
    "New York":      {"country":"USA","lat":40.7, "lon":-74.0, "pop_m":8.3,"local_note":"Milder winters; slight precip increase"},
    "Houston":       {"country":"USA","lat":29.8, "lon":-95.4, "pop_m":2.3,"local_note":"Gulf Coast wetter; flash flood risk elevated"},
    "Chicago":       {"country":"USA","lat":41.9, "lon":-87.6, "pop_m":2.7,"local_note":"Milder winter; Great Lakes ice cover reduced"},
    "Miami":         {"country":"USA","lat":25.8, "lon":-80.2, "pop_m":0.5,"local_note":"Atlantic hurricane season suppressed (El Niño shear)"},
    "Phoenix":       {"country":"USA","lat":33.4, "lon":-112.1,"pop_m":1.6,"local_note":"Arizona monsoon slightly wetter; heat still extreme"},
    "Seattle":       {"country":"USA","lat":47.6, "lon":-122.3,"pop_m":0.7,"local_note":"Above-normal winter rainfall; snowpack reduced"},
    "Dallas":        {"country":"USA","lat":32.8, "lon":-96.8, "pop_m":1.3,"local_note":"Texas wetter in El Niño winter; reduced drought"},
    "San Francisco": {"country":"USA","lat":37.8, "lon":-122.4,"pop_m":0.9,"local_note":"Atmospheric rivers intensify; drought relief"},
    # Peru / South America
    "Lima":          {"country":"PER","lat":-12.0,"lon":-77.0, "pop_m":10.9,"local_note":"Extreme coastal flooding; 1997-98 catastrophic damage"},
    "Trujillo":      {"country":"PER","lat":-8.1, "lon":-79.0, "pop_m":0.8, "local_note":"High flood risk; Moche River overflow"},
    "Piura":         {"country":"PER","lat":-5.2, "lon":-80.6, "pop_m":0.5, "local_note":"Ground zero for El Niño coastal floods"},
    "Iquitos":       {"country":"PER","lat":-3.7, "lon":-73.3, "pop_m":0.4, "local_note":"Amazon drought; river level drops critically"},
    # Brazil
    "São Paulo":     {"country":"BRA","lat":-23.5,"lon":-46.6, "pop_m":12.3,"local_note":"Cantareira reservoir drought; water rationing risk"},
    "Fortaleza":     {"country":"BRA","lat":-3.7, "lon":-38.5, "pop_m":2.6, "local_note":"Northeast Brazil severe drought; Açude Castanhão depletes"},
    "Recife":        {"country":"BRA","lat":-8.1, "lon":-34.9, "pop_m":1.6, "local_note":"Sertão drought; agri collapse risk"},
    "Manaus":        {"country":"BRA","lat":-3.1, "lon":-60.0, "pop_m":2.2, "local_note":"Amazon drought; river transport disrupted"},
    "Salvador":      {"country":"BRA","lat":-12.9,"lon":-38.5, "pop_m":2.9, "local_note":"Bahia moderate drought risk"},
    "Porto Alegre":  {"country":"BRA","lat":-30.0,"lon":-51.2, "pop_m":1.4, "local_note":"Southern Brazil flooding in El Niño (La Plata basin)"},
    # Kenya / East Africa
    "Nairobi":       {"country":"KEN","lat":-1.3, "lon":36.8,  "pop_m":4.4, "local_note":"Above-normal OND rains; flood risk in low areas"},
    "Mombasa":       {"country":"KEN","lat":-4.1, "lon":39.7,  "pop_m":1.2, "local_note":"Coastal flooding; tourism disruption"},
    "Kisumu":        {"country":"KEN","lat":-0.1, "lon":34.8,  "pop_m":0.5, "local_note":"Lake Victoria level rise; shoreline flooding"},
    # Ethiopia
    "Addis Ababa":   {"country":"ETH","lat":9.0,  "lon":38.7,  "pop_m":4.8, "local_note":"Belg rains failure; Koka reservoir low"},
    "Dire Dawa":     {"country":"ETH","lat":9.6,  "lon":41.9,  "pop_m":0.4, "local_note":"Ogaden drought; pastoralist crisis"},
    # South Africa
    "Johannesburg":  {"country":"ZAF","lat":-26.2,"lon":28.0,  "pop_m":5.6, "local_note":"Vaal Dam below 30%; Gauteng water restrictions"},
    "Cape Town":     {"country":"ZAF","lat":-33.9,"lon":18.4,  "pop_m":4.6, "local_note":"Day Zero risk; winter rainfall still OK (Cape gets winter rain)"},
    "Durban":        {"country":"ZAF","lat":-29.9,"lon":31.0,  "pop_m":3.7, "local_note":"KZN summer drought; sugarcane crop risk"},
    # Zimbabwe
    "Harare":        {"country":"ZWE","lat":-17.8,"lon":31.1,  "pop_m":1.5, "local_note":"Kariba Dam at critical low; hydro power cuts"},
    "Bulawayo":      {"country":"ZWE","lat":-20.2,"lon":28.6,  "pop_m":0.7, "local_note":"Severe drought; maize failure risk"},
    # UK / Europe
    "London":        {"country":"GBR","lat":51.5, "lon":-0.1,  "pop_m":9.0, "local_note":"Milder wetter winters; NAO positive phase likely"},
    "Manchester":    {"country":"GBR","lat":53.5, "lon":-2.2,  "pop_m":0.5, "local_note":"Above-normal winter rainfall"},
    "Edinburgh":     {"country":"GBR","lat":55.9, "lon":-3.2,  "pop_m":0.5, "local_note":"Milder winters; reduced snowfall"},
    # Thailand
    "Bangkok":       {"country":"THA","lat":13.8, "lon":100.5, "pop_m":10.7,"local_note":"Reduced wet season; Chao Phraya basin water stress"},
    "Chiang Mai":    {"country":"THA","lat":18.8, "lon":99.0,  "pop_m":0.3, "local_note":"Northern drought; rice crop deficit"},
    # Pakistan
    "Karachi":       {"country":"PAK","lat":24.9, "lon":67.0,  "pop_m":14.9,"local_note":"Severe heat waves; Indus water reduced"},
    "Lahore":        {"country":"PAK","lat":31.5, "lon":74.3,  "pop_m":11.1,"local_note":"Punjab wheat crop stress; groundwater overdraft"},
    "Islamabad":     {"country":"PAK","lat":33.7, "lon":73.1,  "pop_m":1.0, "local_note":"Reduced monsoon; hill reservoirs low"},
    # Bangladesh
    "Dhaka":         {"country":"BGD","lat":23.8, "lon":90.4,  "pop_m":21.0,"local_note":"Reduced monsoon; Brahmaputra lower than normal"},
    "Chittagong":    {"country":"BGD","lat":22.3, "lon":91.8,  "pop_m":2.6, "local_note":"Reduced summer rainfall; port operations normal"},
}

# ── GeoJSON NAME_1 → Config key mapping (simplemaps boundary file) ──────────
# Field in GeoJSON: NAME_1
# Key insight: GeoJSON uses 'Uttaranchal' (old name) → maps to 'Uttarakhand'
GEOJSON_NAME1_TO_CONFIG = {
    "Andaman and Nicobar": "Andaman and Nicobar",
    "Telangana": "Telangana",
    "Andhra Pradesh": "Andhra Pradesh",
    "Arunachal Pradesh": "Arunachal Pradesh",
    "Assam": "Assam",
    "Bihar": "Bihar",
    "Chandigarh": "Chandigarh",
    "Chhattisgarh": "Chhattisgarh",
    "Dādra and Nagar Haveli and Damān and Diu": "Dadra and Nagar Haveli",
    "Delhi": "Delhi",
    "Goa": "Goa",
    "Gujarat": "Gujarat",
    "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh",
    "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka",
    "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra",
    "Manipur": "Manipur",
    "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram",
    "Nagaland": "Nagaland",
    "Odisha": "Odisha",
    "Puducherry": "Puducherry",
    "Punjab": "Punjab",
    "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim",
    "Tamil Nadu": "Tamil Nadu",
    "Tripura": "Tripura",
    "Uttar Pradesh": "Uttar Pradesh",
    "Uttaranchal": "Uttarakhand",
    "West Bengal": "West Bengal",
    "Lakshadweep": "Lakshadweep",
    "Jammu and Kashmir": "Jammu and Kashmir",
    "Ladakh": "Ladakh",
}

# Extra states/UTs added for full GeoJSON coverage
INDIA_STATE_ELNINO["Delhi"] = {'deficit': 15, 'crop_risk': 'High', 'reservoir': 'Severe', 'state_code': 'DL'}
INDIA_STATE_ELNINO["Chandigarh"] = {'deficit': 8, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'CH'}
INDIA_STATE_ELNINO["Dadra and Nagar Haveli"] = {'deficit': 12, 'crop_risk': 'Medium', 'reservoir': 'Moderate', 'state_code': 'DN'}
INDIA_STATE_ELNINO["Lakshadweep"] = {'deficit': 3, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'LD'}
INDIA_STATE_ELNINO["Puducherry"] = {'deficit': 7, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'PY'}
INDIA_STATE_ELNINO["Andaman and Nicobar"] = {'deficit': 2, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'AN'}
INDIA_STATE_ELNINO["Arunachal Pradesh"] = {'deficit': 3, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'AR'}
INDIA_STATE_ELNINO["Manipur"] = {'deficit': 4, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'MN'}
INDIA_STATE_ELNINO["Meghalaya"] = {'deficit': 3, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'ML'}
INDIA_STATE_ELNINO["Mizoram"] = {'deficit': 3, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'MZ'}
INDIA_STATE_ELNINO["Nagaland"] = {'deficit': 4, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'NL'}
INDIA_STATE_ELNINO["Sikkim"] = {'deficit': 3, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'SK'}
INDIA_STATE_ELNINO["Tripura"] = {'deficit': 5, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'TR'}
INDIA_STATE_ELNINO["Uttarakhand"] = {'deficit': 5, 'crop_risk': 'Low', 'reservoir': 'Low', 'state_code': 'UK'}

