"""Payment tracking business logic.

Handles recording of post-procurement payments. Simulates a webhook from a
payment gateway. In a production environment with a real gateway (e.g.,
Razorpay/PayU), this service would verify the webhook signature using
`PAYMENT_GATEWAY_WEBHOOK_SECRET` before accepting the payload.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.base import PaymentRepository, SlotBookingRepository
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentStatus

logger = logging.getLogger("app.services.payment_service")


def record_payment(
    payment_data: PaymentCreate,
    farmer_uid: str,
    payment_repo: PaymentRepository,
    booking_repo: SlotBookingRepository,
) -> PaymentOut:
    """Record a payment against a specific booking.
    
    Verifies the booking exists and belongs to the farmer, checks for
    duplicate payments (idempotency), and creates the payment record.
    """
    # 1. Verify the booking exists and belongs to this farmer
    booking = booking_repo.get(payment_data.booking_id)
    if not booking or booking.get("farmer_id") != farmer_uid:
        raise NotFoundError(f"Booking {payment_data.booking_id} not found or access denied")

    # 2. Check for duplicate payments (idempotency)
    existing = payment_repo.get_by_booking_id(payment_data.booking_id)
    if existing:
        raise ConflictError("Payment already recorded for this booking")

    # 3. Create payment record (Simulating successful gateway webhook)
    payment_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc)

    record = {
        "payment_id": payment_id,
        "farmer_id": farmer_uid,
        "booking_id": payment_data.booking_id,
        "amount": payment_data.amount,
        "transaction_ref": payment_data.transaction_ref,
        "status": PaymentStatus.SUCCESS.value,
        "processed_at": processed_at,
    }

    created = payment_repo.create(payment_id, record)
    logger.info("Recorded payment %s for booking %s", payment_id, payment_data.booking_id)
    return PaymentOut.model_validate(created)


def get_farmer_payments(
    farmer_uid: str,
    payment_repo: PaymentRepository,
) -> List[PaymentOut]:
    """Retrieve all payment records for a specific farmer."""
    records = payment_repo.list_by_farmer(farmer_uid)
    return [PaymentOut.model_validate(r) for r in records]
