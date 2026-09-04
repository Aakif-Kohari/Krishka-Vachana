"""Firestore-backed repository implementations.

# TODO (coordinate with Database & Infrastructure engineer):
#   - Confirm final collection names ("farmers", "crops" are placeholders).
#   - Confirm security rules allow Admin SDK writes as used here (Admin SDK
#     normally bypasses rules, but double-check any custom rule assumptions).
#   - Confirm field-level schema matches what's in app/schemas/farmer.py and
#     app/schemas/crop.py, and update either side if it drifts.
# This file intentionally only *consumes* Firestore via the Admin SDK, per
# team_work_division.md's collaboration note: "Backend consumes Firestore
# via Admin SDK; Infra owns schema/security rules."
"""
import hashlib
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import ValidationError

from app.repositories.base import (
    CentreRepository,
    CropRepository,
    FarmerRepository,
    OtpVerificationResult,
    PaymentRepository,
    QueueRepository,
    SlotBookingRepository,
)
from app.schemas.centre import CentreOut

logger = logging.getLogger("app.repositories.firestore")

FARMERS_COLLECTION = "farmers"
CROPS_COLLECTION = "crops"
AADHAAR_RESERVATIONS_COLLECTION = "aadhaar_reservations"
CENTRES_COLLECTION = "centres"
SLOT_BOOKINGS_COLLECTION = "slot_bookings"
ACTIVE_SLOT_BOOKINGS_COLLECTION = "active_slot_bookings"
# One doc per (centre_id, slot_date, slot_window), used purely as an
# atomic counter so capacity checks don't need to scan/count booking docs
# on every request. Doc id: f"{centre_id}_{slot_date.isoformat()}_{slot_window}".
SLOT_CAPACITY_COUNTERS_COLLECTION = "slot_capacity_counters"
QUEUE_ENTRIES_COLLECTION = "queue_entries"
# One doc per farmer_id / booking_id, used purely as an atomic uniqueness
# index so a farmer (or a booking) can't have two waiting queue entries at
# once - same purpose as ACTIVE_SLOT_BOOKINGS_COLLECTION above.
ACTIVE_FARMER_QUEUE_COLLECTION = "active_farmer_queue_entries"
ACTIVE_BOOKING_QUEUE_COLLECTION = "active_booking_queue_entries"
# One doc per (centre_id, date), used as an atomic counter for the daily
# per-centre token sequence number - same pattern as
# SLOT_CAPACITY_COUNTERS_COLLECTION above. Doc id: f"{centre_id}_{date}".
QUEUE_DAILY_COUNTERS_COLLECTION = "queue_daily_counters"
PAYMENTS_COLLECTION = "payments"
PAYMENT_BOOKING_RESERVATIONS_COLLECTION = "payment_booking_reservations"


