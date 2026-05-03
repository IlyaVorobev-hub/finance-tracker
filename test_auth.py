# test_auth.py
import requests

BASE = "http://127.0.0.1:8000"

print("🔹 Тест /health...")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    print(f"   Status: {r.status_code} | {r.json()}")
except Exception as e:
    print(f"   ❌ {e}")

print("\n🔹 Проверка /api/v1/auth/register...")
try:
    r = requests.post(f"{BASE}/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    }, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ {r.json()}")
    else:
        print(f"   ℹ️ {r.text[:200]}")
except Exception as e:
    print(f"   ❌ {e}")