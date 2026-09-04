"""In-memory repository implementations.

Used automatically when Firebase/Firestore isn't configured yet (see
app/api/deps.py), and directly in tests. Not for production use - data is
lost on process restart and there is no cross-process consistency.
"""
import threading
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.repositories.base import (
    CentreRepository,
    CropRepository,
    FarmerRepository,
    OtpVerificationResult,
    PaymentRepository,
    QueueRepository,
    SlotBookingRepository,
)


class InMemoryFarmerRepository(FarmerRepository):
    """In-memory implementation of FarmerRepository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory farmer repository with thread-safe locking."""
        self._data: Dict[str, Dict[str, Any]] = {}
        self._aadhaar_reservations: Dict[str, str] = {}
        self._lock = threading.Lock()

    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by ID."""
        with self._lock:
            record = self._data.get(farmer_id)
            return dict(record) if record else None

    def is_cluster_delegate_authorized(
        self, delegate_id: str, farmer_ids: List[str]
    ) -> bool:
        """Check delegate grants stored on every requested farmer record."""
        with self._lock:
            if not farmer_ids:
                return False
            for farmer_id in farmer_ids:
                grants = self._data.get(farmer_id, {}).get(
                    "authorized_cluster_delegate_ids"
                )
                if not isinstance(grants, list) or delegate_id not in grants:
                    return False
            return True

    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by Aadhaar hash."""
        with self._lock:
            return next(
                (
                    dict(record)
                    for record in self._data.values()
                    if record.get("aadhaar_hash") == aadhaar_hash
                ),
                None,
            )

    def reserve_aadhaar(self, aadhaar_hash: str, farmer_id: str) -> bool:
        """Atomically reserve an Aadhaar hash for a farmer ID."""
        with self._lock:
            owner = self._aadhaar_reservations.get(aadhaar_hash)
            if owner is not None:
                return owner == farmer_id
            if any(record.get("aadhaar_hash") == aadhaar_hash for record in self._data.values()):
                return False
            self._aadhaar_reservations[aadhaar_hash] = farmer_id
            return True

    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new farmer record."""
        with self._lock:
            record = {"farmer_id": farmer_id, **data}
            self._data[farmer_id] = record
            return dict(record)

    def create_with_aadhaar_reservation(
        self, farmer_id: str, aadhaar_hash: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a farmer record with Aadhaar reservation, or return None if conflict."""
        with self._lock:
            if farmer_id in self._data:
                return None

            owner = self._aadhaar_reservations.get(aadhaar_hash)
            if owner is not None and owner != farmer_id:
                return None
            if any(record.get("aadhaar_hash") == aadhaar_hash for record in self._data.values()):
                return None

            record = {"farmer_id": farmer_id, **data, "aadhaar_hash": aadhaar_hash}
            self._aadhaar_reservations[aadhaar_hash] = farmer_id
            self._data[farmer_id] = record
            return dict(record)

    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a farmer record with the provided data."""
        with self._lock:
            record = self._data.setdefault(farmer_id, {"farmer_id": farmer_id})
            record.update(data)
            return dict(record)

    def issue_phone_otp_challenge(
        self,
        farmer_id: str,
        issued_at: datetime,
        cooldown_seconds: int,
        data: Dict[str, Any],
    ) -> bool:
        """Atomically store an OTP challenge unless the farmer is in cooldown."""
        with self._lock:
            record = self._data.get(farmer_id)
            if record is None:
                return False
            last_issued_at = record.get("phone_otp_issued_at")
            if last_issued_at and issued_at < last_issued_at + timedelta(seconds=cooldown_seconds):
                return False
            record.update({**data, "phone_otp_issued_at": issued_at})
            return True

    def consume_phone_otp_attempt(
        self,
        farmer_id: str,
        submitted_hash: str,
        attempted_at: datetime,
        max_attempts: int,
    ) -> OtpVerificationResult:
        """Atomically verify or consume one phone OTP attempt."""
        with self._lock:
            record = self._data.get(farmer_id)
            if record is None:
                return OtpVerificationResult.NOT_FOUND

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
                record.update(clear_challenge)
                return OtpVerificationResult.EXPIRED

            attempts = record.get("phone_otp_attempts", 0)
            if attempts >= max_attempts:
                record.update(clear_challenge)
                return OtpVerificationResult.LOCKED

            if submitted_hash != stored_hash:
                record["phone_otp_attempts"] = attempts + 1
                return OtpVerificationResult.INCORRECT

            record["phone_verified"] = True
            record.update(clear_challenge)
            return OtpVerificationResult.VERIFIED


class InMemoryCropRepository(CropRepository):
    """In-memory implementation of CropRepository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory crop repository with thread-safe locking."""
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crop record."""
        with self._lock:
            record = {"crop_id": crop_id, **data}
            self._data[crop_id] = record
            return dict(record)

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's crops."""
        with self._lock:
            records = sorted(
                (r for r in self._data.values() if r.get("farmer_id") == farmer_id),
                key=lambda r: r["crop_id"],
            )
            if cursor is not None:
                records = [r for r in records if r["crop_id"] > cursor]
            return [dict(r) for r in records[:limit]] if limit is not None else [dict(r) for r in records]


