"""Repository interfaces.

Backend depends on these abstractions, not on Firestore directly. This
keeps the API layer testable without a live database and gives the
Database & Infrastructure engineer a clear contract to implement/adjust
once the Firestore schema and security rules are finalized, instead of us
touching each other's code directly.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class FarmerRepository(ABC):
    @abstractmethod
    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...


class CropRepository(ABC):
    @abstractmethod
    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]: ...