class FirestoreFarmerRepository(FarmerRepository):
    """Firestore-backed implementation of FarmerRepository."""

    def __init__(self, client) -> None:
        """Initialize with a Firestore client instance."""
        self._client = client

    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by ID from Firestore."""
        doc = self._client.collection(FARMERS_COLLECTION).document(farmer_id).get()
        return doc.to_dict() if doc.exists else None

    def is_cluster_delegate_authorized(
        self, delegate_id: str, farmer_ids: List[str]
    ) -> bool:
        """Check delegate grants stored on every requested farmer document."""
        if not farmer_ids:
            return False
        farmer_collection = self._client.collection(FARMERS_COLLECTION)
        farmer_refs = [farmer_collection.document(farmer_id) for farmer_id in farmer_ids]
        snapshots = list(self._client.get_all(farmer_refs))
        if len(snapshots) != len(farmer_refs):
            return False
        for snapshot in snapshots:
            if not snapshot.exists:
                return False
            farmer = snapshot.to_dict()
            if not isinstance(farmer, dict):
                return False
            grants = farmer.get("authorized_cluster_delegate_ids")
            if not isinstance(grants, list) or delegate_id not in grants:
                return False
        return True

    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by Aadhaar hash from Firestore."""
        query = (
            self._client.collection(FARMERS_COLLECTION)
            .where("aadhaar_hash", "==", aadhaar_hash)
            .limit(1)
        )
        doc = next(iter(query.stream()), None)
        return doc.to_dict() if doc is not None else None

    def reserve_aadhaar(self, aadhaar_hash: str, farmer_id: str) -> bool:
        """Atomically reserve an Aadhaar hash for a farmer ID in a Firestore transaction."""
        reservation_ref = self._client.collection(AADHAAR_RESERVATIONS_COLLECTION).document(
            aadhaar_hash
        )
        matching_farmer_query = (
            self._client.collection(FARMERS_COLLECTION)
            .where("aadhaar_hash", "==", aadhaar_hash)
            .limit(1)
        )
        transaction = self._client.transaction()

        @firestore.transactional
        def reserve(transaction) -> bool:
            reservation = reservation_ref.get(transaction=transaction)
            if reservation.exists:
                return reservation.to_dict().get("farmer_id") == farmer_id

            if next(transaction.get(matching_farmer_query), None) is not None:
                return False

            transaction.create(
                reservation_ref,
                {"aadhaar_hash": aadhaar_hash, "farmer_id": farmer_id},
            )
            return True

        return reserve(transaction)

    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new farmer record in Firestore."""
        ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        ref.set({"farmer_id": farmer_id, **data})
        return {"farmer_id": farmer_id, **data}

    def create_with_aadhaar_reservation(
        self, farmer_id: str, aadhaar_hash: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a farmer record with Aadhaar reservation in a Firestore transaction."""
        farmer_ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        reservation_ref = self._client.collection(AADHAAR_RESERVATIONS_COLLECTION).document(
            aadhaar_hash
        )
        matching_farmer_query = (
            self._client.collection(FARMERS_COLLECTION)
            .where("aadhaar_hash", "==", aadhaar_hash)
            .limit(1)
        )
        record = {"farmer_id": farmer_id, **data, "aadhaar_hash": aadhaar_hash}
        transaction = self._client.transaction()

        @firestore.transactional
        def create(transaction) -> Optional[Dict[str, Any]]:
            farmer = farmer_ref.get(transaction=transaction)
            if farmer.exists:
                return None

            reservation = reservation_ref.get(transaction=transaction)
            if reservation.exists:
                if reservation.to_dict().get("farmer_id") != farmer_id:
                    return None
            else:
                if next(transaction.get(matching_farmer_query), None) is not None:
                    return None
                transaction.create(
                    reservation_ref,
                    {"aadhaar_hash": aadhaar_hash, "farmer_id": farmer_id},
                )

            transaction.create(farmer_ref, record)
            return record

        return create(transaction)

    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a farmer record with the provided data in Firestore."""
        ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        ref.update(data)
        doc = ref.get()
        return doc.to_dict()

    def issue_phone_otp_challenge(
        self,
        farmer_id: str,
        issued_at: datetime,
        cooldown_seconds: int,
        data: Dict[str, Any],
    ) -> bool:
        """Atomically store an OTP challenge unless the farmer is in cooldown."""
        farmer_ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        transaction = self._client.transaction()

        @firestore.transactional
        def issue(transaction) -> bool:
            snapshot = farmer_ref.get(transaction=transaction)
            if not snapshot.exists:
                return False
            last_issued_at = snapshot.to_dict().get("phone_otp_issued_at")
            if last_issued_at and issued_at < last_issued_at + timedelta(seconds=cooldown_seconds):
                return False
            transaction.update(farmer_ref, {**data, "phone_otp_issued_at": issued_at})
            return True

        return issue(transaction)

    def consume_phone_otp_attempt(
        self,
        farmer_id: str,
        submitted_hash: str,
        attempted_at: datetime,
        max_attempts: int,
    ) -> OtpVerificationResult:
        """Atomically verify or consume one phone OTP attempt in a transaction."""
        farmer_ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        transaction = self._client.transaction()

        @firestore.transactional
        def consume(transaction) -> OtpVerificationResult:
            snapshot = farmer_ref.get(transaction=transaction)
            if not snapshot.exists:
                return OtpVerificationResult.NOT_FOUND

            record = snapshot.to_dict()
            stored_hash = record.get("phone_otp_hash")
            expires_at = record.get("phone_otp_expires_at")
            if not stored_hash or not expires_at:
                return OtpVerificationResult.MISSING

            clear_challenge = {
                "phone_otp_hash": None,
                "phone_otp_expires_at": None,
                "phone_otp_attempts": 0,
            }
            if attempted_at > expires_at:
                transaction.update(farmer_ref, clear_challenge)
                return OtpVerificationResult.EXPIRED

            attempts = record.get("phone_otp_attempts", 0)
            if attempts >= max_attempts:
                transaction.update(farmer_ref, clear_challenge)
                return OtpVerificationResult.LOCKED

            if submitted_hash != stored_hash:
                transaction.update(farmer_ref, {"phone_otp_attempts": attempts + 1})
                return OtpVerificationResult.INCORRECT

            transaction.update(farmer_ref, {**clear_challenge, "phone_verified": True})
            return OtpVerificationResult.VERIFIED

        return consume(transaction)


class FirestoreCropRepository(CropRepository):
    """Firestore-backed implementation of CropRepository."""

    def __init__(self, client) -> None:
        """Initialize with a Firestore client instance."""
        self._client = client

    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crop record in Firestore."""
        ref = self._client.collection(CROPS_COLLECTION).document(crop_id)
        ref.set({"crop_id": crop_id, **data})
        return {"crop_id": crop_id, **data}

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's crops."""
        query = (
            self._client.collection(CROPS_COLLECTION)
            .where("farmer_id", "==", farmer_id)
            .order_by("crop_id")
        )
        if cursor is not None:
            query = query.start_after({"crop_id": cursor})
        if limit is not None:
            query = query.limit(limit)
        return [doc.to_dict() for doc in query.stream()]


