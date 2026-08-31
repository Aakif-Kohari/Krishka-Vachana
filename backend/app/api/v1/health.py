"""Health endpoints for uptime checks and deploy-platform probes.

Two endpoints, matching the standard liveness/readiness split used by most
container platforms (Cloud Run, Kubernetes, etc.):

- GET /health         Liveness: is the process up and able to respond?
                       Always 200 while the app is running. Use this for
                       "is it alive, restart if not" checks.
- GET /health/ready    Readiness: is the app able to serve real traffic?
                       Checks Firebase connectivity when Firebase is
                       configured. Returns 503 if a configured dependency
                       is unreachable. Use this for "route traffic here"
                       checks / load balancer health checks.
"""
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, status

from app.core.config import Settings, get_settings
from app.core.firebase import FirebaseState, get_firebase_state

router = APIRouter(tags=["health"])

_started_at = time.monotonic()


@router.get("/health")
def liveness(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "service": "kisansetu-backend",
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.monotonic() - _started_at, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
def readiness(
    response: Response,
    settings: Settings = Depends(get_settings),
    firebase: FirebaseState = Depends(get_firebase_state),
) -> dict:
    checks = {}

    if firebase.is_configured:
        try:
            client = firebase.firestore_client()
            # Cheap connectivity probe - list a single doc, don't care if
            # the collection is empty, only that the call doesn't raise.
            next(iter(client.collection("_health_check").limit(1).stream()), None)
            checks["firestore"] = "ok"
        except Exception as exc:  # pragma: no cover - depends on live infra
            checks["firestore"] = f"error: {exc}"
    else:
        checks["firestore"] = "not_configured (using in-memory fallback)"

    healthy = all(v == "ok" or v.startswith("not_configured") for v in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {"status": "ok" if healthy else "degraded", "checks": checks}
