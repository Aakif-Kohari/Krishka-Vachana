from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from threading import Event

import pytest

from app.core.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.repositories.memory import (
    InMemoryCentreRepository,
    InMemoryCropRepository,
    InMemoryFarmerRepository,
    InMemorySlotBookingRepository,
)
from app.schemas.slot import SlotBookingCreate
from app.services import slot_service

TOMORROW = (date.today() + timedelta(days=1)).isoformat()

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
    client.post("/api/v1/farmers/register", json=FARMER_PAYLOAD, headers=auth_headers)


def _tiny_centre_repo(capacity: int = 1) -> InMemoryCentreRepository:
    seed = [
        {
            "centre_id": "ctr-tiny",
            "name": "Tiny Test Centre",
            "village": "Testville",
            "district": "Solapur",
            "state": "Maharashtra",
            "capacity_per_slot": capacity,
            "created_at": datetime.now(timezone.utc),
        }
    ]
    return InMemoryCentreRepository(seed=seed)


# --- HTTP-level tests (via the shared `client` fixture / seeded centre) ----


def test_book_slot_requires_farmer_profile_first(client, auth_headers, seeded_centre_id):
    response = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_book_slot_success(client, auth_headers, seeded_centre_id, monkeypatch):
    _register_farmer(client, auth_headers)
    started = Event()
    release = Event()

    def slow_notification(*_args):
        started.set()
        release.wait(timeout=2)

    monkeypatch.setattr(slot_service, "_notify_booking_confirmed", slow_notification)
    try:
        with ThreadPoolExecutor(max_workers=1) as caller:
            pending = caller.submit(
                client.post,
                "/api/v1/bookings",
                json={
                    "centre_id": seeded_centre_id,
                    "slot_date": TOMORROW,
                    "slot_window": "08:00-10:00",
                },
                headers=auth_headers,
            )
            assert started.wait(timeout=1)
            response = pending.result(timeout=0.5)
    finally:
        release.set()

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "booked"
    assert body["centre_id"] == seeded_centre_id
    assert body["farmer_id"] == "test-farmer-uid-123"


