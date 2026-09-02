"""Repository interfaces.

Backend depends on these abstractions, not on Firestore directly. This
keeps the API layer testable without a live database and gives the
Database & Infrastructure engineer a clear contract to implement/adjust
once the Firestore schema and security rules are finalized, instead of us
touching each other's code directly.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional


class FarmerRepository(ABC):
    @abstractmethod
    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def reserve_aadhaar(self, aadhaar_hash: str, farmer_id: str) -> bool: ...

    @abstractmethod
    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def create_with_aadhaar_reservation(
        self, farmer_id: str, aadhaar_hash: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...


class CropRepository(ABC):
    @abstractmethod
    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]: ...


class CentreRepository(ABC):
    """Procurement-centre reference data. Read-only from the backend's
    point of view for Phase 2 - centre records are expected to be seeded
    by the Database & Infrastructure engineer once Firestore is wired up.
    """

    @abstractmethod
    def list(
        self, district: Optional[str] = None, state: Optional[str] = None
    ) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def get(self, centre_id: str) -> Optional[Dict[str, Any]]: ...


class SlotBookingRepository(ABC):
    @abstractmethod
    def get(self, booking_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def count_active_bookings(self, centre_id: str, slot_date: date, slot_window: str) -> int: ...

    @abstractmethod
    def create_if_capacity_available(
        self, booking_id: str, capacity: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atomically create a booking iff active bookings for
        (centre_id, slot_date, slot_window) in `data` are below `capacity`.
        Returns None (no partial state left behind) if the slot is full or
        `booking_id` already exists - mirrors
        FarmerRepository.create_with_aadhaar_reservation's reserve-then-create
        pattern so two farmers racing for the last seat can't both win.
        """
        ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def cancel(self, booking_id: str, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a booking owned by farmer_id and free its capacity.
        Returns the updated record, or None if not found or not owned by
        farmer_id (callers should treat both as 404, not 403 - see
        app/services/slot_service.py for why).
        """
        ...
