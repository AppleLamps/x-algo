"""
Test script to verify API key-based rate limiting works correctly.
Run this after starting the backend server.
"""
import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "algo-x-demo-key-2025"  # Replace with your actual API key
RATE_LIMIT = 10  # Should match RATE_LIMIT_REQUESTS in main.py

def test_rate_limiting():
    """Test that rate limiting works based on API key."""
    print("Testing API key-based rate limiting...")
    print(f"Making {RATE_LIMIT + 1} requests to test rate limit of {RATE_LIMIT} requests/minute\n")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "username": "testuser"
    }
    
    success_count = 0
    rate_limited = False
    
    for i in range(RATE_LIMIT + 1):
        try:
            response = requests.post(
                f"{BASE_URL}/insights",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Request {i+1}: Success (200)")
            elif response.status_code == 429:
                rate_limited = True
                print(f"🚫 Request {i+1}: Rate limited (429)")
                print(f"   Response: {response.json()}")
            else:
                print(f"⚠️  Request {i+1}: Unexpected status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request {i+1}: Error - {e}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print(f"\n{'='*60}")
    print(f"Test Results:")
    print(f"  Successful requests: {success_count}/{RATE_LIMIT}")
    print(f"  Rate limiting triggered: {'✅ Yes' if rate_limited else '❌ No'}")
    print(f"{'='*60}\n")
    
    if success_count == RATE_LIMIT and rate_limited:
        print("✅ PASS: Rate limiting is working correctly!")
        return True
    else:
        print("❌ FAIL: Rate limiting is not working as expected")
        return False

def test_different_api_keys():
    """Test that different API keys have separate rate limits."""
    print("\nTesting that different API keys have separate rate limits...")
    print("(This test requires multiple valid API keys)\n")
    
    # This is a conceptual test - you'd need multiple valid API keys
    print("⚠️  Skipping: Requires multiple API keys to test properly")
    print("   Manual test: Use different API keys and verify each has its own limit\n")

if __name__ == "__main__":
    print("="*60)
    print("Rate Limiting Test Suite")
    print("="*60)
    print("\nMake sure the backend server is running on http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Run tests
    test_rate_limiting()
    test_different_api_keys()
    
    print("\n✅ Testing complete!")

