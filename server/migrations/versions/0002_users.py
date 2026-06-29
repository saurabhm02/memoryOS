"""users table (auth registry, org-ready)

Revision ID: 0002_users
Revises: 0001_initial
Create Date: 2026-06-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_users"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("subject", sa.Text(), primary_key=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
