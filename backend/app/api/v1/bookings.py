from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_centre_repository,
    get_crop_repository,
    get_current_farmer_uid,
    get_farmer_repository,
    get_slot_booking_repository,
)
from app.repositories.base import (
    CentreRepository,
    CropRepository,
    FarmerRepository,
    SlotBookingRepository,
)
from app.schemas.slot import SlotBookingCreate, SlotBookingOut
from app.services import slot_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=SlotBookingOut, status_code=status.HTTP_201_CREATED)
def book_slot(
    payload: SlotBookingCreate,
    farmer_id: str = Depends(get_current_farmer_uid),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
    centre_repo: CentreRepository = Depends(get_centre_repository),
    farmer_repo: FarmerRepository = Depends(get_farmer_repository),
    crop_repo: CropRepository = Depends(get_crop_repository),
) -> SlotBookingOut:
    """Book a Smart Slot at a procurement centre for a specific date and time window."""
    return slot_service.book_slot(booking_repo, centre_repo, farmer_repo, crop_repo, farmer_id, payload)


@router.get("/me", response_model=List[SlotBookingOut])
def list_my_bookings(
    farmer_id: str = Depends(get_current_farmer_uid),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
) -> List[SlotBookingOut]:
    """List all bookings for the authenticated farmer."""
    return slot_service.list_my_bookings(booking_repo, farmer_id)


@router.get("/{booking_id}", response_model=SlotBookingOut)
def get_booking(
    booking_id: str,
    farmer_id: str = Depends(get_current_farmer_uid),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
) -> SlotBookingOut:
    """Get a specific booking by ID for the authenticated farmer."""
    return slot_service.get_my_booking(booking_repo, farmer_id, booking_id)


@router.post("/{booking_id}/cancel", response_model=SlotBookingOut)
def cancel_booking(
    booking_id: str,
    farmer_id: str = Depends(get_current_farmer_uid),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
) -> SlotBookingOut:
    """Cancel a booking and free its slot capacity."""
    return slot_service.cancel_booking(booking_repo, farmer_id, booking_id)
