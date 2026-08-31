"""Shared FastAPI dependencies: authentication and repository wiring.

Auth: verifies the Firebase ID token the frontend attaches as
`Authorization: Bearer <token>` (Firebase Authentication itself is owned by
Database & Infrastructure; we only verify tokens it issues, per
team_work_division.md).

Repositories: returns the Firestore-backed implementation when Firebase is
configured, otherwise an in-memory fallback so backend endpoints can be
built and tested before the Firestore project is fully wired up. This
switch is transparent to route handlers and services.
"""
from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.firebase import FirebaseState, get_firebase_state
from app.repositories.base import CropRepository, FarmerRepository
from app.repositories.memory import get_memory_crop_repository, get_memory_farmer_repository


def get_current_farmer_uid(
    authorization: str = Header(default=""),
    settings: Settings = Depends(get_settings),
    firebase: FirebaseState = Depends(get_firebase_state),
) -> str:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError("Empty bearer token")

    if not firebase.is_configured:
        if settings.allow_dev_auth_fallback and settings.is_development:
            # Dev-only shortcut: treat the raw token as the uid so backend
            # endpoints are usable before Infra ships Firebase credentials.
            # Never enabled outside development (see Settings.is_development).
            return token
        raise UnauthorizedError("Auth service unavailable")

    try:
        claims = firebase.verify_id_token(token)
    except Exception as exc:  # firebase_admin raises various auth errors
        raise UnauthorizedError("Invalid or expired token") from exc

    uid = claims.get("uid")
    if not uid:
        raise UnauthorizedError("Token missing uid claim")
    return uid


def get_farmer_repository(
    firebase: FirebaseState = Depends(get_firebase_state),
) -> FarmerRepository:
    client = firebase.firestore_client()
    if client is None:
        return get_memory_farmer_repository()
    from app.repositories.firestore import FirestoreFarmerRepository

    return FirestoreFarmerRepository(client)


def get_crop_repository(
    firebase: FirebaseState = Depends(get_firebase_state),
) -> CropRepository:
    client = firebase.firestore_client()
    if client is None:
        return get_memory_crop_repository()
    from app.repositories.firestore import FirestoreCropRepository

    return FirestoreCropRepository(client)
