"""Dependency injection wiring for the API.

Adapters are singletons created once at startup and stored on ``app.state`` (see
``create_app``). These providers read them from the request and assemble the
application use-cases per request. Swapping how ``UserScope`` is derived (e.g. real
auth later) is a change here only — the routes and use-cases are unaffected.
"""

from __future__ import annotations

from fastapi import Depends, Header, Query, Request

from recallos.adapters.auth import AuthError
from recallos.core.application.ports import (
    AnswerScorer,
    EvidenceLedger,
    MemoryEngine,
    OntologyRepository,
    UserRepository,
)
from recallos.core.application.usecases import (
    BuildCompetencyGraph,
    DiagnoseSession,
    ForgetConcept,
    ImproveMemory,
    ProvisionScope,
    RememberObservation,
    ScoreAnswer,
)
from recallos.core.domain.identity import Principal, UserScope


def get_principal(
    request: Request,
    authorization: str | None = Header(default=None),
) -> Principal:
    """Verify the bearer token and return the authenticated principal. Identity comes
    only from the verified token — never from a client-supplied header or body."""
    verifier = request.app.state.principal_verifier
    if verifier is None:
        raise AuthError("authentication is not configured")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthError("missing bearer token")
    return verifier.verify(authorization.split(" ", 1)[1].strip())


def get_scope(
    principal: Principal = Depends(get_principal),
    domain: str = Query(default="backend_sde"),
) -> UserScope:
    """The learner + domain an operation concerns, derived from the verified principal."""
    return UserScope(user_id=principal.subject, domain=domain)


def get_ontologies(request: Request) -> OntologyRepository:
    return request.app.state.ontologies


def get_memory(request: Request) -> MemoryEngine:
    return request.app.state.memory


def get_ledger(request: Request) -> EvidenceLedger:
    return request.app.state.ledger


def get_user_repo(request: Request) -> UserRepository:
    return request.app.state.user_repo


def get_scorer(request: Request) -> AnswerScorer:
    return request.app.state.scorer


def get_provision_uc(
    memory: MemoryEngine = Depends(get_memory),
    ontologies: OntologyRepository = Depends(get_ontologies),
) -> ProvisionScope:
    return ProvisionScope(memory, ontologies)


def get_remember_uc(
    ledger: EvidenceLedger = Depends(get_ledger),
    memory: MemoryEngine = Depends(get_memory),
    ontologies: OntologyRepository = Depends(get_ontologies),
) -> RememberObservation:
    return RememberObservation(ledger, memory, ontologies)


def get_score_answer_uc(
    ledger: EvidenceLedger = Depends(get_ledger),
    memory: MemoryEngine = Depends(get_memory),
    ontologies: OntologyRepository = Depends(get_ontologies),
    scorer: AnswerScorer = Depends(get_scorer),
) -> ScoreAnswer:
    return ScoreAnswer(
        scorer, RememberObservation(ledger, memory, ontologies), ontologies
    )


def get_diagnose_uc(
    ledger: EvidenceLedger = Depends(get_ledger),
    memory: MemoryEngine = Depends(get_memory),
    ontologies: OntologyRepository = Depends(get_ontologies),
) -> DiagnoseSession:
    return DiagnoseSession(ledger, memory, ontologies)


def get_graph_uc(
    ledger: EvidenceLedger = Depends(get_ledger),
    ontologies: OntologyRepository = Depends(get_ontologies),
) -> BuildCompetencyGraph:
    return BuildCompetencyGraph(ledger, ontologies)


def get_improve_uc(memory: MemoryEngine = Depends(get_memory)) -> ImproveMemory:
    return ImproveMemory(memory)


def get_forget_uc(
    ledger: EvidenceLedger = Depends(get_ledger),
    ontologies: OntologyRepository = Depends(get_ontologies),
) -> ForgetConcept:
    return ForgetConcept(ledger, ontologies)
