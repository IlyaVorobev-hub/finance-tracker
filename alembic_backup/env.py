import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# 🔧 Добавляем корень проекта в sys.path для корректных импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.database import Base, engine
from src.api import models  # 🔥 Критично: Alembic должен "увидеть" модели

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 🔧 FIX: Читаем DATABASE_URL из окружения
def get_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback для локальной разработки
        try:
            from src.core.config import settings
            url = getattr(settings, "DATABASE_URL", None)
        except ImportError:
            pass
    
    if not url:
        raise ValueError("DATABASE_URL не найдена в переменных окружения")
    
    # Render использует postgres://, SQLAlchemy требует postgresql://
    return url.replace("postgres://", "postgresql://", 1)

config.set_main_option("sqlalchemy.url", get_url())
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,  # Для серверлесс-окружений (Render)
        pool_pre_ping=True,  # Проверка соединения перед запросом
        pool_recycle=300  # Пересоздавать соединение каждые 5 минут
    )
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()