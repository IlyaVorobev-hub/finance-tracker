"""add users table and auth

Revision ID: a2feb255b408
Revises: b5004a0a7947
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2feb255b408'
down_revision = 'b5004a0a7947'  # ← Ссылается на вторую миграцию
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Можно добавить дополнительные поля для users, если нужно
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'updated_at')