"""Identity value objects shared across the platform."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserScope:
    """Identifies whose memory, and which learning domain, an operation concerns.
    `domain` selects the ontology. A `tenant_id` is added when multi-tenancy lands;
    today user + domain suffice."""

    user_id: str
    domain: str


@dataclass(frozen=True, slots=True)
class Principal:
    """An authenticated identity derived from a verified token — never client-supplied.
    Provider-agnostic: ``subject`` is the OIDC ``sub`` claim."""

    subject: str
    email: str | None = None


@dataclass(frozen=True, slots=True)
class UserAccount:
    """A persisted user profile keyed by OIDC subject. ``tenant_id`` reserves an org/
    cohort layer for the future; today isolation is per-user."""

    subject: str
    email: str | None
    tenant_id: str | None
