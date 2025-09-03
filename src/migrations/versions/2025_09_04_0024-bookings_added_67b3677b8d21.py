"""bookings added

Revision ID: 67b3677b8d21
Revises: 50397482b1e4
Create Date: 2025-09-04 00:24:41.885045

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67b3677b8d21"
down_revision: Union[str, Sequence[str], None] = "50397482b1e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bookings")
