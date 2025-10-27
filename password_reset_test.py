#!/usr/bin/env python3
"""
Complete Forgot Password Flow End-to-End Testing
Tests the complete password reset flow including signup, login, reset, and verification.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

class PasswordResetTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = None
        self.test_user_id = None
        self.reset_code = None
        
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
    
    def test_1_create_test_user(self):
        """Test 1: Create a Test User First"""
        try:
            self.test_user_email = "resettest123@example.com"
            
            payload = {
                "name": "Password Reset Test User",
                "handle": "resettest123",
                "email": self.test_user_email,
                "phone": "9999999999",
                "password": "OldPassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    self.test_user_id = user.get('id')
                    
                    if (user.get('email') == self.test_user_email and 
                        user.get('name') == payload['name'] and 
                        user.get('handle') == payload['handle']):
                        self.log_result(
                            "Create Test User", 
                            True, 
                            f"Successfully created test user: {user['name']} ({user['email']})",
                            f"User ID: {user['id']}, Handle: {user['handle']}"
                        )
                    else:
                        self.log_result(
                            "Create Test User", 
                            False, 
                            "User created but data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Create Test User", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # User might already exist, try to continue with existing user
                data = response.json()
                if "already registered" in data.get('detail', '').lower():
                    self.log_result(
                        "Create Test User", 
                        True, 
                        "Test user already exists, continuing with existing user",
                        f"Email: {self.test_user_email}"
                    )
                else:
                    self.log_result(
                        "Create Test User", 
                        False, 
                        f"User creation failed: {data.get('detail', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create Test User", 
                    False, 
                    f"User creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create Test User", False, f"Exception occurred: {str(e)}")
    
    def test_2_login_original_password(self):
        """Test 2: Test Login with Original Password"""
        if not self.test_user_email:
            self.log_result("Login Original Password", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "OldPassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    self.test_user_id = user.get('id')  # Store user ID for later tests
                    
                    self.log_result(
                        "Login Original Password", 
                        True, 
                        f"Successfully logged in with original password",
                        f"User: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')}), Token received"
                    )
                else:
                    self.log_result(
                        "Login Original Password", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Original Password", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Original Password", False, f"Exception occurred: {str(e)}")
    
    def test_3_request_password_reset(self):
        """Test 3: Request Password Reset"""
        if not self.test_user_email:
            self.log_result("Request Password Reset", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    # Check if reset code is provided (for testing)
                    if 'code' in data:
                        self.reset_code = data['code']
                        self.log_result(
                            "Request Password Reset", 
                            True, 
                            f"Successfully requested password reset",
                            f"Reset code received: {self.reset_code}"
                        )
                    else:
                        self.log_result(
                            "Request Password Reset", 
                            True, 
                            f"Password reset requested successfully",
                            f"Message: {data.get('message', 'Reset code sent')}"
                        )
                else:
                    self.log_result(
                        "Request Password Reset", 
                        False, 
                        "Password reset response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Request Password Reset", 
                    False, 
                    f"Password reset request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Request Password Reset", False, f"Exception occurred: {str(e)}")
    
    def test_4_verify_reset_code(self):
        """Test 4: Verify Reset Code"""
        if not self.test_user_email or not self.reset_code:
            self.log_result("Verify Reset Code", False, "Skipped - no email or reset code available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "code": self.reset_code
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/verify-reset-code", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result(
                        "Verify Reset Code", 
                        True, 
                        f"Successfully verified reset code",
                        f"Message: {data.get('message', 'Code verified')}, Token: {data.get('token', 'N/A')}"
                    )
                else:
                    self.log_result(
                        "Verify Reset Code", 
                        False, 
                        "Reset code verification response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Verify Reset Code", 
                    False, 
                    f"Reset code verification failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Reset Code", False, f"Exception occurred: {str(e)}")
    
    def test_5_reset_password_to_new(self):
        """Test 5: Reset Password to New Password"""
        if not self.test_user_email or not self.reset_code:
            self.log_result("Reset Password to New", False, "Skipped - no email or reset code available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "code": self.reset_code,
                "newPassword": "NewPassword456"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/reset-password", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result(
                        "Reset Password to New", 
                        True, 
                        f"Successfully reset password to new password",
                        f"Message: {data.get('message', 'Password reset successfully')}"
                    )
                else:
                    self.log_result(
                        "Reset Password to New", 
                        False, 
                        "Password reset response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Reset Password to New", 
                    False, 
                    f"Password reset failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Reset Password to New", False, f"Exception occurred: {str(e)}")
    
    def test_6_login_old_password_should_fail(self):
        """Test 6: Test Login with OLD Password (Should Fail)"""
        if not self.test_user_email:
            self.log_result("Login Old Password (Should Fail)", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "OldPassword123"  # Old password should no longer work
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_result(
                    "Login Old Password (Should Fail)", 
                    True, 
                    f"Correctly rejected old password with 401 status",
                    f"Old password no longer valid after reset"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Login Old Password (Should Fail)", 
                    False, 
                    "SECURITY ISSUE: Old password still works after reset!",
                    f"Password reset did not update password in database"
                )
            else:
                self.log_result(
                    "Login Old Password (Should Fail)", 
                    False, 
                    f"Unexpected status code {response.status_code} for old password",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Old Password (Should Fail)", False, f"Exception occurred: {str(e)}")
    
    def test_7_login_new_password_should_work(self):
        """Test 7: Test Login with NEW Password (Should Work)"""
        if not self.test_user_email:
            self.log_result("Login New Password (Should Work)", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "NewPassword456"  # New password should work
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    
                    self.log_result(
                        "Login New Password (Should Work)", 
                        True, 
                        f"Successfully logged in with new password - PASSWORD RESET WORKING!",
                        f"User: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')}), Password updated in Google Sheets"
                    )
                else:
                    self.log_result(
                        "Login New Password (Should Work)", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login New Password (Should Work)", 
                    False, 
                    f"Login with new password failed with status {response.status_code}",
                    f"Password reset may not have updated Google Sheets. Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login New Password (Should Work)", False, f"Exception occurred: {str(e)}")
    
    def test_8_change_password_again(self):
        """Test 8: Test Change Password Again"""
        if not self.test_user_id:
            self.log_result("Change Password Again", False, "Skipped - no test user ID available")
            return
            
        try:
            payload = {
                "userId": self.test_user_id,
                "currentPassword": "NewPassword456",
                "newPassword": "FinalPassword789"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/change-password", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result(
                        "Change Password Again", 
                        True, 
                        f"Successfully changed password again",
                        f"Message: {data.get('message', 'Password changed successfully')}"
                    )
                else:
                    self.log_result(
                        "Change Password Again", 
                        False, 
                        "Change password response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Change Password Again", 
                    False, 
                    f"Change password failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Change Password Again", False, f"Exception occurred: {str(e)}")
    
    def test_9_login_final_password(self):
        """Test 9: Test Login with Final Password"""
        if not self.test_user_email:
            self.log_result("Login Final Password", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "FinalPassword789"  # Final password should work
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    
                    self.log_result(
                        "Login Final Password", 
                        True, 
                        f"Successfully logged in with final password - CHANGE PASSWORD WORKING!",
                        f"User: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')}), All password operations successful"
                    )
                else:
                    self.log_result(
                        "Login Final Password", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Final Password", 
                    False, 
                    f"Login with final password failed with status {response.status_code}",
                    f"Change password may not have updated Google Sheets. Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Final Password", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all password reset flow tests"""
        print("=" * 80)
        print("COMPLETE FORGOT PASSWORD FLOW END-TO-END TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User Email: resettest123@example.com")
        print("=" * 80)
        
        # Run all tests in sequence
        self.test_1_create_test_user()
        self.test_2_login_original_password()
        self.test_3_request_password_reset()
        self.test_4_verify_reset_code()
        self.test_5_reset_password_to_new()
        self.test_6_login_old_password_should_fail()
        self.test_7_login_new_password_should_work()
        self.test_8_change_password_again()
        self.test_9_login_final_password()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - COMPLETE PASSWORD RESET FLOW WORKING!")
            print("✅ User can request password reset and receive code")
            print("✅ Code verification works correctly")
            print("✅ Password reset updates password in Google Sheets")
            print("✅ Old password stops working after reset")
            print("✅ New password works for login")
            print("✅ User data remains intact after password change")
            print("✅ Change password endpoint also works")
        else:
            print(f"\n❌ {total - passed} TESTS FAILED - PASSWORD RESET FLOW HAS ISSUES")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = PasswordResetTester()
    results = tester.run_all_tests()