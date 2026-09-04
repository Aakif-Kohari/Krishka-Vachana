from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.repositories import firestore as firestore_module
from app.repositories.firestore import (
    ACTIVE_BOOKING_QUEUE_COLLECTION,
    ACTIVE_FARMER_QUEUE_COLLECTION,
    ACTIVE_SLOT_BOOKINGS_COLLECTION,
    CENTRES_COLLECTION,
    FARMERS_COLLECTION,
    PAYMENT_BOOKING_RESERVATIONS_COLLECTION,
    PAYMENTS_COLLECTION,
    QUEUE_DAILY_COUNTERS_COLLECTION,
    QUEUE_ENTRIES_COLLECTION,
    SLOT_BOOKINGS_COLLECTION,
    SLOT_CAPACITY_COUNTERS_COLLECTION,
    FirestoreCentreRepository,
    FirestoreFarmerRepository,
    FirestorePaymentRepository,
    FirestoreQueueRepository,
    FirestoreSlotBookingRepository,
)
from app.repositories.base import OtpVerificationResult


def _snapshot(*, exists, data=None, doc_id="doc-id"):
    """Create a mock Firestore document snapshot for testing."""
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
    """Test that centre list maps Firestore doc IDs and filters case-insensitively."""
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
    """Test that centre list excludes centres from non-matching districts."""
    client = MagicMock()
    collection = MagicMock()
    document = _snapshot(exists=True, doc_id="centre-1", data=dict(_VALID_CENTRE_DATA))
    client.collection.return_value = collection
    collection.stream.return_value = [document]

    assert FirestoreCentreRepository(client).list(district="Nagpur") == []


def test_centre_list_skips_documents_missing_required_fields():
    """Test that malformed centre documents missing required fields are skipped."""
    client = MagicMock()
    collection = MagicMock()
    malformed = _snapshot(exists=True, doc_id="incomplete-centre", data={"name": "Only A Name"})
    client.collection.return_value = collection
    collection.stream.return_value = [malformed]

    assert FirestoreCentreRepository(client).list() == []


def test_centre_list_skips_documents_with_invalid_field_types():
    """Test that centre documents with invalid field types are skipped."""
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
    """Test that centre get maps Firestore document ID to centre_id."""
    client = MagicMock()
    collection = MagicMock()
    document = _snapshot(exists=True, doc_id="centre-from-doc-id", data=dict(_VALID_CENTRE_DATA))
    client.collection.return_value = collection
    collection.document.return_value.get.return_value = document

    record = FirestoreCentreRepository(client).get("centre-from-doc-id")

    assert record["centre_id"] == "centre-from-doc-id"


def test_centre_get_returns_none_for_malformed_document():
    """Test that get returns None for centres with missing required fields."""
    client = MagicMock()
    collection = MagicMock()
    malformed = _snapshot(exists=True, doc_id="incomplete-centre", data={"name": "Only A Name"})
    client.collection.return_value = collection
    collection.document.return_value.get.return_value = malformed

    assert FirestoreCentreRepository(client).get("incomplete-centre") is None


def test_firestore_booking_serializes_date_and_creates_active_key(monkeypatch):
    """Test that slot bookings serialize dates to ISO strings and create active booking keys."""
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


