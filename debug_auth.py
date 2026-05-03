# debug_auth.py
import requests

BASE = "http://127.0.0.1:8000"

print("🔹 POST /api/v1/auth/register...")
try:
    r = requests.post(f"{BASE}/api/v1/auth/register", json={
        "email": "debug@example.com",
        "password": "debug123"
    }, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")