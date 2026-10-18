🛰️ AstroShield AI

Satellite-Driven Natural Disaster Prediction & Autonomous Emergency Dispatch System

🔗 Live Deployment & Resources

Live Mission Control Dashboard: https://astroshield-ai.streamlit.app (Replace with your actual Streamlit Cloud URL)

GitHub Repository: https://github.com/spcoder333/astroshield-ai

Presentation Platform: Quantex Hackathon 2026

📌 Project Overview

AstroShield AI bridges SpaceTech (Earth Observation), ClimateTech (Disaster Risk Reduction), and Autonomous AI into a unified mission control platform.

The platform ingests Near-Real-Time (NRT) multi-spectral geospatial feeds from NASA GIBS and Copernicus/Sentinel-2 endpoints to continuously monitor planetary hazards (wildfires, floods, thermal anomalies). When dynamic threat scoring algorithms detect high-risk scenarios exceeding critical safety thresholds, AstroShield AI autonomously triggers emergency SMS dispatch alerts to field responders via the Twilio REST API—complete with precise UTC timestamps, risk scores, and GPS impact coordinates.

📸 System Screenshots

1. Real-Time 3D Geospatial Threat Map & Telemetry Dashboard
<img width="1920" height="1080" alt="Screenshot 2026-10-18 145146" src="https://github.com/user-attachments/assets/6e46482e-8599-441e-89c4-dbfdddad29ff" />

Figure 1: Interactive PyDeck 3D threat map displaying height-extruded risk columns, real-time orbital pass calculations, and sector telemetry analysis.

✨ Key Capabilities & System Features

🛰️ Dynamic Earth Observation Feed Ingestion: Connects directly to open-access NASA GIBS and Copernicus WMTS web endpoints, pulling multi-spectral imagery raster tiles stamped with current UTC pass times.

📐 Orbital Telemetry & Coverage Tracking: Calculates exact satellite positions, ground tracks, and pass schedules using SGP4/orbital mechanics principles (orbit_engine.py).

🤖 Predictive Hazard Analytics: Evaluates multi-spectral imagery layers and surface thermal anomalies to score sector threat severity dynamically (ai_engine.py).

🗺️ 3D Volumetric Threat Mapping: Renders extruded 3D height pillars and dynamic risk zones over affected GPS coordinates using PyDeck and Streamlit.

🚨 Agentic Emergency Dispatch Gateway: Automatically builds and transmits structured SMS alerts to emergency response personnel via Twilio when safety indices cross critical thresholds (dispatch_engine.py).

🛠️ Tech Stack & System Architecture

+-----------------------------------------------------------------------------------+
|                                   AstroShield AI                                 |
+-----------------------------------------------------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
[ Earth Observation Data ]       [ Space Telemetry Engine ]       [ AI Threat Analytics ]
- NASA GIBS (WMTS)               - Orbital Mechanics              - Multi-Spectral Analysis
- Copernicus / Sentinel-2        - GPS Target Tracking            - Risk Index Calculation
- UTC Tile Sync                  - Ground Pass Timelines          - Impact Radius Estimation
        |                                 |                                 |
        +---------------------------------+---------------------------------+
                                          |
                                          v
                         [ Streamlit Mission Control UI ]
                         - Interactive PyDeck 3D Globe
                         - Sector Analysis & Metrics
                         - Manual Trigger Controls
                                          |
                                          v
                        [ Autonomous Dispatch Gateway ]
                        - Twilio REST API Integration
                        - Automated SMS Field Alerts


Component

Technologies Used

Frontend / Dashboard

Streamlit, PyDeck (3D Deck.gl overlays), Pandas, NumPy

Data Ingestion

Open-access NASA GIBS, Copernicus WMTS, HTTP REST requests

Space Engine

Python math, datetime, orbital coordinate transformation logic

Emergency Dispatch

Twilio REST API, Python-dotenv, OS environment secrets

Deployment Platform

Streamlit Community Cloud

⚙️ Installation & Local Setup

1. Clone the Repository

git clone https://github.com/spcoder333/astroshield-ai.git
cd astroshield-ai


2. Set Up Virtual Environment

# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


4. Configure Environment Variables

Create a .env file in the root directory:

TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
TWILIO_RECIPIENT_NUMBER=your_recipient_phone_number_here


5. Run the Application Locally

streamlit run app.py

How AstroShield AI Utilizes "Real-Time" Data

In remote sensing, continuous live video feeds from orbit are impractically band-heavy and obscured by weather/nightfall. AstroShield AI utilizes Near-Real-Time (NRT) multi-spectral satellite imagery by querying live NASA GIBS and Copernicus API endpoints. Every time the dashboard updates, it programmatically retrieves UTC-stamped imagery tiles to process real surface thermal and infrared reflectance shifts.

AI Integration

AstroShield AI integrates domain-specific algorithms to perform pixel-level anomaly detection on thermal/infrared bands, compute probabilistic Threat Probability Indices (0.00 - 1.00), estimate dynamic Impact Radii (km), and execute autonomous agentic dispatch workflows when critical thresholds are breached.
