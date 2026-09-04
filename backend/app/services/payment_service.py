"""Payment tracking business logic.

Handles post-procurement payments from the development mock flow and from a
production gateway webhook verified with `PAYMENT_GATEWAY_WEBHOOK_SECRET`.
"""
import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import ValidationError

from app.core.exceptions import (
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    ValidationAppError,
)
from app.repositories.base import PaymentRepository, SlotBookingRepository
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentStatus, PaymentWebhookPayload

logger = logging.getLogger("app.services.payment_service")


def record_payment(
    payment_data: PaymentCreate,
    farmer_uid: str,
    payment_repo: PaymentRepository,
    booking_repo: SlotBookingRepository,
) -> PaymentOut:
    """
    Record a payment for a farmer's booking.
    
    Parameters:
        payment_data (PaymentCreate): Payment details, including the booking,
            amount, and transaction reference.
        farmer_uid (str): Identifier of the farmer making the payment.
        payment_repo (PaymentRepository): Repository used to access and store payments.
        booking_repo (SlotBookingRepository): Repository used to verify the booking.
    
    Returns:
        PaymentOut: The recorded payment with a successful status and processing timestamp.
    
    Raises:
        NotFoundError: If the booking does not exist or does not belong to the farmer.
    """
    # 1. Verify the booking exists and belongs to this farmer
    booking = booking_repo.get(payment_data.booking_id)
    if not booking or booking.get("farmer_id") != farmer_uid:
        raise NotFoundError(f"Booking {payment_data.booking_id} not found or access denied")

    # 2. Atomically create the payment or return the record from an earlier delivery.
    payment_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc)

    record = {
        "payment_id": payment_id,
        "farmer_id": farmer_uid,
        "booking_id": payment_data.booking_id,
        "amount_paise": payment_data.amount_paise,
        "transaction_ref": payment_data.transaction_ref,
        "status": PaymentStatus.SUCCESS.value,
        "processed_at": processed_at,
    }

    created = payment_repo.create_or_get_by_booking_id(payment_id, record)
    logger.info("Recorded payment %s for booking %s", payment_id, payment_data.booking_id)
    return PaymentOut.model_validate(created)


def verify_and_parse_webhook(
    body: bytes, signature: str, webhook_secret: str
) -> PaymentWebhookPayload:
    """Verify an HMAC-SHA256 gateway signature before parsing its payload."""
    if not webhook_secret:
        raise ServiceUnavailableError("Payment webhook secret is not configured")

    try:
        supplied_digest = bytes.fromhex(signature.removeprefix("sha256="))
    except ValueError:
        supplied_digest = b""
    expected_digest = hmac.new(
        webhook_secret.encode("utf-8"), body, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(supplied_digest, expected_digest):
        raise UnauthorizedError("Invalid payment webhook signature")

    try:
        return PaymentWebhookPayload.model_validate_json(body)
    except ValidationError as exc:
        raise ValidationAppError("Invalid payment webhook payload") from exc


def record_gateway_payment(
    payment_data: PaymentWebhookPayload,
    payment_repo: PaymentRepository,
    booking_repo: SlotBookingRepository,
) -> PaymentOut:
    """Record a successful, signature-verified gateway payment event."""
    booking = booking_repo.get(payment_data.booking_id)
    if not booking or not booking.get("farmer_id"):
        raise NotFoundError(f"Booking {payment_data.booking_id} not found")
    return record_payment(
        PaymentCreate(
            booking_id=payment_data.booking_id,
            amount_paise=payment_data.amount_paise,
            transaction_ref=payment_data.transaction_ref,
        ),
        booking["farmer_id"],
        payment_repo,
        booking_repo,
    )


def get_farmer_payments(
    farmer_uid: str,
    payment_repo: PaymentRepository,
) -> List[PaymentOut]:
    """Retrieve all payment records for a specific farmer."""
    records = payment_repo.list_by_farmer(farmer_uid)
    return [PaymentOut.model_validate(r) for r in records]
