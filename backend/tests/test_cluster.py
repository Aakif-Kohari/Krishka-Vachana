"""Tests for the village cluster booking system."""
import pytest
from fastapi.testclient import TestClient


def test_cluster_booking_success(client: TestClient, auth_headers, farmer_repo, centre_repo, booking_repo):
    # Setup 2 farmers in the same village
    farmer_repo.create("test-farmer-uid-123", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1"})
    centre_repo.list() # Trigger seed

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": "2026-10-01",
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123", "f2"]
        },
        headers=auth_headers
    )
    assert res.status_code == 201
    assert len(res.json()["booking_ids"]) == 2

def test_cluster_booking_mixed_villages_fails(client: TestClient, auth_headers, farmer_repo):
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V2"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": "2026-10-01",
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["f1", "f2"]
        },
        headers=auth_headers
    )
    assert res.status_code == 400 # Bad Request

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
            "slot_date": "2026-10-01",
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": fids
        },
        headers=auth_headers
    )
    assert res.status_code == 409 # Conflict
    # Verify no partial bookings were created
    assert booking_repo.count_active_bookings("ctr-solapur-apmc", "2026-10-01", "08:00-10:00") == 0


def test_cluster_booking_rejects_non_member_without_delegate_grants(
    client: TestClient, auth_headers, farmer_repo
):
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1"})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1"})

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": "2026-10-01",
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
    delegate_grant = {"authorized_cluster_delegate_ids": ["test-farmer-uid-123"]}
    farmer_repo.create("f1", {"full_name": "F1", "village": "V1", **delegate_grant})
    farmer_repo.create("f2", {"full_name": "F2", "village": "V1", **delegate_grant})
    centre_repo.list()

    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": "2026-10-01",
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
    res = client.post(
        "/api/v1/bookings/cluster",
        json={
            "centre_id": "ctr-solapur-apmc",
            "slot_date": "2026-10-01",
            "slot_window": "08:00-10:00",
            "village": "V1",
            "farmer_ids": ["test-farmer-uid-123", "test-farmer-uid-123"],
        },
        headers=auth_headers,
    )

    assert res.status_code == 422
