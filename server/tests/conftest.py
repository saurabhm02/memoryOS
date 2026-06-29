"""Shared test setup.

Disable IP rate limiting globally so functional tests are deterministic. The dedicated
rate-limit test re-enables it for its own assertions and turns it back off.
"""

from recallos.api.ratelimit import limiter

limiter.enabled = False
