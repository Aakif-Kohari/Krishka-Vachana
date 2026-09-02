from datetime import date
from unittest.mock import MagicMock

from app.repositories import firestore as firestore_module
from app.repositories.firestore import (
    ACTIVE_SLOT_BOOKINGS_COLLECTION,
    CENTRES_COLLECTION,
    SLOT_BOOKINGS_COLLECTION,
    SLOT_CAPACITY_COUNTERS_COLLECTION,
    FirestoreCentreRepository,
    FirestoreSlotBookingRepository,
)


def _snapshot(*, exists, data=None, doc_id="doc-id"):
    snapshot = MagicMock()
    snapshot.exists = exists
    snapshot.id = doc_id
    snapshot.to_dict.return_value = data or {}
    return snapshot


def test_centre_list_backfills_normalized_fields_and_maps_document_id():
    client = MagicMock()
    collection = MagicMock()
    query = MagicMock()
    document = _snapshot(
        exists=True,
        doc_id="centre-from-doc-id",
        data={"district": "Solapur", "state": "Maharashtra"},
    )
    client.collection.return_value = collection
    collection.stream.return_value = [document]
    collection.where.return_value = query
    query.stream.return_value = [document]

    records = FirestoreCentreRepository(client).list(district="SOLAPUR")

    assert records[0]["centre_id"] == "centre-from-doc-id"
    collection.where.assert_called_once_with("district_normalized", "==", "solapur")
    collection.document.return_value.update.assert_called_once_with(
        {"district_normalized": "solapur", "state_normalized": "maharashtra"}
    )


def test_firestore_booking_serializes_date_and_creates_active_key(monkeypatch):
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction

    collections = {
        CENTRES_COLLECTION: MagicMock(),
        SLOT_BOOKINGS_COLLECTION: MagicMock(),
        SLOT_CAPACITY_COUNTERS_COLLECTION: MagicMock(),
        ACTIVE_SLOT_BOOKINGS_COLLECTION: MagicMock(),
    }
    client.collection.side_effect = collections.__getitem__
    booking_ref = collections[SLOT_BOOKINGS_COLLECTION].document.return_value
    counter_ref = collections[SLOT_CAPACITY_COUNTERS_COLLECTION].document.return_value
    active_ref = collections[ACTIVE_SLOT_BOOKINGS_COLLECTION].document.return_value
    booking_ref.get.return_value = _snapshot(exists=False)
    counter_ref.get.return_value = _snapshot(exists=False)
    active_ref.get.return_value = _snapshot(exists=False)

    result = FirestoreSlotBookingRepository(client).create_if_capacity_available(
        "booking-id",
        2,
        {
            "farmer_id": "farmer-id",
            "centre_id": "centre-id",
            "slot_date": date(2026, 9, 3),
            "slot_window": "08:00-10:00",
            "status": "booked",
        },
    )

    assert result["slot_date"] == "2026-09-03"
    collections[SLOT_CAPACITY_COUNTERS_COLLECTION].document.assert_called_once_with(
        "centre-id_2026-09-03_08:00-10:00"
    )
    booking_write = next(
        data for ref, data in (call.args for call in transaction.create.call_args_list)
        if ref is booking_ref
    )
    assert booking_write["slot_date"] == "2026-09-03"
    assert any(call.args[0] is active_ref for call in transaction.create.call_args_list)