def test_firestore_phone_otp_attempt_is_consumed_in_transaction(monkeypatch):
    """Test that OTP verification is atomic and updates phone_verified flag."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction
    farmer_ref = client.collection.return_value.document.return_value
    farmer_ref.get.return_value = _snapshot(
        exists=True,
        data={
            "phone_otp_hash": "expected-hash",
            "phone_otp_expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "phone_otp_attempts": 0,
        },
    )

    result = FirestoreFarmerRepository(client).consume_phone_otp_attempt(
        "farmer-id", "expected-hash", datetime.now(timezone.utc), 5
    )

    assert result is OtpVerificationResult.VERIFIED
    client.collection.assert_called_with(FARMERS_COLLECTION)
    farmer_ref.get.assert_called_once_with(transaction=transaction)
    transaction.update.assert_called_once_with(
        farmer_ref,
        {
            "phone_otp_hash": None,
            "phone_otp_expires_at": None,
            "phone_otp_attempts": 0,
            "phone_verified": True,
        },
    )


def test_firestore_phone_otp_challenge_enforces_cooldown_in_transaction(monkeypatch):
    """Test that OTP challenge issuance rejects a farmer still in cooldown."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction
    farmer_ref = client.collection.return_value.document.return_value
    issued_at = datetime(2026, 9, 4, 8, tzinfo=timezone.utc)
    farmer_ref.get.return_value = _snapshot(
        exists=True,
        data={"phone_otp_issued_at": issued_at - timedelta(seconds=30)},
    )

    issued = FirestoreFarmerRepository(client).issue_phone_otp_challenge(
        "farmer-id",
        issued_at,
        60,
        {"phone_otp_hash": "new-hash"},
    )

    assert issued is False
    farmer_ref.get.assert_called_once_with(transaction=transaction)
    transaction.update.assert_not_called()


