"""Composition root: builds the FastAPI app and wires the adapters.

``create_app`` accepts optional adapters/verifier for testing (inject doubles → fully
offline). In production it leaves them ``None`` and the lifespan builds the real
adapters, the OIDC verifier, and calls ``init_cognee()`` once. Heavy imports are lazy
(inside the lifespan) so the default offline test suite stays light.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from recallos.adapters.auth import JwtPrincipalVerifier
from recallos.api.errors import register_exception_handlers
from recallos.api.ratelimit import limiter
from recallos.api.routers import v1
from recallos.api.schemas import HealthResponse
from recallos.config import settings
from recallos.core.application.ports import (
    AnswerScorer,
    EvidenceLedger,
    MemoryEngine,
    OntologyRepository,
    UserRepository,
)


def create_app(
    *,
    memory: MemoryEngine | None = None,
    ledger: EvidenceLedger | None = None,
    ontologies: OntologyRepository | None = None,
    user_repo: UserRepository | None = None,
    principal_verifier: JwtPrincipalVerifier | None = None,
    scorer: AnswerScorer | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from recallos.adapters.ontology import FileOntologyRepository
        from recallos.apps.interview_prep import ONTOLOGY_DIR

        app.state.ontologies = ontologies or FileOntologyRepository(ONTOLOGY_DIR)

        if memory is None:
            from recallos.adapters.memory.cognee_engine import CogneeMemoryEngine
            from recallos.adapters.memory.cognee_runtime import init_cognee

            await init_cognee()
            app.state.memory = CogneeMemoryEngine()
        else:
            app.state.memory = memory

        if ledger is None:
            from recallos.adapters.persistence import PostgresEvidenceLedger

            app.state.ledger = PostgresEvidenceLedger(settings.database_url)
        else:
            app.state.ledger = ledger

        if user_repo is not None:
            app.state.user_repo = user_repo
        elif settings.database_url:
            from recallos.adapters.persistence import PostgresUserRepository

            app.state.user_repo = PostgresUserRepository(settings.database_url)
        else:
            app.state.user_repo = None

        if scorer is not None:
            app.state.scorer = scorer
        else:
            from recallos.adapters.scoring import GeminiAnswerScorer

            app.state.scorer = GeminiAnswerScorer()

        if principal_verifier is not None:
            app.state.principal_verifier = principal_verifier
        elif settings.oidc_configured():
            app.state.principal_verifier = JwtPrincipalVerifier(
                issuer=settings.oidc_issuer,
                audience=settings.oidc_audience,
                jwks_url=settings.oidc_jwks_url,
                leeway=settings.jwt_leeway_seconds,
            )
        else:
            app.state.principal_verifier = None

        yield

    app = FastAPI(
        title="RecallOS API",
        version="1.0.0",
        description=(
            "RecallOS — a competency-graph memory platform built on Cognee. "
            "v1 powers Backend-Engineer interview prep: remember observations, recall "
            "the root-cause concept, improve (memify), and forget mastered concepts. "
            "All /api/v1 routes require a verified OIDC bearer token."
        ),
        lifespan=lifespan,
    )

    # Rate limiting (IP-keyed; per-key default + tighter limits on expensive verbs).
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    app.include_router(v1.router)
    return app


# Production entrypoint: `uvicorn recallos.api.app:app`. Importing this module does not
# import Cognee/Postgres (the lifespan builds them on startup).
app = create_app()
