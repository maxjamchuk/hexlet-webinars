"""Create incidents table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "SPACE",
                "TIME",
                "CREATURE",
                "TECHNOLOGY",
                "UNKNOWN",
                name="category",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("danger_level", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "NEW",
                "INVESTIGATING",
                "RESOLVED",
                name="incidentstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("incidents")
