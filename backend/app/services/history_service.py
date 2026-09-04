"""Historical farm record business logic.

Aggregates data from multiple repositories into a single unified response
for the frontend dashboard.
"""
from app.repositories.base import CropRepository, PaymentRepository, SlotBookingRepository
from app.schemas.crop import CropOut
from app.schemas.history import FarmHistoryOut
from app.schemas.payment import PaymentOut
from app.schemas.slot import SlotBookingOut


def get_farmer_history(
    farmer_uid: str,
    crop_repo: CropRepository,
    booking_repo: SlotBookingRepository,
    payment_repo: PaymentRepository,
) -> FarmHistoryOut:
    """
    Aggregate a farmer's crop, booking, and payment history.
    
    Returns:
        FarmHistoryOut: The farmer's validated crops, slot bookings, and payments.
    """
    crops_data = crop_repo.list_by_farmer(farmer_uid)
    bookings_data = booking_repo.list_by_farmer(farmer_uid)
    payments_data = payment_repo.list_by_farmer(farmer_uid)

    crops = [CropOut.model_validate(c) for c in crops_data]
    bookings = [SlotBookingOut.model_validate(b) for b in bookings_data]
    payments = [PaymentOut.model_validate(p) for p in payments_data]

    return FarmHistoryOut(
        crops=crops,
        bookings=bookings,
        payments=payments,
    )
