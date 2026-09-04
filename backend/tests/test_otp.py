"""Tests for phone-number OTP verification (Phase 3).

The SMS gateway is unconfigured by default in tests (see .env.example /
Settings defaults), so every request_otp call takes the dry-run path in
app/core/sms.py and logs the code instead of sending it - these tests
recover the code from caplog, mirroring test_health.py's
`test_readiness_hides_firestore_exception` pattern for asserting on
logged content.
"""
import logging
import re

from app.core.config import Settings

FARMER_PAYLOAD = {
    "full_name": "Ravi Kumar",
    "phone_number": "9876543210",
    "aadhaar_number": "123456789012",
    "village": "Rajpur",
    "district": "Solapur",
    "state": "Maharashtra",
    "preferred_language": "mr",
}


def _register_farmer(client, auth_headers):
    """Register a farmer profile for OTP testing."""
    r = client.post("/api/v1/farmers/register", json=FARMER_PAYLOAD, headers=auth_headers)
    assert r.status_code == 201
    return r.json()


def _request_and_capture_code(client, auth_headers, caplog) -> str:
    """Request an OTP and extract the code from the dry-run log message."""
    with caplog.at_level(logging.INFO, logger="app.otp"):
        r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 200, r.json()
    match = re.search(r"dry run.*?:\s*(\d+)", caplog.text)
    assert match, f"could not find OTP code in logs: {caplog.text!r}"
    return match.group(1)


def test_request_otp_requires_registration(client, auth_headers):
    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 404


def test_request_otp_success(client, auth_headers, caplog):
    _register_farmer(client, auth_headers)
    with caplog.at_level(logging.INFO, logger="app.otp"):
        r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {"message": "Verification code sent", "expires_in_seconds": 600}


def test_farmer_starts_unverified(client, auth_headers):
    _register_farmer(client, auth_headers)
    r = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert r.json()["phone_verified"] is False


def test_verify_otp_success(client, auth_headers, caplog):
    _register_farmer(client, auth_headers)
    code = _request_and_capture_code(client, auth_headers, caplog)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)

    assert r.status_code == 200
    assert r.json() == {"phone_verified": True}

    profile = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert profile.json()["phone_verified"] is True


def test_verify_otp_wrong_code(client, auth_headers, caplog):
    _register_farmer(client, auth_headers)
    _request_and_capture_code(client, auth_headers, caplog)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)

    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_verify_otp_without_request_is_conflict(client, auth_headers):
    _register_farmer(client, auth_headers)
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "123456"}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_too_many_attempts_invalidates_code(client, auth_headers, caplog):
    _register_farmer(client, auth_headers)
    code = _request_and_capture_code(client, auth_headers, caplog)

    for _ in range(5):
        r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)
        assert r.status_code == 422

    # The code is now invalidated even though it was correct all along.
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_expired(client, auth_headers, caplog, farmer_repo):
    from datetime import datetime, timedelta, timezone

    farmer = _register_farmer(client, auth_headers)
    code = _request_and_capture_code(client, auth_headers, caplog)

    # Force the stored expiry into the past without touching otp_service's logic.
    farmer_repo.update(
        farmer["farmer_id"],
        {"phone_otp_expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)},
    )

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)
    assert r.status_code == 409


def test_otp_hash_never_returned_in_farmer_response(client, auth_headers, caplog):
    _register_farmer(client, auth_headers)
    _request_and_capture_code(client, auth_headers, caplog)

    profile = client.get("/api/v1/farmers/me", headers=auth_headers)
    body = profile.json()
    assert "phone_otp_hash" not in body
    assert "phone_otp_expires_at" not in body
    assert "phone_otp_attempts" not in body


def test_request_otp_respects_custom_settings(client, auth_headers):
    from app.core.config import get_settings
    from app.main import app

    _register_farmer(client, auth_headers)
    app.dependency_overrides[get_settings] = lambda: Settings(otp_ttl_seconds=120)

    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)

    assert r.status_code == 200
    assert r.json()["expires_in_seconds"] == 120