class FirestoreCentreRepository(CentreRepository):
    """Read-only from the backend's side - centre records are expected to
    be seeded/managed by the Database & Infrastructure engineer. TODO
    (coordinate with them): confirm "centres" is the final collection name
    and that documents match app/schemas/centre.py's CentreOut fields.
    """

    # Fields every CentreOut requires besides centre_id (which is mapped
    # from the Firestore document ID below, not stored as data).
    _REQUIRED_FIELDS = ("name", "village", "district", "state", "capacity_per_slot", "created_at")

    def __init__(self, client) -> None:
        """Initialize with a Firestore client instance."""
        self._client = client

    def _record(self, doc) -> Optional[Dict[str, Any]]:
        """Map a Firestore document to a centre record, or None if malformed.

        Firestore has no case-insensitive query operator (confirmed against
        the Firestore docs - see the PR discussion this fixes), and the
        backend has no write path for centres to keep a normalized shadow
        field in sync (that's Infra's seeding tooling, out of this repo's
        control - see the class docstring). At the scale of a reference
        list of procurement centres (dozens, not millions), it's simpler
        and more robust to fetch the collection and filter in Python here,
        exactly like InMemoryCentreRepository does, than to depend on
        Infra also writing extra normalized fields correctly.
        """
        record = dict(doc.to_dict() or {})
        record["centre_id"] = doc.id
        missing = [f for f in self._REQUIRED_FIELDS if f not in record]
        if missing:
            logger.error(
                "Firestore centre document %s is missing required field(s) %s - skipping it. "
                "Check the seeded data against app/schemas/centre.py:CentreOut.",
                doc.id,
                missing,
            )
            return None
        try:
            return CentreOut.model_validate(record).model_dump(mode="python")
        except ValidationError:
            logger.error(
                "Firestore centre document %s has invalid field types/values - skipping it. "
                "Check the seeded data against app/schemas/centre.py:CentreOut.",
                doc.id,
            )
            return None

    def list(self, district: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List procurement centres from Firestore, optionally filtered by district or state."""
        records = [
            record
            for doc in self._client.collection(CENTRES_COLLECTION).stream()
            if (record := self._record(doc)) is not None
        ]
        if district:
            records = [r for r in records if r["district"].lower() == district.lower()]
        if state:
            records = [r for r in records if r["state"].lower() == state.lower()]
        return records

    def get(self, centre_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a procurement centre by ID from Firestore."""
        doc = self._client.collection(CENTRES_COLLECTION).document(centre_id).get()
        if not doc.exists:
            return None
        return self._record(doc)


def _slot_counter_doc_id(centre_id: str, slot_date: date | str, slot_window: str) -> str:
    """Generate a document ID for a slot capacity counter."""
    slot_date_iso = slot_date.isoformat() if hasattr(slot_date, "isoformat") else str(slot_date)
    return f"{centre_id}_{slot_date_iso}_{slot_window}"


def _active_booking_doc_id(
    farmer_id: str, centre_id: str, slot_date: date | str, slot_window: str
) -> str:
    """Generate a stable document ID for an active farmer/slot booking key."""
    slot_date_iso = slot_date.isoformat() if hasattr(slot_date, "isoformat") else str(slot_date)
    raw_key = "\0".join((farmer_id, centre_id, slot_date_iso, slot_window))
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class FirestoreSlotBookingRepository(SlotBookingRepository):
    """Firestore-backed implementation of SlotBookingRepository.

    TODO (coordinate with Database & Infrastructure engineer): confirm
    "slot_bookings" collection name/schema, and that a dedicated counter
    doc per (centre, date, window) in SLOT_CAPACITY_COUNTERS_COLLECTION is
    an acceptable way to keep capacity checks O(1) instead of counting
    booking docs on every request.
    """

    def __init__(self, client) -> None:
        """Initialize with a Firestore client instance."""
        self._client = client

    def get(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a booking by ID from Firestore."""
        doc = self._client.collection(SLOT_BOOKINGS_COLLECTION).document(booking_id).get()
        return doc.to_dict() if doc.exists else None

    def count_active_bookings(self, centre_id: str, slot_date: date, slot_window: str) -> int:
        """Count active bookings for a specific slot from Firestore counter."""
        doc = (
            self._client.collection(SLOT_CAPACITY_COUNTERS_COLLECTION)
            .document(_slot_counter_doc_id(centre_id, slot_date, slot_window))
            .get()
        )
        return doc.to_dict().get("count", 0) if doc.exists else 0

    def create_if_capacity_available(
        self, booking_id: str, capacity: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a booking if capacity is available in a Firestore transaction."""
        slot_date_iso = data["slot_date"].isoformat()
        booking_ref = self._client.collection(SLOT_BOOKINGS_COLLECTION).document(booking_id)
        counter_ref = self._client.collection(SLOT_CAPACITY_COUNTERS_COLLECTION).document(
            _slot_counter_doc_id(data["centre_id"], slot_date_iso, data["slot_window"])
        )
        active_ref = self._client.collection(ACTIVE_SLOT_BOOKINGS_COLLECTION).document(
            _active_booking_doc_id(
                data["farmer_id"], data["centre_id"], slot_date_iso, data["slot_window"]
            )
        )
        record = {"booking_id": booking_id, **data, "slot_date": slot_date_iso}
        transaction = self._client.transaction()

        @firestore.transactional
        def create(transaction) -> Optional[Dict[str, Any]]:
            existing_booking = booking_ref.get(transaction=transaction)
            if existing_booking.exists:
                return None

            active_booking = active_ref.get(transaction=transaction)
            if active_booking.exists:
                return None

            counter_doc = counter_ref.get(transaction=transaction)
            current = counter_doc.to_dict().get("count", 0) if counter_doc.exists else 0
            if current >= capacity:
                return None

            transaction.set(counter_ref, {"count": current + 1}, merge=True)
            transaction.create(
                active_ref,
                {
                    "booking_id": booking_id,
                    "farmer_id": data["farmer_id"],
                    "centre_id": data["centre_id"],
                    "slot_date": slot_date_iso,
                    "slot_window": data["slot_window"],
                },
            )
            transaction.create(booking_ref, record)
            return record

        return create(transaction)

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's bookings."""
        query = (
            self._client.collection(SLOT_BOOKINGS_COLLECTION)
            .where("farmer_id", "==", farmer_id)
            .order_by("booking_id")
        )
        if cursor is not None:
            query = query.start_after({"booking_id": cursor})
        if limit is not None:
            query = query.limit(limit)
        return [doc.to_dict() for doc in query.stream()]

    def cancel(self, booking_id: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a farmer's booking and release its reserved slot capacity atomically.
        
        Parameters:
        	booking_id (str): Identifier of the booking to cancel.
        	farmer_id (str): Identifier of the farmer who owns the booking.
        
        Returns:
        	Optional[Dict[str, Any]]: The booking record with a cancelled status, or `None` if the booking does not exist or belongs to another farmer.
        """
        booking_ref = self._client.collection(SLOT_BOOKINGS_COLLECTION).document(booking_id)
        transaction = self._client.transaction()

        @firestore.transactional
        def do_cancel(transaction) -> Optional[Dict[str, Any]]:
            snapshot = booking_ref.get(transaction=transaction)
            if not snapshot.exists:
                return None
            record = snapshot.to_dict()
            if record.get("farmer_id") != farmer_id:
                return None
            if record.get("status") != "cancelled":
                counter_ref = self._client.collection(SLOT_CAPACITY_COUNTERS_COLLECTION).document(
                    _slot_counter_doc_id(record["centre_id"], record["slot_date"], record["slot_window"])
                )
                active_ref = self._client.collection(ACTIVE_SLOT_BOOKINGS_COLLECTION).document(
                    _active_booking_doc_id(
                        record["farmer_id"],
                        record["centre_id"],
                        record["slot_date"],
                        record["slot_window"],
                    )
                )
                counter_doc = counter_ref.get(transaction=transaction)
                current = counter_doc.to_dict().get("count", 0) if counter_doc.exists else 0
                transaction.set(counter_ref, {"count": max(0, current - 1)}, merge=True)
                transaction.delete(active_ref)
                record["status"] = "cancelled"
                transaction.update(booking_ref, {"status": "cancelled"})
            return record

        return do_cancel(transaction)


    def create_batch_atomic(
        self, booking_ids: List[str], capacity: int, data_list: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Atomically create multiple slot bookings when all requested bookings can be reserved.
        
        Parameters:
            booking_ids (List[str]): Unique identifiers for the bookings to create.
            capacity (int): Maximum number of bookings allowed for the slot.
            data_list (List[Dict[str, Any]]): Booking data corresponding positionally to
                `booking_ids`.
        
        Returns:
            Optional[List[Dict[str, Any]]]: The created booking records, or `None` if the
            input is empty or mismatched, capacity is insufficient, a booking ID already
            exists, or an active booking conflicts with a requested booking.
        """
        if len(booking_ids) != len(data_list) or not booking_ids:
            return None

        first_data = data_list[0]
        slot_date_iso = first_data["slot_date"] if isinstance(first_data["slot_date"], str) else first_data["slot_date"].isoformat()
        
        counter_ref = self._client.collection(SLOT_CAPACITY_COUNTERS_COLLECTION).document(
            _slot_counter_doc_id(first_data["centre_id"], slot_date_iso, first_data["slot_window"])
        )
        
        booking_refs = [self._client.collection(SLOT_BOOKINGS_COLLECTION).document(bid) for bid in booking_ids]
        active_refs = [
            self._client.collection(ACTIVE_SLOT_BOOKINGS_COLLECTION).document(
                _active_booking_doc_id(d["farmer_id"], d["centre_id"], slot_date_iso, d["slot_window"])
            )
            for d in data_list
        ]

        transaction = self._client.transaction()

        @firestore.transactional
        def create_batch(transaction) -> Optional[List[Dict[str, Any]]]:
            """
            Atomically create a batch of slot bookings when capacity and uniqueness constraints allow it.
            
            Returns:
            	List[Dict[str, Any]]: The created booking records.
            	None: If the batch exceeds capacity or any booking or active-slot record already exists.
            """
            counter_doc = counter_ref.get(transaction=transaction)
            current = counter_doc.to_dict().get("count", 0) if counter_doc.exists else 0
            if current + len(booking_ids) > capacity:
                return None

            for bref, aref in zip(booking_refs, active_refs):
                if bref.get(transaction=transaction).exists:
                    return None
                if aref.get(transaction=transaction).exists:
                    return None

            transaction.set(counter_ref, {"count": current + len(booking_ids)}, merge=True)
            
            created_records = []
            for bid, data, bref, aref in zip(booking_ids, data_list, booking_refs, active_refs):
                record = {"booking_id": bid, **data, "slot_date": slot_date_iso}
                transaction.create(bref, record)
                transaction.create(aref, {
                    "booking_id": bid, "farmer_id": data["farmer_id"],
                    "centre_id": data["centre_id"], "slot_date": slot_date_iso,
                    "slot_window": data["slot_window"],
                })
                created_records.append(record)
                
            return created_records

        return create_batch(transaction)


def _queue_daily_counter_doc_id(centre_id: str, queue_date: str) -> str:
    """Generate a document ID for a centre's daily queue token-sequence counter."""
    return f"{centre_id}_{queue_date}"


class FirestoreQueueRepository(QueueRepository):
    """Firestore-backed implementation of QueueRepository.

    TODO (coordinate with Database & Infrastructure engineer): confirm
    "queue_entries" collection name/schema. The composite index for the
    position query is declared in the repository's firestore.indexes.json.
    """

    def __init__(self, client) -> None:
        """Initialize with a Firestore client instance."""
        self._client = client

    def get(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a queue entry by ID from Firestore."""
        doc = self._client.collection(QUEUE_ENTRIES_COLLECTION).document(queue_id).get()
        return doc.to_dict() if doc.exists else None

    def get_active_for_farmer(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer's current waiting queue entry, if any, from Firestore."""
        index_doc = self._client.collection(ACTIVE_FARMER_QUEUE_COLLECTION).document(farmer_id).get()
        if not index_doc.exists:
            return None
        return self.get(index_doc.to_dict()["queue_id"])

    def get_active_for_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the waiting queue entry checked in against a booking, if any."""
        index_doc = self._client.collection(ACTIVE_BOOKING_QUEUE_COLLECTION).document(booking_id).get()
        if not index_doc.exists:
            return None
        return self.get(index_doc.to_dict()["queue_id"])

    def create_check_in(
        self, queue_id: str, centre_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically check a farmer in, assigning the next daily per-centre sequence number."""
        farmer_id = data["farmer_id"]
        booking_id = data["booking_id"]
        queue_date = data["queue_date"]
        entry_ref = self._client.collection(QUEUE_ENTRIES_COLLECTION).document(queue_id)
        active_farmer_ref = self._client.collection(ACTIVE_FARMER_QUEUE_COLLECTION).document(farmer_id)
        active_booking_ref = self._client.collection(ACTIVE_BOOKING_QUEUE_COLLECTION).document(booking_id)
        counter_ref = self._client.collection(QUEUE_DAILY_COUNTERS_COLLECTION).document(
            _queue_daily_counter_doc_id(centre_id, queue_date)
        )
        transaction = self._client.transaction()

        @firestore.transactional
        def create(transaction) -> Optional[Dict[str, Any]]:
            if active_farmer_ref.get(transaction=transaction).exists:
                return None
            if active_booking_ref.get(transaction=transaction).exists:
                return None

            counter_doc = counter_ref.get(transaction=transaction)
            sequence_number = (counter_doc.to_dict().get("count", 0) if counter_doc.exists else 0) + 1

            record = {
                "queue_id": queue_id,
                "sequence_number": sequence_number,
                **data,
                "queue_date": queue_date,
            }
            transaction.set(counter_ref, {"count": sequence_number}, merge=True)
            transaction.create(active_farmer_ref, {"queue_id": queue_id, "farmer_id": farmer_id})
            transaction.create(active_booking_ref, {"queue_id": queue_id, "booking_id": booking_id})
            transaction.create(entry_ref, record)
            return record

        return create(transaction)

    @staticmethod
    def _count(query) -> int:
        """Execute a Firestore server-side aggregation count query and return the result."""
        results = query.count(alias="count").get()
        return results[0][0].value if results else 0

    def count_waiting_ahead(
        self, centre_id: str, queue_date: str, sequence_number: int
    ) -> int:
        """Count same-day waiting entries at a centre with a lower sequence number."""
        query = (
            self._client.collection(QUEUE_ENTRIES_COLLECTION)
            .where(filter=FieldFilter("centre_id", "==", centre_id))
            .where(filter=FieldFilter("queue_date", "==", queue_date))
            .where(filter=FieldFilter("status", "==", "waiting"))
            .where(filter=FieldFilter("sequence_number", "<", sequence_number))
        )
        return self._count(query)

    def count_waiting(self, centre_id: str, queue_date: str) -> int:
        """Count all waiting entries at a centre on a queue date."""
        query = (
            self._client.collection(QUEUE_ENTRIES_COLLECTION)
            .where(filter=FieldFilter("centre_id", "==", centre_id))
            .where(filter=FieldFilter("queue_date", "==", queue_date))
            .where(filter=FieldFilter("status", "==", "waiting"))
        )
        return self._count(query)

    def resolve(
        self, queue_id: str, farmer_id: str, new_status: str, resolved_at: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a farmer's waiting queue entry and release its active reservations.
        
        Parameters:
            queue_id (str): Identifier of the queue entry.
            farmer_id (str): Farmer who owns the queue entry.
            new_status (str): Terminal status to assign to the entry.
            resolved_at (datetime): Timestamp when the entry was resolved.
        
        Returns:
            Optional[Dict[str, Any]]: The updated queue entry, or None if the entry does not exist, belongs to another farmer, or is not waiting.
        """
        entry_ref = self._client.collection(QUEUE_ENTRIES_COLLECTION).document(queue_id)
        transaction = self._client.transaction()

        @firestore.transactional
        def do_resolve(transaction) -> Optional[Dict[str, Any]]:
            """
            Resolve the farmer's waiting queue entry with the requested status.
            
            Returns:
                Optional[Dict[str, Any]]: The updated queue entry, or `None` if the
                entry does not exist, belongs to another farmer, or is not waiting.
            """
            snapshot = entry_ref.get(transaction=transaction)
            if not snapshot.exists:
                return None
            record = snapshot.to_dict()
            if record.get("farmer_id") != farmer_id or record.get("status") != "waiting":
                return None

            active_farmer_ref = self._client.collection(ACTIVE_FARMER_QUEUE_COLLECTION).document(
                farmer_id
            )
            active_booking_ref = self._client.collection(ACTIVE_BOOKING_QUEUE_COLLECTION).document(
                record["booking_id"]
            )
            transaction.delete(active_farmer_ref)
            transaction.delete(active_booking_ref)
            transaction.update(entry_ref, {"status": new_status, "resolved_at": resolved_at})
            record["status"] = new_status
            record["resolved_at"] = resolved_at
            return record

        return do_resolve(transaction)


class FirestorePaymentRepository(PaymentRepository):
    """Firestore-backed implementation of PaymentRepository."""

    def __init__(self, client) -> None:
        self._client = client

    def get(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a payment by its identifier.
        
        Parameters:
        	payment_id (str): The payment identifier.
        
        Returns:
        	Optional[Dict[str, Any]]: The payment data, or `None` if no matching payment exists.
        """
        doc = self._client.collection(PAYMENTS_COLLECTION).document(payment_id).get()
        return doc.to_dict() if doc.exists else None

    def get_by_booking_id(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the payment associated with a booking.
        
        Parameters:
        	booking_id (str): Identifier of the booking.
        
        Returns:
        	Optional[Dict[str, Any]]: The payment record, or `None` if no payment is found.
        """
        query = self._client.collection(PAYMENTS_COLLECTION).where("booking_id", "==", booking_id).limit(1)
        doc = next(iter(query.stream()), None)
        return doc.to_dict() if doc is not None else None

    def create(self, payment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment record with the specified identifier and data.
        
        Parameters:
        	payment_id (str): Unique identifier for the payment.
        	data (Dict[str, Any]): Payment fields to store.
        
        Returns:
        	Dict[str, Any]: The created payment record, including its identifier.
        """
        return self.create_or_get_by_booking_id(payment_id, data)

    def create_or_get_by_booking_id(
        self, payment_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atomically reserve a booking ID and create or return its payment."""
        booking_id = data["booking_id"]
        reservation_id = hashlib.sha256(booking_id.encode("utf-8")).hexdigest()
        payment_collection = self._client.collection(PAYMENTS_COLLECTION)
        reservation_ref = self._client.collection(
            PAYMENT_BOOKING_RESERVATIONS_COLLECTION
        ).document(reservation_id)
        payment_ref = payment_collection.document(payment_id)
        existing_query = payment_collection.where("booking_id", "==", booking_id).limit(1)
        transaction = self._client.transaction()

        @firestore.transactional
        def create_or_get(transaction) -> Dict[str, Any]:
            reservation = reservation_ref.get(transaction=transaction)
            if reservation.exists:
                existing_id = reservation.to_dict()["payment_id"]
                existing = payment_collection.document(existing_id).get(
                    transaction=transaction
                )
                if not existing.exists:
                    raise RuntimeError("Payment booking reservation is inconsistent")
                return existing.to_dict()

            legacy = next(transaction.get(existing_query), None)
            if legacy is not None:
                existing_record = legacy.to_dict()
                existing_id = existing_record.get("payment_id", legacy.id)
                transaction.create(
                    reservation_ref,
                    {"booking_id": booking_id, "payment_id": existing_id},
                )
                return {"payment_id": existing_id, **existing_record}

            record = {"payment_id": payment_id, **data}
            transaction.create(payment_ref, record)
            transaction.create(
                reservation_ref,
                {"booking_id": booking_id, "payment_id": payment_id},
            )
            return record

        return create_or_get(transaction)

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's payments.
        
        Parameters:
            farmer_id (str): Identifier of the farmer whose payments to retrieve.
        
        Returns:
            List[Dict[str, Any]]: Payment records associated with the farmer.
        """
        query = (
            self._client.collection(PAYMENTS_COLLECTION)
            .where("farmer_id", "==", farmer_id)
            .order_by("payment_id")
        )
        if cursor is not None:
            query = query.start_after({"payment_id": cursor})
        if limit is not None:
            query = query.limit(limit)
        return [doc.to_dict() for doc in query.stream()]
