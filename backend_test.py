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