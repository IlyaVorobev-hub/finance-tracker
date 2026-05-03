# fix_db.py
import sys
sys.path.insert(0, '.')

from src.api.database import engine, Base
from src.api.models import User, Transaction  # Регистрируем модели в Base

print("🔧 Проверяем и создаём недостающие таблицы...")
Base.metadata.create_all(bind=engine)
print("✅ Готово!")