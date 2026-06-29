"""PostgreSQL-backed EvidenceLedger.

Sync SQLAlchemy + psycopg2, wrapped in ``run_in_executor`` to satisfy the async port.
Deliberately simple and reliable; the psycopg2 path is already verified against the
managed database. If real load later justifies it, an async driver can replace this
behind the same port without touching the core.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy import create_engine, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker

from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation

from .models import Base, MasteredConceptRow, ObservationRow

_T = TypeVar("_T")


class PostgresEvidenceLedger:
    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._session = sessionmaker(bind=self._engine, expire_on_commit=False)

    def create_all(self) -> None:
        """Create tables directly (used by tests / first boot). Production schema is
        owned by Alembic; ``create_all`` is idempotent and matches the migration."""
        Base.metadata.create_all(self._engine)

    async def _run(self, fn: Callable[[], _T]) -> _T:
        return await asyncio.get_running_loop().run_in_executor(None, fn)

    async def append(self, scope: UserScope, observation: Observation) -> None:
        def _write() -> None:
            with self._session.begin() as session:
                session.add(
                    ObservationRow(
                        user_id=scope.user_id,
                        domain=scope.domain,
                        concept=observation.concept,
                        score=observation.score,
                        at=observation.at,
                    )
                )

        await self._run(_write)

    async def observations(self, scope: UserScope) -> list[Observation]:
        def _read() -> list[Observation]:
            with self._session() as session:
                rows = (
                    session.execute(
                        select(ObservationRow)
                        .where(
                            ObservationRow.user_id == scope.user_id,
                            ObservationRow.domain == scope.domain,
                        )
                        .order_by(ObservationRow.id)
                    )
                    .scalars()
                    .all()
                )
                return [
                    Observation(concept=r.concept, score=r.score, at=r.at) for r in rows
                ]

        return await self._run(_read)

    async def mark_mastered(self, scope: UserScope, concept: str) -> None:
        def _write() -> None:
            with self._session.begin() as session:
                session.execute(
                    pg_insert(MasteredConceptRow)
                    .values(user_id=scope.user_id, domain=scope.domain, concept=concept)
                    .on_conflict_do_nothing()
                )

        await self._run(_write)

    async def mastered(self, scope: UserScope) -> set[str]:
        def _read() -> set[str]:
            with self._session() as session:
                rows = (
                    session.execute(
                        select(MasteredConceptRow.concept).where(
                            MasteredConceptRow.user_id == scope.user_id,
                            MasteredConceptRow.domain == scope.domain,
                        )
                    )
                    .scalars()
                    .all()
                )
                return set(rows)

        return await self._run(_read)

    async def delete_scope(self, scope: UserScope) -> None:
        """Purge all ledger data for a scope (account/data deletion; also resets test
        state). Per-scope — never global."""

        def _delete() -> None:
            with self._session.begin() as session:
                session.execute(
                    delete(ObservationRow).where(
                        ObservationRow.user_id == scope.user_id,
                        ObservationRow.domain == scope.domain,
                    )
                )
                session.execute(
                    delete(MasteredConceptRow).where(
                        MasteredConceptRow.user_id == scope.user_id,
                        MasteredConceptRow.domain == scope.domain,
                    )
                )

        await self._run(_delete)
