"""Firebase Admin SDK wiring.

Ownership note: the Firebase *project* itself - Authentication config,
Firestore schema, security rules, FCM setup - belongs to the Database &
Infrastructure engineer (see repo's team_work_division.md). This module
only does what the Backend role needs from Firebase per that doc:
"verify Firebase ID tokens" and "consume Firestore via the Admin SDK".

If no service-account credentials are available yet (e.g. Infra hasn't
shared one, or you're developing before that piece lands), this module
degrades gracefully instead of crashing the whole API - see
`is_configured` and app/repositories/memory.py / app/api/deps.py.
"""
import logging
import os
import threading
from functools import lru_cache
from typing import Any, Dict, Optional

from app.core.config import get_settings

logger = logging.getLogger("app.firebase")


class FirebaseState:
    """Lazily-initialized wrapper around the firebase_admin App."""

    def __init__(self) -> None:
        self._app = None
        self._init_attempted = False
        self._init_lock = threading.Lock()

    @property
    def is_configured(self) -> bool:
        """Check if Firebase Admin SDK is successfully initialized."""
        self._ensure_init()
        return self._app is not None

    def _ensure_init(self) -> None:
        """Initialize the Firebase Admin SDK if not already initialized."""
        with self._init_lock:
            if self._init_attempted:
                return
            self._init_attempted = True

            settings = get_settings()
            try:
                import firebase_admin
                from firebase_admin import credentials

                if firebase_admin._apps:  # already initialized elsewhere (e.g. tests)
                    self._app = firebase_admin.get_app()
                    return

                firestore_host = settings.firestore_emulator_host_effective
                auth_host = settings.firebase_auth_emulator_host_effective
                if firestore_host:
                    os.environ.setdefault("FIRESTORE_EMULATOR_HOST", firestore_host)
                if auth_host:
                    os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", auth_host)

                if os.path.exists(settings.firebase_service_account_path):
                    cred = credentials.Certificate(settings.firebase_service_account_path)
                    self._app = firebase_admin.initialize_app(
                        cred, {"projectId": settings.firebase_project_id}
                    )
                elif firestore_host or auth_host:
                    # Emulator mode doesn't need real credentials.
                    self._app = firebase_admin.initialize_app(
                        options={"projectId": settings.firebase_project_id}
                    )
                else:
                    logger.warning(
                        "No Firebase service account found at %s and no emulator host set. "
                        "Backend will run with dev auth/storage fallbacks until "
                        "Infra provides credentials.",
                        settings.firebase_service_account_path,
                    )
            except Exception:  # pragma: no cover - defensive, logged for visibility
                logger.exception("Failed to initialize Firebase Admin SDK")
                self._app = None

    def verify_id_token(self, token: str) -> Dict[str, Any]:
        """Verify a Firebase ID token and return its decoded claims.

        Raises firebase_admin.auth.InvalidIdTokenError (or similar) on
        failure - callers should catch and translate to a 401.
        """
        from firebase_admin import auth as firebase_auth

        self._ensure_init()
        return firebase_auth.verify_id_token(token)

    def firestore_client(self):
        """Return a Firestore client, or None if Firebase isn't configured."""
        self._ensure_init()
        if self._app is None:
            return None
        from firebase_admin import firestore

        return firestore.client()


@lru_cache
def get_firebase_state() -> FirebaseState:
    """Return the cached Firebase state singleton."""
    return FirebaseState()
