# Sprint 2: JWT Auth + Streamlit Dashboard

## Часть 1: JWT-авторизация
- Регистрация/логин (email + password)
- JWT токены (python-jose)
- Хеш паролей (bcrypt)
- Защита роутов `/api/v1/transactions`
- Зависимость `get_current_user`

## Часть 2: Streamlit Dashboard
- Логин в UI
- Баланс + графики (Plotly)
- Таблица транзакций
- Форма добавления
- Фильтр по дате

## Файлы для генерации
- src/api/auth.py
- src/api/models.py (добавить User)
- src/api/schemas.py (добавить UserCreate, Token)
- src/api/routers/auth.py
- src/ui/app.py
- src/ui/requirements.txt