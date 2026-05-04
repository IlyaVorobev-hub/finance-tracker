"""add type column to transactions

Revision ID: ba8e1d072d9e
Revises: a2feb255b408
Create Date: 2024-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba8e1d072d9e'
down_revision = 'a2feb255b408'  # ← Ссылается на третью миграцию
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('type', sa.String(length=20), nullable=False, server_default='expense'))


def downgrade() -> None:
    op.drop_column('transactions', 'type')