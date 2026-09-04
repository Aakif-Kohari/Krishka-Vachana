"""Tests for phone-number OTP verification (Phase 3).

The SMS gateway is unconfigured by default in tests (see .env.example /
Settings defaults). OTP generation is patched to a known value because
delivery logs intentionally redact both the destination and code.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event

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
    """Test that requesting OTP without a registered profile returns 404."""
    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    assert r.status_code == 404


def test_request_otp_success(client, auth_headers, monkeypatch, caplog):
    """Test OTP requests return before delivery and do not log sensitive data."""
    _register_farmer(client, auth_headers)
    code = "123456"
    started = Event()
    release = Event()

    def slow_delivery(*_args):
        started.set()
        release.wait(timeout=2)
        return True

    monkeypatch.setattr(otp_service.secrets, "randbelow", lambda _upper_bound: int(code))
    monkeypatch.setattr(otp_service, "send_sms", slow_delivery)
    try:
        with caplog.at_level(logging.INFO), ThreadPoolExecutor(max_workers=1) as caller:
            pending = caller.submit(
                client.post,
                "/api/v1/farmers/me/phone/otp/request",
                headers=auth_headers,
            )
            assert started.wait(timeout=1)
            r = pending.result(timeout=0.5)
    finally:
        release.set()

    assert r.status_code == 200
    assert r.json() == {"message": "Verification code sent", "expires_in_seconds": 600}
    assert code not in caplog.text
    assert FARMER_PAYLOAD["phone_number"] not in caplog.text


def test_request_otp_rejects_requests_during_cooldown(client, auth_headers, monkeypatch):
    """Test that repeated requests cannot trigger another SMS during cooldown."""
    _register_farmer(client, auth_headers)
    sent_messages = []
    delivered = Event()

    def record_message(_settings, _phone_number, message):
        sent_messages.append(message)
        delivered.set()
        return True

    monkeypatch.setattr(
        otp_service,
        "send_sms",
        record_message,
    )

    first = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)
    second = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)

    assert first.status_code == 200
    assert second.status_code == 409
    assert delivered.wait(timeout=1)
    assert len(sent_messages) == 1


def test_request_otp_allows_request_after_cooldown(farmer_repo, monkeypatch):
    """Test that normal OTP issuance resumes when the cooldown expires."""
    farmer_repo.create("farmer-id", {"phone_number": "9876543210"})
    issued_at = datetime(2026, 9, 4, 8, tzinfo=timezone.utc)
    request_times = iter([issued_at, issued_at + timedelta(seconds=60)])
    deliveries = []
    both_delivered = Event()

    def record_delivery(*_args):
        deliveries.append(True)
        if len(deliveries) == 2:
            both_delivered.set()
        return True

    monkeypatch.setattr(otp_service, "utcnow", lambda: next(request_times))
    monkeypatch.setattr(otp_service, "send_sms", record_delivery)

    otp_service.request_otp(Settings(), farmer_repo, "farmer-id")
    otp_service.request_otp(Settings(), farmer_repo, "farmer-id")

    assert both_delivered.wait(timeout=1)
    assert farmer_repo.get("farmer-id")["phone_otp_issued_at"] == issued_at + timedelta(seconds=60)


def test_farmer_starts_unverified(client, auth_headers):
    """Test that newly registered farmers have phone_verified set to False."""
    _register_farmer(client, auth_headers)
    r = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert r.json()["phone_verified"] is False


def test_verify_otp_success(client, auth_headers, monkeypatch):
    """Test successful OTP verification sets phone_verified to True."""
    _register_farmer(client, auth_headers)
    code = _request_known_code(client, auth_headers, monkeypatch)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)

    assert r.status_code == 200
    assert r.json() == {"phone_verified": True}

    profile = client.get("/api/v1/farmers/me", headers=auth_headers)
    assert profile.json()["phone_verified"] is True


def test_verify_otp_wrong_code(client, auth_headers, monkeypatch):
    """Test that submitting an incorrect OTP code returns validation error."""
    _register_farmer(client, auth_headers)
    _request_known_code(client, auth_headers, monkeypatch)

    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)

    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_verify_otp_without_request_is_conflict(client, auth_headers):
    """Test that verifying OTP without requesting one first returns conflict."""
    _register_farmer(client, auth_headers)
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "123456"}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_too_many_attempts_invalidates_code(client, auth_headers, monkeypatch):
    """Test that exceeding max attempts locks out the OTP code."""
    _register_farmer(client, auth_headers)
    code = _request_known_code(client, auth_headers, monkeypatch)

    for _ in range(5):
        r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": "000000"}, headers=auth_headers)
        assert r.status_code == 422

    # The code is now invalidated even though it was correct all along.
    r = client.post("/api/v1/farmers/me/phone/otp/verify", json={"otp_code": code}, headers=auth_headers)
    assert r.status_code == 409


def test_verify_otp_expired(client, auth_headers, monkeypatch, farmer_repo):
    """Test that expired OTP codes are rejected."""
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
    """Test that OTP internal fields are never exposed in farmer profile responses."""
    _register_farmer(client, auth_headers)
    _request_known_code(client, auth_headers, monkeypatch)

    profile = client.get("/api/v1/farmers/me", headers=auth_headers)
    body = profile.json()
    assert "phone_otp_hash" not in body
    assert "phone_otp_expires_at" not in body
    assert "phone_otp_attempts" not in body
    assert "phone_otp_issued_at" not in body


def test_request_otp_respects_custom_settings(client, auth_headers):
    """Test that OTP request respects custom TTL from settings."""
    from app.core.config import get_settings
    from app.main import app

    _register_farmer(client, auth_headers)
    app.dependency_overrides[get_settings] = lambda: Settings(otp_ttl_seconds=120)

    r = client.post("/api/v1/farmers/me/phone/otp/request", headers=auth_headers)

    assert r.status_code == 200
    assert r.json()["expires_in_seconds"] == 120


@pytest.mark.parametrize(
    ("ttl_seconds", "expected_lifetime"),
    [
        (1, "1 second"),
        (30, "30 seconds"),
        (60, "1 minute"),
        (61, "2 minutes"),
        (120, "2 minutes"),
    ],
)
def test_request_otp_formats_expiration_lifetime(
    farmer_repo, monkeypatch, ttl_seconds, expected_lifetime
):
    """Test that OTP expiration messages are properly formatted for different TTL values."""
    farmer_repo.create("farmer-id", {"phone_number": "9876543210"})
    sent_messages = []
    delivered = Event()

    def record_message(_settings, _phone_number, message):
        sent_messages.append(message)
        delivered.set()
        return True

    monkeypatch.setattr(
        otp_service,
        "send_sms",
        record_message,
    )

    otp_service.request_otp(
        Settings(otp_ttl_seconds=ttl_seconds), farmer_repo, "farmer-id"
    )

    assert delivered.wait(timeout=1)
    assert sent_messages[0].endswith(f"It expires in {expected_lifetime}.")


@pytest.mark.parametrize(
    "field", ["otp_length", "otp_ttl_seconds", "otp_max_attempts", "otp_request_cooldown_seconds"]
)
@pytest.mark.parametrize("value", [0, -1])
def test_otp_settings_reject_non_positive_values(field, value):
    """Test that OTP settings reject non-positive numeric values."""
    with pytest.raises(ValidationError):
        Settings(**{field: value})


@pytest.mark.parametrize("value", [3, 9])
def test_otp_settings_reject_length_outside_request_schema_range(value):
    """Test that configured OTP length stays within the request schema's 4-8 range."""
    with pytest.raises(ValidationError):
        Settings(otp_length=value)


def test_concurrent_valid_otp_can_only_be_consumed_once(farmer_repo):
    """Test that concurrent OTP verification attempts can only succeed once."""
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
        """Helper to verify OTP and return result status."""
        try:
            otp_service.verify_otp(Settings(), farmer_repo, "farmer-id", code)
            return "verified"
        except ConflictError:
            return "consumed"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(verify, range(2)))

    assert sorted(results) == ["consumed", "verified"]
    assert farmer_repo.get("farmer-id")["phone_verified"] is True