# Sample procurement centres for local dev/tests, seeded until the
# Database & Infrastructure engineer wires up a real "centres" Firestore
# collection (see app/repositories/firestore.py). Not production data.
_DEFAULT_SEED_CENTRES: List[Dict[str, Any]] = [
    {
        "centre_id": "ctr-solapur-apmc",
        "name": "Solapur APMC Procurement Centre",
        "village": "Solapur",
        "district": "Solapur",
        "state": "Maharashtra",
        "capacity_per_slot": 40,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    },
    {
        "centre_id": "ctr-pandharpur",
        "name": "Pandharpur Procurement Centre",
        "village": "Pandharpur",
        "district": "Solapur",
        "state": "Maharashtra",
        "capacity_per_slot": 25,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    },
    {
        "centre_id": "ctr-nagpur-apmc",
        "name": "Nagpur APMC Procurement Centre",
        "village": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "capacity_per_slot": 60,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    },
]


class InMemoryCentreRepository(CentreRepository):
    """In-memory implementation of CentreRepository for development and testing."""

    def __init__(self, seed: Optional[List[Dict[str, Any]]] = None) -> None:
        """Initialize in-memory centre repository with optional seed data or default sample centres."""
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, Any]] = {
            record["centre_id"]: dict(record) for record in (seed if seed is not None else _DEFAULT_SEED_CENTRES)
        }

    def list(self, district: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List procurement centres, optionally filtered by district or state."""
        with self._lock:
            records = [dict(r) for r in self._data.values()]
        if district:
            records = [r for r in records if r.get("district", "").lower() == district.lower()]
        if state:
            records = [r for r in records if r.get("state", "").lower() == state.lower()]
        return records

    def get(self, centre_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a procurement centre by ID."""
        with self._lock:
            record = self._data.get(centre_id)
            return dict(record) if record else None


def _slot_key(centre_id: str, slot_date: date, slot_window: str) -> Tuple[str, str, str]:
    """Generate a composite tuple key for a slot from centre, date, and window."""
    slot_date_iso = slot_date.isoformat() if hasattr(slot_date, "isoformat") else str(slot_date)
    return (centre_id, slot_date_iso, slot_window)


class InMemorySlotBookingRepository(SlotBookingRepository):
    """In-memory implementation of SlotBookingRepository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory slot booking repository with thread-safe locking."""
        self._data: Dict[str, Dict[str, Any]] = {}
        self._active_counts: Dict[Tuple[str, str, str], int] = {}
        self._active_booking_ids: Dict[Tuple[str, str, str, str], str] = {}
        self._lock = threading.Lock()

    def get(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a booking by ID."""
        with self._lock:
            record = self._data.get(booking_id)
            return dict(record) if record else None

    def count_active_bookings(self, centre_id: str, slot_date: date, slot_window: str) -> int:
        """Count active bookings for a specific slot."""
        with self._lock:
            return self._active_counts.get(_slot_key(centre_id, slot_date, slot_window), 0)

    def create_if_capacity_available(
        self, booking_id: str, capacity: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a booking if capacity is available."""
        with self._lock:
            if booking_id in self._data:
                return None
            slot_key = _slot_key(data["centre_id"], data["slot_date"], data["slot_window"])
            active_key = (data["farmer_id"], *slot_key)
            if active_key in self._active_booking_ids:
                return None
            current = self._active_counts.get(slot_key, 0)
            if current >= capacity:
                return None
            record = {"booking_id": booking_id, **data}
            self._data[booking_id] = record
            self._active_counts[slot_key] = current + 1
            self._active_booking_ids[active_key] = booking_id
            return dict(record)

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's bookings."""
        with self._lock:
            records = sorted(
                (r for r in self._data.values() if r.get("farmer_id") == farmer_id),
                key=lambda r: r["booking_id"],
            )
            if cursor is not None:
                records = [r for r in records if r["booking_id"] > cursor]
            return [dict(r) for r in records[:limit]] if limit is not None else [dict(r) for r in records]

    def cancel(self, booking_id: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a farmer-owned booking and release its reserved slot capacity.
        
        Parameters:
            booking_id (str): Identifier of the booking to cancel.
            farmer_id (str): Identifier of the farmer who owns the booking.
        
        Returns:
            Optional[Dict[str, Any]]: The updated booking with status ``"cancelled"``, or ``None`` if the booking does not exist or belongs to another farmer.
        """
        with self._lock:
            record = self._data.get(booking_id)
            if record is None or record.get("farmer_id") != farmer_id:
                return None
            if record.get("status") != "cancelled":
                slot_key = _slot_key(
                    record["centre_id"], record["slot_date"], record["slot_window"]
                )
                active_key = (record["farmer_id"], *slot_key)
                self._active_counts[slot_key] = max(
                    0, self._active_counts.get(slot_key, 0) - 1
                )
                self._active_booking_ids.pop(active_key, None)
                record["status"] = "cancelled"
            return dict(record)

    def create_batch_atomic(
        self, booking_ids: List[str], capacity: int, data_list: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Atomically creates multiple bookings when all inputs are valid, capacity is available, and no booking or farmer reservation conflicts exist.
        
        Parameters:
        	booking_ids (List[str]): Unique identifiers for the bookings to create.
        	capacity (int): Maximum number of active bookings allowed for the slot.
        	data_list (List[Dict[str, Any]]): Booking data corresponding positionally to `booking_ids`.
        
        Returns:
        	Optional[List[Dict[str, Any]]]: The created booking records, or `None` if the inputs are mismatched or empty, capacity is insufficient, or a booking conflict exists.
        """
        with self._lock:
            if len(booking_ids) != len(data_list) or not booking_ids:
                return None
                
            first_data = data_list[0]
            first_slot = (
                first_data["centre_id"],
                first_data["slot_date"],
                first_data["slot_window"],
            )
            if any(
                (data["centre_id"], data["slot_date"], data["slot_window"])
                != first_slot
                for data in data_list[1:]
            ):
                return None
            slot_key = _slot_key(first_data["centre_id"], first_data["slot_date"], first_data["slot_window"])
            current = self._active_counts.get(slot_key, 0)
            
            if current + len(booking_ids) > capacity:
                return None

            created_records = []
            for bid, data in zip(booking_ids, data_list):
                if bid in self._data:
                    return None
                active_key = (data["farmer_id"], *slot_key)
                if active_key in self._active_booking_ids:
                    return None
            
            # All checks passed, commit
            for bid, data in zip(booking_ids, data_list):
                record = {"booking_id": bid, **data}
                self._data[bid] = record
                active_key = (data["farmer_id"], *slot_key)
                self._active_booking_ids[active_key] = bid
                created_records.append(dict(record))
                
            self._active_counts[slot_key] = current + len(booking_ids)
            return created_records


class InMemoryQueueRepository(QueueRepository):
    """In-memory implementation of QueueRepository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory queue repository with thread-safe locking."""
        self._data: Dict[str, Dict[str, Any]] = {}
        self._active_farmer_ids: Dict[str, str] = {}  # farmer_id -> queue_id
        self._active_booking_ids: Dict[str, str] = {}  # booking_id -> queue_id
        self._daily_sequence: Dict[Tuple[str, str], int] = {}  # (centre_id, date_iso) -> count
        self._lock = threading.Lock()

    def get(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a queue entry by ID."""
        with self._lock:
            record = self._data.get(queue_id)
            return dict(record) if record else None

    def get_active_for_farmer(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer's current waiting queue entry, if any."""
        with self._lock:
            queue_id = self._active_farmer_ids.get(farmer_id)
            record = self._data.get(queue_id) if queue_id else None
            return dict(record) if record else None

    def get_active_for_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the waiting queue entry checked in against a booking, if any."""
        with self._lock:
            queue_id = self._active_booking_ids.get(booking_id)
            record = self._data.get(queue_id) if queue_id else None
            return dict(record) if record else None

    def create_check_in(
        self, queue_id: str, centre_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically check a farmer in, assigning the next daily per-centre sequence number."""
        with self._lock:
            farmer_id = data["farmer_id"]
            booking_id = data["booking_id"]
            if farmer_id in self._active_farmer_ids or booking_id in self._active_booking_ids:
                return None

            queue_date = data["queue_date"]
            date_key = (centre_id, queue_date)
            sequence_number = self._daily_sequence.get(date_key, 0) + 1
            self._daily_sequence[date_key] = sequence_number

            record = {
                "queue_id": queue_id,
                "sequence_number": sequence_number,
                **data,
                "queue_date": queue_date,
            }
            self._data[queue_id] = record
            self._active_farmer_ids[farmer_id] = queue_id
            self._active_booking_ids[booking_id] = queue_id
            return dict(record)

    def count_waiting_ahead(
        self, centre_id: str, queue_date: str, sequence_number: int
    ) -> int:
        """Count same-day waiting entries at a centre with a lower sequence number."""
        with self._lock:
            return sum(
                1
                for r in self._data.values()
                if r.get("centre_id") == centre_id
                and r.get("queue_date") == queue_date
                and r.get("status") == "waiting"
                and r.get("sequence_number") < sequence_number
            )

    def count_waiting(self, centre_id: str, queue_date: str) -> int:
        """Count all waiting entries at a centre on a queue date."""
        with self._lock:
            return sum(
                1
                for r in self._data.values()
                if r.get("centre_id") == centre_id
                and r.get("queue_date") == queue_date
                and r.get("status") == "waiting"
            )

    def resolve(
        self, queue_id: str, farmer_id: str, new_status: str, resolved_at: datetime
    ) -> Optional[Dict[str, Any]]:
        """Move a farmer's own waiting entry to a terminal status and free its reservations."""
        with self._lock:
            record = self._data.get(queue_id)
            if record is None or record.get("farmer_id") != farmer_id:
                return None
            if record.get("status") != "waiting":
                return None
            record["status"] = new_status
            record["resolved_at"] = resolved_at
            self._active_farmer_ids.pop(farmer_id, None)
            self._active_booking_ids.pop(record["booking_id"], None)
            return dict(record)


class InMemoryPaymentRepository(PaymentRepository):
    """In-memory implementation of PaymentRepository for development and testing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory payment repository with thread-safe locking."""
        self._data: Dict[str, Dict[str, Any]] = {}
        self._payment_ids_by_booking: Dict[str, str] = {}
        self._lock = threading.Lock()

    def get(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a payment record by ID."""
        with self._lock:
            return dict(self._data.get(payment_id)) if payment_id in self._data else None

    def get_by_booking_id(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a payment record by its associated booking ID."""
        with self._lock:
            payment_id = self._payment_ids_by_booking.get(booking_id)
            record = self._data.get(payment_id) if payment_id else None
            return dict(record) if record else None

    def create(self, payment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and store a payment record.
        
        Parameters:
        	payment_id (str): Unique identifier for the payment.
        	data (Dict[str, Any]): Payment fields to include in the record.
        
        Returns:
        	Dict[str, Any]: A copy of the stored payment record.
        """
        return self.create_or_get_by_booking_id(payment_id, data)

    def create_or_get_by_booking_id(
        self, payment_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or retrieve a booking's payment while holding one lock."""
        with self._lock:
            existing_id = self._payment_ids_by_booking.get(data["booking_id"])
            if existing_id is not None:
                return dict(self._data[existing_id])

            record = {"payment_id": payment_id, **data}
            self._data[payment_id] = record
            self._payment_ids_by_booking[data["booking_id"]] = payment_id
            return dict(record)

    def list_by_farmer(
        self, farmer_id: str, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List a stable, optionally bounded page of a farmer's payments."""
        # TODO: Consider ordering by `processed_at` instead of `payment_id` for a more
        # intuitive chronological display in the UI.
        with self._lock:
            records = sorted(
                (r for r in self._data.values() if r.get("farmer_id") == farmer_id),
                key=lambda r: r["payment_id"],
            )
            if cursor is not None:
                records = [r for r in records if r["payment_id"] > cursor]
            return [dict(r) for r in records[:limit]] if limit is not None else [dict(r) for r in records]


# Process-wide singletons so the fallback store behaves consistently across
# requests within a single dev server run.
_farmer_repo = InMemoryFarmerRepository()
_crop_repo = InMemoryCropRepository()
_centre_repo = InMemoryCentreRepository()
_slot_booking_repo = InMemorySlotBookingRepository()
_queue_repo = InMemoryQueueRepository()
_payment_repo = InMemoryPaymentRepository()


def get_memory_farmer_repository() -> InMemoryFarmerRepository:
    """Return the process-wide singleton in-memory farmer repository."""
    return _farmer_repo


def get_memory_crop_repository() -> InMemoryCropRepository:
    """Return the process-wide singleton in-memory crop repository."""
    return _crop_repo


def get_memory_centre_repository() -> InMemoryCentreRepository:
    """Return the process-wide singleton in-memory centre repository."""
    return _centre_repo


def get_memory_slot_booking_repository() -> InMemorySlotBookingRepository:
    """Return the process-wide singleton in-memory slot booking repository."""
    return _slot_booking_repo


def get_memory_queue_repository() -> InMemoryQueueRepository:
    """Return the process-wide singleton in-memory queue repository."""
    return _queue_repo


def get_memory_payment_repository() -> InMemoryPaymentRepository:
    """Return the process-wide singleton in-memory payment repository."""
    return _payment_repo
