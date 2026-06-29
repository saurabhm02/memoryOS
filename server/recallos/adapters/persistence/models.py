"""SQLAlchemy ORM models for the evidence ledger (PostgreSQL).

The ledger is the durable source of truth for mastery. It stores scored observations
and explicit mastery overrides — never concept relationships (those belong to the
authored ontology and the Cognee memory graph).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    """A registered user, keyed by OIDC subject. ``tenant_id`` reserves a future org
    layer; auth verification happens at the edge, not here."""

    __tablename__ = "users"

    subject: Mapped[str] = mapped_column(Text, primary_key=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ObservationRow(Base):
    """One scored observation. Append-only; ordered by ``id`` (insertion order)."""

    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    concept: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 5", name="ck_observations_score_range"),
        Index("ix_observations_scope", "user_id", "domain"),
    )


class MasteredConceptRow(Base):
    """A concept the learner has explicitly mastered (the Forget verb): excluded from
    planning regardless of evidence. Idempotent per (user, domain, concept)."""

    __tablename__ = "mastered_concepts"

    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    concept: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "domain", "concept", name="pk_mastered_concepts"),
    )
