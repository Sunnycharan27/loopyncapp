#!/usr/bin/env python3
"""
Test User Synchronization between Google Sheets and MongoDB
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class UserSyncTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        
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
    
    def test_demo_login_and_sync(self):
        """Test demo login and MongoDB sync"""
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
                    self.demo_user_id = data['user']['id']
                    
                    self.log_result(
                        "Demo Login", 
                        True, 
                        f"Successfully logged in as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}, Handle: {data['user'].get('handle', 'No handle')}"
                    )
                    
                    # Wait a moment for MongoDB sync
                    time.sleep(2)
                    
                    # Now check if user exists in MongoDB
                    check_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
                    
                    if check_response.status_code == 200:
                        user_data = check_response.json()
                        self.log_result(
                            "MongoDB Sync Check", 
                            True, 
                            f"User successfully synced to MongoDB",
                            f"Name: {user_data.get('name', 'Unknown')}, Handle: {user_data.get('handle', 'No handle')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "MongoDB Sync Check", 
                            False, 
                            f"User not found in MongoDB after login - status {check_response.status_code}",
                            f"Response: {check_response.text}"
                        )
                        return False
                else:
                    self.log_result("Demo Login", False, "Login response missing token or user data")
                    return False
            else:
                self.log_result("Demo Login", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Demo Login and Sync", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_multiple_logins(self):
        """Test multiple logins to see if sync is consistent"""
        try:
            for i in range(3):
                payload = {
                    "email": DEMO_EMAIL,
                    "password": DEMO_PASSWORD
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    user_id = data['user']['id']
                    
                    # Check MongoDB immediately after each login
                    check_response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                    
                    if check_response.status_code == 200:
                        print(f"   Login {i+1}: ✅ User found in MongoDB")
                    else:
                        print(f"   Login {i+1}: ❌ User NOT found in MongoDB (status {check_response.status_code})")
                        
                    time.sleep(1)  # Wait between logins
                else:
                    print(f"   Login {i+1}: ❌ Login failed (status {response.status_code})")
            
            self.log_result(
                "Multiple Logins Test", 
                True, 
                "Completed multiple login test - check individual results above",
                "Testing consistency of MongoDB sync"
            )
            return True
                
        except Exception as e:
            self.log_result("Multiple Logins Test", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_friend_request_after_sync(self):
        """Test friend request after ensuring user is synced"""
        if not self.demo_user_id:
            self.log_result("Friend Request After Sync", False, "Skipped - no demo user ID")
            return False
            
        try:
            # First ensure user is in MongoDB
            check_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if check_response.status_code != 200:
                self.log_result(
                    "Friend Request After Sync", 
                    False, 
                    "Cannot test friend request - user not in MongoDB",
                    f"User check status: {check_response.status_code}"
                )
                return False
            
            # Seed data to ensure u1 exists
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Now try friend request
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Friend Request After Sync", 
                    True, 
                    f"Friend request successful: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Friend Request After Sync", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Friend Request After Sync", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_creation_via_auth_me(self):
        """Test if /auth/me creates the user in MongoDB"""
        if not self.demo_token:
            self.log_result("User Creation via /auth/me", False, "Skipped - no demo token")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            # Call /auth/me which should create user if not exists
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('id')
                
                self.log_result(
                    "User Creation via /auth/me", 
                    True, 
                    f"Successfully retrieved user via /auth/me",
                    f"User ID: {user_id}, Name: {data.get('name', 'Unknown')}"
                )
                
                # Now check if user exists in MongoDB
                time.sleep(1)  # Wait for potential async creation
                
                check_response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                
                if check_response.status_code == 200:
                    self.log_result(
                        "MongoDB User Check After /auth/me", 
                        True, 
                        "User found in MongoDB after /auth/me call",
                        "User creation successful"
                    )
                    return True
                else:
                    self.log_result(
                        "MongoDB User Check After /auth/me", 
                        False, 
                        f"User still not found in MongoDB - status {check_response.status_code}",
                        f"Response: {check_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "User Creation via /auth/me", 
                    False, 
                    f"/auth/me failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Creation via /auth/me", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_direct_user_creation(self):
        """Test creating user directly in MongoDB via login process"""
        try:
            # Create a new test user to see the full creation process
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_email = f"synctest_{timestamp}@example.com"
            
            # First signup
            signup_payload = {
                "email": test_email,
                "handle": f"synctest_{timestamp}",
                "name": f"Sync Test User {timestamp}",
                "password": "testpassword123"
            }
            
            signup_response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                test_user_id = signup_data['user']['id']
                
                # Check if user exists in MongoDB immediately
                check_response = self.session.get(f"{BACKEND_URL}/users/{test_user_id}")
                
                if check_response.status_code == 200:
                    self.log_result(
                        "Direct User Creation (Signup)", 
                        True, 
                        f"New user successfully created and found in MongoDB",
                        f"User ID: {test_user_id}"
                    )
                    
                    # Now test friend request with this new user
                    self.session.post(f"{BACKEND_URL}/seed")  # Ensure u1 exists
                    
                    friend_params = {
                        'fromUserId': test_user_id,
                        'toUserId': 'u1'
                    }
                    
                    friend_response = self.session.post(f"{BACKEND_URL}/friends/request", params=friend_params)
                    
                    if friend_response.status_code == 200:
                        self.log_result(
                            "Friend Request with New User", 
                            True, 
                            "Friend request successful with newly created user",
                            "User creation and friend system working correctly"
                        )
                        return True
                    else:
                        self.log_result(
                            "Friend Request with New User", 
                            False, 
                            f"Friend request failed with new user - status {friend_response.status_code}",
                            f"Response: {friend_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Direct User Creation (Signup)", 
                        False, 
                        f"New user not found in MongoDB - status {check_response.status_code}",
                        f"Response: {check_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Direct User Creation (Signup)", 
                    False, 
                    f"Signup failed with status {signup_response.status_code}",
                    f"Response: {signup_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Direct User Creation", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all user sync tests"""
        print("=" * 80)
        print("USER SYNCHRONIZATION TESTING")
        print("=" * 80)
        
        # Test login and sync
        self.test_demo_login_and_sync()
        
        # Test multiple logins
        print("\n" + "=" * 50)
        print("MULTIPLE LOGIN CONSISTENCY TEST")
        print("=" * 50)
        self.test_multiple_logins()
        
        # Test /auth/me user creation
        print("\n" + "=" * 50)
        print("USER CREATION VIA /AUTH/ME")
        print("=" * 50)
        self.test_user_creation_via_auth_me()
        
        # Test friend request after sync
        print("\n" + "=" * 50)
        print("FRIEND REQUEST AFTER SYNC")
        print("=" * 50)
        self.test_friend_request_after_sync()
        
        # Test direct user creation
        print("\n" + "=" * 50)
        print("DIRECT USER CREATION TEST")
        print("=" * 50)
        self.test_direct_user_creation()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print("\n" + "=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = UserSyncTester()
    results = tester.run_all_tests()