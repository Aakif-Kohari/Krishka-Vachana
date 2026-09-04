"""Historical farm record business logic.

Aggregates data from multiple repositories into a single unified response
for the frontend dashboard.
"""
from app.repositories.base import CropRepository, PaymentRepository, SlotBookingRepository
from app.schemas.crop import CropOut
from app.schemas.history import (
    FarmHistoryCursor,
    FarmHistoryOut,
    FarmHistoryPageInfo,
    FarmHistoryQuery,
)
from app.schemas.payment import PaymentOut
from app.schemas.slot import SlotBookingOut


def get_farmer_history(
    farmer_uid: str,
    crop_repo: CropRepository,
    booking_repo: SlotBookingRepository,
    payment_repo: PaymentRepository,
    pagination: FarmHistoryQuery,
) -> FarmHistoryOut:
    """
    Aggregate a farmer's crop, booking, and payment history.
    
    Returns:
        FarmHistoryOut: The farmer's validated crops, slot bookings, and payments.
    """

    positions = pagination.decoded_cursor()
    fetch_limit = pagination.page_size + 1
    crops_data = crop_repo.list_by_farmer(
        farmer_uid, limit=fetch_limit, cursor=positions.crops
    )
    bookings_data = booking_repo.list_by_farmer(
        farmer_uid, limit=fetch_limit, cursor=positions.bookings
    )
    payments_data = payment_repo.list_by_farmer(
        farmer_uid, limit=fetch_limit, cursor=positions.payments
    )

    has_next_page = any(
        len(records) > pagination.page_size
        for records in (crops_data, bookings_data, payments_data)
    )
    crops_data = crops_data[: pagination.page_size]
    bookings_data = bookings_data[: pagination.page_size]
    payments_data = payments_data[: pagination.page_size]

    crops = [CropOut.model_validate(c) for c in crops_data]
    bookings = [SlotBookingOut.model_validate(b) for b in bookings_data]
    payments = [PaymentOut.model_validate(p) for p in payments_data]

    next_positions = FarmHistoryCursor(
        crops=crops[-1].crop_id if crops else positions.crops,
        bookings=bookings[-1].booking_id if bookings else positions.bookings,
        payments=payments[-1].payment_id if payments else positions.payments,
    )

    return FarmHistoryOut(
        crops=crops,
        bookings=bookings,
        payments=payments,
        page=FarmHistoryPageInfo(
            page_size=pagination.page_size,
            next_cursor=next_positions.to_token() if has_next_page else None,
        ),
    )
