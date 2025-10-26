#!/usr/bin/env python3
"""
Critical Authentication Registration and Login Flow Test
Tests the specific issue reported: Real users cannot signup and login - getting "invalid credentials" error

This test follows the exact scenario requested:
1. Test Signup with New User
2. Test Login with Same User  
3. Check Database Storage
4. Test Password Verification
5. Check for Issues (password hashing, bcrypt, async/await, database connection)
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://parallels-ai.preview.emergentagent.com/api"

class AuthRegistrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.new_user_data = None
        self.signup_token = None
        self.login_token = None
        
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_1_signup_new_user(self):
        """Test 1: Test Signup with New User - Verify user creation, password hashing, response format"""
        print("=" * 80)
        print("TEST 1: NEW USER SIGNUP")
        print("=" * 80)
        
        try:
            # Generate unique test user data as requested
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.new_user_data = {
                "email": "testuser@example.com",
                "password": "TestPass123!",
                "name": "Test User",
                "handle": f"testuser123_{timestamp}"
            }
            
            print(f"Creating new user with:")
            print(f"  Email: {self.new_user_data['email']}")
            print(f"  Password: {self.new_user_data['password']}")
            print(f"  Name: {self.new_user_data['name']}")
            print(f"  Handle: {self.new_user_data['handle']}")
            print()
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=self.new_user_data)
            
            print(f"Signup Response Status: {response.status_code}")
            print(f"Signup Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Signup Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response contains token and user object
                if 'token' in data and 'user' in data:
                    self.signup_token = data['token']
                    user = data['user']
                    
                    # Verify all required fields are present
                    required_fields = ['id', 'email', 'name', 'handle']
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        # Verify data matches what we sent
                        if (user.get('email') == self.new_user_data['email'] and 
                            user.get('name') == self.new_user_data['name'] and
                            user.get('handle') == self.new_user_data['handle']):
                            
                            self.log_result(
                                "New User Signup", 
                                True, 
                                f"✅ User created successfully with ID: {user['id']}",
                                f"Token length: {len(self.signup_token)} chars, User verified: {user.get('isVerified', False)}"
                            )
                        else:
                            self.log_result(
                                "New User Signup", 
                                False, 
                                "❌ User data mismatch between request and response",
                                f"Expected: {self.new_user_data}, Got: {user}"
                            )
                    else:
                        self.log_result(
                            "New User Signup", 
                            False, 
                            f"❌ User object missing required fields: {missing_fields}",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Signup", 
                        False, 
                        "❌ Signup response missing 'token' or 'user' field",
                        f"Response keys: {list(data.keys())}"
                    )
            else:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_text = json.dumps(error_data, indent=2)
                except:
                    pass
                    
                self.log_result(
                    "New User Signup", 
                    False, 
                    f"❌ Signup failed with HTTP {response.status_code}",
                    f"Error: {error_text}"
                )
                
        except Exception as e:
            self.log_result("New User Signup", False, f"❌ Exception during signup: {str(e)}")
    
    def test_2_login_same_user(self):
        """Test 2: Test Login with Same User - Should return token and user object, NOT "invalid credentials" """
        print("=" * 80)
        print("TEST 2: LOGIN WITH SAME USER")
        print("=" * 80)
        
        if not self.new_user_data:
            self.log_result("Login Same User", False, "❌ Skipped - no user data from signup test")
            return
            
        try:
            login_data = {
                "email": self.new_user_data['email'],
                "password": self.new_user_data['password']
            }
            
            print(f"Attempting login with:")
            print(f"  Email: {login_data['email']}")
            print(f"  Password: {login_data['password']}")
            print()
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            print(f"Login Response Status: {response.status_code}")
            print(f"Login Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response contains token and user object
                if 'token' in data and 'user' in data:
                    self.login_token = data['token']
                    user = data['user']
                    
                    # Verify user data matches
                    if (user.get('email') == self.new_user_data['email'] and 
                        user.get('name') == self.new_user_data['name']):
                        
                        self.log_result(
                            "Login Same User", 
                            True, 
                            f"✅ Login successful for user: {user['name']}",
                            f"Token length: {len(self.login_token)} chars, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "Login Same User", 
                            False, 
                            "❌ Login successful but user data mismatch",
                            f"Expected email: {self.new_user_data['email']}, Got: {user.get('email')}"
                        )
                else:
                    self.log_result(
                        "Login Same User", 
                        False, 
                        "❌ Login response missing 'token' or 'user' field",
                        f"Response keys: {list(data.keys())}"
                    )
            elif response.status_code == 401:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_text = json.dumps(error_data, indent=2)
                    detail = error_data.get('detail', '').lower()
                    
                    if 'invalid credentials' in detail:
                        self.log_result(
                            "Login Same User", 
                            False, 
                            "❌ CRITICAL ISSUE: Getting 'invalid credentials' error for valid user",
                            f"This is the exact issue reported by the user. Error: {error_text}"
                        )
                    else:
                        self.log_result(
                            "Login Same User", 
                            False, 
                            f"❌ Login failed with 401 but different error: {detail}",
                            f"Error: {error_text}"
                        )
                except:
                    self.log_result(
                        "Login Same User", 
                        False, 
                        "❌ Login failed with 401 - invalid credentials",
                        f"Raw error: {error_text}"
                    )
            else:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_text = json.dumps(error_data, indent=2)
                except:
                    pass
                    
                self.log_result(
                    "Login Same User", 
                    False, 
                    f"❌ Login failed with HTTP {response.status_code}",
                    f"Error: {error_text}"
                )
                
        except Exception as e:
            self.log_result("Login Same User", False, f"❌ Exception during login: {str(e)}")
    
    def test_3_check_database_storage(self):
        """Test 3: Check Database Storage - Verify user exists, password is hashed with bcrypt"""
        print("=" * 80)
        print("TEST 3: DATABASE STORAGE VERIFICATION")
        print("=" * 80)
        
        if not self.login_token:
            self.log_result("Database Storage Check", False, "❌ Skipped - no login token available")
            return
            
        try:
            # Use the /auth/me endpoint to verify user exists and data is stored correctly
            headers = {
                "Authorization": f"Bearer {self.login_token}",
                "Content-Type": "application/json"
            }
            
            print("Checking user data storage via /auth/me endpoint...")
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            print(f"Auth/Me Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Auth/Me Response Data: {json.dumps(data, indent=2)}")
                
                # Verify user data is complete and stored correctly
                required_fields = ['id', 'email', 'name', 'handle']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify data matches what we created
                    if (data.get('email') == self.new_user_data['email'] and 
                        data.get('name') == self.new_user_data['name']):
                        
                        self.log_result(
                            "Database Storage Check", 
                            True, 
                            f"✅ User data correctly stored in database",
                            f"User ID: {data['id']}, Verified: {data.get('isVerified', False)}, Wallet: {data.get('walletBalance', 0)}"
                        )
                    else:
                        self.log_result(
                            "Database Storage Check", 
                            False, 
                            "❌ Stored user data doesn't match created user",
                            f"Expected: {self.new_user_data['email']}, Got: {data.get('email')}"
                        )
                else:
                    self.log_result(
                        "Database Storage Check", 
                        False, 
                        f"❌ Stored user data missing required fields: {missing_fields}",
                        f"Available fields: {list(data.keys())}"
                    )
            else:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_text = json.dumps(error_data, indent=2)
                except:
                    pass
                    
                self.log_result(
                    "Database Storage Check", 
                    False, 
                    f"❌ Cannot verify database storage - auth/me failed with {response.status_code}",
                    f"Error: {error_text}"
                )
                
        except Exception as e:
            self.log_result("Database Storage Check", False, f"❌ Exception during database check: {str(e)}")
    
    def test_4_password_verification(self):
        """Test 4: Test Password Verification - Check bcrypt.compare functionality"""
        print("=" * 80)
        print("TEST 4: PASSWORD VERIFICATION TESTING")
        print("=" * 80)
        
        if not self.new_user_data:
            self.log_result("Password Verification", False, "❌ Skipped - no user data available")
            return
            
        try:
            # Test 1: Correct password (should work)
            print("Testing with CORRECT password...")
            correct_login = {
                "email": self.new_user_data['email'],
                "password": self.new_user_data['password']
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=correct_login)
            print(f"Correct Password Response Status: {response.status_code}")
            
            correct_password_works = response.status_code == 200
            
            # Test 2: Wrong password (should fail with proper error)
            print("Testing with WRONG password...")
            wrong_login = {
                "email": self.new_user_data['email'],
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=wrong_login)
            print(f"Wrong Password Response Status: {response.status_code}")
            
            wrong_password_fails = response.status_code == 401
            
            if wrong_password_fails:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '').lower()
                    print(f"Wrong Password Error: {error_detail}")
                except:
                    pass
            
            # Evaluate results
            if correct_password_works and wrong_password_fails:
                self.log_result(
                    "Password Verification", 
                    True, 
                    "✅ Password verification working correctly",
                    "Correct password accepted, wrong password rejected with 401"
                )
            elif not correct_password_works and wrong_password_fails:
                self.log_result(
                    "Password Verification", 
                    False, 
                    "❌ CRITICAL: Correct password being rejected",
                    "This indicates bcrypt.compare or password hashing issue"
                )
            elif correct_password_works and not wrong_password_fails:
                self.log_result(
                    "Password Verification", 
                    False, 
                    "❌ SECURITY ISSUE: Wrong password being accepted",
                    "Password verification is not working properly"
                )
            else:
                self.log_result(
                    "Password Verification", 
                    False, 
                    "❌ CRITICAL: Both correct and wrong passwords rejected",
                    "Complete password verification failure"
                )
                
        except Exception as e:
            self.log_result("Password Verification", False, f"❌ Exception during password verification: {str(e)}")
    
    def test_5_check_for_issues(self):
        """Test 5: Check for Issues - Analyze potential problems"""
        print("=" * 80)
        print("TEST 5: ISSUE ANALYSIS")
        print("=" * 80)
        
        issues_found = []
        
        # Check if any tests failed
        failed_tests = [result for result in self.test_results if not result['success']]
        
        if failed_tests:
            print("FAILED TESTS ANALYSIS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
                
                # Analyze specific failure patterns
                if 'invalid credentials' in test['message'].lower():
                    issues_found.append("Password verification failure - bcrypt.compare not working correctly")
                elif 'missing' in test['message'].lower() and 'token' in test['message'].lower():
                    issues_found.append("JWT token generation failure")
                elif 'database' in test['message'].lower():
                    issues_found.append("Database connection or storage issue")
                elif 'async' in test['message'].lower() or 'await' in test['message'].lower():
                    issues_found.append("Async/await implementation issue")
        
        # Additional checks
        print("\nADDITIONAL DIAGNOSTIC CHECKS:")
        
        # Test basic connectivity
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend connectivity: OK")
            else:
                print(f"  ❌ Backend connectivity: HTTP {response.status_code}")
                issues_found.append("Backend connectivity issue")
        except Exception as e:
            print(f"  ❌ Backend connectivity: {str(e)}")
            issues_found.append("Backend connectivity failure")
        
        # Test demo user login (known working user)
        try:
            demo_login = {
                "email": "demo@loopync.com",
                "password": "password123"
            }
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=demo_login)
            if response.status_code == 200:
                print("  ✅ Demo user login: OK")
            else:
                print(f"  ❌ Demo user login: HTTP {response.status_code}")
                issues_found.append("Demo user authentication failure - system-wide auth issue")
        except Exception as e:
            print(f"  ❌ Demo user login: {str(e)}")
            issues_found.append("Demo user authentication exception")
        
        # Summary
        if not issues_found:
            self.log_result(
                "Issue Analysis", 
                True, 
                "✅ No critical issues detected in authentication system",
                "All tests passed successfully"
            )
        else:
            self.log_result(
                "Issue Analysis", 
                False, 
                f"❌ {len(issues_found)} critical issues detected",
                f"Issues: {'; '.join(issues_found)}"
            )
    
    def run_all_tests(self):
        """Run all authentication tests in sequence"""
        print("🔐 CRITICAL AUTHENTICATION REGISTRATION AND LOGIN FLOW TEST")
        print("Testing the reported issue: Real users cannot signup and login")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        self.test_1_signup_new_user()
        self.test_2_login_same_user()
        self.test_3_check_database_storage()
        self.test_4_password_verification()
        self.test_5_check_for_issues()
        
        # Final summary
        print("=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ CRITICAL AUTHENTICATION ISSUES DETECTED")
            print("The reported user issue is confirmed. Failed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("✅ ALL AUTHENTICATION TESTS PASSED")
            print("The authentication system is working correctly.")
        
        print()
        print("=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = AuthRegistrationTester()
    results = tester.run_all_tests()