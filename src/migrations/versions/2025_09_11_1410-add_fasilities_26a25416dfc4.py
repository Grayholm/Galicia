"""add fasilities

Revision ID: 26a25416dfc4
Revises: 67b3677b8d21
Create Date: 2025-09-11 14:10:29.195246

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "26a25416dfc4"
down_revision: Union[str, Sequence[str], None] = "67b3677b8d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fasilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rooms_fasilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rooms_id", sa.Integer(), nullable=False),
        sa.Column("fasilities_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fasilities_id"],
            ["fasilities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rooms_id"],
            ["rooms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("rooms_fasilities")
    op.drop_table("fasilities")

