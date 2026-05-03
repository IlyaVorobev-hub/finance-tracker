# test_db.py
from sqlalchemy import create_engine, text

# ВСТАВЬТЕ СЮДА ВАШУ СТРОКУ ИЗ ШАГА 2
TEST_URL = "postgresql://postgres.ftjtsmchgcgmemuylafb:hpVeBd044VKKhlcY@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=verify-ca"

print("🔗 Пытаюсь подключиться...")

try:
    # Создаем движок
    engine = create_engine(TEST_URL, pool_pre_ping=True)
    
    # Пробуем сделать запрос
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("✅ УСПЕХ! Подключено к:", result.scalar())
        
except Exception as e:
    print("❌ ОШИБКА:", str(e)[:100]) # Показываем только начало ошибки