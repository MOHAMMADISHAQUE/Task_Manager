#!/usr/bin/env python3
"""
Test with fresh sample data to confirm the endpoint works
"""

import requests
import json
import uuid

BASE_URL = "https://taskmanager-ai.preview.emergentagent.com/api"

def test_fresh_sample():
    """Test with fresh sample data"""
    
    print("=== TESTING FRESH SAMPLE DATA ===\n")
    
    # Use fresh email to avoid duplicate error
    fresh_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    payload = {
        "name": "Test User",
        "email": fresh_email, 
        "password": "password123"
    }
    
    print(f"Testing with fresh sample data: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Fresh sample data signup worked perfectly")
            data = response.json()
            print(f"User created: {data['user']['email']}")
            print(f"Message: {data['message']}")
        else:
            print(f"❌ FAILED: Got status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"Raw error: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_fresh_sample()