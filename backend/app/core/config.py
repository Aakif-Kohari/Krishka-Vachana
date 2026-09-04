"""Application settings, loaded from environment variables / .env.

Owned by: Backend.
Does NOT define Firestore schema or security rules - those belong to the
Database & Infrastructure engineer. This module only reads the values the
backend needs to talk to services that already exist.
"""
from collections import Counter
from functools import lru_cache
from math import log2
from typing import List, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_MIN_WEBHOOK_SECRET_LENGTH = 32
_MIN_WEBHOOK_SECRET_ENTROPY_BITS = 100
_WEBHOOK_SECRET_PLACEHOLDER_MARKERS = (
    "change-me",
    "changeme",
    "placeholder",
    "replace-with",
    "test-only",
    "your-secret",
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Firebase
    firebase_service_account_path: str = "./secrets/firebase-service-account.json"
    firebase_project_id: str = "krishka-vachana"
    # Convenience: same host:port for both emulators. Prefer the two
    # service-specific overrides below when Auth and Firestore emulators
    # run on different ports (the Firebase Local Emulator Suite defaults
    # do - 9099 vs 8080 - and either can be reconfigured independently).
    firebase_emulator_host: str = ""
    firestore_emulator_host: str = ""
    firebase_auth_emulator_host: str = ""
    allow_dev_auth_fallback: bool = False
    aadhaar_hmac_secret_name: str = ""

    # AI/ML congestion-prediction integration point (Phase 2). AI/ML's real
    # endpoint doesn't exist yet - leave this unset and the backend serves a
    # deterministic occupancy-based heuristic instead (same
    # graceful-degradation shape as the Firebase fallback above). Once
    # AI/ML stands up an endpoint matching app/schemas/congestion.py's
    # contract, set this and no other code changes are needed. See
    # app/services/congestion_service.py.
    congestion_prediction_api_url: str = ""
    congestion_prediction_api_timeout_seconds: float = 3.0

    # CORS
    cors_origins: str = "http://localhost:3000"

    # SMS gateway
    sms_gateway_api_key: str = ""
    sms_gateway_base_url: str = ""
    sms_gateway_timeout_seconds: Optional[float] = Field(default=5.0, gt=0)

    # Phone-number OTP verification (Phase 3, see app/services/otp_service.py).
    # Independent of Firebase Authentication - see app/schemas/otp.py.
    otp_length: int = Field(default=6, ge=4, le=8)
    otp_ttl_seconds: int = Field(default=600, ge=1)
    otp_max_attempts: int = Field(default=5, ge=1)
    otp_request_cooldown_seconds: int = Field(default=60, ge=1)
    otp_hmac_secret: str = Field(min_length=32)

    # API
    api_v1_prefix: str = "/api/v1"

    # Deployment / docs
    app_version: str = "0.1.0"
    enable_docs: bool = True

    # Phase 4: Payment Gateway Integration Point
    payment_gateway_webhook_secret: str = ""

    @model_validator(mode="after")
    def require_secure_production_webhook_secret(self):
        """Require a securely generated webhook secret in production."""
        if self.environment.strip().lower() != "production":
            return self

        secret = self.payment_gateway_webhook_secret
        if not secret or secret != secret.strip():
            raise ValueError("payment gateway webhook secret is required in production")
        if len(secret) < _MIN_WEBHOOK_SECRET_LENGTH:
            raise ValueError(
                "payment gateway webhook secret must be at least "
                f"{_MIN_WEBHOOK_SECRET_LENGTH} characters in production"
            )
        estimated_entropy_bits = -sum(
            count * log2(count / len(secret)) for count in Counter(secret).values()
        )
        if (
            any(marker in secret.lower() for marker in _WEBHOOK_SECRET_PLACEHOLDER_MARKERS)
            or estimated_entropy_bits < _MIN_WEBHOOK_SECRET_ENTROPY_BITS
        ):
            raise ValueError(
                "payment gateway webhook secret must be cryptographically generated "
                "and non-placeholder in production"
            )
        return self

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment.lower() == "development"

    @property
    def firestore_emulator_host_effective(self) -> str:
        """Return the effective Firestore emulator host, falling back to the generic Firebase emulator host."""
        return self.firestore_emulator_host or self.firebase_emulator_host

    @property
    def firebase_auth_emulator_host_effective(self) -> str:
        """Return the effective Firebase Auth emulator host, falling back to the generic Firebase emulator host."""
        return self.firebase_auth_emulator_host or self.firebase_emulator_host


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
