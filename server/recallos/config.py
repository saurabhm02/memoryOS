"""Runtime settings (composition layer — not part of the pure core).

Loaded from environment / server/.env. The core never imports this; only adapters and
the composition root do.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    llm_api_key: str = ""
    embedding_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model: str = "gemini/gemini-2.5-flash"
    embedding_provider: str = "gemini"
    embedding_model: str = "gemini/gemini-embedding-001"
    embedding_dimensions: int = 3072

    # --- Cognee local stores ---
    graph_provider: str = "kuzu"
    cognee_system_dir: str = "./.cognee/system"
    cognee_data_dir: str = "./.cognee/data"
    # We own auth and isolate by dataset-per-user, so Cognee's own access control is off.
    enable_backend_access_control: bool = False

    # --- App database (EvidenceLedger) ---
    database_url: str = ""

    demo_user_id: str = "demo"
    # The sandboxed demo account, resolved to its subject for the reset script.
    demo_email: str = ""
    demo_domain: str = "backend_sde"

    # --- API ---
    # Comma-separated allowed CORS origins for the frontend.
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # --- Authentication (provider-agnostic OIDC; Supabase is the initial provider) ---
    # The backend only verifies standard JWTs against the issuer's JWKS. Swap providers
    # (Keycloak/Authentik/Auth0/Clerk/…) by changing these — no code changes.
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    jwt_leeway_seconds: int = 10

    # Per-key request ceiling applied to every route by the rate limiter.
    rate_limit_default: str = "240/minute"
    # Tighter ceiling for the expensive, LLM-backed verbs.
    rate_limit_expensive: str = "20/minute"

    def oidc_configured(self) -> bool:
        return bool(self.oidc_jwks_url and self.oidc_issuer)

    def resolved_gemini_key(self) -> str:
        return self.gemini_api_key or self.llm_api_key

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
