#!/usr/bin/env python3
"""
Friends System and Calling Backend Integration Test
Tests the complete friend request flow and calling functionality as requested.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"

class FriendsCallingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.user1_id = None
        self.user2_id = None
        self.user1_token = None
        self.user2_token = None
        self.thread_id = None
        
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
    
    def create_test_user(self, email_suffix, name):
        """Create a test user and return user data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            email = f"testuser{email_suffix}_{timestamp}@test.com"
            handle = f"testuser{email_suffix}_{timestamp}"
            
            payload = {
                "email": email,
                "handle": handle,
                "name": name,
                "password": "testpass123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    return {
                        'user_id': data['user']['id'],
                        'token': data['token'],
                        'email': email,
                        'name': name,
                        'handle': handle
                    }
            return None
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def test_create_two_users(self):
        """Test 1: Create Two Test Users"""
        try:
            # Create user1 (caller)
            user1_data = self.create_test_user("1_caller", "Test User 1 (Caller)")
            if user1_data:
                self.user1_id = user1_data['user_id']
                self.user1_token = user1_data['token']
                self.log_result(
                    "Create User 1 (Caller)", 
                    True, 
                    f"Successfully created caller: {user1_data['name']} ({user1_data['email']})",
                    f"User ID: {self.user1_id}"
                )
            else:
                self.log_result("Create User 1 (Caller)", False, "Failed to create caller user")
                return
            
            # Create user2 (receiver)
            user2_data = self.create_test_user("2_receiver", "Test User 2 (Receiver)")
            if user2_data:
                self.user2_id = user2_data['user_id']
                self.user2_token = user2_data['token']
                self.log_result(
                    "Create User 2 (Receiver)", 
                    True, 
                    f"Successfully created receiver: {user2_data['name']} ({user2_data['email']})",
                    f"User ID: {self.user2_id}"
                )
            else:
                self.log_result("Create User 2 (Receiver)", False, "Failed to create receiver user")
                
        except Exception as e:
            self.log_result("Create Two Users", False, f"Exception occurred: {str(e)}")
    
    def test_send_friend_request(self):
        """Test 2: Send Friend Request from User1 to User2"""
        if not self.user1_id or not self.user2_id:
            self.log_result("Send Friend Request", False, "Skipped - user IDs not available")
            return
            
        try:
            params = {
                'fromUserId': self.user1_id,
                'toUserId': self.user2_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        f"Successfully sent friend request from user1 to user2",
                        f"Response: {data.get('message', 'No message')}"
                    )
                else:
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        "Friend request response indicates failure",
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
    
    def test_verify_friend_request_received(self):
        """Test 3: Verify Friend Request Appears in User2's Received Array"""
        if not self.user2_id:
            self.log_result("Verify Friend Request Received", False, "Skipped - user2 ID not available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}")
            
            if response.status_code == 200:
                data = response.json()
                received_requests = data.get('friendRequestsReceived', [])
                
                if self.user1_id in received_requests:
                    self.log_result(
                        "Verify Friend Request Received", 
                        True, 
                        f"Friend request from user1 found in user2's friendRequestsReceived array",
                        f"Received requests: {received_requests}"
                    )
                else:
                    self.log_result(
                        "Verify Friend Request Received", 
                        False, 
                        f"Friend request from user1 NOT found in user2's friendRequestsReceived array",
                        f"Received requests: {received_requests}"
                    )
            else:
                self.log_result(
                    "Verify Friend Request Received", 
                    False, 
                    f"Failed to get user2 data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Friend Request Received", False, f"Exception occurred: {str(e)}")
    
    def test_accept_friend_request(self):
        """Test 4: Accept Friend Request from User2"""
        if not self.user1_id or not self.user2_id:
            self.log_result("Accept Friend Request", False, "Skipped - user IDs not available")
            return
            
        try:
            params = {
                'userId': self.user2_id,
                'friendId': self.user1_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request",
                        f"Response: {data.get('message', 'No message')}"
                    )
                else:
                    self.log_result(
                        "Accept Friend Request", 
                        False, 
                        "Accept friend request response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Accept Friend Request", 
                    False, 
                    f"Accept friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_verify_bidirectional_friendship(self):
        """Test 5: CRITICAL - Verify BOTH users have each other in friends array"""
        if not self.user1_id or not self.user2_id:
            self.log_result("Verify Bidirectional Friendship", False, "Skipped - user IDs not available")
            return
            
        try:
            # Check user1's friends array
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.user1_id}")
            user1_has_user2 = False
            
            if response1.status_code == 200:
                data1 = response1.json()
                friends1 = data1.get('friends', [])
                user1_has_user2 = self.user2_id in friends1
                
                if user1_has_user2:
                    self.log_result(
                        "User1 Friends Array Check", 
                        True, 
                        f"✅ User1 has User2 in friends array",
                        f"User1 friends: {friends1}"
                    )
                else:
                    self.log_result(
                        "User1 Friends Array Check", 
                        False, 
                        f"❌ User1 does NOT have User2 in friends array",
                        f"User1 friends: {friends1}"
                    )
            else:
                self.log_result(
                    "User1 Friends Array Check", 
                    False, 
                    f"Failed to get user1 data with status {response1.status_code}",
                    f"Response: {response1.text}"
                )
                return
            
            # Check user2's friends array
            response2 = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}")
            user2_has_user1 = False
            
            if response2.status_code == 200:
                data2 = response2.json()
                friends2 = data2.get('friends', [])
                user2_has_user1 = self.user1_id in friends2
                
                if user2_has_user1:
                    self.log_result(
                        "User2 Friends Array Check", 
                        True, 
                        f"✅ User2 has User1 in friends array",
                        f"User2 friends: {friends2}"
                    )
                else:
                    self.log_result(
                        "User2 Friends Array Check", 
                        False, 
                        f"❌ User2 does NOT have User1 in friends array",
                        f"User2 friends: {friends2}"
                    )
            else:
                self.log_result(
                    "User2 Friends Array Check", 
                    False, 
                    f"Failed to get user2 data with status {response2.status_code}",
                    f"Response: {response2.text}"
                )
                return
            
            # Overall bidirectional friendship check
            if user1_has_user2 and user2_has_user1:
                self.log_result(
                    "Verify Bidirectional Friendship", 
                    True, 
                    f"✅ CRITICAL SUCCESS: Both users have each other in friends arrays",
                    f"Bidirectional friendship established correctly"
                )
            else:
                self.log_result(
                    "Verify Bidirectional Friendship", 
                    False, 
                    f"❌ CRITICAL FAILURE: Bidirectional friendship not established",
                    f"User1 has User2: {user1_has_user2}, User2 has User1: {user2_has_user1}"
                )
                
        except Exception as e:
            self.log_result("Verify Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_get_friends_list_user1(self):
        """Test 6: Get Friends List for User1"""
        if not self.user1_id:
            self.log_result("Get Friends List User1", False, "Skipped - user1 ID not available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.user1_id}/friends")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for user2 in the friends list
                    user2_found = any(friend.get('id') == self.user2_id for friend in data)
                    
                    if user2_found:
                        user2_friend = next(friend for friend in data if friend.get('id') == self.user2_id)
                        self.log_result(
                            "Get Friends List User1", 
                            True, 
                            f"User2 found in User1's friends list: {user2_friend.get('name', 'Unknown')}",
                            f"Total friends: {len(data)}"
                        )
                    else:
                        self.log_result(
                            "Get Friends List User1", 
                            False, 
                            f"User2 NOT found in User1's friends list",
                            f"Friends: {[f.get('name', 'Unknown') for f in data]}"
                        )
                else:
                    self.log_result(
                        "Get Friends List User1", 
                        False, 
                        "Friends list response is not a list",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Get Friends List User1", 
                    False, 
                    f"Get friends list failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Friends List User1", False, f"Exception occurred: {str(e)}")
    
    def test_get_friends_list_user2(self):
        """Test 7: Get Friends List for User2"""
        if not self.user2_id:
            self.log_result("Get Friends List User2", False, "Skipped - user2 ID not available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}/friends")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for user1 in the friends list
                    user1_found = any(friend.get('id') == self.user1_id for friend in data)
                    
                    if user1_found:
                        user1_friend = next(friend for friend in data if friend.get('id') == self.user1_id)
                        self.log_result(
                            "Get Friends List User2", 
                            True, 
                            f"User1 found in User2's friends list: {user1_friend.get('name', 'Unknown')}",
                            f"Total friends: {len(data)}"
                        )
                    else:
                        self.log_result(
                            "Get Friends List User2", 
                            False, 
                            f"User1 NOT found in User2's friends list",
                            f"Friends: {[f.get('name', 'Unknown') for f in data]}"
                        )
                else:
                    self.log_result(
                        "Get Friends List User2", 
                        False, 
                        "Friends list response is not a list",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Get Friends List User2", 
                    False, 
                    f"Get friends list failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Friends List User2", False, f"Exception occurred: {str(e)}")
    
    def test_friend_status_check(self):
        """Test 8: Test Friend Status Check"""
        if not self.user1_id or not self.user2_id:
            self.log_result("Friend Status Check", False, "Skipped - user IDs not available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.user1_id}/friend-status/{self.user2_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'friends':
                    self.log_result(
                        "Friend Status Check", 
                        True, 
                        f"Friend status correctly returns 'friends'",
                        f"Status: {status}"
                    )
                else:
                    self.log_result(
                        "Friend Status Check", 
                        False, 
                        f"Friend status returned '{status}' instead of 'friends'",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Friend Status Check", 
                    False, 
                    f"Friend status check failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Friend Status Check", False, f"Exception occurred: {str(e)}")
    
    def test_dm_thread_creation(self):
        """Test 9: Test DM Thread Creation Between Friends"""
        if not self.user1_id or not self.user2_id:
            self.log_result("DM Thread Creation", False, "Skipped - user IDs not available")
            return
            
        try:
            params = {
                'userId': self.user1_id,
                'peerUserId': self.user2_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data or 'id' in data:
                    self.thread_id = data.get('threadId') or data.get('id')
                    self.log_result(
                        "DM Thread Creation", 
                        True, 
                        f"Successfully created DM thread between friends",
                        f"Thread ID: {self.thread_id}"
                    )
                else:
                    self.log_result(
                        "DM Thread Creation", 
                        False, 
                        "DM thread response missing thread ID",
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
    
    def test_calling_api_endpoint(self):
        """Test 10: Test Calling API Endpoint (if exists)"""
        if not self.user1_id or not self.user2_id:
            self.log_result("Calling API Endpoint", False, "Skipped - user IDs not available")
            return
            
        try:
            payload = {
                'callerId': self.user1_id,
                'recipientId': self.user2_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'callId' in data or 'id' in data:
                    call_id = data.get('callId') or data.get('id')
                    self.log_result(
                        "Calling API Endpoint", 
                        True, 
                        f"Successfully initiated call between friends",
                        f"Call ID: {call_id}, Call Type: {payload['callType']}"
                    )
                else:
                    self.log_result(
                        "Calling API Endpoint", 
                        True, 
                        f"Call initiation returned 200 OK",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Calling API Endpoint", 
                    False, 
                    f"Calling API endpoint does not exist (404 Not Found)",
                    f"Need to create /api/calls/initiate endpoint"
                )
            else:
                self.log_result(
                    "Calling API Endpoint", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Calling API Endpoint", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("FRIENDS SYSTEM AND CALLING BACKEND INTEGRATION TEST")
        print("=" * 80)
        print()
        
        # Test sequence
        self.test_create_two_users()
        self.test_send_friend_request()
        self.test_verify_friend_request_received()
        self.test_accept_friend_request()
        self.test_verify_bidirectional_friendship()
        self.test_get_friends_list_user1()
        self.test_get_friends_list_user2()
        self.test_friend_status_check()
        self.test_dm_thread_creation()
        self.test_calling_api_endpoint()
        
        # Summary
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
        print("FAILED TESTS:")
        for result in self.test_results:
            if not result['success']:
                print(f"❌ {result['test']}: {result['message']}")
        
        print()
        print("SUCCESS CRITERIA VERIFICATION:")
        
        # Check critical success criteria
        bidirectional_success = any(
            result['test'] == 'Verify Bidirectional Friendship' and result['success'] 
            for result in self.test_results
        )
        
        friends_list_success = any(
            result['test'] in ['Get Friends List User1', 'Get Friends List User2'] and result['success'] 
            for result in self.test_results
        )
        
        friend_status_success = any(
            result['test'] == 'Friend Status Check' and result['success'] 
            for result in self.test_results
        )
        
        dm_thread_success = any(
            result['test'] == 'DM Thread Creation' and result['success'] 
            for result in self.test_results
        )
        
        calling_exists = any(
            result['test'] == 'Calling API Endpoint' 
            for result in self.test_results
        )
        
        print(f"✅ Friend request creates bidirectional friendship: {'YES' if bidirectional_success else 'NO'}")
        print(f"✅ Friends list endpoint works correctly: {'YES' if friends_list_success else 'NO'}")
        print(f"✅ Friend status check returns 'friends': {'YES' if friend_status_success else 'NO'}")
        print(f"✅ DM threads can be created between friends: {'YES' if dm_thread_success else 'NO'}")
        print(f"✅ Calling endpoint exists and works: {'TESTED' if calling_exists else 'NOT TESTED'}")
        
        return self.test_results

if __name__ == "__main__":
    tester = FriendsCallingTester()
    results = tester.run_all_tests()