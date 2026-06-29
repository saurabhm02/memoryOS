"""Reset the sandboxed demo account in place.

Clears the demo user's Evidence Ledger (Postgres) and its Cognee dataset, while
preserving the Supabase account itself. Only ever touches the one configured demo
account (resolved from ``DEMO_EMAIL`` to its subject via the users table).

Manual today:

    cd backend && .venv/bin/python -m recallos.scripts.reset_demo

The work itself is the provider-agnostic ``ResetLearnerMemory`` use-case — the seam a
future scheduled job (cron / authenticated admin endpoint) can call. This script only
resolves the demo scope and invokes it with the production adapters.
"""

from __future__ import annotations

import asyncio

from recallos.config import settings
from recallos.core.application.usecases import ResetLearnerMemory
from recallos.core.domain.identity import UserScope


async def reset_demo() -> None:
    email = settings.demo_email
    if not email:
        raise SystemExit("DEMO_EMAIL is not set — cannot identify the demo account.")

    from recallos.adapters.persistence import (
        PostgresEvidenceLedger,
        PostgresUserRepository,
    )

    users = PostgresUserRepository(settings.database_url)
    account = await users.get_by_email(email)
    if account is None:
        raise SystemExit(
            f"No profile found for demo account {email!r}; it must sign in once first."
        )

    scope = UserScope(user_id=account.subject, domain=settings.demo_domain)

    from recallos.adapters.memory.cognee_engine import CogneeMemoryEngine
    from recallos.adapters.memory.cognee_runtime import init_cognee

    await init_cognee()
    ledger = PostgresEvidenceLedger(settings.database_url)

    await ResetLearnerMemory(CogneeMemoryEngine(), ledger).execute(scope)
    print(
        f"✓ Demo reset complete: {email} "
        f"(subject={account.subject}, domain={scope.domain}). Account preserved."
    )


if __name__ == "__main__":
    asyncio.run(reset_demo())
