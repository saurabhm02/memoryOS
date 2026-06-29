"""Request/response schemas for the HTTP API.

These are transport DTOs only — they validate input shape and serialize domain results.
Concept-vocabulary validation is domain logic (the use-case checks the ontology and
raises `UnknownConceptError`, mapped to HTTP 422), since the closed vocabulary is
per-ontology and not knowable statically here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class ProvisionResponse(BaseModel):
    provisioned: bool = True


class ObservationRequest(BaseModel):
    concept: str = Field(
        min_length=1, description="A concept from the domain's ontology."
    )
    score: int = Field(
        ge=0, le=5, description="Score 0–5 for the answer on this concept."
    )


class ObservationResponse(BaseModel):
    concept: str
    score: int
    memory_written: bool = Field(
        description="True if the observation was ingested into the memory engine. "
        "It is always persisted to the durable ledger regardless."
    )


class RootCauseSchema(BaseModel):
    concept: str
    resolves: list[str]


class DiagnosisResponse(BaseModel):
    weak: list[str]
    root_cause: RootCauseSchema | None
    narration: str | None


class GraphNodeSchema(BaseModel):
    concept: str
    state: str  # "unvisited" | "weak" | "medium" | "mastered"
    score: float | None


class GraphEdgeSchema(BaseModel):
    source: str  # prerequisite
    target: str  # dependent


class GraphResponse(BaseModel):
    nodes: list[GraphNodeSchema]
    edges: list[GraphEdgeSchema]
    root_cause: RootCauseSchema | None


class ImproveResponse(BaseModel):
    nodes_before: int
    nodes_after: int
    edges_before: int
    edges_after: int
    derived_patterns: list[str]


class ForgetRequest(BaseModel):
    concept: str = Field(min_length=1)


class ForgetResponse(BaseModel):
    forgotten: str


class MeResponse(BaseModel):
    subject: str
    email: str | None
    tenant_id: str | None


class AnswerRequest(BaseModel):
    concept: str = Field(
        min_length=1, description="A concept from the domain's ontology."
    )
    question: str = Field(
        default="", description="The question shown to the learner (grading context)."
    )
    answer: str = Field(min_length=1, description="The learner's free-text answer.")


class AnswerAssessmentResponse(BaseModel):
    concept: str
    score: int = Field(ge=0, le=5)
    rationale: str
    demonstrated: list[str]
    missed: list[str]
    memory_written: bool
