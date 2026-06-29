"""Port: the user registry. Maps an OIDC subject to a persisted profile (email, and a
reserved tenant). Auth itself lives at the edge; this only persists who has logged in.
"""

from __future__ import annotations

from typing import Protocol

from recallos.core.domain.identity import UserAccount


class UserRepository(Protocol):
    async def upsert(self, subject: str, email: str | None) -> UserAccount:
        """Create or update the profile for an authenticated subject; return it."""
        ...

    async def get(self, subject: str) -> UserAccount | None:
        """Return the profile for a subject, or None if unknown."""
        ...

    async def get_by_email(self, email: str) -> UserAccount | None:
        """Return the profile for an email, or None if unknown (e.g. resolving the
        configured demo account to its subject)."""
        ...
