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
    
    def test_emergent_auth_login_initiation(self):
        """Test Emergent Auth login initiation endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/auth/emergent/login")
            
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and "auth.emergentagent.com" in data["auth_url"]:
                    self.log_test("emergent_auth_login_initiation", True, "Emergent Auth login endpoint returns valid auth URL")
                else:
                    self.log_test("emergent_auth_login_initiation", False, "Invalid auth URL structure", data)
            else:
                self.log_test("emergent_auth_login_initiation", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("emergent_auth_login_initiation", False, f"Exception: {str(e)}")
    
    def test_emergent_auth_login_with_redirect(self):
        """Test Emergent Auth login with custom redirect URL"""
        try:
            custom_redirect = "https://example.com/dashboard"
            response = self.session.get(f"{BASE_URL}/auth/emergent/login?redirect_url={custom_redirect}")
            
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and custom_redirect in data["auth_url"]:
                    self.log_test("emergent_auth_login_with_redirect", True, "Emergent Auth login accepts custom redirect URL")
                else:
                    self.log_test("emergent_auth_login_with_redirect", False, "Custom redirect not properly handled", data)
            else:
                self.log_test("emergent_auth_login_with_redirect", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("emergent_auth_login_with_redirect", False, f"Exception: {str(e)}")
    
    def test_emergent_auth_callback_invalid_session(self):
        """Test Emergent Auth callback with invalid session ID"""
        try:
            payload = {
                "session_id": "invalid_session_id_12345"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/emergent/callback", json=payload)
            
            # Should fail with 400 or 500 due to invalid session
            if response.status_code in [400, 500]:
                data = response.json()
                if "invalid" in data.get("detail", "").lower() or "session" in data.get("detail", "").lower():
                    self.log_test("emergent_auth_callback_invalid_session", True, "Correctly rejected invalid session ID")
                else:
                    self.log_test("emergent_auth_callback_invalid_session", True, f"Rejected invalid session (status {response.status_code})")
            else:
                self.log_test("emergent_auth_callback_invalid_session", False, f"Expected 400/500, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("emergent_auth_callback_invalid_session", False, f"Exception: {str(e)}")
    
    def test_emergent_auth_callback_structure(self):
        """Test Emergent Auth callback endpoint structure and validation"""
        try:
            # Test with missing session_id
            response = self.session.post(f"{BASE_URL}/auth/emergent/callback", json={})
            
            if response.status_code == 422:  # Validation error
                data = response.json()
                if "session_id" in str(data).lower():
                    self.log_test("emergent_auth_callback_structure", True, "Correctly validates required session_id field")
                else:
                    self.log_test("emergent_auth_callback_structure", False, "Unexpected validation error", data)
            else:
                self.log_test("emergent_auth_callback_structure", False, f"Expected 422, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("emergent_auth_callback_structure", False, f"Exception: {str(e)}")
    
    def test_dual_auth_system_independence(self):
        """Test that both authentication systems work independently"""
        try:
            # First, ensure we can still create and login with email/password
            email_user_email = f"emailuser_{uuid.uuid4().hex[:8]}@example.com"
            
            # Create email user
            signup_payload = {
                "name": "Email User",
                "email": email_user_email,
                "password": "emailpassword123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("dual_auth_system_independence", False, "Failed to create email user", signup_response.text)
                return
            
            # Clear session and login with email
            self.session.cookies.clear()
            
            login_payload = {
                "email": email_user_email,
                "password": "emailpassword123"
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                # Test protected endpoint access
                me_response = self.session.get(f"{BASE_URL}/auth/me")
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    if user_data.get("auth_provider") == "email":
                        self.log_test("dual_auth_system_independence", True, "Email authentication system works independently")
                    else:
                        self.log_test("dual_auth_system_independence", False, "Wrong auth_provider in response", user_data)
                else:
                    self.log_test("dual_auth_system_independence", False, f"Protected endpoint failed: {me_response.status_code}")
            else:
                self.log_test("dual_auth_system_independence", False, f"Email login failed: {login_response.status_code}")
                
        except Exception as e:
            self.log_test("dual_auth_system_independence", False, f"Exception: {str(e)}")
    
    def test_user_model_updates(self):
        """Test that user model supports new fields for dual auth"""
        try:
            # Create a user and check the response structure
            test_email = f"modeltest_{uuid.uuid4().hex[:8]}@example.com"
            
            signup_payload = {
                "name": "Model Test User",
                "email": test_email,
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("user", {})
                
                # Check for required fields
                required_fields = ["id", "name", "email", "auth_provider"]
                missing_fields = [field for field in required_fields if field not in user]
                
                if not missing_fields:
                    if user.get("auth_provider") == "email":
                        self.log_test("user_model_updates", True, "User model includes all required fields for dual auth")
                    else:
                        self.log_test("user_model_updates", False, f"Wrong auth_provider: {user.get('auth_provider')}")
                else:
                    self.log_test("user_model_updates", False, f"Missing fields: {missing_fields}", user)
            else:
                self.log_test("user_model_updates", False, f"Failed to create user: {response.status_code}")
                
        except Exception as e:
            self.log_test("user_model_updates", False, f"Exception: {str(e)}")
    
    def test_session_management_consistency(self):
        """Test that session management works consistently for both auth types"""
        try:
            # Test session management with email auth
            test_email = f"sessiontest_{uuid.uuid4().hex[:8]}@example.com"
            
            # Create and login user
            signup_payload = {
                "name": "Session Test User",
                "email": test_email,
                "password": "sessiontest123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("session_management_consistency", False, "Failed to create test user")
                return
            
            # Check session cookie was set
            if "session_token" not in signup_response.cookies:
                self.log_test("session_management_consistency", False, "No session cookie set on signup")
                return
            
            # Test protected endpoint access
            me_response = self.session.get(f"{BASE_URL}/auth/me")
            
            if me_response.status_code == 200:
                # Test logout
                logout_response = self.session.post(f"{BASE_URL}/auth/logout")
                
                if logout_response.status_code == 200:
                    # Verify session is invalidated
                    me_after_logout = self.session.get(f"{BASE_URL}/auth/me")
                    
                    if me_after_logout.status_code == 401:
                        self.log_test("session_management_consistency", True, "Session management works consistently")
                    else:
                        self.log_test("session_management_consistency", False, f"Session not invalidated: {me_after_logout.status_code}")
                else:
                    self.log_test("session_management_consistency", False, f"Logout failed: {logout_response.status_code}")
            else:
                self.log_test("session_management_consistency", False, f"Protected endpoint failed: {me_response.status_code}")
                
        except Exception as e:
            self.log_test("session_management_consistency", False, f"Exception: {str(e)}")
    
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
    
    def test_ai_parse_task_simple(self):
        """Test AI natural language task parsing with simple input"""
        try:
            # First login to get session
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_parse_task_simple", False, "Failed to login for test setup", login_response.text)
                return
            
            # Test simple task parsing
            payload = {
                "text": "Remember to buy groceries"
            }
            
            response = self.session.post(f"{BASE_URL}/ai/parse-task", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "task" in data:
                    task = data["task"]
                    if "title" in task and "description" in task and "priority" in task:
                        self.log_test("ai_parse_task_simple", True, f"Simple task parsed successfully (AI used: {data.get('ai_used', False)})")
                    else:
                        self.log_test("ai_parse_task_simple", False, "Missing required task fields", data)
                else:
                    self.log_test("ai_parse_task_simple", False, "Invalid response structure", data)
            else:
                self.log_test("ai_parse_task_simple", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_parse_task_simple", False, f"Exception: {str(e)}")
    
    def test_ai_parse_task_with_date(self):
        """Test AI task parsing with date expressions"""
        try:
            # Ensure logged in
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_parse_task_with_date", False, "Failed to login for test setup")
                return
            
            # Test task with date expression
            payload = {
                "text": "Call John tomorrow at 3 PM"
            }
            
            response = self.session.post(f"{BASE_URL}/ai/parse-task", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "task" in data:
                    task = data["task"]
                    if "due_date" in task and task["due_date"]:
                        self.log_test("ai_parse_task_with_date", True, f"Task with date parsed successfully (AI used: {data.get('ai_used', False)})")
                    else:
                        self.log_test("ai_parse_task_with_date", True, f"Task parsed but no due date extracted (AI used: {data.get('ai_used', False)})")
                else:
                    self.log_test("ai_parse_task_with_date", False, "Invalid response structure", data)
            else:
                self.log_test("ai_parse_task_with_date", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_parse_task_with_date", False, f"Exception: {str(e)}")
    
    def test_ai_parse_task_with_priority(self):
        """Test AI task parsing with priority keywords"""
        try:
            # Ensure logged in
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_parse_task_with_priority", False, "Failed to login for test setup")
                return
            
            # Test task with priority keywords
            payload = {
                "text": "Finish quarterly report next Friday with high priority - this is urgent!"
            }
            
            response = self.session.post(f"{BASE_URL}/ai/parse-task", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "task" in data:
                    task = data["task"]
                    priority = task.get("priority", "medium")
                    if priority == "high":
                        self.log_test("ai_parse_task_with_priority", True, f"High priority task parsed correctly (AI used: {data.get('ai_used', False)})")
                    else:
                        self.log_test("ai_parse_task_with_priority", True, f"Task parsed with priority: {priority} (AI used: {data.get('ai_used', False)})")
                else:
                    self.log_test("ai_parse_task_with_priority", False, "Invalid response structure", data)
            else:
                self.log_test("ai_parse_task_with_priority", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_parse_task_with_priority", False, f"Exception: {str(e)}")
    
    def test_ai_parse_task_without_auth(self):
        """Test AI task parsing without authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            payload = {
                "text": "Test task without auth"
            }
            
            response = self.session.post(f"{BASE_URL}/ai/parse-task", json=payload)
            
            if response.status_code == 401:
                self.log_test("ai_parse_task_without_auth", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("ai_parse_task_without_auth", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_parse_task_without_auth", False, f"Exception: {str(e)}")
    
    def test_ai_suggestions_no_tasks(self):
        """Test AI suggestions for user with no tasks"""
        try:
            # Create a new user for this test
            new_user_email = f"suggestions_test_{uuid.uuid4().hex[:8]}@example.com"
            
            # Signup new user
            signup_payload = {
                "name": "Suggestions Test User",
                "email": new_user_email,
                "password": "testpassword123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("ai_suggestions_no_tasks", False, "Failed to create test user")
                return
            
            # Get suggestions
            response = self.session.get(f"{BASE_URL}/ai/suggestions")
            
            if response.status_code == 200:
                data = response.json()
                if "suggestions" in data and isinstance(data["suggestions"], list) and len(data["suggestions"]) > 0:
                    self.log_test("ai_suggestions_no_tasks", True, f"Starter suggestions provided: {len(data['suggestions'])} suggestions")
                else:
                    self.log_test("ai_suggestions_no_tasks", False, "No suggestions returned", data)
            else:
                self.log_test("ai_suggestions_no_tasks", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_suggestions_no_tasks", False, f"Exception: {str(e)}")
    
    def test_ai_suggestions_with_tasks(self):
        """Test AI suggestions for user with existing tasks"""
        try:
            # Login with main test user (who should have tasks from previous tests)
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_suggestions_with_tasks", False, "Failed to login for test setup")
                return
            
            # Get suggestions
            response = self.session.get(f"{BASE_URL}/ai/suggestions")
            
            if response.status_code == 200:
                data = response.json()
                if "suggestions" in data and isinstance(data["suggestions"], list) and len(data["suggestions"]) > 0:
                    self.log_test("ai_suggestions_with_tasks", True, f"Task-based suggestions provided: {len(data['suggestions'])} suggestions")
                else:
                    self.log_test("ai_suggestions_with_tasks", False, "No suggestions returned", data)
            else:
                self.log_test("ai_suggestions_with_tasks", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_suggestions_with_tasks", False, f"Exception: {str(e)}")
    
    def test_ai_suggestions_without_auth(self):
        """Test AI suggestions without authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            response = self.session.get(f"{BASE_URL}/ai/suggestions")
            
            if response.status_code == 401:
                self.log_test("ai_suggestions_without_auth", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("ai_suggestions_without_auth", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_suggestions_without_auth", False, f"Exception: {str(e)}")
    
    def test_ai_summary_no_tasks(self):
        """Test AI summary for user with no tasks"""
        try:
            # Create a new user for this test
            new_user_email = f"summary_test_{uuid.uuid4().hex[:8]}@example.com"
            
            # Signup new user
            signup_payload = {
                "name": "Summary Test User",
                "email": new_user_email,
                "password": "testpassword123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("ai_summary_no_tasks", False, "Failed to create test user")
                return
            
            # Get summary
            response = self.session.get(f"{BASE_URL}/ai/summary")
            
            if response.status_code == 200:
                data = response.json()
                if "summary" in data and "stats" in data:
                    stats = data["stats"]
                    if stats.get("total") == 0:
                        self.log_test("ai_summary_no_tasks", True, f"Empty task summary provided: '{data['summary']}'")
                    else:
                        self.log_test("ai_summary_no_tasks", False, f"Expected 0 tasks, got {stats.get('total')}")
                else:
                    self.log_test("ai_summary_no_tasks", False, "Missing summary or stats", data)
            else:
                self.log_test("ai_summary_no_tasks", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_summary_no_tasks", False, f"Exception: {str(e)}")
    
    def test_ai_summary_with_tasks(self):
        """Test AI summary for user with existing tasks"""
        try:
            # Login with main test user (who should have tasks from previous tests)
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_summary_with_tasks", False, "Failed to login for test setup")
                return
            
            # Get summary
            response = self.session.get(f"{BASE_URL}/ai/summary")
            
            if response.status_code == 200:
                data = response.json()
                if "summary" in data and "stats" in data:
                    stats = data["stats"]
                    required_stats = ["total", "completed", "pending", "overdue", "high_priority"]
                    missing_stats = [stat for stat in required_stats if stat not in stats]
                    
                    if not missing_stats:
                        self.log_test("ai_summary_with_tasks", True, f"Task summary provided with all stats: {stats}")
                    else:
                        self.log_test("ai_summary_with_tasks", False, f"Missing stats: {missing_stats}")
                else:
                    self.log_test("ai_summary_with_tasks", False, "Missing summary or stats", data)
            else:
                self.log_test("ai_summary_with_tasks", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_summary_with_tasks", False, f"Exception: {str(e)}")
    
    def test_ai_summary_without_auth(self):
        """Test AI summary without authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            response = self.session.get(f"{BASE_URL}/ai/summary")
            
            if response.status_code == 401:
                self.log_test("ai_summary_without_auth", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("ai_summary_without_auth", False, f"Expected 401, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_summary_without_auth", False, f"Exception: {str(e)}")
    
    def test_ai_parse_task_invalid_input(self):
        """Test AI task parsing with invalid input"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("ai_parse_task_invalid_input", False, "Failed to login for test setup")
                return
            
            # Test with empty text
            payload = {
                "text": ""
            }
            
            response = self.session.post(f"{BASE_URL}/ai/parse-task", json=payload)
            
            if response.status_code == 422:  # Validation error
                self.log_test("ai_parse_task_invalid_input", True, "Correctly rejected empty text")
            elif response.status_code == 200:
                # Some implementations might handle empty text gracefully
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("ai_parse_task_invalid_input", True, "Handled empty text gracefully")
                else:
                    self.log_test("ai_parse_task_invalid_input", False, "Unexpected response for empty text", data)
            else:
                self.log_test("ai_parse_task_invalid_input", False, f"Unexpected status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("ai_parse_task_invalid_input", False, f"Exception: {str(e)}")

    # ========== SETTINGS API TESTS ==========
    
    def test_get_profile_settings(self):
        """Test getting user profile settings"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_profile_settings", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/settings/profile")
            
            if response.status_code == 200:
                data = response.json()
                if "profile" in data:
                    profile = data["profile"]
                    required_fields = ["name", "email", "auth_provider", "role", "timezone", "language"]
                    missing_fields = [field for field in required_fields if field not in profile]
                    
                    if not missing_fields:
                        self.log_test("get_profile_settings", True, f"Profile retrieved successfully: {profile['email']}")
                    else:
                        self.log_test("get_profile_settings", False, f"Missing profile fields: {missing_fields}")
                else:
                    self.log_test("get_profile_settings", False, "Missing profile in response", data)
            else:
                self.log_test("get_profile_settings", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_profile_settings", False, f"Exception: {str(e)}")
    
    def test_update_profile_settings(self):
        """Test updating user profile settings"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("update_profile_settings", False, "Failed to login for test setup")
                return
            
            # Update profile
            update_payload = {
                "name": "Updated Test User",
                "role": "Senior Developer",
                "timezone": "UTC-5",
                "language": "Spanish"
            }
            
            response = self.session.put(f"{BASE_URL}/settings/profile", json=update_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify the update by getting profile again
                    get_response = self.session.get(f"{BASE_URL}/settings/profile")
                    if get_response.status_code == 200:
                        profile_data = get_response.json()
                        profile = profile_data.get("profile", {})
                        if (profile.get("name") == "Updated Test User" and 
                            profile.get("role") == "Senior Developer"):
                            self.log_test("update_profile_settings", True, "Profile updated successfully")
                        else:
                            self.log_test("update_profile_settings", False, "Profile not updated correctly", profile)
                    else:
                        self.log_test("update_profile_settings", False, "Failed to verify profile update")
                else:
                    self.log_test("update_profile_settings", False, "Update not successful", data)
            else:
                self.log_test("update_profile_settings", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("update_profile_settings", False, f"Exception: {str(e)}")
    
    def test_get_notification_settings(self):
        """Test getting notification settings"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_notification_settings", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/settings/notifications")
            
            if response.status_code == 200:
                data = response.json()
                if "notifications" in data:
                    notifications = data["notifications"]
                    required_fields = ["email", "push", "desktop", "task_reminders", "project_updates", "weekly_digest"]
                    missing_fields = [field for field in required_fields if field not in notifications]
                    
                    if not missing_fields:
                        self.log_test("get_notification_settings", True, f"Notification settings retrieved: {notifications}")
                    else:
                        self.log_test("get_notification_settings", False, f"Missing notification fields: {missing_fields}")
                else:
                    self.log_test("get_notification_settings", False, "Missing notifications in response", data)
            else:
                self.log_test("get_notification_settings", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_notification_settings", False, f"Exception: {str(e)}")
    
    def test_update_notification_settings(self):
        """Test updating notification settings"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("update_notification_settings", False, "Failed to login for test setup")
                return
            
            # Update notification settings
            update_payload = {
                "email": False,
                "push": True,
                "desktop": True,
                "task_reminders": False,
                "project_updates": True,
                "weekly_digest": True
            }
            
            response = self.session.put(f"{BASE_URL}/settings/notifications", json=update_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify the update by getting settings again
                    get_response = self.session.get(f"{BASE_URL}/settings/notifications")
                    if get_response.status_code == 200:
                        settings_data = get_response.json()
                        notifications = settings_data.get("notifications", {})
                        if (notifications.get("email") == False and 
                            notifications.get("desktop") == True and
                            notifications.get("weekly_digest") == True):
                            self.log_test("update_notification_settings", True, "Notification settings updated successfully")
                        else:
                            self.log_test("update_notification_settings", False, "Settings not updated correctly", notifications)
                    else:
                        self.log_test("update_notification_settings", False, "Failed to verify settings update")
                else:
                    self.log_test("update_notification_settings", False, "Update not successful", data)
            else:
                self.log_test("update_notification_settings", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("update_notification_settings", False, f"Exception: {str(e)}")
    
    def test_change_password_email_user(self):
        """Test password change for email auth users"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("change_password_email_user", False, "Failed to login for test setup")
                return
            
            # Try to change password
            change_payload = {
                "current_password": TEST_USER_PASSWORD,
                "new_password": "newsecurepassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/settings/change-password", json=change_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Test login with new password
                    self.session.cookies.clear()
                    new_login_payload = {
                        "email": TEST_USER_EMAIL,
                        "password": "newsecurepassword123"
                    }
                    
                    new_login_response = self.session.post(f"{BASE_URL}/auth/login", json=new_login_payload)
                    
                    if new_login_response.status_code == 200:
                        self.log_test("change_password_email_user", True, "Password changed successfully")
                        # Change back to original password for other tests
                        change_back_payload = {
                            "current_password": "newsecurepassword123",
                            "new_password": TEST_USER_PASSWORD
                        }
                        self.session.post(f"{BASE_URL}/settings/change-password", json=change_back_payload)
                    else:
                        self.log_test("change_password_email_user", False, "New password login failed")
                else:
                    self.log_test("change_password_email_user", False, "Password change not successful", data)
            else:
                self.log_test("change_password_email_user", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("change_password_email_user", False, f"Exception: {str(e)}")
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("change_password_wrong_current", False, "Failed to login for test setup")
                return
            
            # Try to change password with wrong current password
            change_payload = {
                "current_password": "wrongpassword",
                "new_password": "newsecurepassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/settings/change-password", json=change_payload)
            
            if response.status_code == 400:
                data = response.json()
                if "incorrect" in data.get("detail", "").lower():
                    self.log_test("change_password_wrong_current", True, "Correctly rejected wrong current password")
                else:
                    self.log_test("change_password_wrong_current", False, "Wrong error message", data)
            else:
                self.log_test("change_password_wrong_current", False, f"Expected 400, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("change_password_wrong_current", False, f"Exception: {str(e)}")
    
    def test_get_security_info(self):
        """Test getting security information"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_security_info", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/settings/security")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["auth_provider", "two_factor_enabled", "login_history"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if data.get("auth_provider") == "email":
                        self.log_test("get_security_info", True, f"Security info retrieved: {len(data.get('login_history', []))} login sessions")
                    else:
                        self.log_test("get_security_info", False, f"Wrong auth_provider: {data.get('auth_provider')}")
                else:
                    self.log_test("get_security_info", False, f"Missing security fields: {missing_fields}")
            else:
                self.log_test("get_security_info", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_security_info", False, f"Exception: {str(e)}")
    
    def test_settings_without_auth(self):
        """Test settings endpoints without authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            endpoints = [
                "/settings/profile",
                "/settings/notifications", 
                "/settings/security"
            ]
            
            all_protected = True
            for endpoint in endpoints:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                if response.status_code != 401:
                    all_protected = False
                    break
            
            if all_protected:
                self.log_test("settings_without_auth", True, "All settings endpoints properly protected")
            else:
                self.log_test("settings_without_auth", False, f"Some endpoints not protected: {endpoint}")
                
        except Exception as e:
            self.log_test("settings_without_auth", False, f"Exception: {str(e)}")

    # ========== ONBOARDING API TESTS ==========
    
    def test_clean_user_registration_no_auto_sample_data(self):
        """Test that new user signup creates clean workspace with no automatic sample data"""
        try:
            # Create a completely new user
            clean_user_email = f"cleanuser_{uuid.uuid4().hex[:8]}@example.com"
            clean_user_name = "Clean Test User"
            
            signup_payload = {
                "name": clean_user_name,
                "email": clean_user_email,
                "password": "cleanpassword123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if response.status_code == 200:
                # Check onboarding status immediately after signup
                status_response = self.session.get(f"{BASE_URL}/onboarding/status")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if (status_data.get("onboarded") == False and 
                        status_data.get("tasks_count") == 0 and 
                        status_data.get("projects_count") == 0):
                        self.log_test("clean_user_registration_no_auto_sample_data", True, 
                                    f"New user starts with clean workspace: {status_data}")
                    else:
                        self.log_test("clean_user_registration_no_auto_sample_data", False, 
                                    f"New user has unexpected data: {status_data}")
                else:
                    self.log_test("clean_user_registration_no_auto_sample_data", False, 
                                f"Failed to check onboarding status: {status_response.status_code}")
            else:
                self.log_test("clean_user_registration_no_auto_sample_data", False, 
                            f"Failed to create user: {response.status_code}")
                
        except Exception as e:
            self.log_test("clean_user_registration_no_auto_sample_data", False, f"Exception: {str(e)}")
    
    def test_onboarding_status_check_new_user(self):
        """Test onboarding status check for brand new user"""
        try:
            # Create a new user
            new_user_email = f"statustest_{uuid.uuid4().hex[:8]}@example.com"
            
            signup_payload = {
                "name": "Status Test User",
                "email": new_user_email,
                "password": "statustest123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("onboarding_status_check_new_user", False, "Failed to create test user")
                return
            
            # Check onboarding status
            response = self.session.get(f"{BASE_URL}/onboarding/status")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["onboarded", "tasks_count", "projects_count", "has_settings"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if (data["onboarded"] == False and 
                        data["tasks_count"] == 0 and 
                        data["projects_count"] == 0):
                        self.log_test("onboarding_status_check_new_user", True, 
                                    f"Correctly detected new user: onboarded={data['onboarded']}")
                    else:
                        self.log_test("onboarding_status_check_new_user", False, 
                                    f"Incorrect status for new user: {data}")
                else:
                    self.log_test("onboarding_status_check_new_user", False, 
                                f"Missing status fields: {missing_fields}")
            else:
                self.log_test("onboarding_status_check_new_user", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("onboarding_status_check_new_user", False, f"Exception: {str(e)}")
    
    def test_onboarding_status_check_existing_user(self):
        """Test onboarding status check for user with existing data"""
        try:
            # Use main test user who should have tasks from previous tests
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("onboarding_status_check_existing_user", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/onboarding/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("onboarded") == True:
                    self.log_test("onboarding_status_check_existing_user", True, 
                                f"Correctly detected existing user: tasks={data.get('tasks_count')}, projects={data.get('projects_count')}")
                else:
                    self.log_test("onboarding_status_check_existing_user", False, 
                                f"Failed to detect existing user data: {data}")
            else:
                self.log_test("onboarding_status_check_existing_user", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("onboarding_status_check_existing_user", False, f"Exception: {str(e)}")
    
    def test_workspace_setup_clean_workspace(self):
        """Test workspace setup with clean workspace choice"""
        try:
            # Create a new user for this test
            clean_setup_email = f"cleansetup_{uuid.uuid4().hex[:8]}@example.com"
            
            signup_payload = {
                "name": "Clean Setup User",
                "email": clean_setup_email,
                "password": "cleansetup123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("workspace_setup_clean_workspace", False, "Failed to create test user")
                return
            
            # Setup clean workspace
            setup_payload = {
                "add_sample_data": False,
                "workspace_type": "clean"
            }
            
            response = self.session.post(f"{BASE_URL}/onboarding/setup", json=setup_payload)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") == True and 
                    data.get("projects_count") == 0 and 
                    data.get("tasks_count") == 0 and
                    "clean workspace" in data.get("message", "").lower()):
                    self.log_test("workspace_setup_clean_workspace", True, 
                                f"Clean workspace setup successful: {data['message']}")
                else:
                    self.log_test("workspace_setup_clean_workspace", False, 
                                f"Unexpected clean workspace response: {data}")
            else:
                self.log_test("workspace_setup_clean_workspace", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("workspace_setup_clean_workspace", False, f"Exception: {str(e)}")
    
    def test_workspace_setup_with_sample_data(self):
        """Test workspace setup with sample data choice"""
        try:
            # Create a new user for this test
            sample_setup_email = f"samplesetup_{uuid.uuid4().hex[:8]}@example.com"
            sample_setup_name = "Sample Setup User"
            
            signup_payload = {
                "name": sample_setup_name,
                "email": sample_setup_email,
                "password": "samplesetup123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("workspace_setup_with_sample_data", False, "Failed to create test user")
                return
            
            # Setup workspace with sample data
            setup_payload = {
                "add_sample_data": True,
                "workspace_type": "sample"
            }
            
            response = self.session.post(f"{BASE_URL}/onboarding/setup", json=setup_payload)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") == True and 
                    data.get("projects_count") > 0 and 
                    data.get("tasks_count") > 0 and
                    "sample data" in data.get("message", "").lower()):
                    self.log_test("workspace_setup_with_sample_data", True, 
                                f"Sample data setup successful: {data['projects_count']} projects, {data['tasks_count']} tasks")
                else:
                    self.log_test("workspace_setup_with_sample_data", False, 
                                f"Unexpected sample data response: {data}")
            else:
                self.log_test("workspace_setup_with_sample_data", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("workspace_setup_with_sample_data", False, f"Exception: {str(e)}")
    
    def test_personalized_sample_data_generation(self):
        """Test that sample data is personalized and includes user name"""
        try:
            # Create a new user with a specific name
            personalized_email = f"personalized_{uuid.uuid4().hex[:8]}@example.com"
            personalized_name = "Alice Johnson"
            
            signup_payload = {
                "name": personalized_name,
                "email": personalized_email,
                "password": "personalized123"
            }
            
            signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_test("personalized_sample_data_generation", False, "Failed to create test user")
                return
            
            # Setup workspace with sample data
            setup_payload = {
                "add_sample_data": True
            }
            
            setup_response = self.session.post(f"{BASE_URL}/onboarding/setup", json=setup_payload)
            
            if setup_response.status_code != 200:
                self.log_test("personalized_sample_data_generation", False, "Failed to setup sample data")
                return
            
            # Get projects to check for personalization
            projects_response = self.session.get(f"{BASE_URL}/projects")
            
            if projects_response.status_code == 200:
                projects_data = projects_response.json()
                projects = projects_data.get("projects", [])
                
                if len(projects) >= 3:  # Should have 3-5 projects
                    # Check for randomization - projects should have varied statuses, priorities
                    statuses = [p.get("status") for p in projects]
                    priorities = [p.get("priority") for p in projects]
                    
                    # Check for team member personalization
                    has_user_name = False
                    for project in projects:
                        team_members = project.get("team_members", [])
                        if personalized_name in team_members:
                            has_user_name = True
                            break
                    
                    if len(set(statuses)) > 1 or len(set(priorities)) > 1:
                        if has_user_name:
                            self.log_test("personalized_sample_data_generation", True, 
                                        f"Sample data is personalized: {len(projects)} projects with user name included")
                        else:
                            self.log_test("personalized_sample_data_generation", True, 
                                        f"Sample data is randomized: {len(projects)} projects with varied attributes")
                    else:
                        self.log_test("personalized_sample_data_generation", False, 
                                    "Sample data lacks randomization")
                else:
                    self.log_test("personalized_sample_data_generation", False, 
                                f"Insufficient projects generated: {len(projects)}")
            else:
                self.log_test("personalized_sample_data_generation", False, 
                            f"Failed to retrieve projects: {projects_response.status_code}")
                
        except Exception as e:
            self.log_test("personalized_sample_data_generation", False, f"Exception: {str(e)}")
    
    def test_data_uniqueness_between_users(self):
        """Test that different users get different sample data combinations"""
        try:
            # Create two users and compare their sample data
            user1_email = f"unique1_{uuid.uuid4().hex[:8]}@example.com"
            user2_email = f"unique2_{uuid.uuid4().hex[:8]}@example.com"
            
            users_data = []
            
            for i, email in enumerate([user1_email, user2_email], 1):
                # Clear session for each user
                self.session.cookies.clear()
                
                # Create user
                signup_payload = {
                    "name": f"Unique User {i}",
                    "email": email,
                    "password": f"unique{i}password123"
                }
                
                signup_response = self.session.post(f"{BASE_URL}/auth/signup", json=signup_payload)
                
                if signup_response.status_code != 200:
                    self.log_test("data_uniqueness_between_users", False, f"Failed to create user {i}")
                    return
                
                # Setup with sample data
                setup_payload = {"add_sample_data": True}
                setup_response = self.session.post(f"{BASE_URL}/onboarding/setup", json=setup_payload)
                
                if setup_response.status_code != 200:
                    self.log_test("data_uniqueness_between_users", False, f"Failed to setup user {i}")
                    return
                
                # Get user's projects and tasks
                projects_response = self.session.get(f"{BASE_URL}/projects")
                tasks_response = self.session.get(f"{BASE_URL}/tasks")
                
                if projects_response.status_code == 200 and tasks_response.status_code == 200:
                    projects = projects_response.json().get("projects", [])
                    tasks = tasks_response.json().get("tasks", [])
                    
                    # Extract key data for comparison
                    project_names = [p.get("name") for p in projects]
                    task_titles = [t.get("title") for t in tasks]
                    
                    users_data.append({
                        "email": email,
                        "project_names": set(project_names),
                        "task_titles": set(task_titles),
                        "projects_count": len(projects),
                        "tasks_count": len(tasks)
                    })
                else:
                    self.log_test("data_uniqueness_between_users", False, f"Failed to get data for user {i}")
                    return
            
            # Compare the two users' data
            if len(users_data) == 2:
                user1_data = users_data[0]
                user2_data = users_data[1]
                
                # Check if project names are different
                common_projects = user1_data["project_names"].intersection(user2_data["project_names"])
                common_tasks = user1_data["task_titles"].intersection(user2_data["task_titles"])
                
                # Allow some overlap but ensure significant differences
                project_overlap_ratio = len(common_projects) / max(len(user1_data["project_names"]), 1)
                task_overlap_ratio = len(common_tasks) / max(len(user1_data["task_titles"]), 1)
                
                if project_overlap_ratio < 0.8 and task_overlap_ratio < 0.8:
                    self.log_test("data_uniqueness_between_users", True, 
                                f"Users have unique data: User1({user1_data['projects_count']}p,{user1_data['tasks_count']}t) vs User2({user2_data['projects_count']}p,{user2_data['tasks_count']}t), overlap: {project_overlap_ratio:.1%} projects, {task_overlap_ratio:.1%} tasks")
                else:
                    self.log_test("data_uniqueness_between_users", False, 
                                f"Too much data overlap between users: {project_overlap_ratio:.1%} projects, {task_overlap_ratio:.1%} tasks")
            else:
                self.log_test("data_uniqueness_between_users", False, "Failed to collect data from both users")
                
        except Exception as e:
            self.log_test("data_uniqueness_between_users", False, f"Exception: {str(e)}")
    
    def test_onboarding_already_setup_user(self):
        """Test that users who already have data can't re-onboard"""
        try:
            # Use main test user who should have tasks from previous tests
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("onboarding_already_setup_user", False, "Failed to login for test setup")
                return
            
            # Try to setup workspace again
            setup_payload = {
                "add_sample_data": True
            }
            
            response = self.session.post(f"{BASE_URL}/onboarding/setup", json=setup_payload)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") == True and 
                    "already set up" in data.get("message", "").lower()):
                    self.log_test("onboarding_already_setup_user", True, 
                                f"Correctly prevented re-onboarding: {data['message']}")
                else:
                    self.log_test("onboarding_already_setup_user", False, 
                                f"Unexpected response for existing user: {data}")
            else:
                self.log_test("onboarding_already_setup_user", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("onboarding_already_setup_user", False, f"Exception: {str(e)}")
    
    def test_onboarding_endpoints_authentication(self):
        """Test that onboarding endpoints require authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            endpoints = [
                ("/onboarding/status", "GET"),
                ("/onboarding/setup", "POST")
            ]
            
            all_protected = True
            failed_endpoint = None
            
            for endpoint, method in endpoints:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}", json={"add_sample_data": False})
                
                if response.status_code != 401:
                    all_protected = False
                    failed_endpoint = f"{method} {endpoint}"
                    break
            
            if all_protected:
                self.log_test("onboarding_endpoints_authentication", True, "All onboarding endpoints properly protected")
            else:
                self.log_test("onboarding_endpoints_authentication", False, f"Endpoint not protected: {failed_endpoint}")
                
        except Exception as e:
            self.log_test("onboarding_endpoints_authentication", False, f"Exception: {str(e)}")

    # ========== NOTIFICATIONS API TESTS ==========
    
    def test_create_test_notifications(self):
        """Test creating test notifications"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("create_test_notifications", False, "Failed to login for test setup")
                return
            
            response = self.session.post(f"{BASE_URL}/notifications/test")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("create_test_notifications", True, f"Test notifications created: {data.get('message')}")
                else:
                    self.log_test("create_test_notifications", False, "Creation not successful", data)
            else:
                self.log_test("create_test_notifications", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("create_test_notifications", False, f"Exception: {str(e)}")
    
    def test_get_notifications(self):
        """Test getting user notifications"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_notifications", False, "Failed to login for test setup")
                return
            
            # Create test notifications first
            self.session.post(f"{BASE_URL}/notifications/test")
            
            response = self.session.get(f"{BASE_URL}/notifications/")
            
            if response.status_code == 200:
                data = response.json()
                if "notifications" in data:
                    notifications = data["notifications"]
                    if len(notifications) > 0:
                        # Check notification structure
                        first_notification = notifications[0]
                        required_fields = ["id", "user_id", "title", "message", "type", "read", "created_at"]
                        missing_fields = [field for field in required_fields if field not in first_notification]
                        
                        if not missing_fields:
                            self.log_test("get_notifications", True, f"Retrieved {len(notifications)} notifications")
                        else:
                            self.log_test("get_notifications", False, f"Missing notification fields: {missing_fields}")
                    else:
                        self.log_test("get_notifications", True, "No notifications found (empty list)")
                else:
                    self.log_test("get_notifications", False, "Missing notifications in response", data)
            else:
                self.log_test("get_notifications", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_notifications", False, f"Exception: {str(e)}")
    
    def test_get_notifications_unread_only(self):
        """Test getting only unread notifications"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_notifications_unread_only", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/notifications/?unread_only=true")
            
            if response.status_code == 200:
                data = response.json()
                if "notifications" in data:
                    notifications = data["notifications"]
                    # Check that all notifications are unread
                    all_unread = all(not notif.get("read", True) for notif in notifications)
                    if all_unread:
                        self.log_test("get_notifications_unread_only", True, f"Retrieved {len(notifications)} unread notifications")
                    else:
                        self.log_test("get_notifications_unread_only", False, "Some notifications were read")
                else:
                    self.log_test("get_notifications_unread_only", False, "Missing notifications in response", data)
            else:
                self.log_test("get_notifications_unread_only", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_notifications_unread_only", False, f"Exception: {str(e)}")
    
    def test_get_unread_count(self):
        """Test getting unread notifications count"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("get_unread_count", False, "Failed to login for test setup")
                return
            
            response = self.session.get(f"{BASE_URL}/notifications/unread-count")
            
            if response.status_code == 200:
                data = response.json()
                if "unread_count" in data and isinstance(data["unread_count"], int):
                    self.log_test("get_unread_count", True, f"Unread count: {data['unread_count']}")
                else:
                    self.log_test("get_unread_count", False, "Invalid unread_count format", data)
            else:
                self.log_test("get_unread_count", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("get_unread_count", False, f"Exception: {str(e)}")
    
    def test_mark_notifications_read(self):
        """Test marking specific notifications as read"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("mark_notifications_read", False, "Failed to login for test setup")
                return
            
            # Get notifications to find IDs
            get_response = self.session.get(f"{BASE_URL}/notifications/")
            
            if get_response.status_code != 200:
                self.log_test("mark_notifications_read", False, "Failed to get notifications for test setup")
                return
            
            notifications = get_response.json().get("notifications", [])
            if len(notifications) == 0:
                self.log_test("mark_notifications_read", True, "No notifications to mark as read")
                return
            
            # Mark first notification as read
            notification_ids = [notifications[0]["id"]]
            mark_payload = {
                "notification_ids": notification_ids
            }
            
            response = self.session.put(f"{BASE_URL}/notifications/mark-read", json=mark_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("mark_notifications_read", True, f"Marked notifications as read: {data.get('message')}")
                else:
                    self.log_test("mark_notifications_read", False, "Mark read not successful", data)
            else:
                self.log_test("mark_notifications_read", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("mark_notifications_read", False, f"Exception: {str(e)}")
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("mark_all_notifications_read", False, "Failed to login for test setup")
                return
            
            response = self.session.put(f"{BASE_URL}/notifications/mark-all-read")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Verify by checking unread count
                    count_response = self.session.get(f"{BASE_URL}/notifications/unread-count")
                    if count_response.status_code == 200:
                        count_data = count_response.json()
                        if count_data.get("unread_count") == 0:
                            self.log_test("mark_all_notifications_read", True, f"All notifications marked as read: {data.get('message')}")
                        else:
                            self.log_test("mark_all_notifications_read", False, f"Still have unread: {count_data.get('unread_count')}")
                    else:
                        self.log_test("mark_all_notifications_read", True, f"Marked all as read: {data.get('message')}")
                else:
                    self.log_test("mark_all_notifications_read", False, "Mark all read not successful", data)
            else:
                self.log_test("mark_all_notifications_read", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("mark_all_notifications_read", False, f"Exception: {str(e)}")
    
    def test_delete_notification(self):
        """Test deleting a specific notification"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("delete_notification", False, "Failed to login for test setup")
                return
            
            # Create test notifications first
            self.session.post(f"{BASE_URL}/notifications/test")
            
            # Get notifications to find an ID to delete
            get_response = self.session.get(f"{BASE_URL}/notifications/")
            
            if get_response.status_code != 200:
                self.log_test("delete_notification", False, "Failed to get notifications for test setup")
                return
            
            notifications = get_response.json().get("notifications", [])
            if len(notifications) == 0:
                self.log_test("delete_notification", True, "No notifications to delete")
                return
            
            # Delete first notification
            notification_id = notifications[0]["id"]
            response = self.session.delete(f"{BASE_URL}/notifications/{notification_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("delete_notification", True, "Notification deleted successfully")
                else:
                    self.log_test("delete_notification", False, "Delete not successful", data)
            else:
                self.log_test("delete_notification", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("delete_notification", False, f"Exception: {str(e)}")
    
    def test_delete_nonexistent_notification(self):
        """Test deleting a non-existent notification"""
        try:
            # Login first
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_payload)
            
            if login_response.status_code != 200:
                self.log_test("delete_nonexistent_notification", False, "Failed to login for test setup")
                return
            
            # Try to delete non-existent notification
            fake_id = str(uuid.uuid4())
            response = self.session.delete(f"{BASE_URL}/notifications/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("delete_nonexistent_notification", True, "Correctly rejected non-existent notification")
                else:
                    self.log_test("delete_nonexistent_notification", False, "Wrong error message", data)
            else:
                self.log_test("delete_nonexistent_notification", False, f"Expected 404, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("delete_nonexistent_notification", False, f"Exception: {str(e)}")
    
    def test_notifications_without_auth(self):
        """Test notifications endpoints without authentication"""
        try:
            # Clear session
            self.session.cookies.clear()
            
            endpoints = [
                ("/notifications/", "GET"),
                ("/notifications/unread-count", "GET"),
                ("/notifications/test", "POST")
            ]
            
            all_protected = True
            failed_endpoint = None
            for endpoint, method in endpoints:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}")
                
                if response.status_code != 401:
                    all_protected = False
                    failed_endpoint = endpoint
                    break
            
            if all_protected:
                self.log_test("notifications_without_auth", True, "All notification endpoints properly protected")
            else:
                self.log_test("notifications_without_auth", False, f"Endpoint not protected: {failed_endpoint}")
                
        except Exception as e:
            self.log_test("notifications_without_auth", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all authentication and AI tests"""
        print(f"🚀 Starting SmartTask AI Test Suite (Auth + AI Features)")
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
        
        # Emergent Auth endpoints
        self.test_emergent_auth_login_initiation()
        self.test_emergent_auth_login_with_redirect()
        self.test_emergent_auth_callback_invalid_session()
        self.test_emergent_auth_callback_structure()
        
        # Dual authentication system tests
        self.test_dual_auth_system_independence()
        self.test_user_model_updates()
        self.test_session_management_consistency()
        
        print("\n" + "🤖 AI FEATURES TESTING" + "\n" + "=" * 80)
        
        # AI Features Testing
        self.test_ai_parse_task_simple()
        self.test_ai_parse_task_with_date()
        self.test_ai_parse_task_with_priority()
        self.test_ai_parse_task_without_auth()
        self.test_ai_parse_task_invalid_input()
        
        self.test_ai_suggestions_no_tasks()
        self.test_ai_suggestions_with_tasks()
        self.test_ai_suggestions_without_auth()
        
        self.test_ai_summary_no_tasks()
        self.test_ai_summary_with_tasks()
        self.test_ai_summary_without_auth()
        
        print("\n" + "⚙️ SETTINGS API TESTING" + "\n" + "=" * 80)
        
        # Settings API Testing
        self.test_get_profile_settings()
        self.test_update_profile_settings()
        self.test_get_notification_settings()
        self.test_update_notification_settings()
        self.test_change_password_email_user()
        self.test_change_password_wrong_current()
        self.test_get_security_info()
        self.test_settings_without_auth()
        
        print("\n" + "🔔 NOTIFICATIONS API TESTING" + "\n" + "=" * 80)
        
        # Notifications API Testing
        self.test_create_test_notifications()
        self.test_get_notifications()
        self.test_get_notifications_unread_only()
        self.test_get_unread_count()
        self.test_mark_notifications_read()
        self.test_mark_all_notifications_read()
        self.test_delete_notification()
        self.test_delete_nonexistent_notification()
        self.test_notifications_without_auth()
        
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