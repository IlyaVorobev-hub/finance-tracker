# ✅ Новый код для Render + локальной разработки
import os
from dotenv import load_dotenv

# Загружаем переменные из .env (для локальной разработки)
load_dotenv()

# Получаем DATABASE_URL из окружения (Render) или .env (локально)
url = os.getenv("DATABASE_URL")

if not url:
    # Если переменной нет — пробуем прочитать из config (резервный вариант)
    url = config.get_main_option("sqlalchemy.url")

if not url:
    raise ValueError("❌ DATABASE_URL not found in environment or alembic.ini!")

# Для PostgreSQL добавляем SSL-параметры, если их нет
if url.startswith("postgres://") or url.startswith("postgresql://"):
    if "?sslmode=" not in url:
        url += "?sslmode=require"

# Создаём подключение
connectable = create_engine(url, pool_pre_ping=True)

with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()