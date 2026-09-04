"""Repository interfaces.

Backend depends on these abstractions, not on Firestore directly. This
keeps the API layer testable without a live database and gives the
Database & Infrastructure engineer a clear contract to implement/adjust
once the Firestore schema and security rules are finalized, instead of us
touching each other's code directly.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class OtpVerificationResult(str, Enum):
    """Outcome of atomically consuming one phone OTP verification attempt."""

    NOT_FOUND = "not_found"
    MISSING = "missing"
    EXPIRED = "expired"
    LOCKED = "locked"
    INCORRECT = "incorrect"
    VERIFIED = "verified"


class FarmerRepository(ABC):
    """Abstract base class for farmer data persistence."""

    @abstractmethod
    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by ID."""
        ...

    @abstractmethod
    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer record by Aadhaar hash."""
        ...

    @abstractmethod
    def reserve_aadhaar(self, aadhaar_hash: str, farmer_id: str) -> bool:
        """Atomically reserve an Aadhaar hash for a farmer ID."""
        ...

    @abstractmethod
    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new farmer record."""
        ...

    @abstractmethod
    def create_with_aadhaar_reservation(
        self, farmer_id: str, aadhaar_hash: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a farmer record with Aadhaar reservation."""
        ...

    @abstractmethod
    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a farmer record with the provided data."""
        ...

    @abstractmethod
    def issue_phone_otp_challenge(
        self,
        farmer_id: str,
        issued_at: datetime,
        cooldown_seconds: int,
        data: Dict[str, Any],
    ) -> bool:
        """Atomically store an OTP challenge unless the farmer is in cooldown."""
        ...

    @abstractmethod
    def consume_phone_otp_attempt(
        self,
        farmer_id: str,
        submitted_hash: str,
        attempted_at: datetime,
        max_attempts: int,
    ) -> OtpVerificationResult:
        """Atomically verify or consume one phone OTP attempt."""
        ...


class CropRepository(ABC):
    """Abstract base class for crop data persistence."""

    @abstractmethod
    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crop record."""
        ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        """List all crops registered by a farmer."""
        ...


class CentreRepository(ABC):
    """Procurement-centre reference data. Read-only from the backend's
    point of view for Phase 2 - centre records are expected to be seeded
    by the Database & Infrastructure engineer once Firestore is wired up.
    """

    @abstractmethod
    def list(
        self, district: Optional[str] = None, state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List procurement centres, optionally filtered by district or state."""
        ...

    @abstractmethod
    def get(self, centre_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a procurement centre by ID."""
        ...


class SlotBookingRepository(ABC):
    """Abstract base class for slot booking data persistence."""

    @abstractmethod
    def get(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a booking by ID."""
        ...

    @abstractmethod
    def count_active_bookings(self, centre_id: str, slot_date: date, slot_window: str) -> int:
        """Count active bookings for a specific slot."""
        ...

    @abstractmethod
    def create_if_capacity_available(
        self, booking_id: str, capacity: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a booking iff active bookings for
        (centre_id, slot_date, slot_window) in `data` are below `capacity`.
        The same operation also enforces at most one active booking per
        (farmer_id, centre_id, slot_date, slot_window).
        Returns None (no partial state left behind) if the slot is full or
        the booking ID or active-booking key already exists - mirrors
        FarmerRepository.create_with_aadhaar_reservation's reserve-then-create
        pattern so two farmers racing for the last seat can't both win.
        """
        ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        """List all bookings for a farmer."""
        ...

    @abstractmethod
    def cancel(self, booking_id: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a booking owned by the specified farmer and release its capacity.
        
        Parameters:
            booking_id (str): The booking to cancel.
            farmer_id (str): The farmer who owns the booking.
        
        Returns:
            Optional[Dict[str, Any]]: The updated booking record, or None if the booking
            does not exist or is not owned by the farmer.
        """
        ...

    @abstractmethod
    def create_batch_atomic(
        self, booking_ids: List[str], capacity: int, data_list: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Atomically create a batch of bookings when capacity is available for the entire batch.
        
        Parameters:
            booking_ids (List[str]): Identifiers for the bookings to create.
            capacity (int): Maximum number of bookings allowed.
            data_list (List[Dict[str, Any]]): Data for each booking.
        
        Returns:
            Optional[List[Dict[str, Any]]]: All created bookings, or None when capacity is insufficient for the batch.
        """
        ...

class QueueRepository(ABC):
    """Abstract base class for the Dynamic Queue system's live check-in data.

    A Smart Slot booking (SlotBookingRepository) reserves capacity ahead of
    time; a queue entry here represents the farmer's actual, live
    arrival-order position at the centre on the day of their slot. There is
    no separate "centre staff" role in this system yet (see
    team_work_division.md), so every status transition is farmer-initiated
    and ownership-checked - see app/services/queue_service.py.
    """

    @abstractmethod
    def get(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a queue entry by ID."""
        ...

    @abstractmethod
    def get_active_for_farmer(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a farmer's current waiting queue entry, if any."""
        ...

    @abstractmethod
    def get_active_for_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the waiting queue entry checked in against a booking, if any."""
        ...

    @abstractmethod
    def create_check_in(
        self, queue_id: str, centre_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically check a farmer in, assigning the next daily per-centre
        sequence number (used to build the printable token number).
        `data` must include the procurement-centre-local `queue_date`.
        Returns None (no partial state left behind) if farmer_id or
        booking_id in `data` already has an active (waiting) entry - mirrors
        SlotBookingRepository.create_if_capacity_available's reserve-then-
        create pattern.
        """
        ...

    @abstractmethod
    def count_waiting_ahead(
        self, centre_id: str, queue_date: str, sequence_number: int
    ) -> int:
        """Count same-day waiting entries at a centre with a lower sequence number."""
        ...

    @abstractmethod
    def count_waiting(self, centre_id: str, queue_date: str) -> int:
        """Count all waiting entries at a centre on a queue date."""
        ...

    @abstractmethod
    def resolve(
        self, queue_id: str, farmer_id: str, new_status: str, resolved_at: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a farmer's waiting queue entry with a terminal status.
        
        Parameters:
            queue_id (str): Identifier of the queue entry.
            farmer_id (str): Identifier of the farmer who owns the entry.
            new_status (str): Terminal status to assign, either ``"served"`` or ``"left"``.
            resolved_at (datetime): Time at which the entry is resolved.
        
        Returns:
            Optional[Dict[str, Any]]: The updated queue entry, or ``None`` if the entry
            does not exist, belongs to another farmer, or has already been resolved.
        """
        ...

class PaymentRepository(ABC):
    """Abstract base class for payment data persistence."""

    @abstractmethod
    def get(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a payment record by ID."""
        ...

    @abstractmethod
    def get_by_booking_id(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a payment record associated with a booking.
        
        Parameters:
        	booking_id (str): The booking identifier.
        
        Returns:
        	Optional[Dict[str, Any]]: The payment record, or None if no payment is associated with the booking.
        """
        ...

    @abstractmethod
    def create(self, payment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment record with the specified identifier and data.
        
        Parameters:
            payment_id (str): Unique identifier for the payment.
            data (Dict[str, Any]): Payment record fields.
        
        Returns:
            Dict[str, Any]: The created payment record.
        """
        ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        """
        List all payments associated with a farmer.
        
        Parameters:
            farmer_id (str): Identifier of the farmer.
        
        Returns:
            List[Dict[str, Any]]: Payment records for the farmer.
        """
        ...
