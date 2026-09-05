"""Tests for the historical farm record aggregation."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


def test_get_history_empty(client: TestClient, auth_headers):
    """Verify that history returns empty collections for a farmer with no data."""
    res = client.get("/api/v1/farmers/me/history", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["crops"] == []
    assert data["bookings"] == []
    assert data["payments"] == []
    assert data["page"] == {"page_size": 20, "next_cursor": None}

def test_get_history_aggregates_data(client: TestClient, auth_headers, crop_repo, booking_repo, payment_repo):
    """Verify that history aggregates crops, bookings, and payments."""
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


def test_get_history_paginates_each_collection(client: TestClient, auth_headers, crop_repo):
    """Verify that history supports cursor-based pagination."""
    now = datetime.now(timezone.utc)
    for crop_id in ("c1", "c2", "c3"):
        crop_repo.create(
            crop_id,
            {
                "farmer_id": "test-farmer-uid-123",
                "crop_type": "wheat",
                "quantity_quintals": 1,
                "created_at": now,
            },
        )

    first = client.get(
        "/api/v1/farmers/me/history?page_size=2", headers=auth_headers
    )
    assert first.status_code == 200
    assert [crop["crop_id"] for crop in first.json()["crops"]] == ["c1", "c2"]
    assert first.json()["page"]["next_cursor"]

    second = client.get(
        "/api/v1/farmers/me/history",
        params={"page_size": 2, "cursor": first.json()["page"]["next_cursor"]},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert [crop["crop_id"] for crop in second.json()["crops"]] == ["c3"]
    assert second.json()["page"]["next_cursor"] is None


@pytest.mark.parametrize(
    "params",
    [
        {"page_size": 0},
        {"page_size": 101},
        {"cursor": "not-a-valid-cursor"},
    ],
)
def test_get_history_rejects_invalid_pagination(client: TestClient, auth_headers, params):
    """Verify that invalid pagination cursors are rejected."""
    response = client.get(
        "/api/v1/farmers/me/history", params=params, headers=auth_headers
    )
    assert response.status_code == 422
