"""Payment tracking API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, Header, Request, status

from app.api.deps import get_current_farmer_uid, get_payment_repository, get_slot_booking_repository
from app.core.config import Settings, get_settings
from app.core.exceptions import ForbiddenError
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
    settings: Settings = Depends(get_settings),
) -> PaymentOut:
    """
    Record a payment for a booking on behalf of the authenticated farmer.
    
    Parameters:
        payment_data (PaymentCreate): Payment and booking details to record.
        farmer_uid (str): Identifier of the authenticated farmer.
    
    Returns:
        PaymentOut: The recorded payment.
    """
    if not settings.is_development:
        raise ForbiddenError("Mock payment recording is only available in development")
    return payment_service.record_payment(payment_data, farmer_uid, payment_repo, booking_repo)


@router.post("/webhook", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def payment_webhook_endpoint(
    request: Request,
    x_payment_signature: str = Header(default="", alias="X-Payment-Signature"),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    booking_repo: SlotBookingRepository = Depends(get_slot_booking_repository),
    settings: Settings = Depends(get_settings),
) -> PaymentOut:
    """Accept a successful payment event after verifying its gateway signature."""
    payload = payment_service.verify_and_parse_webhook(
        await request.body(),
        x_payment_signature,
        settings.payment_gateway_webhook_secret,
    )
    return payment_service.record_gateway_payment(payload, payment_repo, booking_repo)


@router.get("/me", response_model=List[PaymentOut])
def get_my_payments(
    farmer_uid: str = Depends(get_current_farmer_uid),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
) -> List[PaymentOut]:
    """List all payments for the authenticated farmer."""
    return payment_service.get_farmer_payments(farmer_uid, payment_repo)
