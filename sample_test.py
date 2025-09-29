#!/usr/bin/env python3
"""
Test the exact sample data from the review request
"""

import requests
import json
import uuid

BASE_URL = "https://taskmanager-ai.preview.emergentagent.com/api"

def test_exact_sample():
    """Test with the exact sample data from the review request"""
    
    print("=== TESTING EXACT SAMPLE DATA ===\n")
    
    # Use the exact sample data from the review request
    payload = {
        "name": "Test User",
        "email": "test@example.com", 
        "password": "password123"
    }
    
    print(f"Testing with exact sample data: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Sample data signup worked perfectly")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        elif response.status_code == 400:
            print("❌ FAILED: Sample data signup returned 400")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_exact_sample()