"""Tests for the payment tracking system."""
import hashlib
import hmac
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.main import app


WEBHOOK_SECRET = "q7L9vN2xK4mP8rT5wY1cF6hJ3sU0aB9dE2gI7kM"


@pytest.mark.parametrize(
    "secret",
    [
        "",
        "short",
        " " + "a" * 32,
        "a" * 32 + " ",
        "a" * 32,
        "abcd" * 8,
        "replace-with-a-random-secret-at-least-32-characters",
    ],
)
def test_production_settings_reject_invalid_webhook_secret_syntax(secret):
    """Verify that production settings reject invalid webhook secret syntax."""
    with pytest.raises(ValidationError):
        Settings(environment="production", payment_gateway_webhook_secret=secret)


def test_production_settings_accept_minimum_length_webhook_secret():
    """Verify that production settings accept minimum-length webhook secrets."""
    secret = "q7L9vN2xK4mP8rT5wY1cF6hJ3sU0aB9d"
    assert Settings(
        environment="production", payment_gateway_webhook_secret=secret
    ).payment_gateway_webhook_secret == secret


def test_development_settings_allow_unset_webhook_secret():
    """Verify that development settings allow unset webhook secrets."""
    assert Settings(
        environment="development", payment_gateway_webhook_secret=""
    ).payment_gateway_webhook_secret == ""


def _create_booking(booking_repo, booking_id="booking-1"):
    return booking_repo.create_if_capacity_available(
        booking_id,
        10,
        {
            "farmer_id": "test-farmer-uid-123",
            "centre_id": "ctr-1",
            "slot_date": "2026-10-01",
            "slot_window": "08:00-10:00",
            "status": "confirmed",
        },
    )


def test_record_payment_success(client: TestClient, auth_headers, booking_repo):
    """Development mock payments persist integer paise end to end."""
    _create_booking(booking_repo)

    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 500000, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )

    assert res.status_code == 201
    assert res.json()["status"] == "success"
    assert res.json()["amount_paise"] == 500000
    assert isinstance(res.json()["amount_paise"], int)


def test_record_payment_duplicate_returns_existing(
    client: TestClient, auth_headers, booking_repo
):
    """Repeated delivery for a booking returns the originally stored payment."""
    _create_booking(booking_repo)
    first = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 500000, "transaction_ref": "TXN_001"},
        headers=auth_headers,
    )
    second = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 999999, "transaction_ref": "TXN_002"},
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json() == first.json()


def test_record_payment_invalid_booking(client: TestClient, auth_headers):
    """Verify that recording a payment for an invalid booking fails."""
    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "missing", "amount_paise": 500000, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_record_payment_rejects_non_integer_amount(client: TestClient, auth_headers):
    """Verify that non-integer payment amounts are rejected."""
    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 5000.5, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_mock_payment_is_rejected_outside_development(
    client: TestClient, auth_headers, booking_repo
):
    """Verify that mock payment recording is rejected outside development."""
    _create_booking(booking_repo)
    app.dependency_overrides[get_settings] = lambda: Settings(environment="production")
    try:
        res = client.post(
            "/api/v1/payments",
            json={"booking_id": "booking-1", "amount_paise": 500000, "transaction_ref": "TXN123"},
            headers=auth_headers,
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_signed_gateway_webhook_records_payment(client: TestClient, booking_repo):
    """Verify that a properly signed gateway webhook records a payment."""
    _create_booking(booking_repo)
    # Use a high-entropy 64-char hex string to bypass the "predictable secret" validator
    secret = "f47ac10b58cc4372a5670e02b2c3d4798f4e2d1c9b7a6f5e3d2c1b0a9f8e7d6c"
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="production", payment_gateway_webhook_secret=secret
    )
    try:
        payload = {
            "event": "payment.success",
            "booking_id": "booking-1",
            "amount_paise": 500001,
            "transaction_ref": "GATEWAY_001",
        }
        body = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        res = client.post(
            "/api/v1/payments/webhook",
            content=body,
            headers={"Content-Type": "application/json", "X-Payment-Signature": signature},
        )
        assert res.status_code == 201
        assert res.json()["amount_paise"] == 500001
        assert res.json()["transaction_ref"] == "GATEWAY_001"
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_gateway_webhook_rejects_invalid_signature(client: TestClient, booking_repo):
    """Verify that gateway webhooks with invalid signatures are rejected."""
    _create_booking(booking_repo)
    # Use a high-entropy 64-char hex string to bypass the "predictable secret" validator
    secret = "a1b2c3d4e5f647a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f123"
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="production", payment_gateway_webhook_secret=secret
    )
    try:
        body = json.dumps({
            "event": "payment.success", "booking_id": "booking-1",
            "amount_paise": 500001, "transaction_ref": "GATEWAY_001",
        }).encode()

        res = client.post(
            "/api/v1/payments/webhook", content=body,
            headers={"Content-Type": "application/json", "X-Payment-Signature": "invalid"},
        )
        assert res.status_code == 401
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_gateway_webhook_accepts_sha256_prefix(client: TestClient, booking_repo):
    """Verify the service correctly strips the 'sha256=' prefix from gateway signatures."""
    _create_booking(booking_repo)
    # Use a high-entropy 64-char hex string to bypass the "predictable secret" validator
    secret = "9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8"
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="production", payment_gateway_webhook_secret=secret
    )
    try:
        payload = {
            "event": "payment.success", "booking_id": "booking-1",
            "amount_paise": 500001, "transaction_ref": "GATEWAY_PREFIX_TEST",
        }
        body = json.dumps(payload, separators=(",", ":")).encode()
        # Real gateways like Razorpay send the prefix
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        res = client.post(
            "/api/v1/payments/webhook", content=body,
            headers={"Content-Type": "application/json", "X-Payment-Signature": signature},
        )
        assert res.status_code == 201
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_concurrent_payment_insertions_return_one_record(payment_repo):
    """Prove thread-safety: concurrent identical payments result in only one record."""
    now = datetime.now(timezone.utc)

    def create(payment_id):
        """Helper to create or get a payment record."""
        return payment_repo.create_or_get_by_booking_id(
            payment_id,
            {
                "farmer_id": "farmer-1",
                "booking_id": "booking-1",
                "amount_paise": 500000,
                "transaction_ref": payment_id,
                "status": "success",
                "processed_at": now,
            },
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        records = list(executor.map(create, ["payment-1", "payment-2"]))

    assert records[0] == records[1]
    assert len(payment_repo.list_by_farmer("farmer-1")) == 1
