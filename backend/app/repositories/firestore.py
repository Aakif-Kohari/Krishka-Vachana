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
from typing import Any, Dict, List, Optional

from app.repositories.base import CropRepository, FarmerRepository

FARMERS_COLLECTION = "farmers"
CROPS_COLLECTION = "crops"


class FirestoreFarmerRepository(FarmerRepository):
    def __init__(self, client) -> None:
        self._client = client

    def get(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        doc = self._client.collection(FARMERS_COLLECTION).document(farmer_id).get()
        return doc.to_dict() if doc.exists else None

    def get_by_aadhaar_hash(self, aadhaar_hash: str) -> Optional[Dict[str, Any]]:
        query = (
            self._client.collection(FARMERS_COLLECTION)
            .where("aadhaar_hash", "==", aadhaar_hash)
            .limit(1)
        )
        doc = next(iter(query.stream()), None)
        return doc.to_dict() if doc is not None else None

    def create(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        ref.set({"farmer_id": farmer_id, **data})
        return {"farmer_id": farmer_id, **data}

    def update(self, farmer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        ref = self._client.collection(FARMERS_COLLECTION).document(farmer_id)
        ref.update(data)
        doc = ref.get()
        return doc.to_dict()


class FirestoreCropRepository(CropRepository):
    def __init__(self, client) -> None:
        self._client = client

    def create(self, crop_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        ref = self._client.collection(CROPS_COLLECTION).document(crop_id)
        ref.set({"crop_id": crop_id, **data})
        return {"crop_id": crop_id, **data}

    def list_by_farmer(self, farmer_id: str) -> List[Dict[str, Any]]:
        query = self._client.collection(CROPS_COLLECTION).where("farmer_id", "==", farmer_id)
        return [doc.to_dict() for doc in query.stream()]
