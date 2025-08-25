"""initial migration

Revision ID: 6cfed844add7
Revises: 
Create Date: 2025-08-25 19:28:44.562156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cfed844add7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('hotels')
