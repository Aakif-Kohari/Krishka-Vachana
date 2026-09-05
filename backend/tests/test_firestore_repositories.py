from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, call

import pytest

from app.repositories import firestore as firestore_module
from app.repositories.firestore import (
    ACTIVE_BOOKING_QUEUE_COLLECTION,
    ACTIVE_FARMER_QUEUE_COLLECTION,
    ACTIVE_SLOT_BOOKINGS_COLLECTION,
    CENTRES_COLLECTION,
    CROPS_COLLECTION,
    FARMERS_COLLECTION,
    PAYMENT_BOOKING_RESERVATIONS_COLLECTION,
    PAYMENTS_COLLECTION,
    QUEUE_DAILY_COUNTERS_COLLECTION,
    QUEUE_ENTRIES_COLLECTION,
    SLOT_BOOKINGS_COLLECTION,
    SLOT_CAPACITY_COUNTERS_COLLECTION,
    FirestoreCentreRepository,
    FirestoreCropRepository,
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


@pytest.mark.parametrize(
    ("repository_class", "collection_name", "cursor_field"),
    [
        (FirestoreCropRepository, CROPS_COLLECTION, "crop_id"),
        (FirestoreSlotBookingRepository, SLOT_BOOKINGS_COLLECTION, "booking_id"),
        (FirestorePaymentRepository, PAYMENTS_COLLECTION, "payment_id"),
    ],
)
def test_history_repositories_apply_cursor_and_limit(
    repository_class, collection_name, cursor_field
):
    """Verify that history repositories support cursor-based pagination."""
    client = MagicMock()
    collection = client.collection.return_value
    filtered_query = collection.where.return_value
    ordered_query = filtered_query.order_by.return_value
    cursor_query = ordered_query.start_after.return_value
    limited_query = cursor_query.limit.return_value
    limited_query.stream.return_value = [_snapshot(exists=True, data={cursor_field: "next"})]

    records = repository_class(client).list_by_farmer(
        "farmer-id", limit=3, cursor="current"
    )

    assert records == [{cursor_field: "next"}]
    client.collection.assert_called_once_with(collection_name)
    filter_arg = collection.where.call_args.kwargs["filter"]
    assert filter_arg.field_path == "farmer_id"
    assert filter_arg.op_string == "=="
    assert filter_arg.value == "farmer-id"
    filtered_query.order_by.assert_called_once_with(cursor_field)
    ordered_query.start_after.assert_called_once_with({cursor_field: "current"})
    cursor_query.limit.assert_called_once_with(3)


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


def test_cluster_delegate_authorization_fetches_all_farmers_in_one_call():
    """Verify that delegate authorization checks are batched efficiently."""
    client = MagicMock()
    collection = MagicMock()
    client.collection.return_value = collection
    refs = [MagicMock(), MagicMock()]
    collection.document.side_effect = refs
    client.get_all.return_value = [
        _snapshot(
            exists=True,
            data={"authorized_cluster_delegate_ids": ["delegate-id"]},
        ),
        _snapshot(
            exists=True,
            data={"authorized_cluster_delegate_ids": ["delegate-id"]},
        ),
    ]

    authorized = FirestoreFarmerRepository(client).is_cluster_delegate_authorized(
        "delegate-id", ["farmer-1", "farmer-2"]
    )

    assert authorized is True
    client.get_all.assert_called_once_with(refs)
    for ref in refs:
        ref.get.assert_not_called()


@pytest.mark.parametrize(
    "snapshots",
    [
        [_snapshot(exists=False)],
        [_snapshot(exists=True, data={"authorized_cluster_delegate_ids": "delegate-id"})],
        [],
    ],
)
def test_cluster_delegate_authorization_rejects_missing_or_invalid_grants(snapshots):
    """Verify that delegate authorization rejects missing or invalid grants."""
    client = MagicMock()
    client.get_all.return_value = snapshots

    assert FirestoreFarmerRepository(client).is_cluster_delegate_authorized(
        "delegate-id", ["farmer-1"]
    ) is False


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


def test_firestore_batch_booking_serializes_date(monkeypatch):
    """Verify all batch reads and writes preserve positional booking data."""
    monkeypatch.setattr(firestore_module.firestore, "transactional", lambda function: function)
    client = MagicMock()
    transaction = MagicMock()
    client.transaction.return_value = transaction
    collections = {
        SLOT_BOOKINGS_COLLECTION: MagicMock(),
        SLOT_CAPACITY_COUNTERS_COLLECTION: MagicMock(),
        ACTIVE_SLOT_BOOKINGS_COLLECTION: MagicMock(),
    }
    client.collection.side_effect = collections.__getitem__
    booking_refs = [MagicMock(name="booking_ref_1"), MagicMock(name="booking_ref_2")]
    active_refs = [MagicMock(name="active_ref_1"), MagicMock(name="active_ref_2")]
    collections[SLOT_BOOKINGS_COLLECTION].document.side_effect = booking_refs
    collections[ACTIVE_SLOT_BOOKINGS_COLLECTION].document.side_effect = active_refs
    counter_ref = collections[SLOT_CAPACITY_COUNTERS_COLLECTION].document.return_value
    counter_ref.get.return_value = _snapshot(exists=True, data={"count": 1})
    client.get_all.return_value = [_snapshot(exists=False) for _ in range(4)]

    data_list = [
        {
            "farmer_id": "farmer-1",
            "centre_id": "centre-id",
            "slot_date": date(2026, 9, 3),
            "slot_window": "08:00-10:00",
            "status": "booked",
        },
        {
            "farmer_id": "farmer-2",
            "centre_id": "centre-id",
            "slot_date": date(2026, 9, 3),
            "slot_window": "08:00-10:00",
            "status": "booked",
        },
    ]

    result = FirestoreSlotBookingRepository(client).create_batch_atomic(
        ["booking-1", "booking-2"],
        3,
        data_list,
    )

    expected_records = [
        {"booking_id": booking_id, **data, "slot_date": "2026-09-03"}
        for booking_id, data in zip(["booking-1", "booking-2"], data_list)
    ]
    assert result == expected_records
    counter_ref.get.assert_called_once_with(transaction=transaction)
    client.get_all.assert_called_once_with(
        booking_refs + active_refs, transaction=transaction
    )
    transaction.set.assert_called_once_with(counter_ref, {"count": 3}, merge=True)
    assert transaction.create.call_args_list == [
        call(booking_refs[0], expected_records[0]),
        call(
            active_refs[0],
            {
                "booking_id": "booking-1",
                "farmer_id": "farmer-1",
                "centre_id": "centre-id",
                "slot_date": "2026-09-03",
                "slot_window": "08:00-10:00",
            },
        ),
        call(booking_refs[1], expected_records[1]),
        call(
            active_refs[1],
            {
                "booking_id": "booking-2",
                "farmer_id": "farmer-2",
                "centre_id": "centre-id",
                "slot_date": "2026-09-03",
                "slot_window": "08:00-10:00",
            },
        ),
    ]
    for ref in booking_refs + active_refs:
        ref.get.assert_not_called()


@pytest.mark.parametrize(
    ("booking_ids", "farmer_ids"),
    [
        (["booking-1", "booking-1"], ["farmer-1", "farmer-2"]),
        (["booking-1", "booking-2"], ["farmer-1", "farmer-1"]),
    ],
)
def test_firestore_batch_booking_rejects_duplicate_document_refs(
    booking_ids, farmer_ids
):
    """Verify duplicate booking or active-booking paths are rejected before writes."""
    client = MagicMock()
    collections = {
        SLOT_BOOKINGS_COLLECTION: MagicMock(),
        SLOT_CAPACITY_COUNTERS_COLLECTION: MagicMock(),
        ACTIVE_SLOT_BOOKINGS_COLLECTION: MagicMock(),
    }
    client.collection.side_effect = collections.__getitem__
    booking_refs_by_id = {
        booking_id: MagicMock(name=f"booking_ref_{booking_id}")
        for booking_id in set(booking_ids)
    }
    active_refs_by_farmer = {
        farmer_id: MagicMock(name=f"active_ref_{farmer_id}")
        for farmer_id in set(farmer_ids)
    }
    active_refs = iter(active_refs_by_farmer[farmer_id] for farmer_id in farmer_ids)
    collections[SLOT_BOOKINGS_COLLECTION].document.side_effect = booking_refs_by_id.get
    collections[ACTIVE_SLOT_BOOKINGS_COLLECTION].document.side_effect = (
        lambda _doc_id: next(active_refs)
    )

    result = FirestoreSlotBookingRepository(client).create_batch_atomic(
        booking_ids,
        2,
        [
            {
                "farmer_id": farmer_id,
                "centre_id": "centre-id",
                "slot_date": date(2026, 9, 3),
                "slot_window": "08:00-10:00",
            }
            for farmer_id in farmer_ids
        ],
    )

    assert result is None
    client.transaction.assert_not_called()
    client.get_all.assert_not_called()


def test_firestore_batch_booking_rejects_mixed_slots_before_creating_references():
    """Verify that one batch cannot reserve bookings across multiple slots."""
    client = MagicMock()

    result = FirestoreSlotBookingRepository(client).create_batch_atomic(
        ["booking-1", "booking-2"],
        2,
        [
            {
                "farmer_id": "farmer-1",
                "centre_id": "centre-id",
                "slot_date": date(2026, 9, 3),
                "slot_window": "08:00-10:00",
            },
            {
                "farmer_id": "farmer-2",
                "centre_id": "centre-id",
                "slot_date": date(2026, 9, 3),
                "slot_window": "10:00-12:00",
            },
        ],
    )

    assert result is None
    client.collection.assert_not_called()


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
