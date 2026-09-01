"""Application settings, loaded from environment variables / .env.

Owned by: Backend.
Does NOT define Firestore schema or security rules - those belong to the
Database & Infrastructure engineer. This module only reads the values the
backend needs to talk to services that already exist.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    # CORS
    cors_origins: str = "http://localhost:3000"

    # SMS gateway
    sms_gateway_api_key: str = ""
    sms_gateway_base_url: str = ""

    # API
    api_v1_prefix: str = "/api/v1"

    # Deployment / docs
    app_version: str = "0.1.0"
    enable_docs: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def firestore_emulator_host_effective(self) -> str:
        return self.firestore_emulator_host or self.firebase_emulator_host

    @property
    def firebase_auth_emulator_host_effective(self) -> str:
        return self.firebase_auth_emulator_host or self.firebase_emulator_host


@lru_cache
def get_settings() -> Settings:
    return Settings()
