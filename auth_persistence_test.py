#!/usr/bin/env python3
"""
Complete Authentication System Test - User Registration and Login Persistence
Tests the complete authentication flow as requested by the user to ensure:
1. When an account is created, it's stored permanently
2. Users can login anytime with their email and password
3. The authentication system works like Instagram (persistent accounts)
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"

class AuthPersistenceTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = None
        self.test_user_password = "testpass123"
        self.test_user_handle = None
        self.test_user_name = None
        self.test_user_id = None
        self.verification_code = None
        self.jwt_token = None
        
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
    
    def step_1_check_database_setup(self):
        """Step 1: Check Database Setup - Verify Google Sheets DB and MongoDB are working"""
        print("\n=== STEP 1: DATABASE SETUP VERIFICATION ===")
        
        # Test Google Sheets DB by trying demo login
        try:
            payload = {
                "email": "demo@loopync.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_result(
                        "Google Sheets DB Check", 
                        True, 
                        "Google Sheets database is accessible and working",
                        f"Demo user login successful: {data['user'].get('name', 'Unknown')}"
                    )
                else:
                    self.log_result(
                        "Google Sheets DB Check", 
                        False, 
                        "Google Sheets DB response incomplete",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Google Sheets DB Check", 
                    False, 
                    f"Google Sheets DB not accessible - status {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result("Google Sheets DB Check", False, f"Exception: {str(e)}")
        
        # Test MongoDB by checking if we can access user data
        try:
            # Try to get demo user data from MongoDB
            headers = {
                "Authorization": f"Bearer {data.get('token', '')}" if 'data' in locals() else None,
                "Content-Type": "application/json"
            }
            
            if headers["Authorization"]:
                response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.log_result(
                        "MongoDB Check", 
                        True, 
                        "MongoDB is accessible and working",
                        f"User data retrieved: {user_data.get('name', 'Unknown')}"
                    )
                else:
                    self.log_result(
                        "MongoDB Check", 
                        False, 
                        f"MongoDB not accessible - status {response.status_code}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "MongoDB Check", 
                    False, 
                    "Cannot test MongoDB - no valid token from Google Sheets test",
                    "Skipping MongoDB verification"
                )
        except Exception as e:
            self.log_result("MongoDB Check", False, f"Exception: {str(e)}")
    
    def step_2_create_new_user_account(self):
        """Step 2: Create New User Account with permanent storage"""
        print("\n=== STEP 2: CREATE NEW USER ACCOUNT ===")
        
        # Generate unique test user data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_user_email = f"testuser123_{timestamp}@example.com"
        self.test_user_handle = f"testuser123_{timestamp}"
        self.test_user_name = "Test User Permanent"
        
        try:
            payload = {
                "name": self.test_user_name,
                "handle": self.test_user_handle,
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response contains all required fields
                required_fields = ['token', 'user', 'needsVerification', 'verificationCode']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    user = data['user']
                    self.jwt_token = data['token']
                    self.test_user_id = user.get('id')
                    self.verification_code = data.get('verificationCode')
                    
                    # Verify user object structure
                    user_required = ['id', 'email', 'name', 'handle']
                    user_missing = [field for field in user_required if field not in user]
                    
                    if not user_missing:
                        self.log_result(
                            "Create New User Account", 
                            True, 
                            f"Successfully created permanent user account",
                            f"User: {user['name']} ({user['email']}), ID: {user['id']}, Token: {len(self.jwt_token)} chars, Verification: {data['needsVerification']}"
                        )
                    else:
                        self.log_result(
                            "Create New User Account", 
                            False, 
                            f"User object missing required fields: {user_missing}",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Create New User Account", 
                        False, 
                        f"Signup response missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create New User Account", 
                    False, 
                    f"User creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create New User Account", False, f"Exception: {str(e)}")
    
    def step_3_verify_email(self):
        """Step 3: Verify Email with verification code"""
        print("\n=== STEP 3: EMAIL VERIFICATION ===")
        
        if not self.verification_code or not self.test_user_email:
            self.log_result("Email Verification", False, "Skipped - no verification code or email available")
            return
        
        try:
            payload = {
                "email": self.test_user_email,
                "code": self.verification_code
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/verify-email", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Email Verification", 
                        True, 
                        "Email verification successful",
                        f"User {self.test_user_email} is now verified"
                    )
                else:
                    self.log_result(
                        "Email Verification", 
                        False, 
                        "Email verification response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Email Verification", 
                    False, 
                    f"Email verification failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Email Verification", False, f"Exception: {str(e)}")
    
    def step_4_logout_and_login_again(self):
        """Step 4: Logout and Login Again - Test persistence"""
        print("\n=== STEP 4: LOGOUT AND LOGIN AGAIN ===")
        
        if not self.test_user_email:
            self.log_result("Login After Creation", False, "Skipped - no test user email available")
            return
        
        # Clear current session (simulate logout)
        self.jwt_token = None
        
        try:
            payload = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'token' in data and 'user' in data:
                    user = data['user']
                    self.jwt_token = data['token']
                    
                    # Verify user data matches what we created
                    if (user.get('email') == self.test_user_email and 
                        user.get('name') == self.test_user_name and
                        user.get('id') == self.test_user_id):
                        
                        self.log_result(
                            "Login After Creation", 
                            True, 
                            "Successfully logged in with created credentials - account persisted!",
                            f"User: {user['name']} ({user['email']}), ID: {user['id']}, Token: {len(self.jwt_token)} chars"
                        )
                    else:
                        self.log_result(
                            "Login After Creation", 
                            False, 
                            "Login successful but user data doesn't match created account",
                            f"Expected: {self.test_user_name}/{self.test_user_email}/{self.test_user_id}, Got: {user.get('name')}/{user.get('email')}/{user.get('id')}"
                        )
                else:
                    self.log_result(
                        "Login After Creation", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login After Creation", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login After Creation", False, f"Exception: {str(e)}")
    
    def step_5_test_login_persistence(self):
        """Step 5: Test Login Persistence - Multiple logins"""
        print("\n=== STEP 5: TEST LOGIN PERSISTENCE ===")
        
        if not self.test_user_email:
            self.log_result("Login Persistence Test", False, "Skipped - no test user email available")
            return
        
        # Test multiple logins to ensure persistence
        login_attempts = 3
        successful_logins = 0
        
        for attempt in range(1, login_attempts + 1):
            try:
                payload = {
                    "email": self.test_user_email,
                    "password": self.test_user_password
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'token' in data and 'user' in data:
                        successful_logins += 1
                        print(f"   Login attempt {attempt}/3: ✅ SUCCESS")
                    else:
                        print(f"   Login attempt {attempt}/3: ❌ FAIL - Missing data")
                else:
                    print(f"   Login attempt {attempt}/3: ❌ FAIL - Status {response.status_code}")
                
                # Small delay between attempts
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   Login attempt {attempt}/3: ❌ FAIL - Exception: {str(e)}")
        
        if successful_logins == login_attempts:
            self.log_result(
                "Login Persistence Test", 
                True, 
                f"All {login_attempts} login attempts successful - account persistence verified!",
                f"User can login multiple times with same credentials"
            )
        else:
            self.log_result(
                "Login Persistence Test", 
                False, 
                f"Only {successful_logins}/{login_attempts} login attempts successful",
                "Account persistence may have issues"
            )
    
    def step_6_test_wrong_password(self):
        """Step 6: Test Wrong Password - Security verification"""
        print("\n=== STEP 6: TEST WRONG PASSWORD ===")
        
        if not self.test_user_email:
            self.log_result("Wrong Password Test", False, "Skipped - no test user email available")
            return
        
        try:
            payload = {
                "email": self.test_user_email,
                "password": "wrongpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_result(
                    "Wrong Password Test", 
                    True, 
                    "Correctly rejected wrong password with 401 status",
                    "Security working properly - invalid credentials rejected"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Wrong Password Test", 
                    False, 
                    "SECURITY ISSUE: Wrong password was accepted!",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Wrong Password Test", 
                    False, 
                    f"Unexpected status code {response.status_code} for wrong password",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Wrong Password Test", False, f"Exception: {str(e)}")
    
    def step_7_check_data_persistence(self):
        """Step 7: Check Data Persistence - Verify user data remains in databases"""
        print("\n=== STEP 7: CHECK DATA PERSISTENCE ===")
        
        if not self.jwt_token or not self.test_user_id:
            self.log_result("Data Persistence Check", False, "Skipped - no valid token or user ID available")
            return
        
        # Test 1: Get user from MongoDB via /auth/me
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                if (user_data.get('id') == self.test_user_id and 
                    user_data.get('email') == self.test_user_email):
                    
                    self.log_result(
                        "MongoDB Data Persistence", 
                        True, 
                        "User data persisted correctly in MongoDB",
                        f"Retrieved: {user_data.get('name')} ({user_data.get('email')})"
                    )
                else:
                    self.log_result(
                        "MongoDB Data Persistence", 
                        False, 
                        "User data in MongoDB doesn't match created account",
                        f"Expected: {self.test_user_id}/{self.test_user_email}, Got: {user_data.get('id')}/{user_data.get('email')}"
                    )
            else:
                self.log_result(
                    "MongoDB Data Persistence", 
                    False, 
                    f"Failed to retrieve user data from MongoDB - status {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result("MongoDB Data Persistence", False, f"Exception: {str(e)}")
        
        # Test 2: Get user by ID via /users/{userId}
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                if (user_data.get('id') == self.test_user_id and 
                    user_data.get('email') == self.test_user_email):
                    
                    self.log_result(
                        "User Lookup by ID", 
                        True, 
                        "User can be found by ID - data persistence verified",
                        f"Found: {user_data.get('name')} ({user_data.get('email')})"
                    )
                else:
                    self.log_result(
                        "User Lookup by ID", 
                        False, 
                        "User lookup by ID returned incorrect data",
                        f"Expected: {self.test_user_id}/{self.test_user_email}, Got: {user_data.get('id')}/{user_data.get('email')}"
                    )
            else:
                self.log_result(
                    "User Lookup by ID", 
                    False, 
                    f"Failed to find user by ID - status {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result("User Lookup by ID", False, f"Exception: {str(e)}")
    
    def run_complete_test(self):
        """Run the complete authentication persistence test"""
        print("🚀 STARTING COMPLETE AUTHENTICATION SYSTEM TEST")
        print("=" * 60)
        print("Testing: User Registration and Login Persistence")
        print("Goal: Verify accounts are stored permanently like Instagram")
        print("=" * 60)
        
        # Run all test steps
        self.step_1_check_database_setup()
        self.step_2_create_new_user_account()
        self.step_3_verify_email()
        self.step_4_logout_and_login_again()
        self.step_5_test_login_persistence()
        self.step_6_test_wrong_password()
        self.step_7_check_data_persistence()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🏁 AUTHENTICATION PERSISTENCE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("\n🎯 AUTHENTICATION SYSTEM ASSESSMENT:")
        
        # Check critical requirements
        critical_tests = [
            "Create New User Account",
            "Login After Creation", 
            "Login Persistence Test",
            "Wrong Password Test",
            "MongoDB Data Persistence"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print("🟢 AUTHENTICATION SYSTEM: FULLY FUNCTIONAL")
            print("✅ User accounts are created and stored permanently")
            print("✅ Users can login anytime with their credentials")
            print("✅ Authentication works like Instagram (persistent accounts)")
            print("✅ Security measures are working (wrong passwords rejected)")
            print("✅ Data persistence verified in both databases")
        else:
            print("🔴 AUTHENTICATION SYSTEM: ISSUES FOUND")
            print("❌ Some critical authentication features are not working properly")
            
            failed_critical = [test for test in critical_tests 
                             if not any(r['test'] == test and r['success'] 
                                      for r in self.test_results)]
            if failed_critical:
                print(f"❌ Failed critical tests: {', '.join(failed_critical)}")
        
        if self.test_user_email:
            print(f"\n📧 Test User Created: {self.test_user_email}")
            print(f"🔑 Password: {self.test_user_password}")
            print("💡 This account can be used for further testing")

if __name__ == "__main__":
    tester = AuthPersistenceTester()
    tester.run_complete_test()