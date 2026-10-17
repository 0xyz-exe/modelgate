"""Test rate limiting on endpoint"""
import requests
import time

API_KEY = "mg_5WEKTfx5ZpCoW4kDI5_rBu6nSTpXINmc"
BASE_URL = "http://localhost:8001"

def test_rate_limit_enforcement():
    """Test that rate limit returns 429 after limit"""
    
    # Reset by using a fresh key prefix
    test_key = f"{API_KEY}_test"
    
    print("\nTesting rate limit with limit=5...")
    
    for i in range(7):
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {test_key}",
                "Content-Type": "application/json",
                "X-Rate-Limit": "5"  # Set low limit for testing
            },
            json={
                "model": "test",
                "messages": [{"role": "user", "content": f"test {i}"}]
            }
        )
        
        print(f"Request {i+1}: {response.status_code}", end="")
        
        if "X-RateLimit-Remaining" in response.headers:
            print(f" | Remaining: {response.headers['X-RateLimit-Remaining']}")
        else:
            print()
        
        if response.status_code == 429:
            print(f"✓ Rate limited at request {i+1}")
            return True
        
        time.sleep(0.1)
    
    print("✗ Did not hit rate limit")
    return False

if __name__ == "__main__":
    test_rate_limit_enforcement()
