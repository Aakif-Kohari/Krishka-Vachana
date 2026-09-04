"""Tests for the Dynamic Queue system (Phase 3).

Covers: check-in, live position/wait, complete, leave, centre status,
printable token page, concurrent check-in deduplication, and date
enforcement. HTTP-level tests use the shared single-farmer `client`
fixture (see test_bookings.py); multi-farmer position tests call the
service layer directly, the same pattern test_bookings.py and
test_farmers.py already use for cross-farmer scenarios.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from app.core.exceptions import ConflictError
from app.repositories.memory import InMemoryFarmerRepository, InMemoryQueueRepository, InMemorySlotBookingRepository
from app.schemas.queue import AVERAGE_SERVICE_MINUTES, QueueCheckInCreate
from app.services import queue_service
from app.services.slot_service import PROCUREMENT_CENTRE_TIMEZONE

TODAY_DATE = datetime.now(PROCUREMENT_CENTRE_TIMEZONE).date()
TODAY = TODAY_DATE.isoformat()
TOMORROW = (TODAY_DATE + timedelta(days=1)).isoformat()

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
    r = client.post("/api/v1/farmers/register", json=FARMER_PAYLOAD, headers=auth_headers)
    assert r.status_code == 201
    return r.json()


def _book_slot(client, auth_headers, seeded_centre_id, slot_date=TODAY, slot_window="08:00-10:00"):
    r = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": slot_date, "slot_window": slot_window},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()
    return r.json()


def _check_in(client, auth_headers, booking_id):
    return client.post("/api/v1/queue/check-in", json={"booking_id": booking_id}, headers=auth_headers)


# ---------------------------------------------------------------------------
# Basic check-in
# ---------------------------------------------------------------------------

def test_check_in_success(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)

    r = _check_in(client, auth_headers, booking["booking_id"])

    assert r.status_code == 201, r.json()
    body = r.json()
    assert body["status"] == "waiting"
    assert body["sequence_number"] == 1
    assert body["token_number"] == "001"
    assert body["position"] == 1
    assert body["people_ahead"] == 0
    assert body["estimated_wait_minutes"] == 0


def test_check_in_unknown_booking_is_404(client, auth_headers):
    r = _check_in(client, auth_headers, "non-existent-booking-id")
    assert r.status_code == 404


def test_check_in_rejects_someone_elses_booking(client, auth_headers, seeded_centre_id, booking_repo):
    booking_repo.create_if_capacity_available(
        "other-farmers-booking",
        10,
        {
            "farmer_id": "someone-else",
            "centre_id": seeded_centre_id,
            "slot_date": TODAY_DATE,
            "slot_window": "08:00-10:00",
            "crop_id": None,
            "notes": None,
            "status": "booked",
            "created_at": datetime.now(timezone.utc),
        },
    )
    r = _check_in(client, auth_headers, "other-farmers-booking")
    assert r.status_code == 404


def test_check_in_rejects_future_slot(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id, slot_date=TOMORROW)

    r = _check_in(client, auth_headers, booking["booking_id"])

    assert r.status_code == 409
    assert r.json()["error"]["code"] == "conflict"


def test_check_in_rejects_cancelled_booking(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    cancel = client.post(f"/api/v1/bookings/{booking['booking_id']}/cancel", headers=auth_headers)
    assert cancel.status_code == 200

    r = _check_in(client, auth_headers, booking["booking_id"])
    assert r.status_code == 409


def test_check_in_deduplicates_same_booking(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)

    assert _check_in(client, auth_headers, booking["booking_id"]).status_code == 201
    assert _check_in(client, auth_headers, booking["booking_id"]).status_code == 409


def test_check_in_deduplicates_same_farmer_active_entry(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking1 = _book_slot(client, auth_headers, seeded_centre_id, slot_window="08:00-10:00")
    booking2 = _book_slot(client, auth_headers, seeded_centre_id, slot_window="10:00-12:00")

    assert _check_in(client, auth_headers, booking1["booking_id"]).status_code == 201
    # Same farmer, a different booking - still rejected while the first entry is active.
    assert _check_in(client, auth_headers, booking2["booking_id"]).status_code == 409


# ---------------------------------------------------------------------------
# Live position (multi-farmer, service-level - mirrors test_bookings.py's
# test_capacity_enforced_once_slot_is_full pattern)
# ---------------------------------------------------------------------------

def test_position_reflects_arrival_order_and_updates_when_someone_leaves():
    queue_repo = InMemoryQueueRepository()
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()

    for farmer_id in ("farmer-a", "farmer-b", "farmer-c"):
        farmer_repo.create(farmer_id, {"phone_number": "9876543210", "full_name": "Test"})
        booking_repo.create_if_capacity_available(
            f"booking-{farmer_id}",
            10,
            {
                "farmer_id": farmer_id,
                "centre_id": "centre-1",
                "slot_date": TODAY_DATE,
                "slot_window": "08:00-10:00",
                "crop_id": None,
                "notes": None,
                "status": "booked",
                "created_at": datetime.now(timezone.utc),
            },
        )

    entry_a = queue_service.check_in(
        queue_repo, booking_repo, farmer_repo, "farmer-a", QueueCheckInCreate(booking_id="booking-farmer-a")
    )
    entry_b = queue_service.check_in(
        queue_repo, booking_repo, farmer_repo, "farmer-b", QueueCheckInCreate(booking_id="booking-farmer-b")
    )
    entry_c = queue_service.check_in(
        queue_repo, booking_repo, farmer_repo, "farmer-c", QueueCheckInCreate(booking_id="booking-farmer-c")
    )

    assert (entry_a.position, entry_b.position, entry_c.position) == (1, 2, 3)
    assert entry_c.estimated_wait_minutes == 2 * AVERAGE_SERVICE_MINUTES

    # farmer-a leaves; farmer-b and farmer-c should each move up one place.
    queue_service.leave_queue(queue_repo, "farmer-a", entry_a.queue_id)

    updated_b = queue_service.get_queue_entry(queue_repo, "farmer-b", entry_b.queue_id)
    updated_c = queue_service.get_queue_entry(queue_repo, "farmer-c", entry_c.queue_id)
    assert updated_b.position == 1
    assert updated_c.position == 2


# ---------------------------------------------------------------------------
# GET /queue/me
# ---------------------------------------------------------------------------

def test_get_my_status_returns_waiting_entry(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    _check_in(client, auth_headers, booking["booking_id"])

    r = client.get("/api/v1/queue/me", headers=auth_headers)

    assert r.status_code == 200
    assert r.json()["status"] == "waiting"


def test_get_my_status_404_when_no_active_entry(client, auth_headers):
    r = client.get("/api/v1/queue/me", headers=auth_headers)
    assert r.status_code == 404


def test_get_entry_not_accessible_by_other_farmer(client, auth_headers, seeded_centre_id):
    from app.api import deps
    from app.main import app

    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    app.dependency_overrides[deps.get_current_farmer_uid] = lambda: "other-farmer-id"
    r = client.get(f"/api/v1/queue/{queue_id}", headers=auth_headers)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Complete / leave
# ---------------------------------------------------------------------------

def test_complete_entry(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    r = client.post(f"/api/v1/queue/{queue_id}/complete", headers=auth_headers)

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "served"
    assert body["position"] is None
    assert body["people_ahead"] is None
    assert body["resolved_at"] is not None


def test_leave_queue(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    r = client.post(f"/api/v1/queue/{queue_id}/leave", headers=auth_headers)

    assert r.status_code == 200
    assert r.json()["status"] == "left"


def test_cannot_resolve_already_resolved_entry(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    assert client.post(f"/api/v1/queue/{queue_id}/complete", headers=auth_headers).status_code == 200
    assert client.post(f"/api/v1/queue/{queue_id}/complete", headers=auth_headers).status_code == 404
    assert client.post(f"/api/v1/queue/{queue_id}/leave", headers=auth_headers).status_code == 404


def test_after_leaving_farmer_can_check_in_again(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking1 = _book_slot(client, auth_headers, seeded_centre_id, slot_window="08:00-10:00")
    booking2 = _book_slot(client, auth_headers, seeded_centre_id, slot_window="10:00-12:00")
    queue_id = _check_in(client, auth_headers, booking1["booking_id"]).json()["queue_id"]

    client.post(f"/api/v1/queue/{queue_id}/leave", headers=auth_headers)

    r = _check_in(client, auth_headers, booking2["booking_id"])
    assert r.status_code == 201
    assert r.json()["sequence_number"] == 2


# ---------------------------------------------------------------------------
# Centre aggregate status
# ---------------------------------------------------------------------------

def test_centre_status_waiting_count(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    _check_in(client, auth_headers, booking["booking_id"])

    r = client.get(f"/api/v1/queue/centre/{seeded_centre_id}", headers=auth_headers)

    assert r.status_code == 200
    assert r.json() == {
        "centre_id": seeded_centre_id,
        "waiting_count": 1,
        "estimated_wait_minutes": 1 * AVERAGE_SERVICE_MINUTES,
    }


def test_centre_status_unknown_centre_is_404(client, auth_headers):
    r = client.get("/api/v1/queue/centre/does-not-exist", headers=auth_headers)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Printable token page
# ---------------------------------------------------------------------------

def test_printable_token_returns_html(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    r = client.get(f"/api/v1/queue/{queue_id}/token", headers=auth_headers)

    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "#001" in r.text
    assert "KisanSetu" in r.text
    assert "Print this page" in r.text
    assert "Position 1 in the queue" in r.text


def test_printable_token_reflects_served_status(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]
    client.post(f"/api/v1/queue/{queue_id}/complete", headers=auth_headers)

    r = client.get(f"/api/v1/queue/{queue_id}/token", headers=auth_headers)

    assert r.status_code == 200
    assert "already been served" in r.text


def test_printable_token_not_accessible_by_other_farmer(client, auth_headers, seeded_centre_id):
    from app.api import deps
    from app.main import app

    _register_farmer(client, auth_headers)
    booking = _book_slot(client, auth_headers, seeded_centre_id)
    queue_id = _check_in(client, auth_headers, booking["booking_id"]).json()["queue_id"]

    app.dependency_overrides[deps.get_current_farmer_uid] = lambda: "other-farmer-id"
    r = client.get(f"/api/v1/queue/{queue_id}/token", headers=auth_headers)
    assert r.status_code == 404


def test_printable_token_excluded_from_openapi_schema(client):
    schema = client.get("/openapi.json").json()
    assert "/api/v1/queue/{queue_id}/token" not in schema["paths"]


# ---------------------------------------------------------------------------
# Concurrency safety (in-memory repo)
# ---------------------------------------------------------------------------

def test_concurrent_check_in_same_booking_allows_only_one():
    booking_repo = InMemorySlotBookingRepository()
    queue_repo = InMemoryQueueRepository()
    farmer_repo = InMemoryFarmerRepository()

    farmer_repo.create("f1", {"phone_number": "9876543210", "full_name": "Test"})
    booking_repo.create_if_capacity_available(
        "booking-1",
        10,
        {
            "farmer_id": "f1",
            "centre_id": "centre-1",
            "slot_date": TODAY_DATE,
            "slot_window": "08:00-10:00",
            "crop_id": None,
            "notes": None,
            "status": "booked",
            "created_at": datetime.now(timezone.utc),
        },
    )

    payload = QueueCheckInCreate(booking_id="booking-1")

    def do_check_in(_):
        try:
            return queue_service.check_in(queue_repo, booking_repo, farmer_repo, "f1", payload)
        except ConflictError:
            return None

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(do_check_in, range(3)))

    successes = [r for r in results if r is not None]
    assert len(successes) == 1
    assert successes[0].sequence_number == 1
