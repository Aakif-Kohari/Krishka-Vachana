"""Payment tracking API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_farmer_uid, get_payment_repository, get_slot_booking_repository
from app.repositories.base import PaymentRepository, SlotBookingRepository
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def record_payment_endpoint(
    payment_data: PaymentCreate,
    farmer_uid: str = Depends(get_current_farmer_uid),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
) -> PaymentOut:
    """Record a payment against a booking (simulates a payment gateway webhook)."""
    return payment_service.record_payment(payment_data, farmer_uid, payment_repo, booking_repo)


@router.get("/me", response_model=List[PaymentOut])
def get_my_payments(
    farmer_uid: str = Depends(get_current_farmer_uid),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
) -> List[PaymentOut]:
    """List all payments for the authenticated farmer."""
    return payment_service.get_farmer_payments(farmer_uid, payment_repo)
