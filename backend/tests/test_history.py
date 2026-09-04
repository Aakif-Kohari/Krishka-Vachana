"""Tests for the historical farm record aggregation."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


def test_get_history_empty(client: TestClient, auth_headers):
    res = client.get("/api/v1/farmers/me/history", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["crops"] == []
    assert data["bookings"] == []
    assert data["payments"] == []

def test_get_history_aggregates_data(client: TestClient, auth_headers, crop_repo, booking_repo, payment_repo):
    # Seed some data for the test farmer matching exact schema requirements
    now = datetime.now(timezone.utc)
    
    crop_repo.create("c1", {
        "crop_id": "c1",
        "farmer_id": "test-farmer-uid-123", 
        "crop_type": "wheat", 
        "quantity_quintals": 100,
        "created_at": now
    })
    
    booking_repo.create_if_capacity_available(
        "b1", 10, {
            "booking_id": "b1",
            "farmer_id": "test-farmer-uid-123", 
            "centre_id": "ctr-1", 
            "slot_date": "2026-10-01", 
            "slot_window": "08:00-10:00",
            "status": "confirmed",
            "created_at": now
        }
    )
    
    payment_repo.create("p1", {
        "payment_id": "p1",
        "farmer_id": "test-farmer-uid-123", 
        "booking_id": "b1", 
        "amount_paise": 500000,
        "transaction_ref": "TXN_12345",
        "status": "success",
        "processed_at": now
    })

    res = client.get("/api/v1/farmers/me/history", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["crops"]) == 1
    assert len(data["bookings"]) == 1
    assert len(data["payments"]) == 1
