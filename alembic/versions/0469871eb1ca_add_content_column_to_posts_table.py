"""add content column to posts table

Revision ID: 0469871eb1ca
Revises: 69a46f03bf2d
Create Date: 2024-02-15 15:07:16.125494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0469871eb1ca'
down_revision: Union[str, None] = '69a46f03bf2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
