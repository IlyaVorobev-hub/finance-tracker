import urllib.request
import json

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)
    print(f"✅ Status: {response.status}")
    print(f"✅ Response: {response.read().decode()}")
except Exception as e:
    print(f"❌ Error: {e}")