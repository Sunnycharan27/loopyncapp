#!/usr/bin/env python3
"""
Real User Complete Flow Test - Password Whitespace Fix Verification
Tests the specific scenario requested: signup and login with whitespace handling
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://tribe-messenger.preview.emergentagent.com/api"

class RealUserWhitespaceTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.real_user_token = None
        self.real_user_id = None
        
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
    
    def test_real_user_signup(self):
        """Test 1: Signup with Real User Data"""
        try:
            payload = {
                "email": "realuser@gmail.com",
                "password": "MyRealPass123!",
                "name": "Real User Test",
                "handle": "realuser2024"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.real_user_token = data['token']
                    self.real_user_id = data['user']['id']
                    user = data['user']
                    
                    self.log_result(
                        "Real User Signup", 
                        True, 
                        f"Successfully created user {user['name']} ({user['email']})",
                        f"Token received, User ID: {user['id']}, Handle: {user['handle']}"
                    )
                else:
                    self.log_result(
                        "Real User Signup", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # User might already exist, try to get existing user info
                data = response.json()
                if "already" in data.get('detail', '').lower():
                    self.log_result(
                        "Real User Signup", 
                        True, 
                        "User already exists (acceptable for testing)",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Real User Signup", 
                        False, 
                        f"Signup failed with validation error",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Real User Signup", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Real User Signup", False, f"Exception occurred: {str(e)}")
    
    def test_login_exact_password(self):
        """Test 2: Login with Exact Password (No Whitespace)"""
        try:
            payload = {
                "email": "realuser@gmail.com",
                "password": "MyRealPass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.real_user_token = data['token']
                    self.real_user_id = data['user']['id']
                    user = data['user']
                    
                    self.log_result(
                        "Login Exact Password", 
                        True, 
                        f"Successfully logged in with exact password",
                        f"User: {user['name']}, Token received"
                    )
                else:
                    self.log_result(
                        "Login Exact Password", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Exact Password", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Exact Password", False, f"Exception occurred: {str(e)}")
    
    def test_login_leading_whitespace(self):
        """Test 3: Login with Leading Whitespace (THE CRITICAL FIX)"""
        try:
            payload = {
                "email": "realuser@gmail.com",
                "password": " MyRealPass123!"  # Leading space
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_result(
                        "Login Leading Whitespace", 
                        True, 
                        "✅ CRITICAL FIX WORKING: Login successful with leading space in password",
                        f"Password whitespace stripping is working correctly"
                    )
                else:
                    self.log_result(
                        "Login Leading Whitespace", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Leading Whitespace", 
                    False, 
                    "❌ CRITICAL FIX FAILED: Login failed with leading space in password",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Leading Whitespace", False, f"Exception occurred: {str(e)}")
    
    def test_login_trailing_whitespace(self):
        """Test 4: Login with Trailing Whitespace (THE CRITICAL FIX)"""
        try:
            payload = {
                "email": "realuser@gmail.com",
                "password": "MyRealPass123! "  # Trailing space
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_result(
                        "Login Trailing Whitespace", 
                        True, 
                        "✅ CRITICAL FIX WORKING: Login successful with trailing space in password",
                        f"Password whitespace stripping is working correctly"
                    )
                else:
                    self.log_result(
                        "Login Trailing Whitespace", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Trailing Whitespace", 
                    False, 
                    "❌ CRITICAL FIX FAILED: Login failed with trailing space in password",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Trailing Whitespace", False, f"Exception occurred: {str(e)}")
    
    def test_login_both_whitespace(self):
        """Test 5: Login with Both Leading and Trailing Whitespace"""
        try:
            payload = {
                "email": "realuser@gmail.com",
                "password": " MyRealPass123! "  # Both leading and trailing spaces
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_result(
                        "Login Both Whitespace", 
                        True, 
                        "✅ CRITICAL FIX WORKING: Login successful with both leading and trailing spaces",
                        f"Password whitespace stripping is working correctly"
                    )
                else:
                    self.log_result(
                        "Login Both Whitespace", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Both Whitespace", 
                    False, 
                    "❌ CRITICAL FIX FAILED: Login failed with both leading and trailing spaces",
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Both Whitespace", False, f"Exception occurred: {str(e)}")
    
    def test_user_create_content(self):
        """Test 6: User Can Create Content (Post)"""
        if not self.real_user_token or not self.real_user_id:
            self.log_result("User Create Content", False, "Skipped - no user token/ID available")
            return
            
        try:
            payload = {
                "text": "This is a test post from the real user testing flow!",
                "audience": "public"
            }
            params = {"authorId": self.real_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/posts", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'text' in data and 'authorId' in data:
                    self.log_result(
                        "User Create Content", 
                        True, 
                        f"Successfully created post: {data['id']}",
                        f"Text: {data['text'][:50]}..., Author: {data['authorId']}"
                    )
                else:
                    self.log_result(
                        "User Create Content", 
                        False, 
                        "Create post response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "User Create Content", 
                    False, 
                    f"Create post failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("User Create Content", False, f"Exception occurred: {str(e)}")
    
    def test_user_add_friends(self):
        """Test 7: User Can Add Friends (Send Friend Request to u1)"""
        if not self.real_user_id:
            self.log_result("User Add Friends", False, "Skipped - no user ID available")
            return
            
        try:
            params = {
                'fromUserId': self.real_user_id,
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result(
                        "User Add Friends", 
                        True, 
                        f"Successfully sent friend request to u1",
                        f"Response: {data}"
                    )
                elif 'message' in data and 'already' in data['message'].lower():
                    self.log_result(
                        "User Add Friends", 
                        True, 
                        f"Friend request already exists or users are already friends",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "User Add Friends", 
                        False, 
                        "Friend request response unexpected format",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "User Add Friends", 
                    False, 
                    f"Send friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("User Add Friends", False, f"Exception occurred: {str(e)}")
    
    def test_user_profile_access(self):
        """Test 8: User Profile Accessible"""
        if not self.real_user_id:
            self.log_result("User Profile Access", False, "Skipped - no user ID available")
            return
            
        try:
            # Try both by handle and by ID
            response_by_id = self.session.get(f"{BACKEND_URL}/users/{self.real_user_id}")
            
            if response_by_id.status_code == 200:
                data = response_by_id.json()
                if 'id' in data and 'name' in data and 'email' in data:
                    self.log_result(
                        "User Profile Access", 
                        True, 
                        f"Successfully retrieved user profile by ID",
                        f"User: {data['name']} ({data['email']}), Handle: {data.get('handle', 'N/A')}"
                    )
                else:
                    self.log_result(
                        "User Profile Access", 
                        False, 
                        "User profile response missing required fields",
                        f"Response: {data}"
                    )
            else:
                # Try by handle
                try:
                    response_by_handle = self.session.get(f"{BACKEND_URL}/users/realuser2024")
                    if response_by_handle.status_code == 200:
                        data = response_by_handle.json()
                        self.log_result(
                            "User Profile Access", 
                            True, 
                            f"Successfully retrieved user profile by handle",
                            f"User: {data.get('name', 'Unknown')}"
                        )
                    else:
                        self.log_result(
                            "User Profile Access", 
                            False, 
                            f"User profile access failed - ID: {response_by_id.status_code}, Handle: {response_by_handle.status_code}",
                            f"ID Response: {response_by_id.text}, Handle Response: {response_by_handle.text}"
                        )
                except:
                    self.log_result(
                        "User Profile Access", 
                        False, 
                        f"User profile access failed with status {response_by_id.status_code}",
                        f"Response: {response_by_id.text}"
                    )
                
        except Exception as e:
            self.log_result("User Profile Access", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Real User Complete Flow Test - Password Whitespace Fix Verification")
        print("=" * 80)
        
        # Test sequence
        self.test_real_user_signup()
        self.test_login_exact_password()
        self.test_login_leading_whitespace()  # CRITICAL TEST
        self.test_login_trailing_whitespace()  # CRITICAL TEST
        self.test_login_both_whitespace()
        self.test_user_create_content()
        self.test_user_add_friends()
        self.test_user_profile_access()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Critical whitespace tests summary
        whitespace_tests = [r for r in self.test_results if 'whitespace' in r['test'].lower()]
        whitespace_passed = sum(1 for r in whitespace_tests if r['success'])
        
        print(f"\n🔑 CRITICAL WHITESPACE FIX TESTS:")
        print(f"Whitespace Tests: {len(whitespace_tests)}")
        print(f"Whitespace Passed: {whitespace_passed}")
        
        if whitespace_passed == len(whitespace_tests) and len(whitespace_tests) > 0:
            print("✅ PASSWORD WHITESPACE FIX IS WORKING CORRECTLY!")
        else:
            print("❌ PASSWORD WHITESPACE FIX NEEDS ATTENTION!")
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = RealUserWhitespaceTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)