def test_firestore_queue_check_in_persists_queue_date(monkeypatch):
    """Test that queue check-in persists the explicit centre-local queue_date."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction

    collections = {
        QUEUE_ENTRIES_COLLECTION: MagicMock(),
        ACTIVE_FARMER_QUEUE_COLLECTION: MagicMock(),
        ACTIVE_BOOKING_QUEUE_COLLECTION: MagicMock(),
        QUEUE_DAILY_COUNTERS_COLLECTION: MagicMock(),
    }
    client.collection.side_effect = collections.__getitem__
    entry_ref = collections[QUEUE_ENTRIES_COLLECTION].document.return_value
    farmer_ref = collections[ACTIVE_FARMER_QUEUE_COLLECTION].document.return_value
    booking_ref = collections[ACTIVE_BOOKING_QUEUE_COLLECTION].document.return_value
    counter_ref = collections[QUEUE_DAILY_COUNTERS_COLLECTION].document.return_value
    farmer_ref.get.return_value = _snapshot(exists=False)
    booking_ref.get.return_value = _snapshot(exists=False)
    counter_ref.get.return_value = _snapshot(exists=False)

    result = FirestoreQueueRepository(client).create_check_in(
        "queue-id",
        "centre-id",
        {
            "farmer_id": "farmer-id",
            "booking_id": "booking-id",
            "centre_id": "centre-id",
            "status": "waiting",
            "joined_at": datetime(2026, 9, 3, 19, tzinfo=timezone.utc),
            "queue_date": "2026-09-04",
        },
    )

    assert result["queue_date"] == "2026-09-04"
    collections[QUEUE_DAILY_COUNTERS_COLLECTION].document.assert_called_once_with(
        "centre-id_2026-09-04"
    )
    entry_write = next(
        data
        for ref, data in (call.args for call in transaction.create.call_args_list)
        if ref is entry_ref
    )
    assert entry_write["queue_date"] == "2026-09-04"


def test_firestore_queue_counts_use_aggregation_and_field_filters():
    """Test that count_waiting_ahead uses server-side aggregation with proper filters."""
    client = MagicMock()
    collection = client.collection.return_value
    first_query = collection.where.return_value
    second_query = first_query.where.return_value
    third_query = second_query.where.return_value
    final_query = third_query.where.return_value
    count_value = MagicMock(value=2)
    final_query.count.return_value.get.return_value = [[count_value]]

    result = FirestoreQueueRepository(client).count_waiting_ahead(
        "centre-id", "2026-09-04", 3
    )

    assert result == 2
    client.collection.assert_called_once_with(QUEUE_ENTRIES_COLLECTION)
    filters = [
        collection.where.call_args.kwargs["filter"],
        first_query.where.call_args.kwargs["filter"],
        second_query.where.call_args.kwargs["filter"],
        third_query.where.call_args.kwargs["filter"],
    ]
    assert [(item.field_path, item.op_string, item.value) for item in filters] == [
        ("centre_id", "==", "centre-id"),
        ("queue_date", "==", "2026-09-04"),
        ("status", "==", "waiting"),
        ("sequence_number", "<", 3),
    ]
    final_query.count.assert_called_once_with(alias="count")
    final_query.stream.assert_not_called()


def test_firestore_waiting_count_uses_aggregation_and_field_filters():
    """Test that count_waiting uses server-side aggregation with proper filters."""
    client = MagicMock()
    collection = client.collection.return_value
    first_query = collection.where.return_value
    second_query = first_query.where.return_value
    final_query = second_query.where.return_value
    final_query.count.return_value.get.return_value = [[MagicMock(value=4)]]

    result = FirestoreQueueRepository(client).count_waiting("centre-id", "2026-09-04")

    assert result == 4
    filters = [
        collection.where.call_args.kwargs["filter"],
        first_query.where.call_args.kwargs["filter"],
        second_query.where.call_args.kwargs["filter"],
    ]
    assert [(item.field_path, item.op_string, item.value) for item in filters] == [
        ("centre_id", "==", "centre-id"),
        ("queue_date", "==", "2026-09-04"),
        ("status", "==", "waiting"),
    ]
    final_query.count.assert_called_once_with(alias="count")
    final_query.stream.assert_not_called()


def test_firestore_payment_create_reserves_booking_in_one_transaction(monkeypatch):
    """Payment creation writes its booking reservation and record atomically."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction

    payment_collection = MagicMock()
    reservation_collection = MagicMock()
    client.collection.side_effect = {
        PAYMENTS_COLLECTION: payment_collection,
        PAYMENT_BOOKING_RESERVATIONS_COLLECTION: reservation_collection,
    }.__getitem__
    payment_ref = MagicMock()
    payment_collection.document.return_value = payment_ref
    reservation_ref = reservation_collection.document.return_value
    reservation_ref.get.return_value = _snapshot(exists=False)
    transaction.get.return_value = iter([])
    data = {
        "booking_id": "booking-1",
        "farmer_id": "farmer-1",
        "amount_paise": 500000,
        "transaction_ref": "TXN_001",
        "status": "success",
        "processed_at": datetime.now(timezone.utc),
    }

    result = FirestorePaymentRepository(client).create_or_get_by_booking_id(
        "payment-1", data
    )

    assert result == {"payment_id": "payment-1", **data}
    reservation_ref.get.assert_called_once_with(transaction=transaction)
    assert transaction.create.call_count == 2
    transaction.commit.assert_not_called()


def test_firestore_payment_duplicate_returns_reserved_payment(monkeypatch):
    """A repeated booking delivery returns the reserved existing payment."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction

    payment_collection = MagicMock()
    reservation_collection = MagicMock()
    client.collection.side_effect = {
        PAYMENTS_COLLECTION: payment_collection,
        PAYMENT_BOOKING_RESERVATIONS_COLLECTION: reservation_collection,
    }.__getitem__
    reservation_collection.document.return_value.get.return_value = _snapshot(
        exists=True, data={"booking_id": "booking-1", "payment_id": "payment-existing"}
    )
    existing_record = {
        "payment_id": "payment-existing",
        "booking_id": "booking-1",
        "farmer_id": "farmer-1",
        "amount_paise": 500000,
        "transaction_ref": "TXN_001",
        "status": "success",
        "processed_at": datetime.now(timezone.utc),
    }
    payment_collection.document.return_value.get.return_value = _snapshot(
        exists=True, data=existing_record
    )

    result = FirestorePaymentRepository(client).create_or_get_by_booking_id(
        "payment-new", {**existing_record, "transaction_ref": "TXN_002"}
    )

    assert result == existing_record
    transaction.create.assert_not_called()
