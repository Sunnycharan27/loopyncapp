#!/usr/bin/env python3
"""
Friend-to-Call Flow Testing Suite
Tests the complete flow from friend request to making calls as specified in the review request.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FriendToCallTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.test_user_id = None
        self.test_user_email = None
        self.test_user_token = None
        self.friend_request_id = None
        self.non_friend_user_id = None
        
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
        """Test 1: Login Demo User - POST /api/auth/login with demo@loopync.com / password123"""
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
                    friends_array = user.get('friends', [])
                    
                    if self.demo_user_id:
                        self.log_result(
                            "1. Login Demo User", 
                            True, 
                            f"Successfully logged in demo user: {user.get('name')} (ID: {self.demo_user_id})",
                            f"Friends array contains {len(friends_array)} friends: {friends_array}"
                        )
                    else:
                        self.log_result(
                            "1. Login Demo User", 
                            False, 
                            "Login successful but user ID missing",
                            f"User data: {user}"
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
        """Test 2: Create Test User - POST /api/auth/signup with unique email/handle"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"testuser_{timestamp}@example.com"
            
            payload = {
                "email": self.test_user_email,
                "handle": f"testuser_{timestamp}",
                "name": f"Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.test_user_token = data['token']
                    user = data['user']
                    self.test_user_id = user.get('id')
                    
                    if self.test_user_id:
                        self.log_result(
                            "2. Create Test User", 
                            True, 
                            f"Successfully created test user: {user.get('name')} (ID: {self.test_user_id})",
                            f"Email: {self.test_user_email}, Handle: {user.get('handle')}"
                        )
                    else:
                        self.log_result(
                            "2. Create Test User", 
                            False, 
                            "Signup successful but user ID missing",
                            f"User data: {user}"
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
    
    def test_3_send_friend_request(self):
        """Test 3: Send Friend Request (Demo → Test User) - POST /api/friends/request"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("3. Send Friend Request", False, "Skipped - missing user IDs")
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
                        "3. Send Friend Request", 
                        True, 
                        f"Successfully sent friend request from demo user to test user",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "3. Send Friend Request", 
                        False, 
                        "Friend request response indicates failure",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "3. Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("3. Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_4_accept_friend_request(self):
        """Test 4: Accept Friend Request (Test User Accepts) - POST /api/friends/accept"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("4. Accept Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            # First get pending requests to find the request ID
            get_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/friend-requests")
            
            if get_response.status_code == 200:
                requests_data = get_response.json()
                
                # Look for pending request from demo user
                pending_request = None
                if isinstance(requests_data, dict) and 'received' in requests_data:
                    received_requests = requests_data['received']
                    for req in received_requests:
                        if req.get('id') == self.demo_user_id:
                            pending_request = req
                            break
                
                if pending_request:
                    # Accept the friend request
                    params = {
                        'userId': self.test_user_id,
                        'friendId': self.demo_user_id
                    }
                    
                    accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
                    
                    if accept_response.status_code == 200:
                        accept_data = accept_response.json()
                        if accept_data.get('success'):
                            self.log_result(
                                "4. Accept Friend Request", 
                                True, 
                                f"Successfully accepted friend request",
                                f"Response: {accept_data}"
                            )
                        else:
                            self.log_result(
                                "4. Accept Friend Request", 
                                False, 
                                "Accept response indicates failure",
                                f"Response: {accept_data}"
                            )
                    else:
                        self.log_result(
                            "4. Accept Friend Request", 
                            False, 
                            f"Accept friend request failed with status {accept_response.status_code}",
                            f"Response: {accept_response.text}"
                        )
                else:
                    self.log_result(
                        "4. Accept Friend Request", 
                        False, 
                        "No pending friend request found from demo user",
                        f"Received requests: {requests_data}"
                    )
            else:
                self.log_result(
                    "4. Accept Friend Request", 
                    False, 
                    f"Failed to get friend requests with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                
        except Exception as e:
            self.log_result("4. Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_5_verify_friends_arrays_updated(self):
        """Test 5: Verify Friends Arrays Updated - GET /api/users/{userId} for both users"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("5. Verify Friends Arrays", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check demo user's friends array
            demo_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            test_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}")
            
            demo_success = False
            test_success = False
            
            if demo_response.status_code == 200:
                demo_data = demo_response.json()
                demo_friends = demo_data.get('friends', [])
                if self.test_user_id in demo_friends:
                    demo_success = True
                    
            if test_response.status_code == 200:
                test_data = test_response.json()
                test_friends = test_data.get('friends', [])
                if self.demo_user_id in test_friends:
                    test_success = True
            
            if demo_success and test_success:
                self.log_result(
                    "5. Verify Friends Arrays", 
                    True, 
                    "Both users have each other in friends arrays (bidirectional friendship confirmed)",
                    f"Demo user friends: {demo_friends}, Test user friends: {test_friends}"
                )
            elif demo_success:
                self.log_result(
                    "5. Verify Friends Arrays", 
                    False, 
                    "Demo user has test user as friend, but not vice versa",
                    f"Demo user friends: {demo_friends}, Test user friends: {test_friends}"
                )
            elif test_success:
                self.log_result(
                    "5. Verify Friends Arrays", 
                    False, 
                    "Test user has demo user as friend, but not vice versa",
                    f"Demo user friends: {demo_friends}, Test user friends: {test_friends}"
                )
            else:
                self.log_result(
                    "5. Verify Friends Arrays", 
                    False, 
                    "Neither user has the other in their friends array",
                    f"Demo user friends: {demo_friends}, Test user friends: {test_friends}"
                )
                
        except Exception as e:
            self.log_result("5. Verify Friends Arrays", False, f"Exception occurred: {str(e)}")
    
    def test_6_test_call_initiation_between_friends(self):
        """Test 6: Test Call Initiation Between Friends - POST /api/calls/initiate"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("6. Call Initiation Between Friends", False, "Skipped - missing user IDs")
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
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "6. Call Initiation Between Friends", 
                        True, 
                        f"Successfully initiated video call between friends",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}, Tokens provided"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "6. Call Initiation Between Friends", 
                        False, 
                        f"Call initiated but missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                # This should NOT happen between friends
                self.log_result(
                    "6. Call Initiation Between Friends", 
                    False, 
                    "Call initiation failed with 403 - friends should be able to call each other",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "6. Call Initiation Between Friends", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("6. Call Initiation Between Friends", False, f"Exception occurred: {str(e)}")
    
    def test_7_test_call_rejection_for_non_friends(self):
        """Test 7: Test Call Rejection for Non-Friends - Create another user and try to call"""
        if not self.demo_user_id:
            self.log_result("7. Call Rejection for Non-Friends", False, "Skipped - missing demo user ID")
            return
            
        try:
            # Create another user who is NOT friends with demo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            non_friend_email = f"nonfriend_{timestamp}@example.com"
            
            payload = {
                "email": non_friend_email,
                "handle": f"nonfriend_{timestamp}",
                "name": f"Non Friend {timestamp}",
                "password": "testpassword123"
            }
            
            signup_response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.non_friend_user_id = signup_data['user']['id']
                
                # Now try to initiate call from demo to non-friend
                params = {
                    'callerId': self.demo_user_id,
                    'recipientId': self.non_friend_user_id,
                    'callType': 'video'
                }
                
                call_response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
                
                if call_response.status_code == 403:
                    call_data = call_response.json()
                    if "can only call friends" in call_data.get('detail', '').lower():
                        self.log_result(
                            "7. Call Rejection for Non-Friends", 
                            True, 
                            "Correctly rejected call attempt between non-friends with 403 error",
                            f"Response: {call_data}"
                        )
                    else:
                        self.log_result(
                            "7. Call Rejection for Non-Friends", 
                            False, 
                            "Got 403 but error message doesn't mention friends requirement",
                            f"Response: {call_data}"
                        )
                elif call_response.status_code == 200:
                    self.log_result(
                        "7. Call Rejection for Non-Friends", 
                        False, 
                        "Security issue: Non-friends were allowed to make calls",
                        f"Response: {call_response.text}"
                    )
                else:
                    self.log_result(
                        "7. Call Rejection for Non-Friends", 
                        False, 
                        f"Unexpected status code {call_response.status_code} for non-friend call",
                        f"Response: {call_response.text}"
                    )
            else:
                self.log_result(
                    "7. Call Rejection for Non-Friends", 
                    False, 
                    f"Failed to create non-friend user with status {signup_response.status_code}",
                    f"Response: {signup_response.text}"
                )
                
        except Exception as e:
            self.log_result("7. Call Rejection for Non-Friends", False, f"Exception occurred: {str(e)}")
    
    def test_8_test_friendship_persistence_after_relogin(self):
        """Test 8: Test Friendship Persistence After Re-Login - Login again and verify friends array"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'user' in data:
                    user = data['user']
                    friends_array = user.get('friends', [])
                    
                    if self.test_user_id and self.test_user_id in friends_array:
                        self.log_result(
                            "8. Friendship Persistence After Re-Login", 
                            True, 
                            f"Friendship persists across logins - test user still in friends array",
                            f"Friends array: {friends_array}"
                        )
                    elif self.test_user_id:
                        self.log_result(
                            "8. Friendship Persistence After Re-Login", 
                            False, 
                            "Friendship lost after re-login - test user not in friends array",
                            f"Friends array: {friends_array}, Expected: {self.test_user_id}"
                        )
                    else:
                        self.log_result(
                            "8. Friendship Persistence After Re-Login", 
                            False, 
                            "Cannot verify persistence - test user ID not available",
                            f"Friends array: {friends_array}"
                        )
                else:
                    self.log_result(
                        "8. Friendship Persistence After Re-Login", 
                        False, 
                        "Re-login response missing user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "8. Friendship Persistence After Re-Login", 
                    False, 
                    f"Re-login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("8. Friendship Persistence After Re-Login", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("FRIEND-TO-CALL FLOW COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("=" * 80)
        
        # Run tests in sequence
        self.test_1_login_demo_user()
        self.test_2_create_test_user()
        self.test_3_send_friend_request()
        self.test_4_accept_friend_request()
        self.test_5_verify_friends_arrays_updated()
        self.test_6_test_call_initiation_between_friends()
        self.test_7_test_call_rejection_for_non_friends()
        self.test_8_test_friendship_persistence_after_relogin()
        
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
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if not result['success'] and result['details']:
                print(f"   Error: {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Check critical success criteria
        critical_tests = [
            "3. Send Friend Request",
            "4. Accept Friend Request", 
            "5. Verify Friends Arrays",
            "6. Call Initiation Between Friends",
            "7. Call Rejection for Non-Friends",
            "8. Friendship Persistence After Re-Login"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        print("CRITICAL SUCCESS CRITERIA:")
        print(f"✅ Friend request send works: {'YES' if any(r['test'] == '3. Send Friend Request' and r['success'] for r in self.test_results) else 'NO'}")
        print(f"✅ Friend request accept updates both users' friends arrays: {'YES' if any(r['test'] == '5. Verify Friends Arrays' and r['success'] for r in self.test_results) else 'NO'}")
        print(f"✅ Friends can initiate calls successfully: {'YES' if any(r['test'] == '6. Call Initiation Between Friends' and r['success'] for r in self.test_results) else 'NO'}")
        print(f"✅ Non-friends get 403 error when trying to call: {'YES' if any(r['test'] == '7. Call Rejection for Non-Friends' and r['success'] for r in self.test_results) else 'NO'}")
        print(f"✅ Friendships persist across logins: {'YES' if any(r['test'] == '8. Friendship Persistence After Re-Login' and r['success'] for r in self.test_results) else 'NO'}")
        
        print(f"\nCritical Tests Passed: {critical_passed}/{len(critical_tests)}")
        
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL SUCCESS CRITERIA MET - FRIEND-TO-CALL FLOW IS FULLY FUNCTIONAL!")
        else:
            print("⚠️  SOME CRITICAL TESTS FAILED - FRIEND-TO-CALL FLOW NEEDS ATTENTION")
        
        print("=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = FriendToCallTester()
    results = tester.run_all_tests()