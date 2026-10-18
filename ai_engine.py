"""
ai_engine.py
AstroShield AI – Hazard Threat Analysis Engine
Computes the Hazard Threat Index using simulated satellite-derived
environmental sensor layers: Thermal IR, NDVI, Atmospheric Density.
"""

import math
import random
import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Hazard type definitions
# ---------------------------------------------------------------------------
HAZARD_PROFILES = {
    "Wildfire": {
        "thermal_weight": 0.55,
        "ndvi_weight": 0.30,
        "atmospheric_weight": 0.15,
        "color": "#ff4b4b",
        "icon": "🔥",
        "responder": "Cal Fire Aviation Division + USFS Hotshot Crews",
        "evac_protocol": "Zone A–C immediate evacuation. Highway 1 northbound corridor activated.",
    },
    "Flash Flood": {
        "thermal_weight": 0.10,
        "ndvi_weight": 0.35,
        "atmospheric_weight": 0.55,
        "color": "#4b9eff",
        "icon": "🌊",
        "responder": "FEMA Urban Search & Rescue + National Guard Swift Water Teams",
        "evac_protocol": "Lowland riverine zones cleared. Emergency shelters at elevation > 30 m.",
    },
    "Deforestation/Thermal Spike": {
        "thermal_weight": 0.40,
        "ndvi_weight": 0.45,
        "atmospheric_weight": 0.15,
        "color": "#ff9900",
        "icon": "🌳",
        "responder": "IBAMA Rapid Response + Brazilian Air Force Recon",
        "evac_protocol": "Indigenous territory buffer established. Aerial monitoring active.",
    },
    "Thermal Anomaly": {
        "thermal_weight": 0.70,
        "ndvi_weight": 0.15,
        "atmospheric_weight": 0.15,
        "color": "#ffcc00",
        "icon": "⚡",
        "responder": "Civil Protection Authority + Satellite Ground Station Teams",
        "evac_protocol": "Precautionary standby. Infrastructure inspection ordered.",
    },
}

# ---------------------------------------------------------------------------
# Sector baseline environmental parameters
# ---------------------------------------------------------------------------
SECTOR_ENV_BASELINES = {
    "Sector Alpha: California Coastal Forest": {
        "primary_hazard": "Wildfire",
        "thermal_ir_baseline": 42.5,   # °C surface anomaly
        "ndvi_shift": -0.38,            # vegetation loss index (–1 to 0)
        "atmospheric_density_anomaly": 0.12,  # g/m³ particulate above baseline
    },
    "Sector Beta: Amazon Basin Canopy": {
        "primary_hazard": "Deforestation/Thermal Spike",
        "thermal_ir_baseline": 38.2,
        "ndvi_shift": -0.47,
        "atmospheric_density_anomaly": 0.09,
    },
    "Sector Gamma: Mediterranean Sector": {
        "primary_hazard": "Thermal Anomaly",
        "thermal_ir_baseline": 22.1,
        "ndvi_shift": -0.12,
        "atmospheric_density_anomaly": 0.04,
    },
    "Sector Delta: Southeast Asia Delta": {
        "primary_hazard": "Flash Flood",
        "thermal_ir_baseline": 18.7,
        "ndvi_shift": -0.22,
        "atmospheric_density_anomaly": 0.41,
    },
}


def _compute_thermal_ir_score(baseline: float) -> float:
    """
    Normalise thermal IR anomaly (°C) to 0–1 score.
    Critical threshold: 45°C surface anomaly → score 1.0
    """
    return min(baseline / 45.0, 1.0)


def _compute_ndvi_score(ndvi_shift: float) -> float:
    """
    Normalise NDVI shift to 0–1 threat score.
    A shift of –0.5 (50% canopy loss) → score 1.0.
    """
    return min(abs(ndvi_shift) / 0.5, 1.0)


def _compute_atmospheric_score(density_anomaly: float) -> float:
    """
    Normalise atmospheric particulate anomaly to 0–1 score.
    Threshold: 0.5 g/m³ above baseline → score 1.0
    """
    return min(density_anomaly / 0.5, 1.0)


