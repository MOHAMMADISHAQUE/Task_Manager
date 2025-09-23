#!/usr/bin/env python3
"""
Quick test for the protected endpoint fix
"""

import requests
import uuid

BASE_URL = "https://smarttask-app-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "securepassword123"

session = requests.Session()

# First signup
print("1. Testing signup...")
signup_payload = {
    "name": "Test User",
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}

signup_response = session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
print(f"Signup status: {signup_response.status_code}")

# Then login
print("2. Testing login...")
login_payload = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}

login_response = session.post(f"{BASE_URL}/auth/login", json=login_payload)
print(f"Login status: {login_response.status_code}")

# Test protected endpoint
print("3. Testing protected endpoint...")
me_response = session.get(f"{BASE_URL}/auth/me")
print(f"Protected endpoint status: {me_response.status_code}")

if me_response.status_code == 200:
    data = me_response.json()
    print(f"User data: {data}")
    print("✅ Protected endpoint working!")
else:
    print(f"❌ Protected endpoint failed: {me_response.text}")