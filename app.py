"""
app.py
AstroShield AI — Satellite-Driven Natural Disaster Prediction & Autonomous Emergency Dispatch
Streamlit Mission Control Dashboard  |  v2.0  |  Galaxy BG Edition
"""

import base64
import time
import math
import pathlib
import datetime
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from orbit_engine import get_satellite_position
from ai_engine import analyze_sector_threat
from dispatch_engine import (
    send_emergency_dispatch,
    DEFAULT_TWILIO_ACCOUNT_SID,
    DEFAULT_TWILIO_AUTH_TOKEN,
    DEFAULT_TWILIO_PHONE_NUMBER,
    DEFAULT_RECIPIENT_NUMBER,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AstroShield AI — Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & ENCODE GALAXY BACKGROUND
# ─────────────────────────────────────────────────────────────────────────────
def _load_bg_b64(path: str) -> str:
    img_path = pathlib.Path(path)
    if img_path.exists():
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

BG_B64 = _load_bg_b64("galaxy_bg.jpg")
BG_CSS = (
    f"url('data:image/jpeg;base64,{BG_B64}')"
    if BG_B64
    else "linear-gradient(135deg,#050a10 0%,#0a1628 100%)"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Aerospace Mission Control Dark Theme + Galaxy Background
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Share+Tech+Mono&family=Inter:wght@300;400;600&display=swap');

/* ─── GALAXY BACKGROUND ─── */
.stApp {{
    background: {BG_CSS} center center / cover fixed !important;
    min-height: 100vh;
}}

/* dark overlay so text stays readable */
.stApp::before {{
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(2,6,18,0.88) 0%,
        rgba(5,12,28,0.82) 40%,
        rgba(8,3,20,0.85) 100%
    );
    pointer-events: none;
    z-index: 0;
}}

/* lift all Streamlit content above the overlay */
.stApp > * {{ position: relative; z-index: 1; }}
.block-container {{ padding-top: 0.8rem !important; }}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg,rgba(3,8,22,0.96) 0%,rgba(7,14,36,0.95) 100%) !important;
    border-right: 1px solid rgba(0,229,255,0.12) !important;
    backdrop-filter: blur(16px) !important;
}}
[data-testid="stSidebar"] * {{ color: #e8f4fd !important; }}

/* ─── ANIMATED STAR PARTICLES (CSS only) ─── */
@keyframes twinkle {{
    0%,100% {{ opacity:0.2; transform:scale(1); }}
    50%      {{ opacity:1;   transform:scale(1.4); }}
}}
.star {{
    position:fixed; border-radius:50%; background:#fff;
    animation: twinkle linear infinite;
    pointer-events:none; z-index:0;
}}

/* ─── HEADER ─── */
.astroshield-header {{
    background: linear-gradient(135deg,rgba(5,13,30,0.75) 0%,rgba(11,26,53,0.7) 100%);
    border: 1px solid rgba(0,229,255,0.22);
    border-radius: 16px;
    padding: 22px 30px 18px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(18px);
    box-shadow: 0 0 60px rgba(0,80,200,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}}
.astroshield-header::before {{
    content:'';
    position:absolute; top:0; left:-100%; right:0; height:2px;
    background: linear-gradient(90deg,transparent,#00e5ff,#ff3c3c,#00e5ff,transparent);
    animation: sweepline 4s linear infinite;
}}
@keyframes sweepline {{ 0%{{left:-100%}} 100%{{left:100%}} }}

.header-title {{
    font-family:'Orbitron',monospace !important;
    font-size:2.1rem !important; font-weight:900 !important;
    background: linear-gradient(90deg,#00e5ff 0%,#ffffff 40%,#ff3c3c 80%,#ff8c00 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; letter-spacing:2px; margin:0 !important;
    animation: titleGlow 4s ease-in-out infinite;
}}
@keyframes titleGlow {{
    0%,100% {{ filter: drop-shadow(0 0 8px rgba(0,229,255,0.4)); }}
    50%      {{ filter: drop-shadow(0 0 20px rgba(0,229,255,0.8)); }}
}}
.header-subtitle {{
    font-family:'Share Tech Mono',monospace !important;
    color:#7ab8d4 !important; font-size:0.82rem !important;
    margin-top:5px !important; letter-spacing:1.5px;
}}
.status-badge {{
    display:inline-block;
    background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.45);
    color:#00ff88 !important; font-family:'Share Tech Mono',monospace;
    font-size:0.68rem; padding:3px 12px; border-radius:20px; margin-top:8px;
    animation: pulseBadge 2s ease-in-out infinite;
}}
@keyframes pulseBadge {{
    0%,100% {{ box-shadow:0 0 6px rgba(0,255,136,0.25); }}
    50%      {{ box-shadow:0 0 18px rgba(0,255,136,0.7); }}
}}

/* ─── METRIC CARDS ─── */
.metric-grid {{
    display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:16px;
}}
.metric-card {{
    background: linear-gradient(135deg,rgba(10,20,40,0.75) 0%,rgba(15,30,55,0.7) 100%);
    border:1px solid rgba(0,229,255,0.18); border-radius:12px;
    padding:14px 18px; position:relative; overflow:hidden;
    backdrop-filter:blur(12px);
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    cursor:default;
}}
.metric-card:hover {{
    border-color:rgba(0,229,255,0.6);
    transform:translateY(-4px) scale(1.02);
    box-shadow:0 8px 32px rgba(0,229,255,0.2), 0 0 0 1px rgba(0,229,255,0.1);
}}
.metric-card::after {{
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,rgba(0,229,255,0.6),transparent);
}}
.metric-label {{ font-family:'Share Tech Mono',monospace; font-size:0.62rem; color:#5a8fa8 !important; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:5px; }}
.metric-value {{ font-family:'Orbitron',monospace; font-size:1.05rem; font-weight:600; color:#00e5ff !important; }}
.metric-value.red    {{ color:#ff3c3c !important; text-shadow:0 0 12px rgba(255,60,60,0.5); }}
.metric-value.green  {{ color:#00ff88 !important; text-shadow:0 0 12px rgba(0,255,136,0.4); }}
.metric-value.orange {{ color:#ff8c00 !important; text-shadow:0 0 12px rgba(255,140,0,0.4); }}

/* ─── SECTION HEADERS ─── */
.section-header {{
    font-family:'Orbitron',monospace; font-size:0.82rem; font-weight:600;
    color:#00e5ff !important; letter-spacing:2.5px; text-transform:uppercase;
    border-bottom:1px solid rgba(0,229,255,0.2); padding-bottom:8px; margin-bottom:14px;
    text-shadow:0 0 10px rgba(0,229,255,0.4);
}}

/* ─── SIDEBAR SECTION TITLE ─── */
.sidebar-section-title {{
    font-family:'Orbitron',monospace; font-size:0.7rem; color:#00e5ff !important;
    letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;
    border-bottom:1px solid rgba(0,229,255,0.15); padding-bottom:6px;
}}

/* ─── SECTOR CARDS (clickable sidebar) ─── */
.sector-card {{
    background:linear-gradient(135deg,rgba(8,16,32,0.7),rgba(12,24,48,0.65));
    border:1px solid rgba(0,229,255,0.15); border-radius:10px;
    padding:12px 14px; margin-bottom:8px; cursor:pointer;
    transition:all 0.3s ease; backdrop-filter:blur(10px);
}}
.sector-card:hover {{
    border-color:rgba(0,229,255,0.5);
    box-shadow:0 4px 20px rgba(0,229,255,0.15);
    transform:translateX(4px);
}}
.sector-card.active {{
    border-color:rgba(255,140,0,0.5);
    background:linear-gradient(135deg,rgba(255,140,0,0.08),rgba(255,60,60,0.05));
    box-shadow:0 0 20px rgba(255,140,0,0.15);
}}

/* ─── GLASS PANELS ─── */
.glass-panel {{
    background:linear-gradient(135deg,rgba(8,15,28,0.72),rgba(12,22,42,0.68));
    border:1px solid rgba(0,229,255,0.14); border-radius:12px;
    padding:18px; backdrop-filter:blur(16px);
    box-shadow:0 4px 24px rgba(0,0,0,0.4);
}}

/* ─── AI CARD ─── */
.ai-card {{
    background:linear-gradient(135deg,rgba(6,12,24,0.82) 0%,rgba(10,18,36,0.78) 100%);
    border:1px solid rgba(255,60,60,0.25); border-radius:14px;
    padding:20px; margin-bottom:14px; position:relative; overflow:hidden;
    backdrop-filter:blur(16px);
    box-shadow:0 0 40px rgba(255,60,60,0.08);
    transition:box-shadow 0.3s ease;
}}
.ai-card:hover {{ box-shadow:0 0 60px rgba(255,60,60,0.15); }}
.ai-card::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#ff3c3c,#ff8c00,#ffd700);
}}

/* ─── THREAT SCORE ─── */
.threat-score-big {{
    font-family:'Orbitron',monospace; font-size:3.2rem; font-weight:900; line-height:1;
}}
.threat-score-big.critical {{ color:#ff3c3c !important; text-shadow:0 0 30px rgba(255,60,60,0.7), 0 0 60px rgba(255,60,60,0.3); }}
.threat-score-big.high     {{ color:#ff8c00 !important; text-shadow:0 0 30px rgba(255,140,0,0.6); }}
.threat-score-big.moderate {{ color:#ffd700 !important; text-shadow:0 0 30px rgba(255,215,0,0.5); }}

/* ─── SENSOR BARS ─── */
.sensor-bar-container {{ margin:8px 0; }}
.sensor-bar-label {{
    font-family:'Share Tech Mono',monospace; font-size:0.72rem;
    color:#7ab8d4 !important; margin-bottom:4px;
    display:flex; justify-content:space-between;
}}
.sensor-bar-outer {{
    background:rgba(255,255,255,0.06); border-radius:4px; height:9px; overflow:hidden;
    box-shadow:inset 0 1px 3px rgba(0,0,0,0.5);
}}
.sensor-bar-inner {{
    height:100%; border-radius:4px; position:relative; overflow:hidden;
    transition:width 1.2s cubic-bezier(0.4,0,0.2,1);
}}
.sensor-bar-inner::after {{
    content:''; position:absolute; top:0; left:-100%; width:100%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.35),transparent);
    animation:barShimmer 2.5s ease-in-out infinite;
}}
@keyframes barShimmer {{ 0%{{left:-100%}} 100%{{left:100%}} }}

/* ─── ORBIT TELEMETRY CARD ─── */
.orbit-card {{
    background:rgba(5,12,24,0.75); border:1px solid rgba(0,229,255,0.2);
    border-radius:10px; padding:16px;
    font-family:'Share Tech Mono',monospace; font-size:0.77rem;
    color:#00e5ff !important; line-height:1.9;
    backdrop-filter:blur(12px);
}}
.orbit-card .label {{ color:#3a6a8a !important; }}

/* ─── BUTTONS ─── */
.stButton > button {{
    background:linear-gradient(135deg,rgba(10,25,50,0.8) 0%,rgba(15,35,65,0.75) 100%) !important;
    border:1px solid rgba(0,229,255,0.4) !important; color:#00e5ff !important;
    font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
    letter-spacing:1px !important; border-radius:10px !important;
    padding:0.65rem 1.2rem !important; width:100% !important;
    backdrop-filter:blur(10px) !important;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow:0 0 20px rgba(0,229,255,0.08) !important;
}}
.stButton > button:hover {{
    background:linear-gradient(135deg,rgba(255,60,60,0.15),rgba(255,140,0,0.1)) !important;
    border-color:#ff3c3c !important; color:#ff6b6b !important;
    box-shadow:0 0 30px rgba(255,60,60,0.4),0 4px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px) !important;
}}
.stButton > button:active {{ transform:translateY(0px) !important; }}

/* ─── SELECTBOX ─── */
.stSelectbox > div > div {{
    background:rgba(8,16,32,0.8) !important; border:1px solid rgba(0,229,255,0.2) !important;
    color:#e8f4fd !important; font-family:'Share Tech Mono',monospace !important;
    backdrop-filter:blur(10px) !important; border-radius:8px !important;
}}

/* ─── TEXT INPUTS ─── */
.stTextInput > div > div > input {{
    background:rgba(3,8,20,0.85) !important; border:1px solid rgba(0,229,255,0.2) !important;
    color:#e8f4fd !important; font-family:'Share Tech Mono',monospace !important;
    font-size:0.8rem !important; border-radius:8px !important;
    backdrop-filter:blur(10px) !important;
}}
.stTextInput > div > div > input:focus {{
    border-color:rgba(0,229,255,0.6) !important;
    box-shadow:0 0 12px rgba(0,229,255,0.2) !important;
}}

/* ─── PROGRESS BAR ─── */
.stProgress > div > div {{ background:rgba(255,255,255,0.06) !important; border-radius:4px !important; }}
.stProgress > div > div > div {{ background:linear-gradient(90deg,#00e5ff,#0080ff) !important; border-radius:4px !important; }}

/* ─── ALERTS ─── */
.stSuccess,  .stError, .stWarning, .stInfo {{
    background:rgba(8,16,32,0.8) !important; border-radius:10px !important;
    font-family:'Share Tech Mono',monospace !important;
    backdrop-filter:blur(12px) !important;
}}

/* ─── EXPANDER ─── */
.streamlit-expanderHeader {{
    background:rgba(8,16,32,0.7) !important; border-radius:8px !important;
    font-family:'Share Tech Mono',monospace !important; color:#00e5ff !important;
    backdrop-filter:blur(10px) !important;
}}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:rgba(0,0,0,0.2); }}
::-webkit-scrollbar-thumb {{ background:rgba(0,229,255,0.3); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(0,229,255,0.5); }}

/* ─── ANIMATED SCAN RETICLE ─── */
.scan-reticle {{
    position:relative; width:80px; height:80px; margin:0 auto 10px;
}}
.scan-reticle::before, .scan-reticle::after {{
    content:''; position:absolute; border:1px solid rgba(0,229,255,0.5); border-radius:50%;
}}
.scan-reticle::before {{ inset:0; animation:spinCW 3s linear infinite; }}
.scan-reticle::after  {{ inset:10px; animation:spinCCW 2s linear infinite; border-color:rgba(255,60,60,0.4); }}
@keyframes spinCW  {{ from{{transform:rotate(0deg)}} to{{transform:rotate(360deg)}} }}
@keyframes spinCCW {{ from{{transform:rotate(0deg)}} to{{transform:rotate(-360deg)}} }}

/* ─── PULSE RING (hazard epicentre indicator) ─── */
@keyframes pulseRing {{
    0%   {{ transform:scale(0.9); opacity:1; }}
    100% {{ transform:scale(2.2); opacity:0; }}
}}
.pulse-container {{ position:relative; display:inline-block; }}
.pulse-ring {{
    position:absolute; inset:0; border-radius:50%;
    border:2px solid #ff3c3c;
    animation:pulseRing 1.8s ease-out infinite;
}}

/* ─── INTERACTIVE SECTOR RADIO BUTTONS ─── */
div[data-testid="stRadio"] > label {{
    font-family:'Share Tech Mono',monospace !important; font-size:0.78rem !important;
    color:#a0c8e0 !important;
}}

hr {{ border-color:rgba(0,229,255,0.1) !important; }}
.stSpinner > div {{ border-top-color:#00e5ff !important; }}

/* ─── TABS STYLING ─── */
[data-testid="stTabs"] {{
    background: transparent;
    margin-top: 8px;
}}
[data-testid="stTabs"] [role="tablist"] {{
    gap: 8px;
    border-bottom: 1px solid rgba(0,229,255,0.2) !important;
    padding-bottom: 4px;
}}
[data-testid="stTabs"] button[data-baseweb="tab"] {{
    background: rgba(8,16,32,0.6) !important;
    border: 1px solid rgba(0,229,255,0.18) !important;
    border-radius: 8px 8px 0 0 !important;
    color: #7ab8d4 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 8px 16px !important;
    transition: all 0.25s ease !important;
}}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
    color: #00e5ff !important;
    border-color: rgba(0,229,255,0.5) !important;
    background: rgba(0,229,255,0.08) !important;
}}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
    color: #00e5ff !important;
    background: linear-gradient(180deg, rgba(0,229,255,0.15) 0%, rgba(5,13,30,0.85) 100%) !important;
    border: 1px solid rgba(0,229,255,0.6) !important;
    border-bottom: 2px solid #00e5ff !important;
    box-shadow: 0 0 15px rgba(0,229,255,0.2);
}}
</style>

<!-- CSS-only twinkling stars injected over galaxy bg -->
<div style="position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;">
  <div class="star" style="width:2px;height:2px;top:10%;left:15%;animation-duration:2.3s;animation-delay:0s;"></div>
  <div class="star" style="width:3px;height:3px;top:20%;left:72%;animation-duration:3.1s;animation-delay:0.4s;"></div>
  <div class="star" style="width:2px;height:2px;top:35%;left:88%;animation-duration:2.7s;animation-delay:0.8s;"></div>
  <div class="star" style="width:2px;height:2px;top:55%;left:5%;animation-duration:4.1s;animation-delay:1.2s;"></div>
  <div class="star" style="width:3px;height:3px;top:70%;left:42%;animation-duration:2.9s;animation-delay:0.2s;"></div>
  <div class="star" style="width:2px;height:2px;top:80%;left:90%;animation-duration:3.5s;animation-delay:1.6s;"></div>
  <div class="star" style="width:2px;height:2px;top:5%;left:55%;animation-duration:2.1s;animation-delay:0.6s;"></div>
  <div class="star" style="width:3px;height:3px;top:45%;left:30%;animation-duration:3.8s;animation-delay:0.9s;"></div>
  <div class="star" style="width:2px;height:2px;top:90%;left:18%;animation-duration:2.6s;animation-delay:1.8s;"></div>
  <div class="star" style="width:2px;height:2px;top:62%;left:65%;animation-duration:3.3s;animation-delay:0.3s;"></div>
  <div class="star" style="width:3px;height:3px;top:28%;left:48%;animation-duration:4.2s;animation-delay:1.0s;"></div>
  <div class="star" style="width:2px;height:2px;top:15%;left:80%;animation-duration:2.4s;animation-delay:0.7s;"></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTOR DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
SECTORS = {
    "Sector Alpha: California Coastal Forest": {
        "lat": 37.7749, "lon": -122.4194, "risk": 88,
        "hazard": "Wildfire", "satellite": "Sentinel-2A",
        "emoji": "🔥", "color": "#ff3c3c",
    },
    "Sector Beta: Amazon Basin Canopy": {
        "lat": -3.4653, "lon": -62.2159, "risk": 92,
        "hazard": "Deforestation/Thermal Spike", "satellite": "Landsat-9",
        "emoji": "🌳", "color": "#ff8c00",
    },
    "Sector Gamma: Mediterranean Sector": {
        "lat": 38.9637, "lon": 35.2433, "risk": 45,
        "hazard": "Thermal Anomaly", "satellite": "Sentinel-2A",
        "emoji": "⚡", "color": "#ffd700",
    },
    "Sector Delta: Southeast Asia Delta": {
        "lat": 10.8231, "lon": 106.6297, "risk": 81,
        "hazard": "Flash Flood", "satellite": "Landsat-9",
        "emoji": "🌊", "color": "#4b9eff",
    },
}

HAZARD_COLORS = {
    "Wildfire":                    [255, 60,  30,  210],
    "Deforestation/Thermal Spike": [255, 140, 0,   200],
    "Thermal Anomaly":             [255, 215, 0,   180],
    "Flash Flood":                 [30,  140, 255, 200],
}

# ─────────────────────────────────────────────────────────────────────────────
# NASA GIBS (GLOBAL IMAGERY BROWSE SERVICES) SATELLITE TILE STREAM CONFIG
# ─────────────────────────────────────────────────────────────────────────────
GIBS_250M_MATRIX = {
    0: (2, 1), 1: (3, 2), 2: (5, 3), 3: (10, 5),
    4: (20, 10), 5: (40, 20), 6: (80, 40), 7: (160, 80), 8: (320, 160)
}

GIBS_LAYERS = {
    "Thermal Infrared / Fire Hotspots": {
        "id": "MODIS_Terra_Thermal_Anomalies_All",
        "name": "MODIS_Terra_Thermal_Anomalies_All",
        "display_name": "MODIS Terra Thermal Anomalies & Active Fire Hotspots",
        "badge": "🔥 THERMAL IR / ACTIVE FIRE HOTSPOTS",
        "resolution": "1km Daily Aggregated Thermal Flux",
        "description": "3.9µm and 11µm thermal anomaly channels detecting active wildfires and extreme heat flux.",
        "metrics": [
            ("Thermal Sensor", "MODIS (Terra)"),
            ("Channels", "3.96 µm & 11.0 µm"),
            ("Detection Mode", "Thermal Hotspot Radiometry"),
            ("Data Stream", "NASA GIBS Live Feed"),
        ],
    },
    "Vegetation / Flood Index": {
        "id": "VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1",
        "name": "VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1",
        "display_name": "VIIRS S-NPP Bands M11-I2-I1 (SWIR / NIR / Red)",
        "badge": "🌿 VEGETATION / HYDROLOGICAL FLOOD INDEX",
        "resolution": "250m Multi-Spectral False Color",
        "description": "Short-Wave Infrared composite showing burn scars, vegetation desiccation, and flood inundation in dark navy.",
        "metrics": [
            ("Sensor Platform", "VIIRS (Suomi NPP)"),
            ("Band Combination", "M11 (2.25µm) / I2 / I1"),
            ("GSD Resolution", "250m Surface Sample"),
            ("Atmospheric Pen.", "SWIR Cloud / Smoke Pen."),
        ],
    },
    "True Color Orbital Pass": {
        "id": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "name": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "display_name": "MODIS Terra TrueColor Corrected Reflectance",
        "badge": "🌍 TRUE COLOR OPTICAL PASS",
        "resolution": "250m Optical Earth Observation",
        "description": "Natural optical surface reflectance capturing atmospheric fronts, terrain, and oceanic boundaries.",
        "metrics": [
            ("Optical Radiometer", "MODIS (Terra)"),
            ("Spectral Bands", "Bands 1 (Red), 4 (Green), 3 (Blue)"),
            ("GSD Resolution", "250m Ground Resolution"),
            ("Observation Type", "Direct Broadcast Nadir Pass"),
        ],
    },
}

SECTOR_GIBS_MAPPING = {
    "Sector Alpha: California Coastal Forest": "Thermal Infrared / Fire Hotspots",
    "Sector Beta: Amazon Basin Canopy": "Vegetation / Flood Index",
    "Sector Gamma: Mediterranean Sector": "Thermal Infrared / Fire Hotspots",
    "Sector Delta: Southeast Asia Delta": "Vegetation / Flood Index",
}

def get_nasa_gibs_url(sector_lat: float, sector_lon: float, layer_type: str = "MODIS_Terra_CorrectedReflectance_TrueColor", zoom: int = 5) -> str:
    """
    Dynamically generates real-time satellite imagery tile / stream URL from the NASA GIBS API
    for the current UTC observation date without any local static files or API keys.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")

    # Tile matrix coordinates for EPSG:4326 at level z
    width, height = GIBS_250M_MATRIX.get(zoom, (40, 20))
    r = int((90.0 - sector_lat) / 180.0 * height)
    c = int((sector_lon + 180.0) / 360.0 * width)
    r = max(0, min(height - 1, r))
    c = max(0, min(width - 1, c))

    if "Thermal_Anomalies" in layer_type:
        # High-resolution WMS layer with thermal infrared fire anomaly overlay
        bbox_delta = 3.5
        min_lat = max(-90.0, sector_lat - bbox_delta)
        max_lat = min(90.0, sector_lat + bbox_delta)
        min_lon = max(-180.0, sector_lon - bbox_delta)
        max_lon = min(180.0, sector_lon + bbox_delta)
        return (
            f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
            f"?SERVICE=WMS&REQUEST=GetMap&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor,{layer_type}"
            f"&VERSION=1.3.0&FORMAT=image/png&TRANSPARENT=TRUE&WIDTH=800&HEIGHT=520"
            f"&CRS=EPSG:4326&BBOX={min_lat:.4f},{min_lon:.4f},{max_lat:.4f},{max_lon:.4f}&TIME={date_str}"
        )
    else:
        # NASA GIBS WMTS EPSG:4326 250m imagery tile stream (JPEG format for reflectance layers)
        return f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer_type}/default/{date_str}/250m/{zoom}/{r}/{c}.jpg"

# ─────────────────────────────────────────────────────────────────────────────
# SATELLITE ORBITAL SPECIFICATIONS & SENSOR MATRIX
# ─────────────────────────────────────────────────────────────────────────────
SATELLITE_ORBITAL_SPECS = {
    "Sentinel-2A": {
        "altitude_nominal": "786.4 km",
        "velocity_nominal": "7.52 km/s",
        "inclination": "98.57° Sun-Sync",
        "spectral_res": "10m Spatial",
        "swath": "290 km (MSI Swath)",
        "period": "100.6 min",
        "norad_id": "40697",
        "sensor": "Multi-Spectral Instrument (MSI)",
        "channels": "13 Bands (VNIR, SWIR-1, SWIR-2)",
    },
    "Landsat-9": {
        "altitude_nominal": "705.0 km",
        "velocity_nominal": "7.50 km/s",
        "inclination": "98.22° Sun-Sync",
        "spectral_res": "15m Pan / 30m Multi-Spectral",
        "swath": "185 km Cross-Track",
        "period": "98.9 min",
        "norad_id": "49260",
        "sensor": "OLI-2 & TIRS-2 Radiometers",
        "channels": "11 Bands (VNIR, SWIR, Thermal TIRS)",
    },
}

SECTOR_BAND_METRICS = {
    "Sector Alpha: California Coastal Forest": "Sentinel-2 Band 12 (SWIR 2190nm) & Landsat-9 TIRS Band 10 Thermal Hotspots",
    "Sector Beta: Amazon Basin Canopy": "Landsat-9 OLI-2 Band 7 (SWIR-2 2.2µm) & VIIRS SWIR Deforestation Scar",
    "Sector Gamma: Mediterranean Sector": "Sentinel-3 SLSTR S8/S9 (10.8µm) & Landsat-9 TIRS Band 10 Surface Temperature",
    "Sector Delta: Southeast Asia Delta": "Sentinel-1 C-Band SAR (5.405 GHz) & VIIRS Hydrological Flood Inundation",
}


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "orbit_data"      not in st.session_state: st.session_state.orbit_data      = None
if "ai_data"         not in st.session_state: st.session_state.ai_data         = None
if "scan_ran"        not in st.session_state: st.session_state.scan_ran         = False
if "dispatch_result" not in st.session_state: st.session_state.dispatch_result = None
if "scan_count"      not in st.session_state: st.session_state.scan_count       = 0
if "alert_log"       not in st.session_state: st.session_state.alert_log        = []
if "selected_sector" not in st.session_state: st.session_state.selected_sector  = list(SECTORS.keys())[0]
if "auto_refresh"    not in st.session_state: st.session_state.auto_refresh      = False

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def risk_css_class(risk_level: str) -> str:
    return {"CRITICAL": "critical", "HIGH": "high", "MODERATE": "moderate"}.get(risk_level, "moderate")

def sensor_bar_html(label: str, value: float, color: str) -> str:
    return f"""
<div class="sensor-bar-container">
  <div class="sensor-bar-label">
    <span>{label}</span><span style="color:{color};font-weight:600;">{value:.1f}%</span>
  </div>
  <div class="sensor-bar-outer">
    <div class="sensor-bar-inner" style="width:{value:.1f}%;background:linear-gradient(90deg,{color}66,{color});"></div>
  </div>
</div>"""

def threat_gauge_html(value: float, risk_level: str) -> str:
    """SVG arc gauge for threat index."""
    radius = 54
    circ   = 2 * math.pi * radius
    filled = circ * (value / 100.0)
    color  = {"CRITICAL": "#ff3c3c", "HIGH": "#ff8c00", "MODERATE": "#ffd700"}.get(risk_level, "#ffd700")
    return f"""
<svg width="140" height="140" viewBox="0 0 140 140" style="display:block;margin:0 auto 4px;">
  <defs>
    <filter id="glow-gauge">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- bg ring -->
  <circle cx="70" cy="70" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12"/>
  <!-- filled arc -->
  <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{color}" stroke-width="12"
    stroke-dasharray="{filled:.1f} {circ:.1f}"
    stroke-dashoffset="{circ*0.25:.1f}"
    stroke-linecap="round" filter="url(#glow-gauge)"
    style="transition:stroke-dasharray 1.2s ease;"/>
  <!-- centre text -->
  <text x="70" y="66" text-anchor="middle" font-family="Orbitron,monospace"
    font-size="22" font-weight="900" fill="{color}" filter="url(#glow-gauge)">{value:.0f}%</text>
  <text x="70" y="84" text-anchor="middle" font-family="Share Tech Mono,monospace"
    font-size="9" fill="#5a8fa8">{risk_level}</text>
</svg>"""

def build_pydeck_map(sector_lat, sector_lon, hazard, trajectory, satellite_lat, satellite_lon, impact_radius_km=50.0):
    hazard_color = HAZARD_COLORS.get(hazard, [255, 100, 0, 180])
    impact_radius_m = impact_radius_km * 1000

    hazard_df = pd.DataFrame([{"lat": sector_lat, "lon": sector_lon, "radius": impact_radius_m}])
    hazard_layer = pdk.Layer("ScatterplotLayer", data=hazard_df,
        get_position=["lon","lat"], get_radius="radius",
        get_fill_color=hazard_color, get_line_color=[255,255,0,200],
        stroked=True, line_width_min_pixels=2, opacity=0.32, pickable=True)

    pulse_df = pd.DataFrame([{"lat": sector_lat, "lon": sector_lon, "radius": impact_radius_m * 1.3}])
    pulse_layer = pdk.Layer("ScatterplotLayer", data=pulse_df,
        get_position=["lon","lat"], get_radius="radius",
        get_fill_color=[255,255,255,0], get_line_color=hazard_color[:3]+[120],
        stroked=True, line_width_min_pixels=1, opacity=0.5)

    towers = []
    for i in range(16):
        angle = (i / 16) * 2 * math.pi
        offs  = impact_radius_km * 0.0065
        towers.append({"lat": sector_lat + math.sin(angle)*offs*0.6,
                        "lon": sector_lon + math.cos(angle)*offs,
                        "elevation": impact_radius_km * 250})
    col_layer = pdk.Layer("ColumnLayer", data=pd.DataFrame(towers),
        get_position=["lon","lat"], get_elevation="elevation",
        elevation_scale=1, radius=6000,
        get_fill_color=hazard_color[:3]+[140], auto_highlight=True)

    epi_df = pd.DataFrame([{"lat": sector_lat, "lon": sector_lon}])
    epi_layer = pdk.Layer("ScatterplotLayer", data=epi_df,
        get_position=["lon","lat"], get_radius=5000,
        get_fill_color=[255,255,255,240], get_line_color=[255,60,60,255],
        stroked=True, line_width_min_pixels=3, opacity=0.95)

    arc_data = []
    for i in range(len(trajectory)-1):
        arc_data.append({"src_lon":trajectory[i][0],"src_lat":trajectory[i][1],
                         "tgt_lon":trajectory[i+1][0],"tgt_lat":trajectory[i+1][1]})
    arc_df = pd.DataFrame(arc_data) if arc_data else pd.DataFrame(columns=["src_lon","src_lat","tgt_lon","tgt_lat"])
    arc_layer = pdk.Layer("ArcLayer", data=arc_df,
        get_source_position=["src_lon","src_lat"], get_target_position=["tgt_lon","tgt_lat"],
        get_source_color=[0,220,255,200], get_target_color=[0,80,220,80],
        width_min_pixels=2, get_width=3, auto_highlight=True)

    sat_df = pd.DataFrame([{"lat": satellite_lat, "lon": satellite_lon}])
    sat_layer = pdk.Layer("ScatterplotLayer", data=sat_df,
        get_position=["lon","lat"], get_radius=9000,
        get_fill_color=[0,229,255,230], get_line_color=[255,255,255,255],
        stroked=True, line_width_min_pixels=2, opacity=1.0, pickable=True)

    view_state = pdk.ViewState(latitude=sector_lat, longitude=sector_lon,
                               zoom=5.2, pitch=48, bearing=12)
    return pdk.Deck(
        layers=[hazard_layer, pulse_layer, col_layer, arc_layer, sat_layer, epi_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={"html":"<b style='color:#00e5ff;font-family:monospace;'>AstroShield Zone</b><br/>Lat/Lon: {lat} / {lon}",
                 "style":{"background":"rgba(5,12,28,0.9)","color":"#00e5ff","fontFamily":"monospace","fontSize":"12px","border":"1px solid rgba(0,229,255,0.3)","borderRadius":"8px","padding":"8px"}})

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-REFRESH LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.auto_refresh and st.session_state.scan_ran:
    time.sleep(0.1)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────────────────────────────────────
uptime_s  = int(time.time()) % 86400
uptime_hm = f"{uptime_s//3600:02d}h {(uptime_s%3600)//60:02d}m"
total_alerts = len(st.session_state.alert_log)

st.markdown(f"""
<div class="astroshield-header">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:10px;">
    <div>
      <div class="header-title">🛰️ AstroShield AI — Aerospace Sentinel</div>
      <div class="header-subtitle">SATELLITE-DRIVEN NATURAL DISASTER PREDICTION &amp; AUTONOMOUS EMERGENCY DISPATCH</div>
      <span class="status-badge">● SYSTEM ONLINE — ALL SUBSYSTEMS NOMINAL</span>
    </div>
    <div style="text-align:right;font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a8a;">
      <div style="color:#00e5ff;">UTC {datetime.datetime.utcnow().strftime('%Y-%m-%d')}</div>
      <div>{datetime.datetime.utcnow().strftime('%H:%M:%S')} UTC</div>
      <div style="margin-top:4px;">SCANS: {st.session_state.scan_count} &nbsp;|&nbsp; ALERTS: {total_alerts}</div>
    </div>
  </div>
  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-label">▸ Orbital Propagator</div>
      <div class="metric-value green">Active SGP4</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">▸ Uplink Latency</div>
      <div class="metric-value">18 ms</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">▸ Monitored Satellites</div>
      <div class="metric-value" style="font-size:0.78rem;">Sentinel-2A / Landsat-9</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">▸ System Uptime</div>
      <div class="metric-value orange">{uptime_hm}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">▸ Sector Selection Matrix</div>', unsafe_allow_html=True)

    sector_names = list(SECTORS.keys())
    selected_sector = st.selectbox(
        "Active Monitoring Sector",
        sector_names,
        index=sector_names.index(st.session_state.selected_sector),
        label_visibility="collapsed",
        key="sector_select",
    )
    if selected_sector != st.session_state.selected_sector:
        st.session_state.selected_sector = selected_sector
        st.session_state.scan_ran = False
        st.session_state.orbit_data = None
        st.session_state.ai_data    = None
        st.session_state.dispatch_result = None

    sector_info = SECTORS[selected_sector]
    lat   = sector_info["lat"]
    lon   = sector_info["lon"]
    risk  = sector_info["risk"]
    hcol  = sector_info["color"]

    # Risk bar
    bar_w = risk
    st.markdown(f"""
<div class="glass-panel" style="margin:10px 0;padding:14px;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a8a;margin-bottom:6px;">GPS COORDINATES</div>
  <div style="font-family:'Orbitron',monospace;font-size:0.82rem;color:#00e5ff;">{lat:+.4f}° &nbsp; {lon:+.4f}°</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a8a;margin-top:8px;">PRIMARY HAZARD</div>
  <div style="font-family:'Orbitron',monospace;font-size:0.78rem;color:{hcol};">{sector_info['emoji']} {sector_info['hazard']}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a8a;margin-top:8px;">BASE RISK INDEX</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#5a8fa8;margin-bottom:4px;display:flex;justify-content:space-between;"><span>0%</span><span style="color:{hcol};font-family:'Orbitron',monospace;">{risk}%</span><span>100%</span></div>
  <div style="background:rgba(255,255,255,0.06);border-radius:5px;height:10px;overflow:hidden;">
    <div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{hcol}88,{hcol});border-radius:5px;box-shadow:0 0 10px {hcol}66;"></div>
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#3a6a8a;margin-top:8px;">ASSIGNED SATELLITE</div>
  <div style="font-family:'Orbitron',monospace;font-size:0.78rem;color:#00e5ff;">{sector_info['satellite']}</div>
</div>
""", unsafe_allow_html=True)

    # Auto-refresh toggle
    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-Refresh Telemetry (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">▸ Twilio Dispatch Config</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,rgba(0,255,136,0.06),rgba(0,180,100,0.04));
            border:1px solid rgba(0,255,136,0.25);border-radius:10px;
            padding:12px 14px;backdrop-filter:blur(10px);">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="font-size:1rem;">🔒</span>
    <span style="font-family:'Orbitron',monospace;font-size:0.7rem;color:#00ff88;letter-spacing:1px;">CREDENTIALS SECURED</span>
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#3a8a5a;line-height:1.7;">
    API keys are stored securely<br/>
    server-side and never exposed<br/>
    in the browser interface.
  </div>
  <div style="margin-top:8px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;">
    <span style="color:#3a6a8a;">SENDER &nbsp;&nbsp;</span>
    <span style="color:#00e5ff;">+1 ••• ••• ••34</span><br/>
    <span style="color:#3a6a8a;">RECIPIENT</span>
    <span style="color:#00e5ff;">+91 ••• ••• ••33</span>
  </div>
</div>""", unsafe_allow_html=True)

    # Alert Log
    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">▸ Dispatch Alert Log</div>', unsafe_allow_html=True)
    if st.session_state.alert_log:
        for entry in reversed(st.session_state.alert_log[-5:]):
            st.markdown(f"""
<div style="background:rgba(255,60,60,0.07);border-left:2px solid #ff3c3c;border-radius:4px;
            padding:6px 10px;margin-bottom:6px;font-family:'Share Tech Mono',monospace;font-size:0.68rem;">
  <span style="color:#ff8c00;">{entry['time']}</span><br/>
  <span style="color:#e8f4fd;">{entry['sector']}</span><br/>
  <span style="color:#ff3c3c;">{entry['status']}</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.72rem;color:#3a6a8a;padding:6px 0;">No dispatches yet.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#2a4a6a;text-align:center;">
  AstroShield AI v2.0 · LEO Sentinel Grid<br/>
  🌌 Galaxy Observation Mode Active
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
col_map, col_ai = st.columns([1.3, 1.0], gap="medium")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — 3D MAP
# ══════════════════════════════════════════════════════════════════════════════
with col_map:
    st.markdown('<div class="section-header">◈ Real-Time 3D Geospatial Threat Map</div>', unsafe_allow_html=True)

    sat_lat    = lat + 3.5
    sat_lon    = lon + 2.8
    trajectory = [[lon + t * 1.2, lat - t * 0.4] for t in range(-8, 12)]
    impact_r   = 50.0

    if st.session_state.orbit_data:
        od = st.session_state.orbit_data
        sat_lat    = od["latitude"]
        sat_lon    = od["longitude"]
        trajectory = od["pass_trajectory"]
    if st.session_state.ai_data:
        impact_r = st.session_state.ai_data.get("impact_radius_km", 50.0)

    deck = build_pydeck_map(lat, lon, sector_info["hazard"], trajectory, sat_lat, sat_lon, impact_r)
    st.pydeck_chart(deck, use_container_width=True, height=470)

    # Map legend
    hcol_rgb = ",".join(str(x) for x in HAZARD_COLORS.get(sector_info["hazard"], [255,100,0])[:3])
    st.markdown(f"""
<div style="display:flex;gap:16px;flex-wrap:wrap;padding:8px 4px;font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#5a8fa8;">
  <span>⬤ <span style="color:#ffffff;">Epicentre</span></span>
  <span>⬤ <span style="color:rgb({hcol_rgb});">Impact Zone ({impact_r:.0f} km)</span></span>
  <span>⬤ <span style="color:#00e5ff;">Satellite ({sector_info['satellite']})</span></span>
  <span>〜 <span style="color:#4488ff;">Orbital Arc</span></span>
</div>""", unsafe_allow_html=True)

    # ── Satellite Observation Subsystem Container ──
    with st.container():
        st.markdown('<div class="section-header" style="margin-top:16px;">📡 Satellite Observation Subsystem</div>', unsafe_allow_html=True)
        tab_spectral, tab_telemetry = st.tabs([
            "🛰️ Active Sector Multi-Spectral Capture",
            "📊 Orbital Pass & Sensor Diagnostics",
        ])

        with tab_spectral:
            default_layer_key = SECTOR_GIBS_MAPPING.get(selected_sector, "Thermal Infrared / Fire Hotspots")
            layer_options = list(GIBS_LAYERS.keys())

            col_layer_sel, col_date_badge = st.columns([1.6, 1.0])
            with col_layer_sel:
                selected_layer_key = st.selectbox(
                    "NASA GIBS Multi-Spectral Band Layer",
                    layer_options,
                    index=layer_options.index(default_layer_key),
                    key="gibs_layer_select",
                    label_visibility="collapsed",
                )

            layer_info = GIBS_LAYERS[selected_layer_key]
            layer_id = layer_info["id"]
            layer_name = layer_info["name"]

            now_utc = datetime.datetime.now(datetime.timezone.utc)
            latest_date = now_utc.strftime("%Y-%m-%d")

            with col_date_badge:
                st.markdown(f"""
<div style="text-align:right;font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#00e5ff;padding-top:6px;">
  <span>Acquired UTC: <strong style="color:#00ff88;">{latest_date}</strong></span>
</div>""", unsafe_allow_html=True)

            # Dynamically generate real-time NASA GIBS tile / stream URL
            gibs_tile_url = get_nasa_gibs_url(lat, lon, layer_id, zoom=5)

            # Band metric string for selected sector
            band_metric_str = SECTOR_BAND_METRICS.get(selected_sector, "Sentinel-2 SWIR / Landsat-9 TIRS Band 10 Surface Temperature")

            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;margin:6px 0 10px;">
  <div>
    <span style="font-family:'Orbitron',monospace;font-size:0.75rem;color:#00e5ff;">
      ▸ {layer_info['badge']}
    </span>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#a0c8e0;margin-top:2px;">
      📡 Metric: <span style="color:#ff8c00;">{band_metric_str}</span>
    </div>
  </div>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#ff8c00;
               background:rgba(255,140,0,0.1);border:1px solid rgba(255,140,0,0.3);
               border-radius:12px;padding:2px 8px;">
    {layer_info['resolution']}
  </span>
</div>""", unsafe_allow_html=True)

            caption_banner = f"📡 NASA GIBS Live Space Stream | Layer: {layer_name} | Acquired UTC: {latest_date}"

            st.image(
                gibs_tile_url,
                caption=caption_banner,
                use_container_width=True,
            )

            metric_cols = st.columns(4)
            for m_idx, (m_label, m_val) in enumerate(layer_info["metrics"]):
                with metric_cols[m_idx]:
                    st.markdown(f"""
<div style="background:rgba(5,12,24,0.75);border:1px solid rgba(0,229,255,0.15);
            border-radius:8px;padding:8px 6px;text-align:center;font-family:'Share Tech Mono',monospace;margin-top:6px;">
  <div style="color:#3a6a8a;font-size:0.6rem;margin-bottom:2px;">{m_label}</div>
  <div style="color:#00e5ff;font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:600;">{m_val}</div>
</div>""", unsafe_allow_html=True)

        with tab_telemetry:
            sat_name = sector_info["satellite"]
            sat_spec = SATELLITE_ORBITAL_SPECS.get(sat_name, SATELLITE_ORBITAL_SPECS["Sentinel-2A"])

            if st.session_state.orbit_data:
                od = st.session_state.orbit_data
                disp_alt = f"{od['altitude_km']:.1f} km"
                disp_vel = f"{od['velocity_km_s']:.4f} km/s"
                disp_ssp = f"{od['latitude']:+.4f}°, {od['longitude']:+.4f}°"
                disp_src = "⚡ LIVE SGP4 / CELESTRAK" if od["source"] == "sgp4" else "◎ PROPAGATED SGP4 NOMINAL"
                disp_time = od["timestamp"][11:19] + " UTC"
            else:
                disp_alt = sat_spec["altitude_nominal"]
                disp_vel = sat_spec["velocity_nominal"]
                disp_ssp = f"{lat + 3.5:+.4f}°, {lon + 2.8:+.4f}° (Acquisition Track)"
                disp_src = "◎ SGP4 NOMINAL EPHEMERIS"
                disp_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S") + " UTC"

            disp_inc = sat_spec["inclination"]
            disp_res = sat_spec["spectral_res"]

            # Top 4 Hero Telemetry Metrics Matrix
            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
            with t_col1:
                st.markdown(f"""
<div class="metric-card" style="padding:12px;">
  <div class="metric-label">▸ Satellite Altitude</div>
  <div class="metric-value">{disp_alt}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#3a6a8a;margin-top:3px;">LEO Orbital Height</div>
</div>""", unsafe_allow_html=True)
            with t_col2:
                st.markdown(f"""
<div class="metric-card" style="padding:12px;">
  <div class="metric-label">▸ Orbital Velocity</div>
  <div class="metric-value green">{disp_vel}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#3a6a8a;margin-top:3px;">Keplerian Vectors</div>
</div>""", unsafe_allow_html=True)
            with t_col3:
                st.markdown(f"""
<div class="metric-card" style="padding:12px;">
  <div class="metric-label">▸ Pass Inclination</div>
  <div class="metric-value orange">{disp_inc}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#3a6a8a;margin-top:3px;">Sun-Synchronous</div>
</div>""", unsafe_allow_html=True)
            with t_col4:
                st.markdown(f"""
<div class="metric-card" style="padding:12px;">
  <div class="metric-label">▸ Spectral Res.</div>
  <div class="metric-value" style="font-size:1.0rem;">{disp_res}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#3a6a8a;margin-top:3px;">Ground Sampling GSD</div>
</div>""", unsafe_allow_html=True)

            # Detailed Diagnostics Matrix Panel
            st.markdown(f"""
<div class="glass-panel" style="margin-top:12px;padding:16px;">
  <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(0,229,255,0.15);padding-bottom:8px;margin-bottom:12px;">
    <span style="font-family:'Orbitron',monospace;font-size:0.78rem;color:#00e5ff;letter-spacing:1px;">
      ▸ {sat_name.upper()} — SENSOR &amp; ORBITAL DIAGNOSTICS
    </span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00ff88;background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);padding:2px 8px;border-radius:12px;">
      {disp_src}
    </span>
  </div>
  <div style="display:grid;grid-template-columns:repeat(2, 1fr);gap:10px;font-family:'Share Tech Mono',monospace;font-size:0.73rem;color:#c0d8e8;">
    <div><span style="color:#5a8fa8;">SUB-SATELLITE POINT (SSP):</span> <strong style="color:#00e5ff;">{disp_ssp}</strong></div>
    <div><span style="color:#5a8fa8;">NORAD CATALOG ID:</span> <strong style="color:#e8f4fd;">{sat_spec['norad_id']}</strong></div>
    <div><span style="color:#5a8fa8;">SENSOR PAYLOAD:</span> <strong style="color:#e8f4fd;">{sat_spec['sensor']}</strong></div>
    <div><span style="color:#5a8fa8;">IMAGING SWATH:</span> <strong style="color:#00e5ff;">{sat_spec['swath']}</strong></div>
    <div><span style="color:#5a8fa8;">SPECTRAL CHANNELS:</span> <strong style="color:#e8f4fd;">{sat_spec['channels']}</strong></div>
    <div><span style="color:#5a8fa8;">ORBITAL PERIOD:</span> <strong style="color:#ff8c00;">{sat_spec['period']}</strong></div>
    <div><span style="color:#5a8fa8;">TELEMETRY TIMESTAMP:</span> <strong style="color:#00e5ff;">{disp_time}</strong></div>
    <div><span style="color:#5a8fa8;">TARGET SECTOR LOCK:</span> <strong style="color:#00ff88;">{selected_sector.split(':')[0]} [ACTIVE TRACK]</strong></div>
  </div>
</div>""", unsafe_allow_html=True)


    # Orbit telemetry card
    if st.session_state.orbit_data:
        od = st.session_state.orbit_data
        src_tag = "⚡ LIVE SGP4" if od["source"] == "sgp4" else "◎ SIM TELEMETRY"
        st.markdown(f"""
<div class="orbit-card" style="margin-top:10px;">
  <div style="color:#00e5ff;font-family:'Orbitron',monospace;font-size:0.75rem;margin-bottom:10px;display:flex;justify-content:space-between;">
    <span>▸ {od['satellite'].upper()} — LIVE TELEMETRY</span>
    <span style="color:#3a8fa8;font-size:0.62rem;">{src_tag}</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
    <div><span class="label">LAT / LON &nbsp;</span> {od['latitude']:+.4f}° / {od['longitude']:+.4f}°</div>
    <div><span class="label">ALTITUDE &nbsp;</span> {od['altitude_km']:.1f} km</div>
    <div><span class="label">VELOCITY &nbsp;</span> {od['velocity_km_s']:.4f} km/s</div>
    <div><span class="label">TIMESTAMP</span> {od['timestamp'][11:19]} UTC</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Interactive compare bar chart
    if st.session_state.scan_ran and st.session_state.ai_data:
        ad = st.session_state.ai_data
        with st.expander("📊 Environmental Sensor Deep-Dive", expanded=False):
            compare_df = pd.DataFrame({
                "Layer":  ["Thermal IR", "NDVI Shift", "Atmospheric"],
                "Score":  [ad["thermal_ir_score"], ad["ndvi_score"], ad["atmospheric_score"]],
                "Weight": [0.55, 0.30, 0.15],
            })
            st.dataframe(
                compare_df.style
                    .background_gradient(subset=["Score"], cmap="RdYlGn_r")
                    .format({"Score": "{:.1f}%", "Weight": "{:.0%}"}),
                use_container_width=True, hide_index=True
            )
            st.markdown(f"""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#5a8fa8;margin-top:6px;">
  Raw readings: Thermal {ad['raw_thermal_ir_celsius']}°C &nbsp;|&nbsp;
  NDVI {ad['raw_ndvi_shift']:+.3f} &nbsp;|&nbsp;
  Atm. {ad['raw_atmospheric_anomaly_g_m3']:+.3f} g/m³
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — AI DIAGNOSTICS + DISPATCH
# ══════════════════════════════════════════════════════════════════════════════
with col_ai:
    st.markdown('<div class="section-header">◈ AI Threat Diagnostics & Dispatch Gateway</div>', unsafe_allow_html=True)

    # ── SCAN BUTTON ──
    scan_label = f"🚀  Trigger SGP4 Orbit Pass & AI Threat Scan  (#{st.session_state.scan_count+1})"
    if st.button(scan_label, key="scan_btn"):
        prog = st.progress(0, text="⚙️ Initialising SGP4 propagator …")
        for i in range(0, 35, 5):
            time.sleep(0.07); prog.progress(i, text="⚙️ Computing Keplerian orbital elements …")
        orbit_data = get_satellite_position(sector_info["satellite"], lat, lon)
        for i in range(35, 70, 5):
            time.sleep(0.06); prog.progress(i, text="🧠 Analysing Thermal IR layer …")
        ai_result = analyze_sector_threat(selected_sector, risk)
        for i in range(70, 100, 5):
            time.sleep(0.05); prog.progress(i, text="📡 Synthesising multi-spectral threat index …")
        prog.progress(100, text="✅ Analysis complete!")
        time.sleep(0.4); prog.empty()

        st.session_state.orbit_data      = orbit_data
        st.session_state.ai_data         = ai_result
        st.session_state.scan_ran        = True
        st.session_state.scan_count     += 1
        st.session_state.dispatch_result = None
        st.rerun()

    # ── AI DIAGNOSTIC CARD ──
    if st.session_state.ai_data and st.session_state.scan_ran:
        ad  = st.session_state.ai_data
        css = risk_css_class(ad["risk_level"])
        rl_color = {"CRITICAL":"#ff3c3c","HIGH":"#ff8c00","MODERATE":"#ffd700"}.get(ad["risk_level"],"#ffd700")

        st.markdown(f"""
<div class="ai-card">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <div style="font-family:'Orbitron',monospace;font-size:0.78rem;color:#00e5ff;letter-spacing:1.5px;">
      AI THREAT DIAGNOSTIC — ACTIVE
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#3a6a8a;">
      {ad['analysis_timestamp'][11:19]} UTC
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;">
    <div>
      {threat_gauge_html(ad['threat_confidence'], ad['risk_level'])}
    </div>
    <div style="flex:1;">
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#3a6a8a;">PRIMARY HAZARD</div>
      <div style="font-family:'Orbitron',monospace;font-size:0.95rem;color:{ad['hazard_color']};margin:4px 0;text-shadow:0 0 12px {ad['hazard_color']}88;">
        {ad['hazard_icon']} {ad['hazard_type']}
      </div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#3a6a8a;margin-top:6px;">IMPACT RADIUS</div>
      <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#ff8c00;text-shadow:0 0 10px rgba(255,140,0,0.5);">
        {ad['impact_radius_km']:.0f} km
      </div>
      <div style="margin-top:8px;">
        <span style="font-family:'Orbitron',monospace;font-size:0.68rem;
                     color:{rl_color};letter-spacing:2px;
                     background:rgba(255,60,60,0.1);border:1px solid {rl_color}55;
                     border-radius:20px;padding:2px 10px;">
          ▸ {ad['risk_level']}
        </span>
      </div>
    </div>
  </div>

  <div style="border-top:1px solid rgba(0,229,255,0.1);padding-top:12px;">
    <div style="font-family:'Orbitron',monospace;font-size:0.68rem;color:#00e5ff;letter-spacing:1px;margin-bottom:10px;">
      ▸ ENVIRONMENTAL ANOMALY SENSORS
    </div>
    {sensor_bar_html("🌡️ Thermal IR Surface Layer",   ad['thermal_ir_score'],   "#ff3c3c")}
    {sensor_bar_html("🌿 NDVI Vegetation Shift",       ad['ndvi_score'],         "#ff8c00")}
    {sensor_bar_html("💨 Atmospheric Density Delta",   ad['atmospheric_score'],  "#4b9eff")}
  </div>

  <div style="margin-top:14px;background:rgba(255,60,60,0.06);border:1px solid rgba(255,60,60,0.2);
              border-radius:8px;padding:12px;">
    <div style="font-family:'Orbitron',monospace;font-size:0.68rem;color:#ff8c00;letter-spacing:1px;margin-bottom:6px;">
      ▸ RECOMMENDED AUTONOMOUS ACTION
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.73rem;color:#c0d8e8;line-height:1.55;">
      {ad['recommended_action']}
    </div>
  </div>

  <div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-family:'Share Tech Mono',monospace;font-size:0.7rem;">
    <div style="background:rgba(5,10,22,0.8);border:1px solid rgba(0,229,255,0.1);border-radius:8px;padding:8px;text-align:center;">
      <div style="color:#3a6a8a;font-size:0.62rem;margin-bottom:3px;">Thermal IR</div>
      <div style="color:#ff3c3c;font-family:'Orbitron',monospace;font-size:0.82rem;">{ad['raw_thermal_ir_celsius']:.1f}°C</div>
    </div>
    <div style="background:rgba(5,10,22,0.8);border:1px solid rgba(0,229,255,0.1);border-radius:8px;padding:8px;text-align:center;">
      <div style="color:#3a6a8a;font-size:0.62rem;margin-bottom:3px;">NDVI Δ</div>
      <div style="color:#ff8c00;font-family:'Orbitron',monospace;font-size:0.82rem;">{ad['raw_ndvi_shift']:+.3f}</div>
    </div>
    <div style="background:rgba(5,10,22,0.8);border:1px solid rgba(0,229,255,0.1);border-radius:8px;padding:8px;text-align:center;">
      <div style="color:#3a6a8a;font-size:0.62rem;margin-bottom:3px;">Atm. g/m³</div>
      <div style="color:#4b9eff;font-family:'Orbitron',monospace;font-size:0.82rem;">{ad['raw_atmospheric_anomaly_g_m3']:+.3f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── DISPATCH SECTION ──
        st.markdown('<div class="section-header" style="margin-top:4px;">◈ Autonomous Emergency Dispatch Gateway</div>', unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,60,60,0.06),rgba(255,140,0,0.04));
            border:1px solid rgba(255,60,60,0.28);border-radius:12px;padding:14px;margin-bottom:12px;
            backdrop-filter:blur(10px);">
  <div style="font-family:'Orbitron',monospace;font-size:0.7rem;color:#ff8c00;letter-spacing:1.5px;margin-bottom:10px;">
    ▸ DISPATCH PREVIEW
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.74rem;color:#a0c4d8;line-height:1.75;">
    🚨 <strong style="color:#ff3c3c;">ASTROSHIELD EMERGENCY DISPATCH</strong><br/>
    Hazard: <span style="color:{ad['hazard_color']};">{ad['hazard_type'].upper()}</span><br/>
    Sector: {selected_sector}<br/>
    GPS: {lat:.4f}°N, {lon:.4f}°E<br/>
    Threat Index: <span style="color:#ff3c3c;font-weight:600;">{ad['threat_confidence']:.1f}%</span>
    &nbsp;<span style="color:{rl_color};">[{ad['risk_level']}]</span><br/>
    Impact: {ad['impact_radius_km']:.0f} km radius<br/>
    To: <span style="color:#00e5ff;">+91 ••• ••• ••33 &nbsp;<span style="color:#3a6a8a;font-size:0.65rem;">(secured)</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

        if st.button("⚡ Execute Immediate Emergency Dispatch", key="dispatch_btn"):
            with st.spinner("📡 Connecting to Twilio Emergency Gateway …"):
                time.sleep(0.8)
            result = send_emergency_dispatch(
                account_sid=DEFAULT_TWILIO_ACCOUNT_SID,
                auth_token =DEFAULT_TWILIO_AUTH_TOKEN,
                from_number=DEFAULT_TWILIO_PHONE_NUMBER,
                to_number  =DEFAULT_RECIPIENT_NUMBER,
                sector=selected_sector,
                risk_index=ad["threat_confidence"],
                gps_coords=(lat, lon),
                hazard_type=ad["hazard_type"],
                impact_radius_km=ad["impact_radius_km"],
                risk_level=ad["risk_level"],
            )
            st.session_state.dispatch_result = result
            # Append to log
            st.session_state.alert_log.append({
                "time": datetime.datetime.utcnow().strftime("%H:%M:%S UTC"),
                "sector": selected_sector[:30],
                "status": "✅ SENT" if result["status"] == "success" else ("⚠️ DEMO" if result["status"] == "demo" else "❌ ERROR"),
            })
            st.rerun()

        if st.session_state.dispatch_result:
            dr = st.session_state.dispatch_result
            if dr["status"] == "success":
                st.success(dr["message"])
            elif dr["status"] == "demo":
                st.warning(dr["message"])
            else:
                st.error(dr["message"])
            with st.expander("📋 Full SMS Message Content", expanded=False):
                st.code(dr["sms_body"], language=None)

    else:
        # Pre-scan placeholder
        st.markdown("""
<div class="glass-panel" style="text-align:center;padding:50px 24px;margin-top:8px;">
  <div class="scan-reticle"></div>
  <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00e5ff;letter-spacing:2px;margin-bottom:10px;">
    AWAITING ORBIT PASS TRIGGER
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.76rem;color:#3a6a8a;line-height:1.9;">
    Select a monitoring sector from the sidebar,<br/>
    then click <span style="color:#00e5ff;">🚀 Trigger SGP4 Orbit Pass &amp; AI Threat Scan</span><br/>
    to initiate satellite telemetry acquisition and<br/>
    multi-spectral hazard analysis.
  </div>
  <div style="margin-top:24px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap;font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#1e3a52;">
    <span style="background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.12);padding:4px 10px;border-radius:20px;">SGP4 ENGINE</span>
    <span style="background:rgba(255,60,60,0.06);border:1px solid rgba(255,60,60,0.12);padding:4px 10px;border-radius:20px;">THERMAL IR</span>
    <span style="background:rgba(255,140,0,0.06);border:1px solid rgba(255,140,0,0.12);padding:4px 10px;border-radius:20px;">NDVI LAYER</span>
    <span style="background:rgba(75,158,255,0.06);border:1px solid rgba(75,158,255,0.12);padding:4px 10px;border-radius:20px;">ATMOSPHERIC</span>
    <span style="background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.12);padding:4px 10px;border-radius:20px;">AUTO-DISPATCH</span>
  </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BOTTOM ROW — Sector Comparison + Live Threat Matrix
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">◈ Global Sector Threat Overview Matrix</div>', unsafe_allow_html=True)

overview_cols = st.columns(4)
for i, (sname, sdata) in enumerate(SECTORS.items()):
    is_active = (sname == selected_sector)
    border_col = sdata["color"] if is_active else "rgba(0,229,255,0.12)"
    glow       = f"0 0 20px {sdata['color']}44" if is_active else "none"
    with overview_cols[i]:
        short_name = sname.split(":")[0].strip()
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(8,15,28,0.75),rgba(12,22,40,0.7));
            border:1px solid {border_col};border-radius:12px;padding:14px 12px;
            backdrop-filter:blur(14px);box-shadow:{glow};
            transition:all 0.3s ease;margin-bottom:4px;">
  <div style="font-family:'Orbitron',monospace;font-size:0.72rem;color:#00e5ff;margin-bottom:6px;letter-spacing:1px;">
    {short_name}
    {"&nbsp;<span style='font-size:0.6rem;background:rgba(0,229,255,0.15);border:1px solid rgba(0,229,255,0.3);padding:1px 6px;border-radius:10px;'>ACTIVE</span>" if is_active else ""}
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#5a8fa8;margin-bottom:4px;">{sdata['hazard']}</div>
  <div style="font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:900;color:{sdata['color']};
              text-shadow:0 0 16px {sdata['color']}66;margin:4px 0;">{sdata['risk']}%</div>
  <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:5px;overflow:hidden;">
    <div style="width:{sdata['risk']}%;height:100%;background:linear-gradient(90deg,{sdata['color']}88,{sdata['color']});border-radius:4px;"></div>
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.63rem;color:#3a6a8a;margin-top:6px;">
    {sdata['satellite']} &nbsp;·&nbsp; {sdata['emoji']}
  </div>
</div>""", unsafe_allow_html=True)

# Auto-refresh rerun
if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()
