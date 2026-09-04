"""Tests for the payment tracking system."""
import pytest
from fastapi.testclient import TestClient


def test_record_payment_success(client: TestClient, auth_headers, booking_repo, farmer_repo):
    """Test successful payment recording against a valid booking."""
    # Setup: Create a farmer and a booking
    farmer_repo.create("test-farmer-uid-123", {"full_name": "Test", "village": "V1"})
    booking_repo.create_if_capacity_available(
        "booking-1", 
        10, 
        {
            "farmer_id": "test-farmer-uid-123", 
            "centre_id": "ctr-1", 
            "slot_date": "2026-10-01", 
            "slot_window": "08:00-10:00",
            "status": "confirmed"
        }
    )

    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "booking-1", "amount": 5000.0, "transaction_ref": "TXN123"},
        headers=auth_headers
    )
    assert res.status_code == 201
    assert res.json()["status"] == "success"
    assert res.json()["amount"] == 5000.0


def test_record_payment_duplicate_fails(client: TestClient, auth_headers, booking_repo, farmer_repo):
    """Test that recording a payment twice for the same booking returns a 409 Conflict."""
    farmer_repo.create("test-farmer-uid-123", {"full_name": "Test", "village": "V1"})
    booking_repo.create_if_capacity_available(
        "booking-1", 
        10, 
        {
            "farmer_id": "test-farmer-uid-123", 
            "centre_id": "ctr-1", 
            "slot_date": "2026-10-01", 
            "slot_window": "08:00-10:00",
            "status": "confirmed"
        }
    )
    
    # First payment succeeds (Note: transaction_ref must be >= 5 chars)
    res1 = client.post(
        "/api/v1/payments", 
        json={"booking_id": "booking-1", "amount": 5000.0, "transaction_ref": "TXN_001"}, 
        headers=auth_headers
    )
    assert res1.status_code == 201
    
    # Second payment fails (idempotency check)
    res2 = client.post(
        "/api/v1/payments", 
        json={"booking_id": "booking-1", "amount": 5000.0, "transaction_ref": "TXN_002"}, 
        headers=auth_headers
    )
    assert res2.status_code == 409  # Conflict


def test_record_payment_invalid_booking(client: TestClient, auth_headers):
    """Test that recording a payment for a non-existent booking returns a 404 Not Found."""
    res = client.post(
        "/api/v1/payments",
        json={"booking_id": "non-existent-booking-id", "amount": 5000.0, "transaction_ref": "TXN123"},
        headers=auth_headers
    )
    assert res.status_code == 404  # Not Found
