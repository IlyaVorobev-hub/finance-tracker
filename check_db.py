# check_db.py
import sqlite3

conn = sqlite3.connect('finance.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
conn.close()

print('✅ Таблицы в БД:', tables)

if 'users' in tables and 'transactions' in tables:
    print('🎉 ВСЕ ТАБЛИЦЫ НА МЕСТЕ!')
else:
    print('❌ Не хватает таблиц:', [t for t in ['users', 'transactions'] if t not in tables])
    