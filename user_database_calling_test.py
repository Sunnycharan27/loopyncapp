#!/usr/bin/env python3
"""
User Database Issue for Calling Functionality - Comprehensive Test
Tests the specific issue: "Failed to start call" error because currentUser.id doesn't exist in MongoDB users collection.

Investigation and Fix Sequence:
1. Check Current Logged-in User (demo@loopync.com / password123)
2. Verify User Exists in MongoDB
3. Check Database User Records
4. Fix: Ensure Login Creates/Updates User in MongoDB
5. Manual Fix if Needed
6. Verify Friends Relationship
7. Re-test Call Initiation
8. Test Login Flow
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class UserDatabaseCallingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.friends_list = []
        
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
    
    def test_1_check_current_logged_in_user(self):
        """Test 1: Check Current Logged-in User (demo@loopync.com / password123)"""
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
                    self.demo_user_id = user.get('id')
                    
                    # Capture the exact user ID returned in login response
                    self.log_result(
                        "Check Current Logged-in User", 
                        True, 
                        f"Successfully logged in as {user['name']} ({user['email']})",
                        f"User ID captured: {self.demo_user_id}, Token: {self.demo_token[:20]}..."
                    )
                    
                    # Store friends list for later verification
                    self.friends_list = user.get('friends', [])
                    print(f"   Friends array: {self.friends_list}")
                    
                else:
                    self.log_result(
                        "Check Current Logged-in User", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Check Current Logged-in User", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Check Current Logged-in User", False, f"Exception occurred: {str(e)}")
    
    def test_2_verify_user_exists_in_mongodb(self):
        """Test 2: Verify User Exists in MongoDB"""
        if not self.demo_user_id:
            self.log_result("Verify User Exists in MongoDB", False, "Skipped - no demo user ID available")
            return
            
        try:
            # GET /api/users/{user_id_from_login}
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data['id'] == self.demo_user_id:
                    self.log_result(
                        "Verify User Exists in MongoDB", 
                        True, 
                        f"User document exists in MongoDB with ID: {self.demo_user_id}",
                        f"User data: {data.get('name')} ({data.get('email')}) - Handle: @{data.get('handle')}"
                    )
                    
                    # Check if user has friends for calling
                    friends = data.get('friends', [])
                    print(f"   MongoDB friends array: {friends}")
                    
                else:
                    self.log_result(
                        "Verify User Exists in MongoDB", 
                        False, 
                        "User document found but ID mismatch",
                        f"Expected: {self.demo_user_id}, Found: {data.get('id')}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Verify User Exists in MongoDB", 
                    False, 
                    f"User not found in MongoDB - This confirms the issue!",
                    f"User ID {self.demo_user_id} does not exist in users collection"
                )
            else:
                self.log_result(
                    "Verify User Exists in MongoDB", 
                    False, 
                    f"Failed to check user existence with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify User Exists in MongoDB", False, f"Exception occurred: {str(e)}")
    
    def test_3_check_database_user_records(self):
        """Test 3: Check Database User Records"""
        try:
            # GET /api/users/search?q=Sunnycharan
            response1 = self.session.get(f"{BACKEND_URL}/users/search", params={'q': 'Sunnycharan'})
            
            if response1.status_code == 200:
                data1 = response1.json()
                self.log_result(
                    "Search Users - Sunnycharan", 
                    True, 
                    f"Found {len(data1)} users matching 'Sunnycharan'",
                    f"Users: {[u.get('name', 'Unknown') for u in data1]}"
                )
            else:
                self.log_result(
                    "Search Users - Sunnycharan", 
                    False, 
                    f"Search failed with status {response1.status_code}",
                    f"Response: {response1.text}"
                )
            
            # GET /api/users/search?q=demo
            response2 = self.session.get(f"{BACKEND_URL}/users/search", params={'q': 'demo'})
            
            if response2.status_code == 200:
                data2 = response2.json()
                self.log_result(
                    "Search Users - demo", 
                    True, 
                    f"Found {len(data2)} users matching 'demo'",
                    f"Users: {[u.get('name', 'Unknown') + ' (' + u.get('email', 'No email') + ')' for u in data2]}"
                )
                
                # Check if our demo user is in the search results
                demo_found = False
                for user in data2:
                    if user.get('id') == self.demo_user_id or user.get('email') == DEMO_EMAIL:
                        demo_found = True
                        print(f"   Demo user found in search: {user}")
                        break
                
                if not demo_found:
                    print(f"   WARNING: Demo user {self.demo_user_id} not found in search results")
                    
            else:
                self.log_result(
                    "Search Users - demo", 
                    False, 
                    f"Search failed with status {response2.status_code}",
                    f"Response: {response2.text}"
                )
                
        except Exception as e:
            self.log_result("Check Database User Records", False, f"Exception occurred: {str(e)}")
    
    def test_4_ensure_login_creates_user_in_mongodb(self):
        """Test 4: Fix - Ensure Login Creates/Updates User in MongoDB"""
        if not self.demo_user_id:
            self.log_result("Ensure Login Creates User", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Check the login endpoint logic (around line 1104-1210 in server.py)
            # The login should create user in MongoDB if not exists
            
            # First, let's verify the current state by calling /auth/me
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Verify Auth/Me Endpoint", 
                    True, 
                    f"Auth/me working - User: {data.get('name')} ({data.get('email')})",
                    f"User ID: {data.get('id')}, Friends: {data.get('friends', [])}"
                )
                
                # Check if this user has friends for testing
                friends = data.get('friends', [])
                if len(friends) == 0:
                    print(f"   WARNING: User has no friends - this will cause calling to fail")
                else:
                    print(f"   User has {len(friends)} friends: {friends}")
                    
            else:
                self.log_result(
                    "Verify Auth/Me Endpoint", 
                    False, 
                    f"Auth/me failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Ensure Login Creates User", False, f"Exception occurred: {str(e)}")
    
    def test_5_manual_fix_if_needed(self):
        """Test 5: Manual Fix if Needed - Create user in MongoDB if not exists"""
        if not self.demo_user_id:
            self.log_result("Manual Fix User Creation", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Check if user exists in MongoDB again
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 404:
                # User doesn't exist, we need to create it manually
                # This would typically be done by the backend, but let's verify the issue
                self.log_result(
                    "Manual Fix - User Missing", 
                    False, 
                    f"CONFIRMED: User {self.demo_user_id} missing from MongoDB users collection",
                    "This is the root cause of the calling issue - user not in MongoDB"
                )
                
                # The fix should be in the login endpoint to ensure user is created in MongoDB
                # Let's try logging in again to trigger user creation
                payload = {
                    "email": DEMO_EMAIL,
                    "password": DEMO_PASSWORD
                }
                
                login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    new_user_id = login_data.get('user', {}).get('id')
                    
                    # Check if user now exists in MongoDB
                    check_response = self.session.get(f"{BACKEND_URL}/users/{new_user_id}")
                    
                    if check_response.status_code == 200:
                        self.log_result(
                            "Manual Fix - Re-login Success", 
                            True, 
                            f"User now exists in MongoDB after re-login",
                            f"User ID: {new_user_id}"
                        )
                        self.demo_user_id = new_user_id  # Update for subsequent tests
                    else:
                        self.log_result(
                            "Manual Fix - Re-login Failed", 
                            False, 
                            f"User still missing from MongoDB after re-login",
                            f"Check response: {check_response.status_code}"
                        )
                        
            elif response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Manual Fix - User Exists", 
                    True, 
                    f"User already exists in MongoDB",
                    f"User: {data.get('name')} with {len(data.get('friends', []))} friends"
                )
                
        except Exception as e:
            self.log_result("Manual Fix User Creation", False, f"Exception occurred: {str(e)}")
    
    def test_6_verify_friends_relationship(self):
        """Test 6: Verify Friends Relationship"""
        if not self.demo_user_id:
            self.log_result("Verify Friends Relationship", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Get user's friends array
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get('friends', [])
                
                if len(friends) > 0:
                    self.log_result(
                        "Verify Friends Relationship", 
                        True, 
                        f"User has {len(friends)} friends for calling",
                        f"Friends: {friends}"
                    )
                    
                    # Check if Ram Charan (or test users) are in friends array
                    test_friends = ['u1', 'u2', 'u3']  # Common test user IDs
                    found_test_friends = [f for f in friends if f in test_friends]
                    
                    if found_test_friends:
                        print(f"   Test friends found: {found_test_friends}")
                    else:
                        print(f"   No test friends (u1, u2, u3) found in friends array")
                        
                else:
                    self.log_result(
                        "Verify Friends Relationship", 
                        False, 
                        f"User has no friends - this will cause calling to fail",
                        "Need to add friends for testing calling functionality"
                    )
                    
            else:
                self.log_result(
                    "Verify Friends Relationship", 
                    False, 
                    f"Failed to get user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Friends Relationship", False, f"Exception occurred: {str(e)}")
    
    def test_7_retest_call_initiation(self):
        """Test 7: Re-test Call Initiation"""
        if not self.demo_user_id:
            self.log_result("Re-test Call Initiation", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Get user's friends to test calling
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if user_response.status_code != 200:
                self.log_result("Re-test Call Initiation", False, "Cannot get user data for calling test")
                return
                
            user_data = user_response.json()
            friends = user_data.get('friends', [])
            
            if len(friends) == 0:
                self.log_result(
                    "Re-test Call Initiation", 
                    False, 
                    "Cannot test calling - user has no friends",
                    "Need friends relationship for calling to work"
                )
                return
            
            # Try to initiate a call with the first friend
            recipient_id = friends[0]
            
            # POST /api/calls/initiate with corrected user IDs
            params = {
                'callerId': self.demo_user_id,
                'recipientId': recipient_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'callId' in data and 'channelName' in data:
                    self.log_result(
                        "Re-test Call Initiation", 
                        True, 
                        f"Call initiation successful! No 'Caller not found' error",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    self.log_result(
                        "Re-test Call Initiation", 
                        False, 
                        "Call response missing required fields",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if "Caller not found" in str(error_data):
                    self.log_result(
                        "Re-test Call Initiation", 
                        False, 
                        "ISSUE CONFIRMED: 'Caller not found' error - user not in MongoDB",
                        f"Error: {error_data}"
                    )
                else:
                    self.log_result(
                        "Re-test Call Initiation", 
                        False, 
                        f"Call failed with 404 but different error: {error_data}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "Re-test Call Initiation", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Re-test Call Initiation", False, f"Exception occurred: {str(e)}")
    
    def test_8_test_login_flow(self):
        """Test 8: Test Login Flow - Logout and login again"""
        try:
            # Test the complete login flow to verify user data persists
            
            # Step 1: Logout (clear current session)
            self.demo_token = None
            
            # Step 2: Login again
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    new_token = data['token']
                    user = data['user']
                    new_user_id = user.get('id')
                    
                    # Step 3: Verify user data persists in MongoDB
                    user_check = self.session.get(f"{BACKEND_URL}/users/{new_user_id}")
                    
                    if user_check.status_code == 200:
                        user_data = user_check.json()
                        friends = user_data.get('friends', [])
                        
                        self.log_result(
                            "Test Login Flow", 
                            True, 
                            f"Login flow working - user persists in MongoDB",
                            f"User ID: {new_user_id}, Friends: {len(friends)}"
                        )
                        
                        # Step 4: Confirm auto-friending logic works
                        if len(friends) > 0:
                            print(f"   Auto-friending working: {friends}")
                        else:
                            print(f"   WARNING: No friends after login - auto-friending may not be working")
                            
                    else:
                        self.log_result(
                            "Test Login Flow", 
                            False, 
                            f"User missing from MongoDB after fresh login",
                            f"User check status: {user_check.status_code}"
                        )
                        
                else:
                    self.log_result(
                        "Test Login Flow", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test Login Flow", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Login Flow", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("USER DATABASE ISSUE FOR CALLING FUNCTIONALITY - COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {DEMO_EMAIL}")
        print("=" * 80)
        
        # Run tests in sequence
        self.test_1_check_current_logged_in_user()
        self.test_2_verify_user_exists_in_mongodb()
        self.test_3_check_database_user_records()
        self.test_4_ensure_login_creates_user_in_mongodb()
        self.test_5_manual_fix_if_needed()
        self.test_6_verify_friends_relationship()
        self.test_7_retest_call_initiation()
        self.test_8_test_login_flow()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if not result['success'] and result['details']:
                print(f"   Issue: {result['details']}")
        
        print("\n" + "=" * 80)
        print("EXPECTED RESULTS VERIFICATION:")
        print("=" * 80)
        
        # Check if we achieved the expected results
        user_id_captured = self.demo_user_id is not None
        user_in_mongodb = any("User document exists in MongoDB" in r['message'] for r in self.test_results if r['success'])
        friends_verified = any("friends for calling" in r['message'] for r in self.test_results if r['success'])
        call_works = any("Call initiation successful" in r['message'] for r in self.test_results if r['success'])
        
        print(f"✅ Identify exact user ID that's logging in: {'YES' if user_id_captured else 'NO'}")
        print(f"✅ Find/fix user record in MongoDB: {'YES' if user_in_mongodb else 'NO'}")
        print(f"✅ Ensure user has friends for calling: {'YES' if friends_verified else 'NO'}")
        print(f"✅ Call initiation works after fix: {'YES' if call_works else 'NO'}")
        
        if user_id_captured:
            print(f"\nDemo User ID: {self.demo_user_id}")
        
        return self.test_results

if __name__ == "__main__":
    tester = UserDatabaseCallingTester()
    results = tester.run_all_tests()