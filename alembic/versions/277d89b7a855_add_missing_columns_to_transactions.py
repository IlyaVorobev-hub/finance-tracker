"""Add missing columns to transactions (BATCH-MODE SAFE)

Revision ID: 277d89b7a855
Revises: 0a3a836a9694
Create Date: 2026-05-05 15:42:35.641130

"""
from typing import Sequence, Union
from sqlalchemy import inspect

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '277d89b7a855'
down_revision: Union[str, Sequence[str], None] = '0a3a836a9694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — BATCH-MODE SAFE for SQLite + PostgreSQL"""
    
    connection = op.get_bind()
    inspector = inspect(connection)
    is_sqlite = connection.dialect.name == 'sqlite'
    
    # Получаем список существующих колонок
    existing_columns = [col['name'] for col in inspector.get_columns('transactions')]
    
    # === ДОБАВЛЯЕМ НОВЫЕ КОЛОНКИ ===
    
    if 'category' not in existing_columns:
        op.add_column(
            'transactions', 
            sa.Column('category', sa.String(length=100), nullable=False, server_default='Другое')
        )
    
    if 'date' not in existing_columns:
        op.add_column(
            'transactions', 
            sa.Column('date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE'))
        )
    
    # === ИЗМЕНЯЕМ ТИПЫ КОЛОНОК (только PostgreSQL) ===
    if not is_sqlite:
        if 'description' in existing_columns:
            op.alter_column(
                'transactions', 
                'description',
                existing_type=sa.VARCHAR(length=255),
                type_=sa.String(length=500),
                existing_nullable=True
            )
        
        if 'created_at' in existing_columns:
            op.alter_column(
                'transactions', 
                'created_at',
                existing_type=sa.DATETIME(),
                nullable=True
            )
        
        if 'payment_method' in existing_columns:
            op.alter_column(
                'transactions', 
                'payment_method',
                existing_type=sa.VARCHAR(length=50),
                type_=sa.String(length=20),
                nullable=False,
                server_default='card'
            )
    
    # === ИНДЕКСЫ ===
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('transactions')]
    
    if 'ix_transactions_id' not in existing_indexes:
        op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    
    # === ВНЕШНИЙ КЛЮЧ: используем batch mode для SQLite ===
    existing_fks = inspector.get_foreign_keys('transactions')
    has_user_fk = any(fk['referred_table'] == 'users' for fk in existing_fks)
    
    if not has_user_fk:
        if is_sqlite:
            # 🔧 SQLite: используем batch mode для добавления FK
            with op.batch_alter_table('transactions', schema=None) as batch_op:
                batch_op.create_foreign_key(
                    'fk_transactions_user_id',
                    'users', 
                    ['user_id'], 
                    ['id'],
                    ondelete='CASCADE'
                )
        else:
            # PostgreSQL: обычное добавление FK
            op.create_foreign_key(
                'fk_transactions_user_id',
                'transactions', 'users', 
                ['user_id'], ['id'],
                ondelete='CASCADE'
            )
    
    # === ТАБЛИЦА users ===
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    user_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    
    if 'ix_users_email' not in user_indexes:
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    if 'ix_users_id' not in user_indexes:
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    if 'updated_at' in user_columns:
        op.drop_column('users', 'updated_at')


def downgrade() -> None:
    """Downgrade schema — безопасный откат"""
    
    connection = op.get_bind()
    inspector = inspect(connection)
    is_sqlite = connection.dialect.name == 'sqlite'
    
    # === ТАБЛИЦА users ===
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'updated_at' not in user_columns:
        op.add_column('users', sa.Column('updated_at', sa.DATETIME(), nullable=True))
    
    user_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    if 'ix_users_email' in user_indexes:
        op.drop_index(op.f('ix_users_email'), table_name='users')
    if 'ix_users_id' in user_indexes:
        op.drop_index(op.f('ix_users_id'), table_name='users')
    
    # === ТАБЛИЦА transactions ===
    
    # Удаляем внешний ключ
    existing_fks = inspector.get_foreign_keys('transactions')
    if any(fk['name'] == 'fk_transactions_user_id' for fk in existing_fks):
        if is_sqlite:
            with op.batch_alter_table('transactions', schema=None) as batch_op:
                batch_op.drop_constraint('fk_transactions_user_id', type_='foreignkey')
        else:
            op.drop_constraint('fk_transactions_user_id', 'transactions', type_='foreignkey')
    
    # Удаляем индексы
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('transactions')]
    if 'ix_transactions_id' in existing_indexes:
        op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    
    # Откат изменений типов (только PostgreSQL)
    if not is_sqlite:
        tx_cols = [c['name'] for c in inspector.get_columns('transactions')]
        if 'payment_method' in tx_cols:
            op.alter_column(
                'transactions', 
                'payment_method',
                existing_type=sa.String(length=20),
                type_=sa.VARCHAR(length=50),
                nullable=True
            )
        if 'created_at' in tx_cols:
            op.alter_column(
                'transactions', 
                'created_at',
                existing_type=sa.DATETIME(),
                nullable=False
            )
        if 'description' in tx_cols:
            op.alter_column(
                'transactions', 
                'description',
                existing_type=sa.String(length=500),
                type_=sa.VARCHAR(length=255),
                existing_nullable=True
            )
    
    # Удаляем добавленные колонки
    tx_cols = [c['name'] for c in inspector.get_columns('transactions')]
    if 'date' in tx_cols:
        op.drop_column('transactions', 'date')
    if 'category' in tx_cols:
        op.drop_column('transactions', 'category')