"""In-memory repository implementations.

Used automatically when Firebase/Firestore isn't configured yet (see
app/api/deps.py), and directly in tests. Not for production use - data is
lost on process restart and there is no cross-process consistency.
"""
import threading
from typing import Any, Dict, List, Optional

from app.repositories.base import CropRepository, FarmerRepository


class InMemoryFarmerRepository(FarmerRepository):
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._aadhaar_reservations: Dict[str, str] = {}
        self._lock = threading.Lock()

    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._data.get(farmer_id)
            return dict(record) if record else None

    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]:
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
        with self._lock:
            owner = self._aadhaar_reservations.get(aadhaar_hash)
            if owner is not None:
                return owner == farmer_id
            if any(record.get("aadhaar_hash") == aadhaar_hash for record in self._data.values()):
                return False
            self._aadhaar_reservations[aadhaar_hash] = farmer_id
            return True

    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            record = {"farmer_id": farmer_id, **data}
            self._data[farmer_id] = record
            return dict(record)

    def create_with_aadhaar_reservation(
        self, farmer_id: str, aadhaar_hash: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
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
        with self._lock:
            record = self._data.setdefault(farmer_id, {"farmer_id": farmer_id})
            record.update(data)
            return dict(record)


class InMemoryCropRepository(CropRepository):
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            record = {"crop_id": crop_id, **data}
            self._data[crop_id] = record
            return dict(record)

    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(r) for r in self._data.values() if r.get("farmer_id") == farmer_id]


# Process-wide singletons so the fallback store behaves consistently across
# requests within a single dev server run.
_farmer_repo = InMemoryFarmerRepository()
_crop_repo = InMemoryCropRepository()


def get_memory_farmer_repository() -> InMemoryFarmerRepository:
    return _farmer_repo


def get_memory_crop_repository() -> InMemoryCropRepository:
    return _crop_repo
