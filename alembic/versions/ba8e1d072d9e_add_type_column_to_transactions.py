"""add type column to transactions

Revision ID: ba8e1d072d9e
Revises: a2feb255b408
Create Date: 2026-05-02 21:10:42.948965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba8e1d072d9e'
down_revision: Union[str, Sequence[str], None] = 'a2feb255b408'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавляем колонку с дефолтным значением 'expense'
    op.add_column('transactions', sa.Column('type', sa.String(length=20), nullable=False, server_default='expense'))
    
    # 2. Гарантируем, что все существующие записи получат 'expense'
    op.execute("UPDATE transactions SET type = 'expense' WHERE type IS NULL")


def downgrade() -> None:
    op.drop_column('transactions', 'type')
