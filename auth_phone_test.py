#!/usr/bin/env python3
"""
Authentication with Phone Number Field Testing Suite
Tests the complete authentication system with phone number field as requested.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"

class AuthPhoneTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = None
        self.test_user_token = None
        
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
    
    def test_new_user_signup_with_phone(self):
        """Test 1: New User Signup with Phone Number"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"testuser123_{timestamp}@example.com"
            
            payload = {
                "name": "Test User",
                "handle": f"testuser123_{timestamp}",
                "email": self.test_user_email,
                "phone": f"987654{timestamp[-4:]}",  # Use timestamp for unique phone
                "password": "Test@1234"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.test_user_token = data['token']
                    user = data['user']
                    
                    # Validate user data includes phone number
                    if (user.get('email') == self.test_user_email and 
                        user.get('name') == "Test User" and 
                        user.get('phone') == "9876543210" and
                        user.get('id')):
                        self.log_result(
                            "New User Signup with Phone Number", 
                            True, 
                            f"Successfully created user with phone number",
                            f"User: {user['name']}, Email: {user['email']}, Phone: {user['phone']}, ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "New User Signup with Phone Number", 
                            False, 
                            "Signup successful but user data incomplete or phone missing",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Signup with Phone Number", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "New User Signup with Phone Number", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("New User Signup with Phone Number", False, f"Exception occurred: {str(e)}")
    
    def test_login_with_phone_user(self):
        """Test 2: Login Test with user that has phone number"""
        if not self.test_user_email:
            self.log_result("Login Test", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "Test@1234"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    token = data['token']
                    user = data['user']
                    
                    # Validate user data includes phone number
                    if (user.get('email') == self.test_user_email and 
                        user.get('phone') == "9876543210" and
                        user.get('name') and 
                        user.get('id')):
                        self.log_result(
                            "Login Test", 
                            True, 
                            f"Successfully logged in user with phone number",
                            f"User: {user['name']}, Email: {user['email']}, Phone: {user['phone']}, Token received"
                        )
                    else:
                        self.log_result(
                            "Login Test", 
                            False, 
                            "Login successful but user data incomplete or phone missing",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Login Test", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Test", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Test", False, f"Exception occurred: {str(e)}")
    
    def test_invalid_credentials(self):
        """Test 3: Test Invalid Credentials"""
        if not self.test_user_email:
            self.log_result("Test Invalid Credentials", False, "Skipped - no test user email available")
            return
            
        try:
            payload = {
                "email": self.test_user_email,
                "password": "WrongPassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                data = response.json()
                if "invalid credentials" in data.get('detail', '').lower():
                    self.log_result(
                        "Test Invalid Credentials", 
                        True, 
                        "Correctly rejected invalid credentials with 401 status",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Test Invalid Credentials", 
                        True, 
                        "Rejected invalid credentials with 401 but message unclear",
                        f"Response: {data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Test Invalid Credentials", 
                    False, 
                    "Security issue: Invalid credentials were accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Test Invalid Credentials", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid credentials",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Invalid Credentials", False, f"Exception occurred: {str(e)}")
    
    def test_duplicate_phone_number(self):
        """Test 4: Test Duplicate Phone Number"""
        try:
            # Try to signup with same phone number
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            payload = {
                "name": "Another Test User",
                "handle": f"anotheruser_{timestamp}",
                "email": f"anotheruser_{timestamp}@example.com",
                "phone": "9876543210",  # Same phone as first user
                "password": "AnotherTest@1234"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                detail = data.get('detail', '').lower()
                if "phone" in detail and ("already" in detail or "registered" in detail):
                    self.log_result(
                        "Test Duplicate Phone Number", 
                        True, 
                        "Correctly rejected duplicate phone number with 400 status",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Test Duplicate Phone Number", 
                        False, 
                        "Got 400 status but error message doesn't mention phone duplication",
                        f"Response: {data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Test Duplicate Phone Number", 
                    False, 
                    "Security issue: Duplicate phone number was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Test Duplicate Phone Number", 
                    False, 
                    f"Unexpected status code {response.status_code} for duplicate phone",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Duplicate Phone Number", False, f"Exception occurred: {str(e)}")
    
    def test_signup_without_phone(self):
        """Test 5: Test Signup Without Phone (optional field)"""
        try:
            # Generate unique test user data without phone
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            payload = {
                "name": "No Phone User",
                "handle": f"nophone_{timestamp}",
                "email": f"nophone_{timestamp}@example.com",
                "password": "NoPhone@1234"
                # Note: No phone field included
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    
                    # Validate user data - phone should be empty or not present
                    if (user.get('email') == payload['email'] and 
                        user.get('name') == "No Phone User" and 
                        user.get('id')):
                        # Check phone field is empty or not present
                        phone = user.get('phone', '')
                        if phone == '' or phone is None:
                            self.log_result(
                                "Test Signup Without Phone", 
                                True, 
                                f"Successfully created user without phone number",
                                f"User: {user['name']}, Email: {user['email']}, Phone: '{phone}', ID: {user['id']}"
                            )
                        else:
                            self.log_result(
                                "Test Signup Without Phone", 
                                False, 
                                f"User created but phone field has unexpected value: '{phone}'",
                                f"User data: {user}"
                            )
                    else:
                        self.log_result(
                            "Test Signup Without Phone", 
                            False, 
                            "Signup successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Test Signup Without Phone", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test Signup Without Phone", 
                    False, 
                    f"Signup without phone failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Signup Without Phone", False, f"Exception occurred: {str(e)}")
    
    def test_user_data_persistence(self):
        """Test 6: Verify User Data Persistence in MongoDB"""
        if not self.test_user_token:
            self.log_result("User Data Persistence", False, "Skipped - no test user token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.test_user_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if ('id' in data and 'name' in data and 'email' in data and 
                    data.get('phone') == "9876543210"):
                    self.log_result(
                        "User Data Persistence", 
                        True, 
                        f"User data persisted correctly in MongoDB",
                        f"User: {data.get('name')}, Email: {data.get('email')}, Phone: {data.get('phone')}"
                    )
                else:
                    self.log_result(
                        "User Data Persistence", 
                        False, 
                        "User data retrieved but phone number missing or incorrect",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "User Data Persistence", 
                    False, 
                    f"Failed to retrieve user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("User Data Persistence", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all authentication tests with phone number"""
        print("=" * 80)
        print("AUTHENTICATION WITH PHONE NUMBER FIELD TESTING SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run tests in sequence
        self.test_new_user_signup_with_phone()
        self.test_login_with_phone_user()
        self.test_invalid_credentials()
        self.test_duplicate_phone_number()
        self.test_signup_without_phone()
        self.test_user_data_persistence()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['message']}")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        
        return passed == total

if __name__ == "__main__":
    tester = AuthPhoneTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)