def _add_stochastic_noise(value: float, amplitude: float = 0.04) -> float:
    """Add small Gaussian noise to simulate real sensor variance."""
    noise = random.gauss(0, amplitude)
    return max(0.0, min(1.0, value + noise))


def _classify_risk(threat_index: float) -> str:
    if threat_index >= 80:
        return "CRITICAL"
    elif threat_index >= 55:
        return "HIGH"
    elif threat_index >= 30:
        return "MODERATE"
    return "LOW"


def _compute_impact_radius(threat_index: float, hazard_type: str) -> float:
    """
    Estimate impact radius in km based on threat index and hazard type.
    Uses an exponential growth model calibrated per hazard class.
    """
    base_km = {
        "Wildfire": 85.0,
        "Flash Flood": 60.0,
        "Deforestation/Thermal Spike": 120.0,
        "Thermal Anomaly": 40.0,
    }.get(hazard_type, 50.0)

    return round(base_km * (threat_index / 100.0) ** 0.7, 1)


def _recommended_action(
    hazard_type: str,
    risk_level: str,
    profile: dict,
) -> str:
    urgency = {
        "CRITICAL": "IMMEDIATE",
        "HIGH": "URGENT",
        "MODERATE": "ELEVATED",
        "LOW": "MONITORING",
    }.get(risk_level, "MONITORING")

    return (
        f"[{urgency}] Deploy {profile['responder']}. "
        f"{profile['evac_protocol']}"
    )


def analyze_sector_threat(sector_name: str, base_risk: float) -> dict:
    """
    Compute a full hazard threat analysis for a given sector.

    Parameters
    ----------
    sector_name : str
        Name matching SECTOR_ENV_BASELINES keys.
    base_risk   : float
        Baseline risk percentage (0–100) defined per sector.

    Returns
    -------
    dict with keys:
      hazard_type, threat_confidence, risk_level, recommended_action,
      impact_radius_km, thermal_ir_score, ndvi_score, atmospheric_score,
      raw_thermal_ir, raw_ndvi_shift, raw_atmospheric_anomaly,
      analysis_timestamp
    """
    env = SECTOR_ENV_BASELINES.get(sector_name, {
        "primary_hazard": "Thermal Anomaly",
        "thermal_ir_baseline": 20.0,
        "ndvi_shift": -0.10,
        "atmospheric_density_anomaly": 0.05,
    })

    hazard_type = env["primary_hazard"]
    profile = HAZARD_PROFILES[hazard_type]

    # Raw sensor layer scores
    thermal_score = _add_stochastic_noise(
        _compute_thermal_ir_score(env["thermal_ir_baseline"])
    )
    ndvi_score = _add_stochastic_noise(
        _compute_ndvi_score(env["ndvi_shift"])
    )
    atm_score = _add_stochastic_noise(
        _compute_atmospheric_score(env["atmospheric_density_anomaly"])
    )

    # Weighted Hazard Threat Index
    hti_raw = (
        profile["thermal_weight"] * thermal_score
        + profile["ndvi_weight"] * ndvi_score
        + profile["atmospheric_weight"] * atm_score
    )

    # Blend with the sector's defined base risk for calibration
    base_factor = base_risk / 100.0
    hti_blended = 0.6 * hti_raw + 0.4 * base_factor
    threat_index = round(min(hti_blended * 100.0, 100.0), 1)

    risk_level = _classify_risk(threat_index)
    impact_radius = _compute_impact_radius(threat_index, hazard_type)
    action = _recommended_action(hazard_type, risk_level, profile)

    return {
        "hazard_type": hazard_type,
        "hazard_icon": profile["icon"],
        "hazard_color": profile["color"],
        "threat_confidence": threat_index,
        "risk_level": risk_level,
        "recommended_action": action,
        "impact_radius_km": impact_radius,
        "thermal_ir_score": round(thermal_score * 100, 1),
        "ndvi_score": round(ndvi_score * 100, 1),
        "atmospheric_score": round(atm_score * 100, 1),
        "raw_thermal_ir_celsius": env["thermal_ir_baseline"],
        "raw_ndvi_shift": env["ndvi_shift"],
        "raw_atmospheric_anomaly_g_m3": env["atmospheric_density_anomaly"],
        "analysis_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
