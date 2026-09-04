"""Tests for phone-number OTP verification (Phase 3).

The SMS gateway is unconfigured by default in tests (see .env.example /
Settings defaults). OTP generation is patched to a known value because
delivery logs intentionally redact both the destination and code.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import ConflictError
from app.services import otp_service

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


def _request_known_code(client, auth_headers, monkeypatch) -> str:
    """Request an OTP after replacing randomness with a deterministic value."""
    code = "123456"
    monkeypatch.setattr(otp_service.secrets, "randbelow", lambda _upper_bound: int(code))
    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 200, r.json()
    return code


def test_request_otp_requires_registration(client, auth_headers):
    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 404


def test_request_otp_success(client, auth_headers, monkeypatch, caplog):
    _register_farmer(client, auth_headers)
    code = "123456"
    monkeypatch.setattr(otp_service.secrets, "randbelow", lambda _upper_bound: int(code))
    with caplog.at_level(logging.INFO):
        r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)

    assert r.status_code == 200
    assert r.json() == {"message": "Verification code sent", "expires_in_seconds": 600}
    assert code not in caplog.text
    assert FARMER_PAYLOAD["phone_number"] not in caplog.text


def test_farmer_starts_unverified(client, auth_headers):
    _register_farmer(client, auth_headers)
    r = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert r.json()["phone_verified"] is False


def test_verify_otp_success(client, auth_headers, monkeypatch):
    _register_farmer(client, auth_headers)
    code = _request_known_code(client, auth_headers, monkeypatch)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)

    assert r.status_code == 200
    assert r.json() == {"phone_verified": True}

    profile = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert profile.json()["phone_verified"] is True


def test_verify_otp_wrong_code(client, auth_headers, monkeypatch):
    _register_farmer(client, auth_headers)
    _request_known_code(client, auth_headers, monkeypatch)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)

    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_verify_otp_without_request_is_conflict(client, auth_headers):
    _register_farmer(client, auth_headers)
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "123456"}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_too_many_attempts_invalidates_code(client, auth_headers, monkeypatch):
    _register_farmer(client, auth_headers)
    code = _request_known_code(client, auth_headers, monkeypatch)

    for _ in range(5):
        r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)
        assert r.status_code == 422

    # The code is now invalidated even though it was correct all along.
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_expired(client, auth_headers, monkeypatch, farmer_repo):
    farmer = _register_farmer(client, auth_headers)
    code = _request_known_code(client, auth_headers, monkeypatch)

    # Force the stored expiry into the past without touching otp_service's logic.
    farmer_repo.update(
        farmer["farmer_id"],
        {"phone_otp_expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)},
    )

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)
    assert r.status_code == 409


def test_otp_hash_never_returned_in_farmer_response(client, auth_headers, monkeypatch):
    _register_farmer(client, auth_headers)
    _request_known_code(client, auth_headers, monkeypatch)

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


@pytest.mark.parametrize("field", ["otp_length", "otp_ttl_seconds", "otp_max_attempts"])
@pytest.mark.parametrize("value", [0, -1])
def test_otp_settings_reject_non_positive_values(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_concurrent_valid_otp_can_only_be_consumed_once(farmer_repo):
    code = "123456"
    farmer_repo.create(
        "farmer-id",
        {
            "phone_otp_hash": otp_service._hash_code(code),
            "phone_otp_expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
            "phone_otp_attempts": 0,
            "phone_verified": False,
        },
    )

    def verify(_):
        try:
            otp_service.verify_otp(Settings(), farmer_repo, "farmer-id", code)
            return "verified"
        except ConflictError:
            return "consumed"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(verify, range(2)))

    assert sorted(results) == ["consumed", "verified"]
    assert farmer_repo.get("farmer-id")["phone_verified"] is True
