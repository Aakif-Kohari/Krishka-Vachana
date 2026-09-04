"""Tests for the payment tracking system."""
import hashlib
import hmac
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


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
    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "missing", "amount_paise": 500000, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_record_payment_rejects_non_integer_amount(client: TestClient, auth_headers):
    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 5000.5, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_mock_payment_is_rejected_outside_development(
    client: TestClient, auth_headers, booking_repo
):
    _create_booking(booking_repo)
    app.dependency_overrides[get_settings] = lambda: Settings(environment="production")

    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount_paise": 500000, "transaction_ref": "TXN123"},
        headers=auth_headers,
    )

    assert res.status_code == 403


def test_signed_gateway_webhook_records_payment(client: TestClient, booking_repo):
    _create_booking(booking_repo)
    secret = "test-webhook-secret"
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="production", payment_gateway_webhook_secret=secret
    )
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


def test_gateway_webhook_rejects_invalid_signature(client: TestClient, booking_repo):
    _create_booking(booking_repo)
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="production", payment_gateway_webhook_secret="expected-secret"
    )
    body = json.dumps(
        {
            "event": "payment.success",
            "booking_id": "booking-1",
            "amount_paise": 500001,
            "transaction_ref": "GATEWAY_001",
        }
    ).encode()

    res = client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Payment-Signature": "invalid"},
    )

    assert res.status_code == 401


def test_concurrent_payment_insertions_return_one_record(payment_repo):
    now = datetime.now(timezone.utc)

    def create(payment_id):
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
