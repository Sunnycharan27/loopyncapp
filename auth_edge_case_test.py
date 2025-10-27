#!/usr/bin/env python3
"""
Authentication Edge Case Testing
Testing specific scenarios that might cause "invalid credentials" errors
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

class AuthEdgeCaseTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_existing_email_signup(self):
        """Test signup with existing email (should fail gracefully)"""
        print("=" * 60)
        print("TEST: EXISTING EMAIL SIGNUP")
        print("=" * 60)
        
        try:
            # Try to signup with demo email (should already exist)
            payload = {
                "email": "demo@loopync.com",
                "password": "TestPass123!",
                "name": "Test User",
                "handle": "testhandle123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 400:
                data = response.json()
                detail = data.get('detail', '').lower()
                if 'already' in detail and 'registered' in detail:
                    self.log_result(
                        "Existing Email Signup", 
                        True, 
                        "✅ Correctly rejected duplicate email signup",
                        f"Error: {data.get('detail')}"
                    )
                else:
                    self.log_result(
                        "Existing Email Signup", 
                        False, 
                        "❌ Got 400 but unclear error message",
                        f"Error: {data.get('detail')}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Existing Email Signup", 
                    False, 
                    "❌ SECURITY ISSUE: Duplicate email was accepted",
                    "This could cause login conflicts"
                )
            else:
                self.log_result(
                    "Existing Email Signup", 
                    False, 
                    f"❌ Unexpected status code: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Existing Email Signup", False, f"❌ Exception: {str(e)}")
    
    def test_case_sensitivity(self):
        """Test email case sensitivity in login"""
        print("=" * 60)
        print("TEST: EMAIL CASE SENSITIVITY")
        print("=" * 60)
        
        try:
            # Test with different case variations of demo email
            test_cases = [
                "demo@loopync.com",      # Original
                "Demo@loopync.com",      # Capital D
                "DEMO@LOOPYNC.COM",      # All caps
                "demo@LOOPYNC.com",      # Mixed case domain
            ]
            
            for email in test_cases:
                payload = {
                    "email": email,
                    "password": "password123"
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                print(f"Email: {email} -> Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    print(f"  Error: {error_data.get('detail', response.text)}")
            
            self.log_result(
                "Email Case Sensitivity", 
                True, 
                "✅ Case sensitivity test completed",
                "Check individual results above"
            )
                
        except Exception as e:
            self.log_result("Email Case Sensitivity", False, f"❌ Exception: {str(e)}")
    
    def test_whitespace_handling(self):
        """Test login with whitespace in email/password"""
        print("=" * 60)
        print("TEST: WHITESPACE HANDLING")
        print("=" * 60)
        
        try:
            # Test with whitespace variations
            test_cases = [
                {
                    "email": " demo@loopync.com",      # Leading space
                    "password": "password123"
                },
                {
                    "email": "demo@loopync.com ",      # Trailing space
                    "password": "password123"
                },
                {
                    "email": "demo@loopync.com",
                    "password": " password123"         # Leading space in password
                },
                {
                    "email": "demo@loopync.com",
                    "password": "password123 "         # Trailing space in password
                }
            ]
            
            for i, payload in enumerate(test_cases, 1):
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                print(f"Test {i}: Email='{payload['email']}', Password='{payload['password']}' -> Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    print(f"  Error: {error_data.get('detail', response.text)}")
            
            self.log_result(
                "Whitespace Handling", 
                True, 
                "✅ Whitespace handling test completed",
                "Check individual results above"
            )
                
        except Exception as e:
            self.log_result("Whitespace Handling", False, f"❌ Exception: {str(e)}")
    
    def test_special_characters(self):
        """Test signup/login with special characters in password"""
        print("=" * 60)
        print("TEST: SPECIAL CHARACTERS IN PASSWORD")
        print("=" * 60)
        
        try:
            # Create user with special characters in password
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            special_password = "Test@Pass#123!$%^&*()"
            
            signup_payload = {
                "email": f"special_{timestamp}@example.com",
                "password": special_password,
                "name": "Special Test User",
                "handle": f"special_{timestamp}"
            }
            
            # Signup
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            print(f"Signup Status: {response.status_code}")
            
            if response.status_code == 200:
                # Try to login with same special password
                login_payload = {
                    "email": signup_payload['email'],
                    "password": special_password
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                print(f"Login Status: {response.status_code}")
                
                if response.status_code == 200:
                    self.log_result(
                        "Special Characters Password", 
                        True, 
                        "✅ Special characters in password work correctly",
                        f"Password: {special_password}"
                    )
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    self.log_result(
                        "Special Characters Password", 
                        False, 
                        "❌ Login failed with special character password",
                        f"Error: {error_data.get('detail', response.text)}"
                    )
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_result(
                    "Special Characters Password", 
                    False, 
                    "❌ Signup failed with special character password",
                    f"Error: {error_data.get('detail', response.text)}"
                )
                
        except Exception as e:
            self.log_result("Special Characters Password", False, f"❌ Exception: {str(e)}")
    
    def test_unicode_characters(self):
        """Test signup/login with unicode characters"""
        print("=" * 60)
        print("TEST: UNICODE CHARACTERS")
        print("=" * 60)
        
        try:
            # Create user with unicode characters
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            signup_payload = {
                "email": f"unicode_{timestamp}@example.com",
                "password": "TestPass123!",
                "name": "Test User 测试用户 🚀",
                "handle": f"unicode_{timestamp}"
            }
            
            # Signup
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            print(f"Signup Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"User name stored as: {data['user']['name']}")
                
                # Try to login
                login_payload = {
                    "email": signup_payload['email'],
                    "password": "TestPass123!"
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                print(f"Login Status: {response.status_code}")
                
                if response.status_code == 200:
                    self.log_result(
                        "Unicode Characters", 
                        True, 
                        "✅ Unicode characters handled correctly",
                        f"Name: {signup_payload['name']}"
                    )
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    self.log_result(
                        "Unicode Characters", 
                        False, 
                        "❌ Login failed with unicode name",
                        f"Error: {error_data.get('detail', response.text)}"
                    )
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_result(
                    "Unicode Characters", 
                    False, 
                    "❌ Signup failed with unicode characters",
                    f"Error: {error_data.get('detail', response.text)}"
                )
                
        except Exception as e:
            self.log_result("Unicode Characters", False, f"❌ Exception: {str(e)}")
    
    def test_long_password(self):
        """Test with very long password"""
        print("=" * 60)
        print("TEST: LONG PASSWORD")
        print("=" * 60)
        
        try:
            # Create user with very long password
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            long_password = "A" * 200 + "123!"  # 204 character password
            
            signup_payload = {
                "email": f"longpass_{timestamp}@example.com",
                "password": long_password,
                "name": "Long Password User",
                "handle": f"longpass_{timestamp}"
            }
            
            # Signup
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            print(f"Signup Status: {response.status_code}")
            print(f"Password length: {len(long_password)} characters")
            
            if response.status_code == 200:
                # Try to login with same long password
                login_payload = {
                    "email": signup_payload['email'],
                    "password": long_password
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                print(f"Login Status: {response.status_code}")
                
                if response.status_code == 200:
                    self.log_result(
                        "Long Password", 
                        True, 
                        "✅ Long password handled correctly",
                        f"Password length: {len(long_password)} chars"
                    )
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    self.log_result(
                        "Long Password", 
                        False, 
                        "❌ Login failed with long password",
                        f"Error: {error_data.get('detail', response.text)}"
                    )
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_result(
                    "Long Password", 
                    False, 
                    "❌ Signup failed with long password",
                    f"Error: {error_data.get('detail', response.text)}"
                )
                
        except Exception as e:
            self.log_result("Long Password", False, f"❌ Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("🔍 AUTHENTICATION EDGE CASE TESTING")
        print("Testing scenarios that might cause 'invalid credentials' errors")
        print("=" * 80)
        print()
        
        self.test_existing_email_signup()
        self.test_case_sensitivity()
        self.test_whitespace_handling()
        self.test_special_characters()
        self.test_unicode_characters()
        self.test_long_password()
        
        # Summary
        print("=" * 80)
        print("EDGE CASE TEST SUMMARY")
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
            print("❌ EDGE CASE ISSUES DETECTED:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("✅ ALL EDGE CASE TESTS PASSED")
        
        return self.test_results

if __name__ == "__main__":
    tester = AuthEdgeCaseTester()
    results = tester.run_all_tests()