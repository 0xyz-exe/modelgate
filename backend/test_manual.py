"""Test endpoints manually"""
import httpx

BASE_URL = "http://localhost:8000"
API_KEY = "mg_5WEKTfx5ZpCoW4kDI5_rBu6nSTpXINmc"

# Test health
print("Testing /health...")
resp = httpx.get(f"{BASE_URL}/health")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Test chat
print("Testing /v1/chat/completions...")
resp = httpx.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello test"}]
    }
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"Response: {resp.json()}")
else:
    print(f"Error: {resp.text}")
