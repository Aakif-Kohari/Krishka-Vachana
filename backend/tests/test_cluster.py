"""Tests for the village cluster booking system."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

FUTURE_SLOT_DATE = (date.today() + timedelta(days=30)).isoformat()


def test_cluster_booking_success(client: TestClient, auth_headers, farmer_repo, centre_repo, booking_repo):
    """Verify successful cluster booking for farmers from the same village."""
    # Setup 2 farmers in the same village
    farmer_repo.create("test-farmer-uid-123", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123", "f2"]
        },
        headers=auth_headers
    )
    assert res.status_code == 201
    assert len(res.json()["booking_ids"]) == 2

def test_cluster_booking_mixed_villages_fails(client: TestClient, auth_headers, farmer_repo):
    """Verify that cluster bookings fail when farmers are from different villages."""
    # Create the authenticated user so they pass the delegate/member check
    farmer_repo.create("test-farmer-uid-123", {"full_name": "F0", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V2"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123", "f2"] # Include authenticated user
        },
        headers=auth_headers
    )
    assert res.status_code == 422 # ValidationAppError (422 Unprocessable Entity)

def test_cluster_booking_insufficient_capacity_rolls_back(client: TestClient, auth_headers, farmer_repo, booking_repo):
    """
    Verify that a cluster booking exceeding slot capacity is rejected without creating partial bookings.
    """
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1"})
    
    # Fill capacity (Solapur APMC has 40 per slot)
    # We'll just try to book 41 farmers to force a failure
    fids = ["test-farmer-uid-123", *[f"f{i}" for i in range(40)]]
    for fid in fids:
        farmer_repo.create(fid, {"full_name": fid, "village": "V1"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": fids
        },
        headers=auth_headers
    )
    assert res.status_code == 409 # Conflict
    # Verify no partial bookings were created
    assert booking_repo.count_active_bookings(
        "ctr-solapur-apmc", date.fromisoformat(FUTURE_SLOT_DATE), "08:00-10:00"
    ) == 0


def test_cluster_booking_rejects_non_member_without_delegate_grants(
    client: TestClient, auth_headers, farmer_repo
):
    """Verify that non-members cannot create cluster bookings without delegate authorization."""
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["f1", "f2"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 403


def test_cluster_booking_allows_repository_backed_delegate(
    client: TestClient, auth_headers, farmer_repo, centre_repo
):
    """Verify that authorized delegates can create cluster bookings."""
    delegate_grant = {"authorized_cluster_delegate_ids": ["test-farmer-uid-123"]}
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1", **delegate_grant})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1", **delegate_grant})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["f1", "f2"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 201


def test_cluster_booking_rejects_duplicate_farmer_ids(
    client: TestClient, auth_headers
):
    """Verify that duplicate farmer IDs in a cluster booking are rejected."""
    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123", "test-farmer-uid-123"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 422


def test_cluster_booking_strips_claimed_village(
    client: TestClient, auth_headers, farmer_repo, centre_repo
):
    """Verify that the claimed village name is trimmed."""
    farmer_repo.create(
        "test-farmer-uid-123", {"full_name": "F1", "village": "V1"}
    )
    centre_repo.list()

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "  V1  ",
            "farmer_ids": ["test-farmer-uid-123"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 201
    assert res.json()["village"] == "V1"


def test_cluster_booking_rejects_whitespace_only_village(client: TestClient, auth_headers):
    """Verify that whitespace-only village names are rejected."""
    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": FUTURE_SLOT_DATE,
            "slot_window": "08:00-10:00",
            "village": "   ",
            "farmer_ids": ["test-farmer-uid-123"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 422


def test_cluster_booking_resolves_centre_before_rejecting_past_date(
    client: TestClient, auth_headers, farmer_repo
):
    """Verify that unknown centre errors take precedence over past date validation."""
    from datetime import date, timedelta
    past_date = (date.today() - timedelta(days=1)).isoformat()
    
    # Create the authenticated user so they pass the delegate/member check
    farmer_repo.create("test-farmer-uid-123", {"full_name": "F0", "village": "V1"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "does-not-exist-centre",
            "slot_date": past_date,
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123"],
        },
        headers=auth_headers,
    )
    # Should be 404 Not Found (centre), not 422 Validation (past date)
    assert res.status_code == 404
