"""Test chat completion endpoint"""
import httpx
import json

API_KEY = "mg_5WEKTfx5ZpCoW4kDI5_rBu6nSTpXINmc"
BASE_URL = "http://localhost:8000"

def test_chat_completion():
    """Test /v1/chat/completions endpoint"""
    
    response = httpx.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello, this is a test"}
            ],
            "temperature": 0.7,
        },
        timeout=10.0,
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "choices" in data
    assert "usage" in data
    assert data["usage"]["source"] == "DEMO"
    print("\n✓ Test passed!")


if __name__ == "__main__":
    test_chat_completion()
