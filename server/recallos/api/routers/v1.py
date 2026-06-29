"""RecallOS API v1 — the four memory verbs, provisioning, and the current-user profile.

Each route is a thin shell: resolve the authenticated scope, call one use-case, serialize
the result. Every route requires a verified bearer token (via ``get_scope`` /
``get_principal``). Expensive, LLM-backed verbs carry a tighter rate limit.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from recallos.api import deps
from recallos.api.ratelimit import limiter
from recallos.api.schemas import (
    AnswerAssessmentResponse,
    AnswerRequest,
    DiagnosisResponse,
    ForgetRequest,
    ForgetResponse,
    GraphEdgeSchema,
    GraphNodeSchema,
    GraphResponse,
    ImproveResponse,
    MeResponse,
    ObservationRequest,
    ObservationResponse,
    ProvisionResponse,
    RootCauseSchema,
)
from recallos.config import settings
from recallos.core.application.ports import UserRepository
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

router = APIRouter(prefix="/api/v1", tags=["competency"])

_EXPENSIVE = settings.rate_limit_expensive


@router.get("/me", response_model=MeResponse, summary="Current user profile")
async def me(
    principal: Principal = Depends(deps.get_principal),
    users: UserRepository = Depends(deps.get_user_repo),
) -> MeResponse:
    """Confirm the session and upsert the learner's profile (called after login)."""
    account = await users.upsert(principal.subject, principal.email)
    return MeResponse(
        subject=account.subject, email=account.email, tenant_id=account.tenant_id
    )


@router.post(
    "/provision", response_model=ProvisionResponse, summary="Provision a learner"
)
@limiter.limit(_EXPENSIVE)
async def provision(
    request: Request,
    scope: UserScope = Depends(deps.get_scope),
    use_case: ProvisionScope = Depends(deps.get_provision_uc),
) -> ProvisionResponse:
    """Prepare the learner's memory space and seed the authored ontology into it."""
    await use_case.execute(scope)
    return ProvisionResponse()


@router.post(
    "/observations",
    response_model=ObservationResponse,
    summary="Remember an observation",
)
@limiter.limit(_EXPENSIVE)
async def add_observation(
    request: Request,
    body: ObservationRequest,
    scope: UserScope = Depends(deps.get_scope),
    use_case: RememberObservation = Depends(deps.get_remember_uc),
) -> ObservationResponse:
    """REMEMBER: record a scored observation (durable ledger + memory graph)."""
    result = await use_case.execute(scope, body.concept, body.score)
    return ObservationResponse(
        concept=result.observation.concept,
        score=result.observation.score,
        memory_written=result.memory_written,
    )


@router.post(
    "/answers",
    response_model=AnswerAssessmentResponse,
    summary="Submit an answer for LLM grading",
)
@limiter.limit(_EXPENSIVE)
async def submit_answer(
    request: Request,
    body: AnswerRequest,
    scope: UserScope = Depends(deps.get_scope),
    use_case: ScoreAnswer = Depends(deps.get_score_answer_uc),
) -> AnswerAssessmentResponse:
    """SCORE: grade the learner's answer (0–5 + feedback), then remember the score."""
    result = await use_case.execute(scope, body.concept, body.question, body.answer)
    assessment = result.assessment
    return AnswerAssessmentResponse(
        concept=body.concept,
        score=assessment.score,
        rationale=assessment.rationale,
        demonstrated=list(assessment.demonstrated),
        missed=list(assessment.missed),
        memory_written=result.memory_written,
    )


@router.get(
    "/diagnosis", response_model=DiagnosisResponse, summary="Recall the root cause"
)
@limiter.limit(_EXPENSIVE)
async def get_diagnosis(
    request: Request,
    scope: UserScope = Depends(deps.get_scope),
    use_case: DiagnoseSession = Depends(deps.get_diagnose_uc),
) -> DiagnosisResponse:
    """RECALL: the weak set and the deterministic upstream root cause, with narration."""
    diagnosis = await use_case.execute(scope)
    root_cause = (
        RootCauseSchema(
            concept=diagnosis.root_cause.concept,
            resolves=list(diagnosis.root_cause.resolves),
        )
        if diagnosis.root_cause is not None
        else None
    )
    return DiagnosisResponse(
        weak=sorted(diagnosis.weak),
        root_cause=root_cause,
        narration=diagnosis.narration,
    )


@router.get("/graph", response_model=GraphResponse, summary="The competency graph")
async def get_graph(
    scope: UserScope = Depends(deps.get_scope),
    use_case: BuildCompetencyGraph = Depends(deps.get_graph_uc),
) -> GraphResponse:
    """The hero view: every concept with its mastery state, the prerequisite edges, and
    the diagnosed root cause. Deterministic and fast (ontology + ledger; no Cognee)."""
    view = await use_case.execute(scope)
    return GraphResponse(
        nodes=[
            GraphNodeSchema(
                concept=node.concept,
                state=node.state,
                score=round(node.score, 2) if node.score is not None else None,
            )
            for node in view.nodes
        ],
        edges=[
            GraphEdgeSchema(source=edge.source, target=edge.target) for edge in view.edges
        ],
        root_cause=(
            RootCauseSchema(
                concept=view.root_cause.concept,
                resolves=list(view.root_cause.resolves),
            )
            if view.root_cause is not None
            else None
        ),
    )


@router.post("/improve", response_model=ImproveResponse, summary="Improve (memify)")
@limiter.limit(_EXPENSIVE)
async def improve(
    request: Request,
    scope: UserScope = Depends(deps.get_scope),
    use_case: ImproveMemory = Depends(deps.get_improve_uc),
) -> ImproveResponse:
    """IMPROVE: derive emergent patterns over the accumulated memory graph."""
    delta = await use_case.execute(scope)
    return ImproveResponse(
        nodes_before=delta.nodes_before,
        nodes_after=delta.nodes_after,
        edges_before=delta.edges_before,
        edges_after=delta.edges_after,
        derived_patterns=list(delta.derived_patterns),
    )


@router.post(
    "/forget", response_model=ForgetResponse, summary="Forget a mastered concept"
)
async def forget(
    body: ForgetRequest,
    scope: UserScope = Depends(deps.get_scope),
    use_case: ForgetConcept = Depends(deps.get_forget_uc),
) -> ForgetResponse:
    """FORGET: stop drilling a mastered concept (excluded from planning, history kept)."""
    await use_case.execute(scope, body.concept)
    return ForgetResponse(forgotten=body.concept)
