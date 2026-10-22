"""driver standings

Revision ID: 3c1f0a9d2b77
Revises: eb633afff086
Create Date: 2026-10-21 20:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3c1f0a9d2b77"
down_revision: str | Sequence[str] | None = "eb633afff086"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "driver_standings",
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("season", "round", "driver_id"),
    )


def downgrade() -> None:
    op.drop_table("driver_standings")
