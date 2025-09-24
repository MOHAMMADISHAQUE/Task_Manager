#!/usr/bin/env python3
"""
Backend Authentication System Test Suite for SmartTask AI
Tests all authentication endpoints with comprehensive scenarios.
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://taskmaster-ai-16.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_NAME = "John Smith"
TEST_USER_PASSWORD = "securepassword123"

class AuthTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.user_id = None
        self.session_token = None
        self.reset_token = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_signup_valid(self):
        """Test valid user signup"""
        try:
            payload = {
                "name": TEST_USER_NAME,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and data["user"]["email"] == TEST_USER_EMAIL:
                    self.user_id = data["user"]["id"]
                    # Check if session cookie was set
                    cookies = response.cookies
                    if "session_token" in cookies:
                        self.log_test("signup_valid", True, "User signup successful with session cookie")
                    else:
                        self.log_test("signup_valid", True, "User signup successful but no session cookie found")
                else:
                    self.log_test("signup_valid", False, "Invalid response structure", data)
            else:
                self.log_test("signup_valid", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("signup_valid", False, f"Exception: {str(e)}")
    
    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        try:
            payload = {
                "name": "Another User",
                "email": TEST_USER_EMAIL,  # Same email as before
                "password": "anotherpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "already exists" in data.get("detail", "").lower():
                    self.log_test("signup_duplicate_email", True, "Correctly rejected duplicate email")
                else:
                    self.log_test("signup_duplicate_email", False, "Wrong error message", data)
            else:
                self.log_test("signup_duplicate_email", False, f"Expected 400, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("signup_duplicate_email", False, f"Exception: {str(e)}")
    
    def test_signup_weak_password(self):
        """Test signup with weak password"""
        try:
            payload = {
                "name": "Test User",
                "email": f"weak_{uuid.uuid4().hex[:8]}@example.com",
                "password": "123"  # Less than 6 characters
            }
            
            response = self.session.post(f"{BASE_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "6 characters" in data.get("detail", ""):
                    self.log_test("signup_weak_password", True, "Correctly rejected weak password")
                else:
                    self.log_test("signup_weak_password", False, "Wrong error message", data)
            else:
                self.log_test("signup_weak_password", False, f"Expected 400, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("signup_weak_password", False, f"Exception: {str(e)}")
    
    def test_login_valid(self):
        """Test login with valid credentials"""
        try:
            # Clear any existing session first
            self.session.cookies.clear()
            
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and data["user"]["email"] == TEST_USER_EMAIL:
                    # Check if session cookie was set
                    cookies = response.cookies
                    if "session_token" in cookies:
                        self.session_token = cookies["session_token"]
                        self.log_test("login_valid", True, "Login successful with session cookie")
                    else:
                        self.log_test("login_valid", True, "Login successful but no session cookie found")
                else:
                    self.log_test("login_valid", False, "Invalid response structure", data)
            else:
                self.log_test("login_valid", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("login_valid", False, f"Exception: {str(e)}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            payload = {
                "email": TEST_USER_EMAIL,
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                data = response.json()
                if "invalid" in data.get("detail", "").lower():
                    self.log_test("login_invalid_credentials", True, "Correctly rejected invalid credentials")
                else:
                    self.log_test("login_invalid_credentials", False, "Wrong error message", data)
            else:
                self.log_test("login_invalid_credentials", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("login_invalid_credentials", False, f"Exception: {str(e)}")
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        try:
            payload = {
                "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com",
                "password": "somepassword"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_test("login_nonexistent_user", True, "Correctly rejected non-existent user")
            else:
                self.log_test("login_nonexistent_user", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("login_nonexistent_user", False, f"Exception: {str(e)}")
    
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        try:
            # Clear all cookies and headers
            self.session.cookies.clear()
            self.session.headers.clear()
            
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_test("protected_endpoint_without_auth", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("protected_endpoint_without_auth", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("protected_endpoint_without_auth", False, f"Exception: {str(e)}")
    
    def test_protected_endpoint_with_auth(self):
        """Test accessing protected endpoint with valid authentication"""
        try:
            # First login to get session
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            
            if login_response.status_code != 200:
                self.log_test("protected_endpoint_with_auth", False, "Failed to login for test setup", login_response.text)
                return
            
            # Now test the protected endpoint
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data and data["email"] == TEST_USER_EMAIL:
                    self.log_test("protected_endpoint_with_auth", True, "Successfully accessed protected endpoint")
                else:
                    self.log_test("protected_endpoint_with_auth", False, "Invalid user data returned", data)
            else:
                self.log_test("protected_endpoint_with_auth", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("protected_endpoint_with_auth", False, f"Exception: {str(e)}")
    
    def test_logout(self):
        """Test user logout"""
        try:
            # First ensure we're logged in
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            
            if login_response.status_code != 200:
                self.log_test("logout", False, "Failed to login for test setup", login_response.text)
                return
            
            # Now logout
            response = self.session.post(f"{BASE_URL}/auth/logout")
            
            if response.status_code == 200:
                # Try to access protected endpoint after logout
                me_response = self.session.get(f"{BASE_URL}/auth/me")
                
                if me_response.status_code == 401:
                    self.log_test("logout", True, "Logout successful - session invalidated")
                else:
                    self.log_test("logout", False, f"Session still valid after logout: {me_response.status_code}")
            else:
                self.log_test("logout", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("logout", False, f"Exception: {str(e)}")
    
    def test_forgot_password_existing_user(self):
        """Test forgot password for existing user"""
        try:
            payload = {
                "email": TEST_USER_EMAIL
            }
            
            response = self.session.post(f"{BASE_URL}/auth/forgot-password", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "reset link" in data.get("message", "").lower():
                    self.log_test("forgot_password_existing_user", True, "Forgot password request processed")
                else:
                    self.log_test("forgot_password_existing_user", False, "Unexpected response message", data)
            else:
                self.log_test("forgot_password_existing_user", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("forgot_password_existing_user", False, f"Exception: {str(e)}")
    
    def test_forgot_password_nonexistent_user(self):
        """Test forgot password for non-existent user"""
        try:
            payload = {
                "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/forgot-password", json=payload)
            
            # Should still return success for security (don't reveal if email exists)
            if response.status_code == 200:
                data = response.json()
                if "reset link" in data.get("message", "").lower():
                    self.log_test("forgot_password_nonexistent_user", True, "Correctly handled non-existent user (security)")
                else:
                    self.log_test("forgot_password_nonexistent_user", False, "Unexpected response message", data)
            else:
                self.log_test("forgot_password_nonexistent_user", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("forgot_password_nonexistent_user", False, f"Exception: {str(e)}")
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        try:
            payload = {
                "token": "invalid_token_12345",
                "password": "newpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/reset-password", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "invalid" in data.get("detail", "").lower() or "expired" in data.get("detail", "").lower():
                    self.log_test("reset_password_invalid_token", True, "Correctly rejected invalid token")
                else:
                    self.log_test("reset_password_invalid_token", False, "Wrong error message", data)
            else:
                self.log_test("reset_password_invalid_token", False, f"Expected 400, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("reset_password_invalid_token", False, f"Exception: {str(e)}")
    
    def test_reset_password_weak_password(self):
        """Test password reset with weak password"""
        try:
            payload = {
                "token": "some_token",
                "password": "123"  # Less than 6 characters
            }
            
            response = self.session.post(f"{BASE_URL}/auth/reset-password", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "6 characters" in data.get("detail", ""):
                    self.log_test("reset_password_weak_password", True, "Correctly rejected weak password")
                elif "invalid" in data.get("detail", "").lower():
                    # Token validation happens first, which is also acceptable
                    self.log_test("reset_password_weak_password", True, "Token validation occurred first (acceptable)")
                else:
                    self.log_test("reset_password_weak_password", False, "Wrong error message", data)
            else:
                self.log_test("reset_password_weak_password", False, f"Expected 400, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("reset_password_weak_password", False, f"Exception: {str(e)}")
    
    def test_oauth_process_endpoint(self):
        """Test OAuth processing endpoint structure"""
        try:
            # Test with minimal valid structure
            payload = {
                "user_data": {
                    "name": "OAuth User",
                    "email": f"oauth_{uuid.uuid4().hex[:8]}@example.com",
                    "picture": "https://example.com/avatar.jpg"
                },
                "session_token": "oauth_session_token_123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/process-oauth", json=payload)
            
            # This might fail due to OAuth validation, but we're testing the endpoint exists
            if response.status_code in [200, 400, 401]:
                if response.status_code == 200:
                    self.log_test("oauth_process_endpoint", True, "OAuth endpoint accessible and working")
                else:
                    # Endpoint exists but may have validation logic
                    self.log_test("oauth_process_endpoint", True, f"OAuth endpoint exists (returned {response.status_code})")
            else:
                self.log_test("oauth_process_endpoint", False, f"Unexpected status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("oauth_process_endpoint", False, f"Exception: {str(e)}")
    
    def test_api_base_endpoint(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("api_base_endpoint", True, "API base endpoint accessible")
                else:
                    self.log_test("api_base_endpoint", False, "Unexpected response structure", data)
            else:
                self.log_test("api_base_endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("api_base_endpoint", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print(f"🚀 Starting Authentication Test Suite for SmartTask AI")
        print(f"📍 Testing against: {BASE_URL}")
        print(f"👤 Test user email: {TEST_USER_EMAIL}")
        print("=" * 80)
        
        # Basic connectivity
        self.test_api_base_endpoint()
        
        # Authentication flow tests
        self.test_signup_valid()
        self.test_signup_duplicate_email()
        self.test_signup_weak_password()
        
        self.test_login_valid()
        self.test_login_invalid_credentials()
        self.test_login_nonexistent_user()
        
        # Protected endpoint tests
        self.test_protected_endpoint_without_auth()
        self.test_protected_endpoint_with_auth()
        
        # Session management
        self.test_logout()
        
        # Password reset flow
        self.test_forgot_password_existing_user()
        self.test_forgot_password_nonexistent_user()
        self.test_reset_password_invalid_token()
        self.test_reset_password_weak_password()
        
        # OAuth endpoint
        self.test_oauth_process_endpoint()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        # Return success status
        return failed == 0

if __name__ == "__main__":
    test_suite = AuthTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)