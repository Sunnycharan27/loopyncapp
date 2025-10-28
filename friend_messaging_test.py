#!/usr/bin/env python3
"""
Friend Request and Messaging System Test
Tests the specific scenario: "You can only call friends" error in Messenger
Root cause: demo user has no friends in database
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FriendMessagingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.available_users = []
        self.friend_user_id = None
        self.dm_thread_id = None
        
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
    
    def test_1_demo_user_login(self):
        """Test 1: Verify Demo User Login and ID"""
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
                    
                    if self.demo_user_id and user.get('email') == DEMO_EMAIL:
                        self.log_result(
                            "Demo User Login", 
                            True, 
                            f"Successfully logged in as {user.get('name', 'Unknown')}",
                            f"User ID: {self.demo_user_id}, Email: {user.get('email')}"
                        )
                    else:
                        self.log_result(
                            "Demo User Login", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
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
    
    def test_2_demo_user_friends_list(self):
        """Test 2: Check Demo User's Current Friends List"""
        if not self.demo_token:
            self.log_result("Demo User Friends List", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get('friends', [])
                
                self.log_result(
                    "Demo User Friends List", 
                    True, 
                    f"Demo user currently has {len(friends)} friends",
                    f"Friends list: {friends}"
                )
                
                # Also check via friends endpoint
                if self.demo_user_id:
                    friends_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friends")
                    if friends_response.status_code == 200:
                        friends_data = friends_response.json()
                        self.log_result(
                            "Demo User Friends API", 
                            True, 
                            f"Friends API returned {len(friends_data)} friends",
                            f"Friends: {[f.get('name', 'Unknown') for f in friends_data[:3]]}"
                        )
                    
            else:
                self.log_result(
                    "Demo User Friends List", 
                    False, 
                    f"Failed to get user profile with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Friends List", False, f"Exception occurred: {str(e)}")
    
    def test_3_find_available_users(self):
        """Test 3: Find Available Users to Befriend"""
        try:
            # First, seed data to ensure we have users
            seed_response = self.session.post(f"{BACKEND_URL}/seed")
            if seed_response.status_code == 200:
                print("   Seeded test data successfully")
            
            # Search for users
            search_response = self.session.get(f"{BACKEND_URL}/users/search", params={'q': 'sunnyram'})
            
            if search_response.status_code == 200:
                search_users = search_response.json()
                if search_users:
                    self.log_result(
                        "Find Sunnyram User", 
                        True, 
                        f"Found {len(search_users)} users matching 'sunnyram'",
                        f"Users: {[u.get('name', 'Unknown') for u in search_users]}"
                    )
                    # Use first user as potential friend
                    if search_users[0].get('id') != self.demo_user_id:
                        self.friend_user_id = search_users[0].get('id')
                        self.available_users.extend(search_users)
            
            # Get all users if search didn't work
            if not self.available_users:
                users_response = self.session.get(f"{BACKEND_URL}/users", params={'limit': 10})
                
                if users_response.status_code == 200:
                    all_users = users_response.json()
                    # Filter out demo user
                    available = [u for u in all_users if u.get('id') != self.demo_user_id]
                    self.available_users = available
                    
                    if available:
                        self.friend_user_id = available[0].get('id')
                        self.log_result(
                            "Find Available Users", 
                            True, 
                            f"Found {len(available)} available users to befriend",
                            f"First user: {available[0].get('name', 'Unknown')} (ID: {available[0].get('id')})"
                        )
                    else:
                        self.log_result(
                            "Find Available Users", 
                            False, 
                            "No available users found to befriend",
                            f"Total users: {len(all_users)}"
                        )
                else:
                    self.log_result(
                        "Find Available Users", 
                        False, 
                        f"Failed to get users list with status {users_response.status_code}",
                        f"Response: {users_response.text}"
                    )
            
        except Exception as e:
            self.log_result("Find Available Users", False, f"Exception occurred: {str(e)}")
    
    def test_4_send_friend_request(self):
        """Test 4: Send Friend Request from Demo User to Another User"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Send Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': self.friend_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if data.get('nowFriends'):
                        self.log_result(
                            "Send Friend Request", 
                            True, 
                            "Friend request auto-accepted (users are now friends)",
                            f"Message: {data.get('message', 'No message')}"
                        )
                    else:
                        self.log_result(
                            "Send Friend Request", 
                            True, 
                            "Friend request sent successfully",
                            f"Message: {data.get('message', 'No message')}"
                        )
                else:
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        f"Friend request failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_5_accept_friend_request(self):
        """Test 5: Accept Friend Request (simulate from other user's perspective)"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Accept Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check if friend request exists and needs acceptance
            friend_requests_response = self.session.get(f"{BACKEND_URL}/users/{self.friend_user_id}/friend-requests")
            
            if friend_requests_response.status_code == 200:
                requests_data = friend_requests_response.json()
                received_requests = requests_data.get('received', [])
                
                # Look for request from demo user
                demo_request = None
                for req in received_requests:
                    if req.get('id') == self.demo_user_id:
                        demo_request = req
                        break
                
                if demo_request:
                    # Accept the friend request
                    accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", 
                                                      params={'userId': self.friend_user_id, 'friendId': self.demo_user_id})
                    
                    if accept_response.status_code == 200:
                        accept_data = accept_response.json()
                        self.log_result(
                            "Accept Friend Request", 
                            True, 
                            "Friend request accepted successfully",
                            f"Message: {accept_data.get('message', 'No message')}"
                        )
                    else:
                        self.log_result(
                            "Accept Friend Request", 
                            False, 
                            f"Failed to accept friend request with status {accept_response.status_code}",
                            f"Response: {accept_response.text}"
                        )
                else:
                    # Check if they're already friends
                    friend_status_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/{self.friend_user_id}")
                    if friend_status_response.status_code == 200:
                        status_data = friend_status_response.json()
                        if status_data.get('status') == 'friends':
                            self.log_result(
                                "Accept Friend Request", 
                                True, 
                                "Users are already friends (no pending request to accept)",
                                f"Friend status: {status_data.get('status')}"
                            )
                        else:
                            self.log_result(
                                "Accept Friend Request", 
                                False, 
                                f"No pending friend request found from demo user",
                                f"Received requests: {[r.get('name', 'Unknown') for r in received_requests]}"
                            )
            else:
                self.log_result(
                    "Accept Friend Request", 
                    False, 
                    f"Failed to get friend requests with status {friend_requests_response.status_code}",
                    f"Response: {friend_requests_response.text}"
                )
                
        except Exception as e:
            self.log_result("Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_6_verify_friendship(self):
        """Test 6: Verify Both Users Have Each Other in Friends Arrays"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Verify Friendship", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check demo user's friends list
            demo_friends_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friends")
            
            if demo_friends_response.status_code == 200:
                demo_friends = demo_friends_response.json()
                demo_friend_ids = [f.get('id') for f in demo_friends]
                
                # Check friend user's friends list
                friend_friends_response = self.session.get(f"{BACKEND_URL}/users/{self.friend_user_id}/friends")
                
                if friend_friends_response.status_code == 200:
                    friend_friends = friend_friends_response.json()
                    friend_friend_ids = [f.get('id') for f in friend_friends]
                    
                    demo_has_friend = self.friend_user_id in demo_friend_ids
                    friend_has_demo = self.demo_user_id in friend_friend_ids
                    
                    if demo_has_friend and friend_has_demo:
                        self.log_result(
                            "Verify Friendship", 
                            True, 
                            "Bidirectional friendship established successfully",
                            f"Demo user friends: {len(demo_friends)}, Friend user friends: {len(friend_friends)}"
                        )
                    else:
                        self.log_result(
                            "Verify Friendship", 
                            False, 
                            f"Friendship not bidirectional - Demo has friend: {demo_has_friend}, Friend has demo: {friend_has_demo}",
                            f"Demo friends: {demo_friend_ids}, Friend friends: {friend_friend_ids}"
                        )
                else:
                    self.log_result(
                        "Verify Friendship", 
                        False, 
                        f"Failed to get friend's friends list with status {friend_friends_response.status_code}",
                        f"Response: {friend_friends_response.text}"
                    )
            else:
                self.log_result(
                    "Verify Friendship", 
                    False, 
                    f"Failed to get demo user's friends list with status {demo_friends_response.status_code}",
                    f"Response: {demo_friends_response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_7_create_dm_thread(self):
        """Test 7: Test DM Thread Creation Between Demo User and Friend"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Create DM Thread", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'userId': self.demo_user_id,
                'peerUserId': self.friend_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    self.dm_thread_id = data['threadId']
                    self.log_result(
                        "Create DM Thread", 
                        True, 
                        f"DM thread created successfully",
                        f"Thread ID: {self.dm_thread_id}"
                    )
                else:
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        "DM thread response missing threadId",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # Check if thread already exists
                data = response.json()
                if "already exists" in data.get('detail', '').lower():
                    # Try to get existing thread
                    threads_response = self.session.get(f"{BACKEND_URL}/dm/threads", params={'userId': self.demo_user_id})
                    if threads_response.status_code == 200:
                        threads_data = threads_response.json()
                        threads = threads_data if isinstance(threads_data, list) else threads_data.get('items', [])
                        
                        for thread in threads:
                            if thread.get('peer', {}).get('id') == self.friend_user_id:
                                self.dm_thread_id = thread.get('id')
                                self.log_result(
                                    "Create DM Thread", 
                                    True, 
                                    "DM thread already exists (using existing)",
                                    f"Thread ID: {self.dm_thread_id}"
                                )
                                return
                    
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        "Thread exists but couldn't retrieve ID",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        f"DM thread creation failed: {data.get('detail', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create DM Thread", 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create DM Thread", False, f"Exception occurred: {str(e)}")
    
    def test_8_friend_status_api(self):
        """Test 8: Test Friend Status API"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Friend Status API", False, "Skipped - missing user IDs")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/{self.friend_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'friends':
                    self.log_result(
                        "Friend Status API", 
                        True, 
                        f"Friend status API returned correct status: {status}",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Friend Status API", 
                        False, 
                        f"Friend status API returned unexpected status: {status}",
                        f"Expected: 'friends', Got: {status}"
                    )
            else:
                self.log_result(
                    "Friend Status API", 
                    False, 
                    f"Friend status API failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Friend Status API", False, f"Exception occurred: {str(e)}")
    
    def test_9_call_initiation_api(self):
        """Test 9: Test Call Initiation API"""
        if not self.demo_user_id or not self.friend_user_id:
            self.log_result("Call Initiation API", False, "Skipped - missing user IDs")
            return
            
        try:
            payload = {
                'callerId': self.demo_user_id,
                'recipientId': self.friend_user_id,
                'callType': 'voice'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Call Initiation API", 
                    True, 
                    "Call initiation succeeded (no 403 error)",
                    f"Response: {data}"
                )
            elif response.status_code == 403:
                data = response.json()
                if "only call friends" in data.get('detail', '').lower():
                    self.log_result(
                        "Call Initiation API", 
                        False, 
                        "Call initiation failed with 'You can only call friends' error",
                        f"This indicates the friendship is not properly established. Response: {data}"
                    )
                else:
                    self.log_result(
                        "Call Initiation API", 
                        False, 
                        f"Call initiation failed with 403 error: {data.get('detail', 'Unknown')}",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                # Call initiation endpoint might not exist, check if it's implemented
                self.log_result(
                    "Call Initiation API", 
                    False, 
                    "Call initiation endpoint not found (404) - may not be implemented",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Call Initiation API", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation API", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("FRIEND REQUEST AND MESSAGING SYSTEM TEST")
        print("Testing scenario: 'You can only call friends' error in Messenger")
        print("=" * 80)
        
        self.test_1_demo_user_login()
        self.test_2_demo_user_friends_list()
        self.test_3_find_available_users()
        self.test_4_send_friend_request()
        self.test_5_accept_friend_request()
        self.test_6_verify_friendship()
        self.test_7_create_dm_thread()
        self.test_8_friend_status_api()
        self.test_9_call_initiation_api()
        
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
        if self.friend_user_id:
            print(f"  • Friend User ID: {self.friend_user_id}")
        if self.dm_thread_id:
            print(f"  • DM Thread ID: {self.dm_thread_id}")
        
        # Check if the main issue is resolved
        friends_established = any(r['test'] == 'Verify Friendship' and r['success'] for r in self.test_results)
        call_working = any(r['test'] == 'Call Initiation API' and r['success'] for r in self.test_results)
        
        if friends_established and call_working:
            print("\n✅ SUCCESS: Demo user now has friends and can make calls!")
        elif friends_established:
            print("\n⚠️  PARTIAL SUCCESS: Demo user has friends but call API may need investigation")
        else:
            print("\n❌ ISSUE PERSISTS: Demo user still has no friends - friendship establishment failed")

if __name__ == "__main__":
    tester = FriendMessagingTester()
    tester.run_all_tests()