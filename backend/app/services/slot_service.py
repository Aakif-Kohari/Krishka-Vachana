"""Smart Slot booking business logic.

Capacity is enforced per (centre_id, slot_date, slot_window) via the
repository's create_if_capacity_available - the same atomic
reserve-then-create pattern app/services/farmer_service.py uses for
Aadhaar uniqueness, so two farmers racing for the last slot in a window
can't both succeed (see tests/test_bookings.py's concurrency test).
"""
import uuid
from typing import List

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.base import (
    CentreRepository,
    CropRepository,
    FarmerRepository,
    SlotBookingRepository,
)
from app.schemas.slot import SlotBookingCreate, SlotBookingOut, utcnow


def book_slot(
    booking_repo: SlotBookingRepository,
    centre_repo: CentreRepository,
    farmer_repo: FarmerRepository,
    crop_repo: CropRepository,
    farmer_id: str,
    payload: SlotBookingCreate,
) -> SlotBookingOut:
    if farmer_repo.get(farmer_id) is None:
        raise NotFoundError("Register a farmer profile before booking a slot")

    centre = centre_repo.get(payload.centre_id)
    if centre is None:
        raise NotFoundError("Procurement centre not found")

    if payload.crop_id is not None:
        farmer_crops = crop_repo.list_by_farmer(farmer_id)
        if not any(c["crop_id"] == payload.crop_id for c in farmer_crops):
            raise NotFoundError("crop_id does not belong to a registered crop for this farmer")

    # Guard against accidental double-submission of the exact same slot by
    # the same farmer - a separate concern from the capacity check below,
    # which is about other farmers competing for the same seats.
    duplicate = any(
        b["status"] == "booked"
        and b["centre_id"] == payload.centre_id
        and b["slot_date"] == payload.slot_date
        and b["slot_window"] == payload.slot_window
        for b in booking_repo.list_by_farmer(farmer_id)
    )
    if duplicate:
        raise ConflictError("You already have an active booking for this centre, date, and window")

    booking_id = str(uuid.uuid4())
    record = booking_repo.create_if_capacity_available(
        booking_id,
        centre["capacity_per_slot"],
        {
            "farmer_id": farmer_id,
            "centre_id": payload.centre_id,
            "slot_date": payload.slot_date,
            "slot_window": payload.slot_window,
            "crop_id": payload.crop_id,
            "notes": payload.notes,
            "status": "booked",
            "created_at": utcnow(),
        },
    )
    if record is None:
        raise ConflictError(
            "This slot window is fully booked - choose a different window, date, or centre"
        )
    return SlotBookingOut.model_validate(record)


def list_my_bookings(booking_repo: SlotBookingRepository, farmer_id: str) -> List[SlotBookingOut]:
    records = booking_repo.list_by_farmer(farmer_id)
    records.sort(key=lambda r: (r["slot_date"], r["slot_window"]), reverse=True)
    return [SlotBookingOut.model_validate(r) for r in records]


def get_my_booking(booking_repo: SlotBookingRepository, farmer_id: str, booking_id: str) -> SlotBookingOut:
    record = booking_repo.get(booking_id)
    # Booking exists but belongs to someone else: still 404, not 403, so we
    # don't leak whether a given booking_id exists to a farmer who doesn't
    # own it.
    if record is None or record.get("farmer_id") != farmer_id:
        raise NotFoundError("Booking not found")
    return SlotBookingOut.model_validate(record)


def cancel_booking(booking_repo: SlotBookingRepository, farmer_id: str, booking_id: str) -> SlotBookingOut:
    record = booking_repo.cancel(booking_id, farmer_id)
    if record is None:
        raise NotFoundError("Booking not found")
    return SlotBookingOut.model_validate(record)
