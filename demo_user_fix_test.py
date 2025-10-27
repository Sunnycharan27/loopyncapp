#!/usr/bin/env python3
"""
Demo User Data Consistency Fix Test
Addresses the root cause: Demo user from Google Sheets auth vs MongoDB seeded users mismatch
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class DemoUserFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        
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
    
    def test_1_demo_user_login_and_id(self):
        """Test 1: Verify Demo User Login and Capture ID"""
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
                    
                    self.log_result(
                        "Demo User Login", 
                        True, 
                        f"Demo user logged in successfully",
                        f"User ID: {self.demo_user_id}, Name: {user.get('name')}, Email: {user.get('email')}"
                    )
                else:
                    self.log_result(
                        "Demo User Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo User Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Login", False, f"Exception occurred: {str(e)}")
    
    def test_2_check_demo_user_in_mongodb(self):
        """Test 2: Check if Demo User Exists in MongoDB Users Collection"""
        if not self.demo_user_id:
            self.log_result("Demo User in MongoDB", False, "Skipped - no demo user ID")
            return
            
        try:
            # Try to get the demo user via the users API
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Demo User in MongoDB", 
                    True, 
                    f"Demo user found in MongoDB users collection",
                    f"User: {data.get('name')} ({data.get('handle')}) - {data.get('email')}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Demo User in MongoDB", 
                    False, 
                    "Demo user NOT found in MongoDB users collection (404)",
                    "This is the root cause of the friendship issues"
                )
            else:
                self.log_result(
                    "Demo User in MongoDB", 
                    False, 
                    f"Unexpected status {response.status_code} when checking demo user",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User in MongoDB", False, f"Exception occurred: {str(e)}")
    
    def test_3_create_demo_user_in_mongodb(self):
        """Test 3: Create Demo User in MongoDB if Missing"""
        if not self.demo_user_id:
            self.log_result("Create Demo User in MongoDB", False, "Skipped - no demo user ID")
            return
            
        try:
            # First check if user already exists
            check_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if check_response.status_code == 200:
                self.log_result(
                    "Create Demo User in MongoDB", 
                    True, 
                    "Demo user already exists in MongoDB",
                    "No creation needed"
                )
                return
            
            # Create the demo user by calling a protected endpoint that triggers user creation
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            # The /auth/me endpoint should create the user in MongoDB if it doesn't exist
            me_response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                
                # Now check if the user exists in the users collection
                check_again_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
                
                if check_again_response.status_code == 200:
                    user_data = check_again_response.json()
                    self.log_result(
                        "Create Demo User in MongoDB", 
                        True, 
                        "Demo user successfully created/synced in MongoDB",
                        f"User: {user_data.get('name')} ({user_data.get('handle')})"
                    )
                else:
                    self.log_result(
                        "Create Demo User in MongoDB", 
                        False, 
                        "Demo user still not found in MongoDB after /auth/me call",
                        f"Status: {check_again_response.status_code}"
                    )
            else:
                self.log_result(
                    "Create Demo User in MongoDB", 
                    False, 
                    f"/auth/me call failed with status {me_response.status_code}",
                    f"Response: {me_response.text}"
                )
                
        except Exception as e:
            self.log_result("Create Demo User in MongoDB", False, f"Exception occurred: {str(e)}")
    
    def test_4_seed_compatible_users(self):
        """Test 4: Seed Users and Ensure Demo User Can Interact"""
        try:
            # Seed the database
            seed_response = self.session.post(f"{BACKEND_URL}/seed")
            
            if seed_response.status_code == 200:
                seed_data = seed_response.json()
                self.log_result(
                    "Seed Compatible Users", 
                    True, 
                    f"Successfully seeded database",
                    f"Created: {seed_data.get('users', 0)} users, {seed_data.get('posts', 0)} posts"
                )
            else:
                self.log_result(
                    "Seed Compatible Users", 
                    False, 
                    f"Seed operation failed with status {seed_response.status_code}",
                    f"Response: {seed_response.text}"
                )
                
        except Exception as e:
            self.log_result("Seed Compatible Users", False, f"Exception occurred: {str(e)}")
    
    def test_5_demo_user_friend_request_to_seeded_user(self):
        """Test 5: Test Friend Request from Demo User to Seeded User"""
        if not self.demo_user_id:
            self.log_result("Demo User Friend Request", False, "Skipped - no demo user ID")
            return
            
        try:
            # Try to send friend request from demo user to u1
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Demo User Friend Request", 
                        True, 
                        f"Friend request successful: {data.get('message')}",
                        f"Now friends: {data.get('nowFriends', False)}"
                    )
                else:
                    self.log_result(
                        "Demo User Friend Request", 
                        False, 
                        f"Friend request failed: {data.get('message')}",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                data = response.json()
                self.log_result(
                    "Demo User Friend Request", 
                    False, 
                    "Friend request failed - User not found (404)",
                    f"This confirms demo user is not properly synced to MongoDB. Response: {data}"
                )
            else:
                self.log_result(
                    "Demo User Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_6_accept_friend_request_u1_to_demo(self):
        """Test 6: Accept Friend Request from u1 to Demo User"""
        if not self.demo_user_id:
            self.log_result("Accept Friend Request u1->Demo", False, "Skipped - no demo user ID")
            return
            
        try:
            # Accept friend request from u1's perspective
            params = {
                'userId': 'u1',
                'friendId': self.demo_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Accept Friend Request u1->Demo", 
                    True, 
                    f"Friend request accepted: {data.get('message')}",
                    f"Response: {data}"
                )
            elif response.status_code == 400:
                data = response.json()
                detail = data.get('detail', '').lower()
                if "no pending" in detail:
                    self.log_result(
                        "Accept Friend Request u1->Demo", 
                        False, 
                        "No pending friend request found",
                        "Demo user's friend request may not have been created properly"
                    )
                else:
                    self.log_result(
                        "Accept Friend Request u1->Demo", 
                        False, 
                        f"Accept failed: {data.get('detail')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Accept Friend Request u1->Demo", 
                    False, 
                    f"Accept failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Accept Friend Request u1->Demo", False, f"Exception occurred: {str(e)}")
    
    def test_7_verify_demo_user_friends_list(self):
        """Test 7: Verify Demo User Now Has Friends"""
        if not self.demo_user_id:
            self.log_result("Verify Demo User Friends", False, "Skipped - no demo user ID")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friends")
            
            if response.status_code == 200:
                friends = response.json()
                if len(friends) > 0:
                    self.log_result(
                        "Verify Demo User Friends", 
                        True, 
                        f"Demo user now has {len(friends)} friends",
                        f"Friends: {[f.get('name', 'Unknown') for f in friends]}"
                    )
                else:
                    self.log_result(
                        "Verify Demo User Friends", 
                        False, 
                        "Demo user still has no friends",
                        "Friendship establishment failed"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Verify Demo User Friends", 
                    False, 
                    "Demo user not found when checking friends (404)",
                    "Demo user still not properly synced to MongoDB"
                )
            else:
                self.log_result(
                    "Verify Demo User Friends", 
                    False, 
                    f"Failed to get friends with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Demo User Friends", False, f"Exception occurred: {str(e)}")
    
    def test_8_dm_thread_creation(self):
        """Test 8: Test DM Thread Creation After Friendship"""
        if not self.demo_user_id:
            self.log_result("DM Thread Creation", False, "Skipped - no demo user ID")
            return
            
        try:
            params = {
                'userId': self.demo_user_id,
                'peerUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                thread_id = data.get('threadId')
                self.log_result(
                    "DM Thread Creation", 
                    True, 
                    f"DM thread created successfully",
                    f"Thread ID: {thread_id}"
                )
            elif response.status_code == 403:
                data = response.json()
                if "friends" in data.get('detail', '').lower():
                    self.log_result(
                        "DM Thread Creation", 
                        False, 
                        "DM thread creation failed - Must be friends",
                        "Friendship was not properly established"
                    )
                else:
                    self.log_result(
                        "DM Thread Creation", 
                        False, 
                        f"DM thread creation failed: {data.get('detail')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "DM Thread Creation", 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Thread Creation", False, f"Exception occurred: {str(e)}")
    
    def test_9_call_initiation_check(self):
        """Test 9: Test Call Initiation (Should Work After Friendship)"""
        if not self.demo_user_id:
            self.log_result("Call Initiation Check", False, "Skipped - no demo user ID")
            return
            
        try:
            # Check if call initiation endpoint exists and works
            params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'voice'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Call Initiation Check", 
                    True, 
                    "Call initiation succeeded (no 403 friends error)",
                    f"Response: {data}"
                )
            elif response.status_code == 403:
                data = response.json()
                if "friends" in data.get('detail', '').lower():
                    self.log_result(
                        "Call Initiation Check", 
                        False, 
                        "Call initiation still failing with 'friends' error",
                        "The original issue persists - demo user cannot call friends"
                    )
                else:
                    self.log_result(
                        "Call Initiation Check", 
                        False, 
                        f"Call initiation failed: {data.get('detail')}",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Call Initiation Check", 
                    False, 
                    "Call initiation endpoint not found (404)",
                    "Endpoint may not be implemented yet"
                )
            elif response.status_code == 422:
                data = response.json()
                self.log_result(
                    "Call Initiation Check", 
                    False, 
                    "Call initiation failed with validation error (422)",
                    f"Endpoint exists but parameter format may be wrong. Response: {data}"
                )
            else:
                self.log_result(
                    "Call Initiation Check", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation Check", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("DEMO USER DATA CONSISTENCY FIX TEST")
        print("Root Cause: Demo user from Google Sheets auth vs MongoDB seeded users mismatch")
        print("=" * 80)
        
        self.test_1_demo_user_login_and_id()
        self.test_2_check_demo_user_in_mongodb()
        self.test_3_create_demo_user_in_mongodb()
        self.test_4_seed_compatible_users()
        self.test_5_demo_user_friend_request_to_seeded_user()
        self.test_6_accept_friend_request_u1_to_demo()
        self.test_7_verify_demo_user_friends_list()
        self.test_8_dm_thread_creation()
        self.test_9_call_initiation_check()
        
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
        
        print("\nFailed Tests:")
        for result in self.test_results:
            if not result['success']:
                print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\nKey Findings:")
        if self.demo_user_id:
            print(f"  • Demo User ID: {self.demo_user_id}")
        
        # Root cause analysis
        mongodb_exists = any(r['test'] == 'Demo User in MongoDB' and r['success'] for r in self.test_results)
        friends_working = any(r['test'] == 'Verify Demo User Friends' and r['success'] for r in self.test_results)
        dm_working = any(r['test'] == 'DM Thread Creation' and r['success'] for r in self.test_results)
        
        print("\n" + "=" * 80)
        print("ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        if not mongodb_exists:
            print("❌ CRITICAL ISSUE: Demo user from Google Sheets auth is not synced to MongoDB")
            print("   This prevents all friend-related functionality from working")
            print("   The demo user exists in Google Sheets but not in the MongoDB users collection")
        elif not friends_working:
            print("⚠️  ISSUE: Demo user exists in MongoDB but friendship establishment failed")
            print("   Friend request/accept flow has issues")
        elif not dm_working:
            print("⚠️  ISSUE: Friendship works but DM thread creation failed")
            print("   DM system may have additional friendship validation")
        else:
            print("✅ SUCCESS: All systems working - demo user can now interact with friends")

if __name__ == "__main__":
    tester = DemoUserFixTester()
    tester.run_all_tests()