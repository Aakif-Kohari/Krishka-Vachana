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
from datetime import date
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from app.repositories.base import CentreRepository, CropRepository, FarmerRepository, SlotBookingRepository

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


class FirestoreFarmerRepository(FarmerRepository):
    """Firestore-backed implementation of FarmerRepository."""

    def __init__(self, client) -> None:
        self._client = client

    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by ID from Firestore."""
        doc = self._client.collection(FARMERS_COLLECTION).document(farmer_id).get()
        return doc.to_dict() if doc.exists else None

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


class FirestoreCropRepository(CropRepository):
    """Firestore-backed implementation of CropRepository."""

    def __init__(self, client) -> None:
        self._client = client

    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crop record in Firestore."""
        ref = self._client.collection(CROPS_COLLECTION).document(crop_id)
        ref.set({"crop_id": crop_id, **data})
        return {"crop_id": crop_id, **data}

    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        """List all crops registered by a farmer from Firestore."""
        query = self._client.collection(CROPS_COLLECTION).where("farmer_id", "==", farmer_id)
        return [doc.to_dict() for doc in query.stream()]


class FirestoreCentreRepository(CentreRepository):
    """Read-only from the backend's side - centre records are expected to
    be seeded/managed by the Database & Infrastructure engineer. TODO
    (coordinate with them): confirm "centres" is the final collection name
    and that documents match app/schemas/centre.py's CentreOut fields.
    """

    def __init__(self, client) -> None:
        self._client = client

    @staticmethod
    def _normalized(value: str) -> str:
        return value.lower()

    def _record(self, doc) -> Dict[str, Any]:
        record = doc.to_dict()
        record.setdefault("centre_id", doc.id)
        return record

    def _backfill_normalized_fields(self) -> None:
        """Populate normalized filter fields on legacy and externally seeded records."""
        collection = self._client.collection(CENTRES_COLLECTION)
        for doc in collection.stream():
            record = doc.to_dict()
            updates = {}
            for field in ("district", "state"):
                value = record.get(field)
                if isinstance(value, str):
                    normalized_field = f"{field}_normalized"
                    normalized_value = self._normalized(value)
                    if record.get(normalized_field) != normalized_value:
                        updates[normalized_field] = normalized_value
            if updates:
                collection.document(doc.id).update(updates)

    def list(self, district: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List procurement centres from Firestore, optionally filtered by district or state."""
        self._backfill_normalized_fields()
        query = self._client.collection(CENTRES_COLLECTION)
        if district:
            query = query.where("district_normalized", "==", self._normalized(district))
        if state:
            query = query.where("state_normalized", "==", self._normalized(state))
        return [self._record(doc) for doc in query.stream()]

    def get(self, centre_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a procurement centre by ID from Firestore."""
        ref = self._client.collection(CENTRES_COLLECTION).document(centre_id)
        doc = ref.get()
        if not doc.exists:
            return None
        record = self._record(doc)
        updates = {
            f"{field}_normalized": self._normalized(record[field])
            for field in ("district", "state")
            if isinstance(record.get(field), str)
            and record.get(f"{field}_normalized") != self._normalized(record[field])
        }
        if updates:
            ref.update(updates)
        return record


def _slot_counter_doc_id(centre_id: str, slot_date: date, slot_window: str) -> str:
    """Generate a document ID for a slot capacity counter."""
    slot_date_iso = slot_date.isoformat() if hasattr(slot_date, "isoformat") else str(slot_date)
    return f"{centre_id}_{slot_date_iso}_{slot_window}"


def _active_booking_doc_id(
    farmer_id: str, centre_id: str, slot_date: date, slot_window: str
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

            transaction.set(counter_ref, {"count": current + 1})
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

    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        """List all bookings for a farmer from Firestore."""
        query = self._client.collection(SLOT_BOOKINGS_COLLECTION).where("farmer_id", "==", farmer_id)
        return [doc.to_dict() for doc in query.stream()]

    def cancel(self, booking_id: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a booking and free its slot capacity in a Firestore transaction."""
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
                transaction.set(counter_ref, {"count": max(0, current - 1)})
                transaction.delete(active_ref)
                record["status"] = "cancelled"
                transaction.update(booking_ref, {"status": "cancelled"})
            return record

        return do_cancel(transaction)
