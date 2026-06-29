"""Maps domain errors to HTTP responses at the edge, so use-cases stay transport-free.

Starlette resolves handlers along the exception's MRO, so the specific handlers below
take precedence over the `RecallOSDomainError` base handler.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from recallos.adapters.auth import AuthError
from recallos.core.domain.errors import (
    OntologyNotFoundError,
    OntologyValidationError,
    RecallOSDomainError,
    ScoringError,
    UnknownConceptError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthError)
    async def _auth_error(_: Request, exc: AuthError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "authentication required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(UnknownConceptError)
    async def _unknown_concept(_: Request, exc: UnknownConceptError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ScoringError)
    async def _scoring_error(_: Request, exc: ScoringError) -> JSONResponse:
        # The grader (LLM) failed; the client may retry. Never a fabricated score.
        return JSONResponse(
            status_code=502, content={"detail": "could not grade the answer"}
        )

    @app.exception_handler(OntologyNotFoundError)
    async def _ontology_not_found(_: Request, exc: OntologyNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(OntologyValidationError)
    async def _ontology_invalid(_: Request, exc: OntologyValidationError) -> JSONResponse:
        # A malformed authored ontology is a server-side configuration fault.
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(RecallOSDomainError)
    async def _domain_error(_: Request, exc: RecallOSDomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
