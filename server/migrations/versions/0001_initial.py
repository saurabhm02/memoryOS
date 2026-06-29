"""initial schema: observations + mastered_concepts

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "observations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("concept", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "score >= 0 AND score <= 5", name="ck_observations_score_range"
        ),
    )
    op.create_index("ix_observations_scope", "observations", ["user_id", "domain"])

    op.create_table(
        "mastered_concepts",
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("concept", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "user_id", "domain", "concept", name="pk_mastered_concepts"
        ),
    )


def downgrade() -> None:
    op.drop_table("mastered_concepts")
    op.drop_index("ix_observations_scope", table_name="observations")
    op.drop_table("observations")
