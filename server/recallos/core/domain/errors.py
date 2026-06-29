"""Domain-level errors. These describe violations of platform rules, independent
of any transport (HTTP) or storage concern — adapters translate them at the edge.
"""

from __future__ import annotations


class RecallOSDomainError(Exception):
    """Base class for every domain-level error."""


class OntologyValidationError(RecallOSDomainError):
    """An ontology is malformed: a dangling prerequisite, a cycle, a duplicate
    concept, or a missing required field."""


class OntologyNotFoundError(RecallOSDomainError):
    """No ontology exists for the requested domain (and version, if given)."""


class UnknownConceptError(RecallOSDomainError):
    """A concept is not part of an ontology's closed vocabulary."""


class ScoringError(RecallOSDomainError):
    """The answer scorer could not produce a valid assessment (LLM unavailable,
    malformed response, or empty answer). Callers never fabricate a score."""