def test_book_slot_unknown_centre_is_404(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/bookings",
        json={"centre_id": "does-not-exist", "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_book_slot_invalid_window_is_422(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "midnight"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_book_slot_rejects_past_date(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": "2020-01-01", "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_book_slot_resolves_centre_before_rejecting_past_date(client, auth_headers):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/bookings",
        json={"centre_id": "does-not-exist", "slot_date": "2020-01-01", "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_book_slot_rejects_unknown_crop_id(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    response = client.post(
        "/api/v1/bookings",
        json={
            "centre_id": seeded_centre_id,
            "slot_date": TOMORROW,
            "slot_window": "08:00-10:00",
            "crop_id": "does-not-exist",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_book_slot_links_registered_crop(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    crop_response = client.post(
        "/api/v1/crops", json={"crop_type": "wheat", "quantity_quintals": 10}, headers=auth_headers
    )
    crop_id = crop_response.json()["crop_id"]

    response = client.post(
        "/api/v1/bookings",
        json={
            "centre_id": seeded_centre_id,
            "slot_date": TOMORROW,
            "slot_window": "08:00-10:00",
            "crop_id": crop_id,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["crop_id"] == crop_id


def test_book_slot_rejects_duplicate_for_same_farmer(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    payload = {"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"}
    first = client.post("/api/v1/bookings", json=payload, headers=auth_headers)
    assert first.status_code == 201

    second = client.post("/api/v1/bookings", json=payload, headers=auth_headers)
    assert second.status_code == 409


def test_list_my_bookings(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    )
    response = client.get("/api/v1/bookings/me", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_booking_by_id(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    created = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    ).json()
    response = client.get(f"/api/v1/bookings/{created['booking_id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["booking_id"] == created["booking_id"]


def test_get_booking_not_found(client, auth_headers):
    response = client.get("/api/v1/bookings/does-not-exist", headers=auth_headers)
    assert response.status_code == 404


def test_cancel_booking(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    created = client.post(
        "/api/v1/bookings",
        json={"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"},
        headers=auth_headers,
    ).json()

    response = client.post(f"/api/v1/bookings/{created['booking_id']}/cancel", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_frees_the_slot_for_a_rebooking_by_the_same_farmer(client, auth_headers, seeded_centre_id):
    _register_farmer(client, auth_headers)
    payload = {"centre_id": seeded_centre_id, "slot_date": TOMORROW, "slot_window": "08:00-10:00"}
    created = client.post("/api/v1/bookings", json=payload, headers=auth_headers).json()

    client.post(f"/api/v1/bookings/{created['booking_id']}/cancel", headers=auth_headers)

    rebooked = client.post("/api/v1/bookings", json=payload, headers=auth_headers)
    assert rebooked.status_code == 201


def test_cancel_unknown_booking_is_404(client, auth_headers):
    response = client.post("/api/v1/bookings/does-not-exist/cancel", headers=auth_headers)
    assert response.status_code == 404


# --- Service-level tests: capacity/concurrency across *different* farmers -
# (the `client` fixture pins a single farmer id, so cross-farmer races are
# exercised directly against the service, mirroring
# test_farmers.py's concurrent-Aadhaar-registration tests.)


def test_capacity_enforced_once_slot_is_full():
    centre_repo = _tiny_centre_repo(capacity=1)
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_repo.create("farmer-a", {})
    farmer_repo.create("farmer-b", {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny", slot_date=date.today() + timedelta(days=1), slot_window="08:00-10:00"
    )

    first = slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-a", payload)
    assert first.status == "booked"

    with pytest.raises(ConflictError):
        slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-b", payload)


def test_booking_date_uses_procurement_centre_business_timezone(monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            assert tz == slot_service.PROCUREMENT_CENTRE_TIMEZONE
            return cls(2026, 9, 3, 0, 30, tzinfo=tz)

    monkeypatch.setattr(slot_service, "datetime", FixedDateTime)
    centre_repo = _tiny_centre_repo()
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_repo.create("farmer-a", {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny", slot_date=date(2026, 9, 2), slot_window="08:00-10:00"
    )

    with pytest.raises(ValidationAppError):
        slot_service.book_slot(
            booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-a", payload
        )


def test_concurrent_booking_respects_capacity():
    centre_repo = _tiny_centre_repo(capacity=1)
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_ids = ["farmer-a", "farmer-b", "farmer-c"]
    for fid in farmer_ids:
        farmer_repo.create(fid, {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny", slot_date=date.today() + timedelta(days=1), slot_window="08:00-10:00"
    )

    def attempt(farmer_id):
        try:
            return slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, farmer_id, payload)
        except ConflictError:
            return None

    with ThreadPoolExecutor(max_workers=len(farmer_ids)) as executor:
        results = list(executor.map(attempt, farmer_ids))

    assert sum(result is not None for result in results) == 1


def test_concurrent_same_farmer_booking_allows_exactly_one_active_booking():
    centre_repo = _tiny_centre_repo(capacity=2)
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_repo.create("farmer-a", {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny",
        slot_date=date.today() + timedelta(days=1),
        slot_window="08:00-10:00",
    )

    def attempt():
        try:
            return slot_service.book_slot(
                booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-a", payload
            )
        except ConflictError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: attempt(), range(2)))

    assert sum(result is not None for result in results) == 1
    assert booking_repo.count_active_bookings(
        payload.centre_id, payload.slot_date, payload.slot_window
    ) == 1


def test_cancel_frees_capacity_for_a_different_farmer():
    centre_repo = _tiny_centre_repo(capacity=1)
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_repo.create("farmer-a", {})
    farmer_repo.create("farmer-b", {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny", slot_date=date.today() + timedelta(days=1), slot_window="08:00-10:00"
    )

    booking = slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-a", payload)
    slot_service.cancel_booking(booking_repo, "farmer-a", booking.booking_id)

    second = slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-b", payload)
    assert second.status == "booked"


def test_cannot_cancel_someone_elses_booking():
    centre_repo = _tiny_centre_repo(capacity=1)
    booking_repo = InMemorySlotBookingRepository()
    farmer_repo = InMemoryFarmerRepository()
    crop_repo = InMemoryCropRepository()
    farmer_repo.create("farmer-a", {})
    farmer_repo.create("farmer-b", {})
    payload = SlotBookingCreate(
        centre_id="ctr-tiny", slot_date=date.today() + timedelta(days=1), slot_window="08:00-10:00"
    )
    booking = slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, "farmer-a", payload)

    with pytest.raises(NotFoundError):
        slot_service.cancel_booking(booking_repo, "farmer-b", booking.booking_id)

    # Still active for its actual owner.
    assert booking_repo.get(booking.booking_id)["status"] == "booked"
