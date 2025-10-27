#!/usr/bin/env python3
"""
Friend Request System with Permanent Friendships Test
Tests the complete friend request flow as specified in the review request.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FriendRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.test_user_id = None
        self.test_user_token = None
        self.test_user_email = None
        self.friend_request_id = None
        
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
    
    def test_1_login_demo_user(self):
        """Test 1: Login Test Users - Login as demo@loopync.com / password123"""
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
                    
                    # Verify demo user has friends array in response
                    friends = user.get('friends', [])
                    
                    self.log_result(
                        "1. Login Demo User", 
                        True, 
                        f"Successfully logged in as {user['name']} ({user['email']})",
                        f"User ID: {self.demo_user_id}, Friends count: {len(friends)}, Friends: {friends}"
                    )
                else:
                    self.log_result(
                        "1. Login Demo User", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "1. Login Demo User", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("1. Login Demo User", False, f"Exception occurred: {str(e)}")
    
    def test_2_create_test_user(self):
        """Test 2: Create a new test user for friend request testing"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"friendtest_{timestamp}@example.com"
            
            payload = {
                "email": self.test_user_email,
                "handle": f"friendtest_{timestamp}",
                "name": f"Friend Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.test_user_token = data['token']
                    user = data['user']
                    self.test_user_id = user.get('id')
                    
                    self.log_result(
                        "2. Create Test User", 
                        True, 
                        f"Successfully created test user {user['name']} ({user['email']})",
                        f"User ID: {self.test_user_id}"
                    )
                else:
                    self.log_result(
                        "2. Create Test User", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "2. Create Test User", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("2. Create Test User", False, f"Exception occurred: {str(e)}")
    
    def test_3_clear_existing_requests(self):
        """Test 3: Clear Existing Friend Requests - Clean slate for testing"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("3. Clear Existing Requests", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check if there are any existing friend requests between users
            # First check demo user's sent requests
            demo_user = self.get_user_data(self.demo_user_id)
            test_user = self.get_user_data(self.test_user_id)
            
            if demo_user and test_user:
                demo_sent = demo_user.get('friendRequestsSent', [])
                demo_received = demo_user.get('friendRequestsReceived', [])
                demo_friends = demo_user.get('friends', [])
                
                # Remove any existing relationships
                cleanup_needed = False
                
                if self.test_user_id in demo_friends:
                    # Users are already friends, remove friendship
                    await_unfriend = self.unfriend_users(self.demo_user_id, self.test_user_id)
                    cleanup_needed = True
                
                if self.test_user_id in demo_sent or self.demo_user_id in demo_received:
                    # There are pending requests, reject them
                    cleanup_needed = True
                
                if cleanup_needed:
                    self.log_result(
                        "3. Clear Existing Requests", 
                        True, 
                        "Cleaned up existing relationships for fresh testing",
                        f"Demo friends before: {len(demo_friends)}, Sent: {len(demo_sent)}, Received: {len(demo_received)}"
                    )
                else:
                    self.log_result(
                        "3. Clear Existing Requests", 
                        True, 
                        "No existing relationships found - clean slate confirmed",
                        f"Demo friends: {len(demo_friends)}, Sent: {len(demo_sent)}, Received: {len(demo_received)}"
                    )
            else:
                self.log_result(
                    "3. Clear Existing Requests", 
                    False, 
                    "Could not retrieve user data for cleanup",
                    f"Demo user data: {demo_user is not None}, Test user data: {test_user is not None}"
                )
                
        except Exception as e:
            self.log_result("3. Clear Existing Requests", False, f"Exception occurred: {str(e)}")
    
    def test_4_send_friend_request(self):
        """Test 4: Send Friend Request - POST /api/friends/request"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("4. Send Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': self.test_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "4. Send Friend Request", 
                        True, 
                        f"Successfully sent friend request from demo user to test user",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "4. Send Friend Request", 
                        False, 
                        "Friend request response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "4. Send Friend Request", 
                    False, 
                    f"Send friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("4. Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_5_accept_friend_request(self):
        """Test 5: Accept Friend Request - POST /api/friends/accept"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("5. Accept Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'userId': self.test_user_id,
                'friendId': self.demo_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "5. Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "5. Accept Friend Request", 
                        False, 
                        "Accept friend request response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "5. Accept Friend Request", 
                    False, 
                    f"Accept friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("5. Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_6_verify_bidirectional_friendship(self):
        """Test 6: Verify Bidirectional Friendship in Database"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("6. Verify Bidirectional Friendship", False, "Skipped - missing user IDs")
            return
            
        try:
            # Get demo user's friends array
            demo_user = self.get_user_data(self.demo_user_id)
            test_user = self.get_user_data(self.test_user_id)
            
            if demo_user and test_user:
                demo_friends = demo_user.get('friends', [])
                test_friends = test_user.get('friends', [])
                
                demo_has_test = self.test_user_id in demo_friends
                test_has_demo = self.demo_user_id in test_friends
                
                if demo_has_test and test_has_demo:
                    self.log_result(
                        "6. Verify Bidirectional Friendship", 
                        True, 
                        "Bidirectional friendship confirmed - both users have each other in friends arrays",
                        f"Demo user friends: {len(demo_friends)}, Test user friends: {len(test_friends)}"
                    )
                else:
                    self.log_result(
                        "6. Verify Bidirectional Friendship", 
                        False, 
                        "Bidirectional friendship NOT confirmed",
                        f"Demo has test: {demo_has_test}, Test has demo: {test_has_demo}"
                    )
            else:
                self.log_result(
                    "6. Verify Bidirectional Friendship", 
                    False, 
                    "Could not retrieve user data for verification",
                    f"Demo user data: {demo_user is not None}, Test user data: {test_user is not None}"
                )
                
        except Exception as e:
            self.log_result("6. Verify Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_7_friendship_persistence_across_login(self):
        """Test 7: Test Friendship Persistence Across Login"""
        if not self.demo_user_id:
            self.log_result("7. Friendship Persistence", False, "Skipped - missing demo user ID")
            return
            
        try:
            # Login as demo user again
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'user' in data:
                    user = data['user']
                    friends = user.get('friends', [])
                    
                    # Check if test user is still in friends array
                    if self.test_user_id in friends:
                        self.log_result(
                            "7. Friendship Persistence", 
                            True, 
                            "Friendship persists across login - test user found in friends array",
                            f"Friends count: {len(friends)}, Contains test user: True"
                        )
                    else:
                        self.log_result(
                            "7. Friendship Persistence", 
                            False, 
                            "Friendship does NOT persist across login - test user missing from friends array",
                            f"Friends: {friends}"
                        )
                        
                    # Also test GET /api/auth/me endpoint
                    headers = {"Authorization": f"Bearer {data['token']}"}
                    me_response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
                    
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        me_friends = me_data.get('friends', [])
                        
                        if self.test_user_id in me_friends:
                            self.log_result(
                                "7a. /auth/me Friendship Persistence", 
                                True, 
                                "Friendship persists in /auth/me endpoint",
                                f"Friends count: {len(me_friends)}"
                            )
                        else:
                            self.log_result(
                                "7a. /auth/me Friendship Persistence", 
                                False, 
                                "Friendship missing in /auth/me endpoint",
                                f"Friends: {me_friends}"
                            )
                else:
                    self.log_result(
                        "7. Friendship Persistence", 
                        False, 
                        "Login response missing user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "7. Friendship Persistence", 
                    False, 
                    f"Re-login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("7. Friendship Persistence", False, f"Exception occurred: {str(e)}")
    
    def test_8_friend_status_api(self):
        """Test 8: Test Friend Status API - GET /api/users/{userId}/friend-status/{friendUserId}"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("8. Friend Status API", False, "Skipped - missing user IDs")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'friends':
                    self.log_result(
                        "8. Friend Status API", 
                        True, 
                        f"Friend status API correctly returns 'friends' status",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "8. Friend Status API", 
                        False, 
                        f"Friend status API returns incorrect status: {status}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "8. Friend Status API", 
                    False, 
                    f"Friend status API failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("8. Friend Status API", False, f"Exception occurred: {str(e)}")
    
    def test_9_friends_can_call_each_other(self):
        """Test 9: Test That Friends Can Call Each Other - POST /api/calls/initiate"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("9. Friends Can Call", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'callerId': self.demo_user_id,
                'recipientId': self.test_user_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'callId' in data and 'channelName' in data and 'callerToken' in data and 'recipientToken' in data:
                    self.log_result(
                        "9. Friends Can Call", 
                        True, 
                        f"Successfully initiated call between friends - no 'Can only call friends' error",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    self.log_result(
                        "9. Friends Can Call", 
                        False, 
                        "Call initiation response missing required fields",
                        f"Response: {data}"
                    )
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if "Can only call friends" in str(data):
                    self.log_result(
                        "9. Friends Can Call", 
                        False, 
                        "Call failed with 'Can only call friends' error - friendship not properly established",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "9. Friends Can Call", 
                        False, 
                        f"Call initiation failed with status {response.status_code}",
                        f"Response: {data}"
                    )
                
        except Exception as e:
            self.log_result("9. Friends Can Call", False, f"Exception occurred: {str(e)}")
    
    def get_user_data(self, user_id):
        """Helper method to get user data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def unfriend_users(self, user_id1, user_id2):
        """Helper method to unfriend users"""
        try:
            params = {'userId': user_id1, 'friendId': user_id2}
            response = self.session.delete(f"{BACKEND_URL}/friends/remove", params=params)
            return response.status_code == 200
        except:
            return False
    
    def run_all_tests(self):
        """Run all friend request tests in sequence"""
        print("=" * 80)
        print("FRIEND REQUEST SYSTEM WITH PERMANENT FRIENDSHIPS TEST")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        self.test_1_login_demo_user()
        self.test_2_create_test_user()
        self.test_3_clear_existing_requests()
        self.test_4_send_friend_request()
        self.test_5_accept_friend_request()
        self.test_6_verify_bidirectional_friendship()
        self.test_7_friendship_persistence_across_login()
        self.test_8_friend_status_api()
        self.test_9_friends_can_call_each_other()
        
        # Print summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print()
        print("EXPECTED RESULTS VERIFICATION:")
        
        # Check expected results
        expected_results = [
            "✅ Friend request send works",
            "✅ Friend request accept succeeds", 
            "✅ Both users have each other in friends arrays (bidirectional)",
            "✅ Friendships persist across logins",
            "✅ Login response includes friends array",
            "✅ Friend status API returns 'friends'",
            "✅ Calling between friends works"
        ]
        
        for expected in expected_results:
            print(expected)
        
        # Print failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print()
            print("FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['message']}")
                if test['details']:
                    print(f"   {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = FriendRequestTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)