import requests
import time
import random
from datetime import datetime

def test_monitoring():
    """Test various monitoring scenarios"""
    base_url = "https://localhost:5001"  # Use HTTPS since SSL is enabled
    
    print("\n=== Testing Sentry Monitoring ===\n")
    
    def log_test(name, response):
        status = "✅ Passed" if response.status_code in [200, 201] else "❌ Failed"
        print(f"{status} - {name}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
    
    # 1. Test Performance Monitoring
    print("1. Testing Performance Monitoring")
    
    # Normal encryption
    response = requests.post(
        f"{base_url}/encrypt",
        json={"text": "test message"},
        verify=False  # For self-signed cert
    )
    log_test("Normal Encryption", response)
    
    # Slow operation simulation
    time.sleep(2.1)  # Trigger slow operation alert
    response = requests.post(
        f"{base_url}/encrypt",
        json={"text": "slow test message"},
        verify=False
    )
    log_test("Slow Operation", response)
    
    # 2. Test Error Tracking
    print("\n2. Testing Error Tracking")
    
    # Invalid request
    response = requests.post(
        f"{base_url}/encrypt",
        json={},  # Missing required field
        verify=False
    )
    log_test("Invalid Request", response)
    
    # 3. Test Security Events
    print("\n3. Testing Security Events")
    
    # Authentication failure
    response = requests.post(
        f"{base_url}/login",
        json={
            "instagram_handle": "test_user",
            "code": "invalid_code"
        },
        verify=False
    )
    log_test("Authentication Failure", response)
    
    # 4. Test Rate Limiting
    print("\n4. Testing Rate Limiting")
    
    # Make multiple rapid requests
    for i in range(6):  # Should trigger rate limit
        response = requests.post(
            f"{base_url}/login",
            json={
                "instagram_handle": f"test_user_{i}",
                "code": "test_code"
            },
            verify=False
        )
        if response.status_code == 429:  # Rate limit reached
            print("✅ Rate limiting working as expected")
            break
    
    # 5. Test Database Error Tracking
    print("\n5. Testing Database Error Tracking")
    
    # Invalid database operation
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "instagram_url": "https://instagram.com/p/invalid"
        },
        verify=False
    )
    log_test("Database Error", response)
    
    print("\nTest completed. Check Sentry dashboard for alerts and events.")
    print("Note: Some 'failures' above are expected as they test error handling.")

if __name__ == "__main__":
    test_monitoring() 