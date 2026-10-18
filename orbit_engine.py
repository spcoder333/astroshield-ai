"""
orbit_engine.py
AstroShield AI – SGP4 Orbital Mechanics Engine
Computes satellite positions, altitude, velocity, and pass trajectories
using real TLE data with deterministic mock fallback.
"""

import math
import time
import datetime
import numpy as np
import requests
from sgp4.api import Satrec, jday

# ---------------------------------------------------------------------------
# TLE Data – hardcoded fallback (updated periodically)
# ---------------------------------------------------------------------------
FALLBACK_TLES = {
    "Sentinel-2A": (
        "1 40697U 15028A   24290.50000000  .00000000  00000-0  00000-0 0  9999",
        "2 40697  98.5703  50.0000 0001000  90.0000 270.0000 14.30818144 99999",
    ),
    "Landsat-9": (
        "1 49260U 21088A   24290.50000000  .00000000  00000-0  00000-0 0  9999",
        "2 49260  98.2216  51.2500 0001362  82.1234 278.0100 14.57110499 99999",
    ),
    "ISS (ZARYA)": (
        "1 25544U 98067A   24290.50000000  .00014600  00000-0  00000-0 0  9999",
        "2 25544  51.6416 180.0000 0002850  25.0000 335.0000 15.49957275 99999",
    ),
}

# CelesTrak live TLE endpoint
CELESTRAK_URL = "https://celestrak.org/SATCAT/tle.php?FORMAT=tle"
CELESTRAK_NAMED = {
    "Sentinel-2A": "https://celestrak.org/satcat/tle.php?CATNR=40697",
    "Landsat-9":   "https://celestrak.org/satcat/tle.php?CATNR=49260",
    "ISS (ZARYA)": "https://celestrak.org/satcat/tle.php?CATNR=25544",
}


def _fetch_live_tle(satellite_name: str):
    """Attempt to fetch a live TLE from CelesTrak. Returns (line1, line2) or None."""
    url = CELESTRAK_NAMED.get(satellite_name)
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            lines = [l.strip() for l in resp.text.strip().splitlines() if l.strip()]
            # Expected format: [Name, Line1, Line2]
            if len(lines) >= 3:
                return lines[1], lines[2]
            elif len(lines) == 2:
                return lines[0], lines[1]
    except Exception:
        pass
    return None


def _get_tle(satellite_name: str):
    """Return (line1, line2) – live if available, else hardcoded fallback."""
    live = _fetch_live_tle(satellite_name)
    if live:
        return live
    return FALLBACK_TLES.get(satellite_name, FALLBACK_TLES["Sentinel-2A"])


def _sgp4_position(line1: str, line2: str, dt: datetime.datetime):
    """
    Propagate a satellite at datetime dt using SGP4.
    Returns (lat_deg, lon_deg, alt_km, velocity_km_s).
    """
    sat = Satrec.twoline2rv(line1, line2)
    yr, mo, day = dt.year, dt.month, dt.day
    hr, mn, sec = dt.hour, dt.minute, dt.second + dt.microsecond / 1e6
    jd, fr = jday(yr, mo, day, hr, mn, sec)
    e, r, v = sat.sgp4(jd, fr)

    if e != 0:
        raise RuntimeError(f"SGP4 propagation error code {e}")

    # ECI → geodetic (approximate)
    x, y, z = r  # km
    vx, vy, vz = v  # km/s

    # Earth rotation angle (GMST)
    gmst_rad = _gmst(jd + fr)
    lon_rad = math.atan2(y, x) - gmst_rad
    lon_rad = (lon_rad + math.pi) % (2 * math.pi) - math.pi

    r_xy = math.sqrt(x**2 + y**2)
    lat_rad = math.atan2(z, r_xy)

    # Iterative geodetic latitude (WGS-84)
    a = 6378.137   # km
    f = 1 / 298.257223563
    e2 = 2 * f - f**2
    for _ in range(5):
        N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
        r_norm = math.sqrt(x**2 + y**2 + z**2)
        lat_rad = math.atan2(z + e2 * N * math.sin(lat_rad), r_xy)

    alt_km = r_norm - a

    velocity_km_s = math.sqrt(vx**2 + vy**2 + vz**2)

    return (
        math.degrees(lat_rad),
        math.degrees(lon_rad),
        round(alt_km, 2),
        round(velocity_km_s, 4),
    )


def _gmst(jd_ut1: float) -> float:
    """Compute Greenwich Mean Sidereal Time in radians."""
    T = (jd_ut1 - 2451545.0) / 36525.0
    theta = (
        67310.54841
        + (876600.0 * 3600 + 8640184.812866) * T
        + 0.093104 * T**2
        - 6.2e-6 * T**3
    )
    return math.radians(theta % 86400 / 240.0)


def _mock_telemetry(satellite_name: str, sector_lat: float, sector_lon: float):
    """
    Deterministic mock telemetry for when SGP4 propagation fails.
    Offsets from sector coordinates to simulate a realistic overhead pass.
    """
    seed = hash(satellite_name) % 1000
    np.random.seed(seed)
    lat = sector_lat + np.random.uniform(-3.0, 3.0)
    lon = sector_lon + np.random.uniform(-3.0, 3.0)

    alt_map = {"Sentinel-2A": 786.0, "Landsat-9": 705.0, "ISS (ZARYA)": 408.0}
    vel_map = {"Sentinel-2A": 7.46, "Landsat-9": 7.50, "ISS (ZARYA)": 7.66}

    return {
        "satellite": satellite_name,
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "altitude_km": alt_map.get(satellite_name, 750.0),
        "velocity_km_s": vel_map.get(satellite_name, 7.5),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source": "mock",
        "pass_trajectory": _generate_pass_arc(lat, lon),
    }


def _generate_pass_arc(center_lat: float, center_lon: float, n_points: int = 20):
    """Generate a list of [lon, lat] waypoints representing a polar orbital arc."""
    arc = []
    for i in range(n_points):
        t = (i - n_points // 2) / (n_points // 2)
        arc.append(
            [
                round(center_lon + t * 6.0, 4),
                round(center_lat - t * 2.0, 4),
            ]
        )
    return arc


def get_satellite_position(
    satellite_name: str,
    sector_lat: float,
    sector_lon: float,
) -> dict:
    """
    Primary entry point.
    Attempts real SGP4 propagation; falls back to deterministic mock.

    Returns dict with:
      satellite, latitude, longitude, altitude_km, velocity_km_s,
      timestamp, source, pass_trajectory
    """
    try:
        line1, line2 = _get_tle(satellite_name)
        now = datetime.datetime.utcnow()
        lat, lon, alt, vel = _sgp4_position(line1, line2, now)

        return {
            "satellite": satellite_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "altitude_km": alt,
            "velocity_km_s": vel,
            "timestamp": now.isoformat() + "Z",
            "source": "sgp4",
            "pass_trajectory": _generate_pass_arc(lat, lon),
        }

    except Exception:
        return _mock_telemetry(satellite_name, sector_lat, sector_lon)
