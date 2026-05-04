from logging.config import fileConfig
from sqlalchemy import create_engine  # ✅ ДОБАВЛЕНО!
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv

# Загружаем переменные из .env (для локальной разработки)
load_dotenv()

# Импорт ваших моделей (для авто-генерации миграций)
# Замените на ваш реальный путь к моделям:
from src.api.models import Base  # ✅ Проверьте путь!

# Alembic Config object
config = context.config

# Настройка логгера
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для авто-генерации
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    
    # Получаем DATABASE_URL из окружения (Render) или .env (локально)
    url = os.getenv("DATABASE_URL")
    
    if not url:
        # Резервный вариант: читаем из alembic.ini
        url = config.get_main_option("sqlalchemy.url")
    
    if not url:
        raise ValueError("❌ DATABASE_URL not found!")
    
    # Отладочный вывод (удалите после успешного деплоя)
    print("=" * 60)
    print(f"🔗 ALEMBIC: DATABASE_URL exists: {url is not None}")
    if url:
        print(f"🔗 ALEMBIC: Starts with: {url[:30]}...")
        print(f"🔗 ALEMBIC: Is PostgreSQL: {url.startswith('postgres')}")
    print("=" * 60)
    
    # Для PostgreSQL добавляем SSL-параметры
    if url and (url.startswith("postgres://") or url.startswith("postgresql://")):
        if "?sslmode=" not in url:
            url += "?sslmode=require"
    
    # Создаём движок
    connectable = create_engine(url, pool_pre_ping=True)
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# Главный входной пункт
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()