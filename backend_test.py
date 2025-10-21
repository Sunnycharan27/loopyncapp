#!/usr/bin/env python3
"""
Backend API Testing Suite
Tests authentication, uploads, friend requests, DM threads, and search functionality for the Loopync app.
"""

import requests
import json
import uuid
import io
from datetime import datetime
from PIL import Image

# Configuration
BACKEND_URL = "https://vibehub-5.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.new_user_token = None
        self.new_user_email = None
        self.uploaded_file_url = None
        self.friend_request_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_demo_login(self):
        """Test 1: Demo Login with demo@loopync.com"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.demo_token = data['token']
                    user = data['user']
                    
                    # Validate user data
                    if (user.get('email') == DEMO_EMAIL and 
                        user.get('name') and 
                        user.get('id')):
                        self.log_result(
                            "Demo Login", 
                            True, 
                            f"Successfully logged in as {user['name']} ({user['email']})",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "Demo Login", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Demo Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo Login", False, f"Exception occurred: {str(e)}")
    
    def test_new_user_signup(self):
        """Test 2: New User Signup"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.new_user_email = f"testuser_{timestamp}@example.com"
            
            payload = {
                "email": self.new_user_email,
                "handle": f"testuser_{timestamp}",
                "name": f"Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.new_user_token = data['token']
                    user = data['user']
                    
                    # Validate user data
                    if (user.get('email') == self.new_user_email and 
                        user.get('name') == payload['name'] and 
                        user.get('id')):
                        self.log_result(
                            "New User Signup", 
                            True, 
                            f"Successfully created user {user['name']} ({user['email']})",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "New User Signup", 
                            False, 
                            "Signup successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Signup", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "New User Signup", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("New User Signup", False, f"Exception occurred: {str(e)}")
    
    def test_new_user_login(self):
        """Test 3: Login with newly created user"""
        if not self.new_user_email:
            self.log_result("New User Login", False, "Skipped - no new user email available")
            return
            
        try:
            payload = {
                "email": self.new_user_email,
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    token = data['token']
                    user = data['user']
                    
                    # Validate user data
                    if (user.get('email') == self.new_user_email and 
                        user.get('name') and 
                        user.get('id')):
                        self.log_result(
                            "New User Login", 
                            True, 
                            f"Successfully logged in new user {user['name']}",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "New User Login", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "New User Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("New User Login", False, f"Exception occurred: {str(e)}")
    
    def test_jwt_token_validation(self):
        """Test 4: JWT Token Validation via /auth/me endpoint"""
        if not self.demo_token:
            self.log_result("JWT Token Validation", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'email' in data:
                    self.log_result(
                        "JWT Token Validation", 
                        True, 
                        f"Token validated successfully for user {data.get('name', 'Unknown')}",
                        f"User data: {data}"
                    )
                else:
                    self.log_result(
                        "JWT Token Validation", 
                        False, 
                        "Token validated but user data incomplete",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "JWT Token Validation", 
                    False, 
                    f"Token validation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Exception occurred: {str(e)}")
    
    def test_protected_route_access(self):
        """Test 5: Protected Route Access with valid token"""
        if not self.demo_token:
            self.log_result("Protected Route Access", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Protected Route Access", 
                    True, 
                    "Successfully accessed protected route with valid token",
                    f"User: {data.get('name', 'Unknown')} ({data.get('email', 'Unknown')})"
                )
            else:
                self.log_result(
                    "Protected Route Access", 
                    False, 
                    f"Protected route access failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Protected Route Access", False, f"Exception occurred: {str(e)}")
    
    def test_invalid_credentials(self):
        """Test 6: Invalid Credentials Test"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Credentials", 
                    True, 
                    "Correctly rejected invalid credentials with 401 status",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Invalid Credentials", 
                    False, 
                    "Security issue: Invalid credentials were accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Invalid Credentials", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid credentials",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Invalid Credentials", False, f"Exception occurred: {str(e)}")
    
    def test_duplicate_email_signup(self):
        """Test 7: Duplicate Email Signup Test"""
        try:
            payload = {
                "email": DEMO_EMAIL,  # Using existing demo email
                "handle": "duplicate_test",
                "name": "Duplicate Test User",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "already" in data.get('detail', '').lower():
                    self.log_result(
                        "Duplicate Email Signup", 
                        True, 
                        "Correctly rejected duplicate email with 400 status",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Duplicate Email Signup", 
                        False, 
                        "Got 400 status but error message unclear",
                        f"Response: {data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Duplicate Email Signup", 
                    False, 
                    "Security issue: Duplicate email was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Duplicate Email Signup", 
                    False, 
                    f"Unexpected status code {response.status_code} for duplicate email",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Duplicate Email Signup", False, f"Exception occurred: {str(e)}")
    
    def test_invalid_token_access(self):
        """Test 8: Invalid Token Access Test"""
        try:
            headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Token Access", 
                    True, 
                    "Correctly rejected invalid token with 401 status",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Invalid Token Access", 
                    False, 
                    "Security issue: Invalid token was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Invalid Token Access", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid token",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Invalid Token Access", False, f"Exception occurred: {str(e)}")
    
    def test_no_token_access(self):
        """Test 9: No Token Access Test"""
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result(
                    "No Token Access", 
                    True, 
                    f"Correctly rejected request without token (status {response.status_code})",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "No Token Access", 
                    False, 
                    "Security issue: Request without token was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "No Token Access", 
                    False, 
                    f"Unexpected status code {response.status_code} for no token",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("No Token Access", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("=" * 60)
        print("BACKEND AUTHENTICATION TESTING SUITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("=" * 60)
        
        # Run tests in order
        self.test_demo_login()
        self.test_new_user_signup()
        self.test_new_user_login()
        self.test_jwt_token_validation()
        self.test_protected_route_access()
        self.test_invalid_credentials()
        self.test_duplicate_email_signup()
        self.test_invalid_token_access()
        self.test_no_token_access()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        return passed == total

def main():
    """Main test runner"""
    tester = AuthTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All authentication tests passed!")
        return 0
    else:
        print("⚠️  Some authentication tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())