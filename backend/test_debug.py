"""Test with full error details"""
import httpx
import traceback

BASE_URL = "http://localhost:8000"
API_KEY = "mg_5WEKTfx5ZpCoW4kDI5_rBu6nSTpXINmc"

try:
    print("Testing /v1/chat/completions...")
    resp = httpx.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello test"}]
        },
        timeout=10.0
    )
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}")
    print(f"Body: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n✓ SUCCESS")
        print(f"ID: {data['id']}")
        print(f"Model: {data['model']}")
        print(f"Content: {data['choices'][0]['message']['content']}")
        print(f"Usage: {data['usage']}")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
