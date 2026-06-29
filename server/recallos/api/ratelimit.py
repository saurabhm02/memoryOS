"""Shared rate limiter. IP-keyed; a per-key default plus tighter limits on the
expensive LLM-backed verbs. In-memory store now (single instance); swap to Redis when
it's introduced in a later milestone.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from recallos.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)
