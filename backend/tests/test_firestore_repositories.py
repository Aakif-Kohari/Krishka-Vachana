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


_VALID_CENTRE_DATA = {
    "name": "Test Centre",
    "village": "Testville",
    "district": "Solapur",
    "state": "Maharashtra",
    "capacity_per_slot": 10,
    "created_at": "2026-01-01T00:00:00+00:00",
}


def test_centre_list_maps_document_id_and_filters_case_insensitively():
    client = MagicMock()
    collection = MagicMock()
    document = _snapshot(
        exists=True,
        doc_id="centre-from-doc-id",
        data={**_VALID_CENTRE_DATA, "centre_id": "legacy-centre-id"},
    )
    client.collection.return_value = collection
    collection.stream.return_value = [document]

    # No Firestore query filter is applied server-side (Firestore has no
    # case-insensitive operator) - filtering happens in Python, matching
    # InMemoryCentreRepository's behavior.
    records = FirestoreCentreRepository(client).list(district="SOLAPUR")

    assert len(records) == 1
    assert records[0]["centre_id"] == "centre-from-doc-id"
    collection.where.assert_not_called()


def test_centre_list_filters_out_non_matching_district():
    client = MagicMock()
    collection = MagicMock()
    document = _snapshot(exists=True, doc_id="centre-1", data=dict(_VALID_CENTRE_DATA))
    client.collection.return_value = collection
    collection.stream.return_value = [document]

    assert FirestoreCentreRepository(client).list(district="Nagpur") == []


def test_centre_list_skips_documents_missing_required_fields():
    client = MagicMock()
    collection = MagicMock()
    malformed = _snapshot(exists=True, doc_id="incomplete-centre", data={"name": "Only A Name"})
    client.collection.return_value = collection
    collection.stream.return_value = [malformed]

    assert FirestoreCentreRepository(client).list() == []


def test_centre_list_skips_documents_with_invalid_field_types():
    client = MagicMock()
    collection = MagicMock()
    malformed = _snapshot(
        exists=True,
        doc_id="bad-centre",
        data={**_VALID_CENTRE_DATA, "district": 123},
    )
    client.collection.return_value = collection
    collection.stream.return_value = [malformed]

    assert FirestoreCentreRepository(client).list() == []


def test_centre_get_maps_document_id():
    client = MagicMock()
    collection = MagicMock()
    document = _snapshot(exists=True, doc_id="centre-from-doc-id", data=dict(_VALID_CENTRE_DATA))
    client.collection.return_value = collection
    collection.document.return_value.get.return_value = document

    record = FirestoreCentreRepository(client).get("centre-from-doc-id")

    assert record["centre_id"] == "centre-from-doc-id"


def test_centre_get_returns_none_for_malformed_document():
    client = MagicMock()
    collection = MagicMock()
    malformed = _snapshot(exists=True, doc_id="incomplete-centre", data={"name": "Only A Name"})
    client.collection.return_value = collection
    collection.document.return_value.get.return_value = malformed

    assert FirestoreCentreRepository(client).get("incomplete-centre") is None


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
