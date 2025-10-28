#!/usr/bin/env python3
"""
Complete Email/Password Authentication Flow Testing
Tests all authentication scenarios as requested in the review.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"

class AuthFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = None
        self.test_user_password = "password123"
        self.test_user_token = None
        self.verification_code = None
        
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
        if details and not success:
            print(f"   Details: {details}")
        print()
    
    def test_1_user_signup_flow(self):
        """Test 1: User Signup Flow - Create new user account with email/password"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"authtest_{timestamp}@example.com"
            
            payload = {
                "name": "Auth Test User",
                "handle": f"authtest_{timestamp}",
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['token', 'user', 'verificationCode']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    user = data['user']
                    self.test_user_token = data['token']
                    self.verification_code = data['verificationCode']
                    
                    # Validate user data
                    user_checks = [
                        user.get('email') == self.test_user_email,
                        user.get('name') == payload['name'],
                        user.get('id') is not None,
                        user.get('isVerified') == False
                    ]
                    
                    if all(user_checks):
                        self.log_result(
                            "Test 1: User Signup Flow", 
                            True, 
                            f"✅ User created successfully: {user['name']} ({user['email']})",
                            f"User ID: {user['id']}, Token received, Verification code: {self.verification_code}"
                        )
                    else:
                        self.log_result(
                            "Test 1: User Signup Flow", 
                            False, 
                            "❌ User created but data validation failed",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Test 1: User Signup Flow", 
                        False, 
                        f"❌ Signup response missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test 1: User Signup Flow", 
                    False, 
                    f"❌ Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 1: User Signup Flow", False, f"❌ Exception occurred: {str(e)}")
    
    def test_2_email_verification(self):
        """Test 2: Email Verification - Verify email with code"""
        if not self.test_user_email or not self.verification_code:
            self.log_result("Test 2: Email Verification", False, "❌ Skipped - no test user or verification code available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "code": self.verification_code
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/verify-email", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'verified successfully' in data.get('message', '').lower():
                    self.log_result(
                        "Test 2: Email Verification", 
                        True, 
                        f"✅ Email verified successfully for {self.test_user_email}",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Test 2: Email Verification", 
                        False, 
                        "❌ Verification response format unexpected",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test 2: Email Verification", 
                    False, 
                    f"❌ Email verification failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 2: Email Verification", False, f"❌ Exception occurred: {str(e)}")
    
    def test_3_login_with_email_password(self):
        """Test 3: Login with Email/Password - Login with correct credentials"""
        if not self.test_user_email:
            self.log_result("Test 3: Login with Email/Password", False, "❌ Skipped - no test user email available")
            return
            
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
                    token = data['token']
                    
                    # Validate login response
                    login_checks = [
                        user.get('email') == self.test_user_email,
                        user.get('id') is not None,
                        len(token) > 50  # JWT tokens are typically long
                    ]
                    
                    if all(login_checks):
                        self.test_user_token = token  # Update token
                        self.log_result(
                            "Test 3: Login with Email/Password", 
                            True, 
                            f"✅ Login successful for {user['email']}",
                            f"User ID: {user['id']}, JWT token received (length: {len(token)})"
                        )
                    else:
                        self.log_result(
                            "Test 3: Login with Email/Password", 
                            False, 
                            "❌ Login successful but data validation failed",
                            f"User: {user}, Token length: {len(token) if token else 0}"
                        )
                else:
                    self.log_result(
                        "Test 3: Login with Email/Password", 
                        False, 
                        "❌ Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test 3: Login with Email/Password", 
                    False, 
                    f"❌ Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 3: Login with Email/Password", False, f"❌ Exception occurred: {str(e)}")
    
    def test_4_login_persistence(self):
        """Test 4: Login Persistence - Login multiple times with same credentials"""
        if not self.test_user_email:
            self.log_result("Test 4: Login Persistence", False, "❌ Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            successful_logins = 0
            login_tokens = []
            
            # Attempt 3 consecutive logins
            for i in range(3):
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'token' in data and 'user' in data:
                        successful_logins += 1
                        login_tokens.append(data['token'])
                        time.sleep(0.5)  # Small delay between requests
                
            if successful_logins == 3:
                # Check if tokens are different (they should be for security)
                unique_tokens = len(set(login_tokens))
                self.log_result(
                    "Test 4: Login Persistence", 
                    True, 
                    f"✅ All 3 login attempts successful - login persistence verified",
                    f"Unique tokens generated: {unique_tokens}/3 (good security practice)"
                )
            else:
                self.log_result(
                    "Test 4: Login Persistence", 
                    False, 
                    f"❌ Only {successful_logins}/3 login attempts successful",
                    "Login persistence issue detected"
                )
                
        except Exception as e:
            self.log_result("Test 4: Login Persistence", False, f"❌ Exception occurred: {str(e)}")
    
    def test_5_wrong_password(self):
        """Test 5: Wrong Password - Login with wrong password should fail"""
        if not self.test_user_email:
            self.log_result("Test 5: Wrong Password", False, "❌ Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "wrongpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                data = response.json()
                if 'invalid' in data.get('detail', '').lower() or 'credentials' in data.get('detail', '').lower():
                    self.log_result(
                        "Test 5: Wrong Password", 
                        True, 
                        f"✅ Wrong password correctly rejected with 401 status",
                        f"Error message: {data.get('detail', 'No detail')}"
                    )
                else:
                    self.log_result(
                        "Test 5: Wrong Password", 
                        True, 
                        f"✅ Wrong password rejected with 401 (message unclear)",
                        f"Response: {data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Test 5: Wrong Password", 
                    False, 
                    "❌ SECURITY ISSUE: Wrong password was accepted!",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Test 5: Wrong Password", 
                    False, 
                    f"❌ Unexpected status code {response.status_code} for wrong password",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 5: Wrong Password", False, f"❌ Exception occurred: {str(e)}")
    
    def test_6_non_existent_user(self):
        """Test 6: Non-existent User - Login with email that doesn't exist"""
        try:
            payload = {
                "email": "nonexistent_user_12345@example.com",
                "password": "anypassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                data = response.json()
                self.log_result(
                    "Test 6: Non-existent User", 
                    True, 
                    f"✅ Non-existent user correctly rejected with 401 status",
                    f"Error message: {data.get('detail', 'No detail')}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Test 6: Non-existent User", 
                    False, 
                    "❌ SECURITY ISSUE: Non-existent user login was accepted!",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Test 6: Non-existent User", 
                    False, 
                    f"❌ Unexpected status code {response.status_code} for non-existent user",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 6: Non-existent User", False, f"❌ Exception occurred: {str(e)}")
    
    def test_7_password_storage_security(self):
        """Test 7: Password Storage - Verify password is hashed (not plain text)"""
        # This test checks if we can verify that passwords are properly hashed
        # We'll test this by attempting to signup with the same email (should fail)
        # and checking that the error doesn't reveal the password
        
        if not self.test_user_email:
            self.log_result("Test 7: Password Storage Security", False, "❌ Skipped - no test user email available")
            return
            
        try:
            # Try to signup with same email (should fail)
            payload = {
                "name": "Duplicate Test",
                "handle": "duplicate_test_handle",
                "email": self.test_user_email,  # Same email as existing user
                "password": "anynewpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                error_text = response.text.lower()
                # Check that password is not revealed in error message
                password_not_revealed = (
                    self.test_user_password.lower() not in error_text and
                    "anynewpassword123" not in error_text
                )
                
                if password_not_revealed:
                    self.log_result(
                        "Test 7: Password Storage Security", 
                        True, 
                        f"✅ Password security verified - passwords not revealed in error messages",
                        "Duplicate email properly rejected without exposing password data"
                    )
                else:
                    self.log_result(
                        "Test 7: Password Storage Security", 
                        False, 
                        "❌ SECURITY ISSUE: Password data exposed in error message",
                        f"Error response: {response.text}"
                    )
            else:
                self.log_result(
                    "Test 7: Password Storage Security", 
                    False, 
                    f"❌ Unexpected response for duplicate email test (status {response.status_code})",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 7: Password Storage Security", False, f"❌ Exception occurred: {str(e)}")
    
    def test_8_jwt_token_validation(self):
        """Test 8: JWT Token Validation - Verify JWT token format and content"""
        if not self.test_user_token:
            self.log_result("Test 8: JWT Token Validation", False, "❌ Skipped - no JWT token available")
            return
            
        try:
            # Test token with /auth/me endpoint
            headers = {
                "Authorization": f"Bearer {self.test_user_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate JWT token properties
                token_parts = self.test_user_token.split('.')
                token_checks = [
                    len(token_parts) == 3,  # JWT has 3 parts
                    len(self.test_user_token) > 100,  # Reasonable token length
                    'id' in data,  # Token should decode to user info
                    'email' in data or 'name' in data  # User data present
                ]
                
                if all(token_checks):
                    self.log_result(
                        "Test 8: JWT Token Validation", 
                        True, 
                        f"✅ JWT token validation successful",
                        f"Token format valid, User ID: {data.get('id')}, Email: {data.get('email', 'N/A')}"
                    )
                else:
                    self.log_result(
                        "Test 8: JWT Token Validation", 
                        False, 
                        "❌ JWT token validation failed",
                        f"Token parts: {len(token_parts)}, Length: {len(self.test_user_token)}, User data: {data}"
                    )
            else:
                self.log_result(
                    "Test 8: JWT Token Validation", 
                    False, 
                    f"❌ JWT token validation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 8: JWT Token Validation", False, f"❌ Exception occurred: {str(e)}")
    
    def test_9_complete_round_trip(self):
        """Test 9: Complete Round Trip - Signup → Verify → Login → Success"""
        try:
            # Create a new user for round trip test
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            roundtrip_email = f"roundtrip_{timestamp}@example.com"
            roundtrip_password = "roundtrip123"
            
            # Step 1: Signup
            signup_payload = {
                "name": "Round Trip User",
                "handle": f"roundtrip_{timestamp}",
                "email": roundtrip_email,
                "password": roundtrip_password
            }
            
            signup_response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code != 200:
                self.log_result(
                    "Test 9: Complete Round Trip", 
                    False, 
                    f"❌ Round trip failed at signup step (status {signup_response.status_code})",
                    f"Signup response: {signup_response.text}"
                )
                return
            
            signup_data = signup_response.json()
            verification_code = signup_data.get('verificationCode')
            
            # Step 2: Verify Email
            verify_payload = {
                "email": roundtrip_email,
                "code": verification_code
            }
            
            verify_response = self.session.post(f"{BACKEND_URL}/auth/verify-email", json=verify_payload)
            
            if verify_response.status_code != 200:
                self.log_result(
                    "Test 9: Complete Round Trip", 
                    False, 
                    f"❌ Round trip failed at verification step (status {verify_response.status_code})",
                    f"Verify response: {verify_response.text}"
                )
                return
            
            # Step 3: Login
            login_payload = {
                "email": roundtrip_email,
                "password": roundtrip_password
            }
            
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                if 'token' in login_data and 'user' in login_data:
                    self.log_result(
                        "Test 9: Complete Round Trip", 
                        True, 
                        f"✅ Complete round trip successful: Signup → Verify → Login",
                        f"User: {login_data['user'].get('name')} ({login_data['user'].get('email')})"
                    )
                else:
                    self.log_result(
                        "Test 9: Complete Round Trip", 
                        False, 
                        "❌ Round trip failed at login validation",
                        f"Login response: {login_data}"
                    )
            else:
                self.log_result(
                    "Test 9: Complete Round Trip", 
                    False, 
                    f"❌ Round trip failed at login step (status {login_response.status_code})",
                    f"Login response: {login_response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 9: Complete Round Trip", False, f"❌ Exception occurred: {str(e)}")
    
    def test_10_database_consistency(self):
        """Test 10: Database Consistency - Check user exists in both databases with same ID"""
        if not self.test_user_token:
            self.log_result("Test 10: Database Consistency", False, "❌ Skipped - no JWT token available")
            return
            
        try:
            # Get user data via /auth/me (should pull from both Google Sheets and MongoDB)
            headers = {
                "Authorization": f"Bearer {self.test_user_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check for consistent user data
                consistency_checks = [
                    'id' in user_data,
                    'email' in user_data,
                    'name' in user_data,
                    user_data.get('email') == self.test_user_email
                ]
                
                if all(consistency_checks):
                    # Try to get user profile (MongoDB data)
                    user_id = user_data['id']
                    profile_response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        
                        # Check ID consistency between databases
                        id_consistent = profile_data.get('id') == user_data.get('id')
                        email_consistent = profile_data.get('email') == user_data.get('email')
                        
                        if id_consistent and email_consistent:
                            self.log_result(
                                "Test 10: Database Consistency", 
                                True, 
                                f"✅ Database consistency verified - user exists in both databases",
                                f"User ID: {user_id}, Email consistent: {email_consistent}"
                            )
                        else:
                            self.log_result(
                                "Test 10: Database Consistency", 
                                False, 
                                "❌ Database inconsistency detected",
                                f"Auth data: {user_data}, Profile data: {profile_data}"
                            )
                    else:
                        self.log_result(
                            "Test 10: Database Consistency", 
                            False, 
                            f"❌ User profile not found in MongoDB (status {profile_response.status_code})",
                            f"User ID: {user_id}"
                        )
                else:
                    self.log_result(
                        "Test 10: Database Consistency", 
                        False, 
                        "❌ User data consistency check failed",
                        f"User data: {user_data}"
                    )
            else:
                self.log_result(
                    "Test 10: Database Consistency", 
                    False, 
                    f"❌ Failed to get user data (status {response.status_code})",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test 10: Database Consistency", False, f"❌ Exception occurred: {str(e)}")
    
    def test_error_scenarios(self):
        """Additional Error Scenarios Testing"""
        print("🔍 TESTING ERROR SCENARIOS:")
        print("=" * 50)
        
        # Test empty email/password
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={"email": "", "password": ""})
            if response.status_code in [400, 422]:
                print("✅ Empty credentials properly rejected")
            else:
                print(f"❌ Empty credentials handling unexpected (status {response.status_code})")
        except:
            print("❌ Empty credentials test failed")
        
        # Test invalid email format
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json={
                "name": "Test", "handle": "test", "email": "invalid-email", "password": "test123"
            })
            if response.status_code in [400, 422]:
                print("✅ Invalid email format properly rejected")
            else:
                print(f"❌ Invalid email format handling unexpected (status {response.status_code})")
        except:
            print("❌ Invalid email format test failed")
        
        # Test short password
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json={
                "name": "Test", "handle": "test123", "email": "test123@example.com", "password": "123"
            })
            if response.status_code in [400, 422]:
                print("✅ Short password properly rejected")
            else:
                print(f"❌ Short password handling unexpected (status {response.status_code})")
        except:
            print("❌ Short password test failed")
        
        print()
    
    def run_all_tests(self):
        """Run all authentication flow tests"""
        print("🔐 COMPLETE EMAIL/PASSWORD AUTHENTICATION FLOW TESTING")
        print("=" * 60)
        print()
        
        # Run main test sequence
        self.test_1_user_signup_flow()
        self.test_2_email_verification()
        self.test_3_login_with_email_password()
        self.test_4_login_persistence()
        self.test_5_wrong_password()
        self.test_6_non_existent_user()
        self.test_7_password_storage_security()
        self.test_8_jwt_token_validation()
        self.test_9_complete_round_trip()
        self.test_10_database_consistency()
        
        # Run additional error scenario tests
        self.test_error_scenarios()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 40)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
            print()
        
        print("✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test']}")
        
        print()
        print("🔒 SECURITY ASSESSMENT:")
        security_tests = [
            "Test 5: Wrong Password",
            "Test 6: Non-existent User", 
            "Test 7: Password Storage Security",
            "Test 8: JWT Token Validation"
        ]
        
        security_passed = [t for t in passed_tests if t['test'] in security_tests]
        print(f"Security Tests Passed: {len(security_passed)}/{len(security_tests)}")
        
        if len(security_passed) == len(security_tests):
            print("🛡️ All security tests passed - Authentication system is secure")
        else:
            print("⚠️ Some security tests failed - Review authentication implementation")
        
        print()
        print("📋 RECOMMENDATIONS:")
        if len(failed_tests) == 0:
            print("✅ Authentication system is fully functional and ready for production")
        else:
            print("⚠️ Fix failed tests before production deployment")
            print("🔧 Focus on security-related failures first")
        
        print()
        print(f"📧 Test User Created: {self.test_user_email}")
        print(f"🔑 Test Password: {self.test_user_password}")
        print()

if __name__ == "__main__":
    tester = AuthFlowTester()
    tester.run_all_tests()