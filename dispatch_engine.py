"""
dispatch_engine.py
AstroShield AI - Autonomous Emergency Dispatch Gateway
Integrates Twilio REST API to fire real-time SMS emergency alerts
to field responders with full error handling and fallback messaging.
"""

from __future__ import annotations
import os
import datetime
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Hardcoded default Twilio credentials (overridable from UI)
# ---------------------------------------------------------------------------

from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Read Twilio credentials dynamically from .env
DEFAULT_TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
DEFAULT_TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
DEFAULT_TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
DEFAULT_RECIPIENT_NUMBER = os.getenv("TWILIO_RECIPIENT_NUMBER", "")


def _build_sms_body(
    hazard_type: str,
    sector_name: str,
    gps_coords: Tuple[float, float],
    risk_index: float,
    impact_radius_km: float,
    risk_level: str,
) -> str:
    """
    Construct the emergency SMS body conforming to the AstroShield
    emergency dispatch protocol.
    """
    lat, lon = gps_coords
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return (
        f"🚨 ASTROSHIELD EMERGENCY DISPATCH\n"
        f"{'─' * 34}\n"
        f"Hazard: {hazard_type.upper()}\n"
        f"Sector: {sector_name}\n"
        f"GPS: {lat:.4f}°N, {lon:.4f}°E\n"
        f"Threat Index: {risk_index:.1f}%  [{risk_level}]\n"
        f"Impact Radius: {impact_radius_km:.0f} km\n"
        f"Time: {timestamp}\n"
        f"{'─' * 34}\n"
        f"⚡ IMMEDIATE EVACUATION RECOMMENDED.\n"
        f"Routes dispatched to local first responders.\n"
        f"AstroShield AI Autonomous Dispatch v1.0"
    )


def send_emergency_dispatch(
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    sector: str,
    risk_index: float,
    gps_coords: Tuple[float, float],
    hazard_type: str = "Unknown Hazard",
    impact_radius_km: float = 0.0,
    risk_level: str = "CRITICAL",
) -> dict:
    """
    Send a real SMS emergency dispatch via Twilio.

    Parameters
    ----------
    account_sid     : Twilio Account SID
    auth_token      : Twilio Auth Token
    from_number     : Verified Twilio sender number (+E.164)
    to_number       : Recipient phone number (+E.164)
    sector          : Human-readable sector name
    risk_index      : Hazard Threat Index (0–100)
    gps_coords      : (latitude, longitude) tuple
    hazard_type     : Primary hazard classification string
    impact_radius_km: Estimated impact radius in kilometres
    risk_level      : "CRITICAL" | "HIGH" | "MODERATE"

    Returns
    -------
    dict:
      status     : "success" | "error" | "demo"
      message    : Status detail string
      sms_sid    : Twilio message SID (on success)
      sms_body   : The constructed message body
    """
    # Use defaults for any blank/None values
    account_sid = (account_sid or "").strip() or DEFAULT_TWILIO_ACCOUNT_SID
    auth_token  = (auth_token  or "").strip() or DEFAULT_TWILIO_AUTH_TOKEN
    from_number = (from_number or "").strip() or DEFAULT_TWILIO_PHONE_NUMBER
    to_number   = (to_number   or "").strip() or DEFAULT_RECIPIENT_NUMBER

    sms_body = _build_sms_body(
        hazard_type=hazard_type,
        sector_name=sector,
        gps_coords=gps_coords,
        risk_index=risk_index,
        impact_radius_km=impact_radius_km,
        risk_level=risk_level,
    )

    # Guard: refuse to send if credentials look placeholder-like
    if len(account_sid) < 10 or len(auth_token) < 10:
        return {
            "status": "demo",
            "message": (
                "⚠️  No valid Twilio credentials provided. "
                "Running in demo mode — SMS not sent."
            ),
            "sms_sid": None,
            "sms_body": sms_body,
        }

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=sms_body,
            from_=from_number,
            to=to_number,
        )

        return {
            "status": "success",
            "message": (
                f"✅ SMS dispatched successfully!\n"
                f"Twilio SID: {message.sid}\n"
                f"To: {to_number}  |  Status: {message.status}"
            ),
            "sms_sid": message.sid,
            "sms_body": sms_body,
        }

    except Exception as exc:
        exc_str = str(exc)

        # Friendly error categorisation
        if "authenticate" in exc_str.lower() or "20003" in exc_str:
            friendly = (
                "❌ Authentication failed — check your Twilio Auth Token. "
                "SMS not sent."
            )
        elif "21608" in exc_str or "unverified" in exc_str.lower():
            friendly = (
                "❌ Recipient number is unverified on your Twilio trial account. "
                "Verify the number at twilio.com/user/account/phone-numbers/verified."
            )
        elif "21212" in exc_str or "invalid" in exc_str.lower():
            friendly = (
                "❌ Invalid sender or recipient phone number format. "
                "Use E.164 format, e.g. +919994104033."
            )
        else:
            friendly = f"❌ Twilio error: {exc_str[:200]}"

        return {
            "status": "error",
            "message": friendly,
            "sms_sid": None,
            "sms_body": sms_body,
        }
