"""add payment method column

Revision ID: 0a3a836a9694
Revises: ba8e1d072d9e
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a3a836a9694'
down_revision = 'ba8e1d072d9e'  # ← Ссылается на четвёртую миграцию
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('payment_method', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('transactions', 'payment_method')