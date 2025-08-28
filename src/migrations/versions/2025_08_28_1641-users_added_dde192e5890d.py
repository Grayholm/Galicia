"""users added

Revision ID: dde192e5890d
Revises: 63f7593d263b
Create Date: 2025-08-28 16:41:03.470531

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dde192e5890d"
down_revision: Union[str, Sequence[str], None] = "63f7593d263b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=False),
        sa.Column("birth_day", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("phone_number", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
    )


def downgrade() -> None:
    op.drop_table("users")
