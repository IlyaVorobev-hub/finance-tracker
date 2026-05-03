# Sprint 1: База данных + FastAPI CRUD
## Требования
- SQLAlchemy 2.0 declarative models
- Alembic для миграций (SQLite для MVP)
- Pydantic v2 schemas
- FastAPI роутер `/api/v1/transactions`
- CRUD: create, read, list (пагинация 10/стр)
- Валидация: amount > 0, category не пустая, дата ISO
- Изоляция по пользователю (mock user_id=1)
- Типизация, docstrings, HTTPException для 404/400

## Файлы для генерации
- src/api/database.py
- src/api/models.py
- src/api/schemas.py
- src/api/routers/transactions.py
- src/api/main.py
- alembic.ini + alembic/env.py

## Ограничения
- Не используй `query()`, только `select()`
- Не хардкодь подключения
- Выводи код строго по файлам с путями
- После генерации укажи команды: `uvicorn src.api.main:app --reload` и `alembic upgrade head`