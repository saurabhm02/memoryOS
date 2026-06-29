"""UserRepository implementations: in-memory (tests/dev) and PostgreSQL (production).

Sync SQLAlchemy + ``run_in_executor`` behind the async port, matching the ledger.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker

from recallos.core.domain.identity import UserAccount

from .models import Base, UserRow

_T = TypeVar("_T")


def _to_account(row: UserRow) -> UserAccount:
    return UserAccount(subject=row.subject, email=row.email, tenant_id=row.tenant_id)


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[str, UserAccount] = {}

    async def upsert(self, subject: str, email: str | None) -> UserAccount:
        existing = self._users.get(subject)
        account = UserAccount(
            subject=subject,
            email=email if email is not None else (existing.email if existing else None),
            tenant_id=existing.tenant_id if existing else None,
        )
        self._users[subject] = account
        return account

    async def get(self, subject: str) -> UserAccount | None:
        return self._users.get(subject)

    async def get_by_email(self, email: str) -> UserAccount | None:
        return next((u for u in self._users.values() if u.email == email), None)


class PostgresUserRepository:
    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._session = sessionmaker(bind=self._engine, expire_on_commit=False)

    def create_all(self) -> None:
        Base.metadata.create_all(self._engine)

    async def _run(self, fn: Callable[[], _T]) -> _T:
        return await asyncio.get_running_loop().run_in_executor(None, fn)

    async def upsert(self, subject: str, email: str | None) -> UserAccount:
        def _write() -> UserAccount:
            with self._session.begin() as session:
                stmt = (
                    pg_insert(UserRow)
                    .values(subject=subject, email=email)
                    .on_conflict_do_update(
                        index_elements=[UserRow.subject],
                        set_={"email": email},
                    )
                    .returning(UserRow)
                )
                row = session.execute(stmt).scalar_one()
                return _to_account(row)

        return await self._run(_write)

    async def get(self, subject: str) -> UserAccount | None:
        def _read() -> UserAccount | None:
            with self._session() as session:
                row = session.execute(
                    select(UserRow).where(UserRow.subject == subject)
                ).scalar_one_or_none()
                return _to_account(row) if row else None

        return await self._run(_read)

    async def get_by_email(self, email: str) -> UserAccount | None:
        def _read() -> UserAccount | None:
            with self._session() as session:
                row = session.execute(
                    select(UserRow).where(UserRow.email == email).limit(1)
                ).scalar_one_or_none()
                return _to_account(row) if row else None

        return await self._run(_read)
