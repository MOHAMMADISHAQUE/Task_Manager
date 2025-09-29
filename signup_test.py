#!/usr/bin/env python3
"""
Focused test for the /api/auth/signup endpoint to identify 400 Bad Request issues.
"""

import requests
import json
import uuid
import sys

# Configuration
BASE_URL = "https://taskmanager-ai.preview.emergentagent.com/api"

def test_signup_endpoint():
    """Test the signup endpoint with various scenarios"""
    
    print("=== SIGNUP ENDPOINT TESTING ===\n")
    
    # Test 1: Valid signup request
    print("Test 1: Valid signup request")
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    
    payload = {
        "name": "Test User",
        "email": test_email,
        "password": "password123"
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Valid signup worked")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ FAILED: Valid signup failed")
            print(f"Response text: {response.text}")
            
            # Try to parse as JSON for better error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Different email formats
    email_formats = [
        "user@domain.com",
        "user.name@domain.com", 
        "user+tag@domain.co.uk",
        "user123@subdomain.domain.org"
    ]
    
    for i, email in enumerate(email_formats, 2):
        print(f"Test {i}: Email format test - {email}")
        
        payload = {
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Email format {email} accepted")
            else:
                print(f"❌ FAILED: Email format {email} rejected")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Raw error: {response.text}")
                    
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        print()
    
    print("="*50 + "\n")
    
    # Test 3: Missing fields
    missing_field_tests = [
        {"email": "test@example.com", "password": "password123"},  # Missing name
        {"name": "Test User", "password": "password123"},  # Missing email
        {"name": "Test User", "email": "test@example.com"},  # Missing password
        {}  # Missing all fields
    ]
    
    for i, payload in enumerate(missing_field_tests, 6):
        missing_fields = []
        if "name" not in payload: missing_fields.append("name")
        if "email" not in payload: missing_fields.append("email") 
        if "password" not in payload: missing_fields.append("password")
        
        print(f"Test {i}: Missing fields - {', '.join(missing_fields) if missing_fields else 'all fields'}")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 422:  # Validation error expected
                print("✅ SUCCESS: Correctly rejected missing fields")
                try:
                    error_data = response.json()
                    print(f"Validation errors: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw error: {response.text}")
            elif response.status_code == 400:
                print("✅ SUCCESS: Rejected with 400 (also acceptable)")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Raw error: {response.text}")
            else:
                print(f"❌ UNEXPECTED: Expected 422 or 400, got {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        print()
    
    print("="*50 + "\n")
    
    # Test 4: Invalid email formats
    invalid_emails = [
        "notanemail",
        "@domain.com",
        "user@",
        "user@domain",
        "user space@domain.com"
    ]
    
    for i, email in enumerate(invalid_emails, 10):
        print(f"Test {i}: Invalid email format - {email}")
        
        payload = {
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code in [400, 422]:
                print("✅ SUCCESS: Correctly rejected invalid email")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Raw error: {response.text}")
            else:
                print(f"❌ UNEXPECTED: Expected 400/422, got {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_signup_endpoint()