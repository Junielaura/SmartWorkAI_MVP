"""Add scheduling scope and make report link optional.

Revision ID: 8c1f2d3a4b5e
Revises: 627b7063aaff
Create Date: 2026-11-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c1f2d3a4b5e"
down_revision: Union[str, Sequence[str], None] = "627b7063aaff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "report_schedules",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "report_schedules",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "report_schedules",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.alter_column(
        "report_schedules",
        "report_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_foreign_key(
        "fk_report_schedules_organization_id",
        "report_schedules",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_report_schedules_owner_id",
        "report_schedules",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_report_schedules_owner_id", "report_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_report_schedules_organization_id",
        "report_schedules",
        type_="foreignkey",
    )
    op.alter_column(
        "report_schedules",
        "report_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("report_schedules", "created_at")
    op.drop_column("report_schedules", "owner_id")
    op.drop_column("report_schedules", "organization_id")
