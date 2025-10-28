#!/usr/bin/env python3
"""
Friend Request Acceptance Debug Test
Debug and Fix Friend Request Acceptance for Real Users

This test follows the exact investigation sequence requested:
1. Login Real Users
2. Check Current Friend Status  
3. Send Friend Request (User 1 → User 2)
4. Check Pending Requests
5. Accept Friend Request (User 2 Accepts)
6. Debug Accept Endpoint
7. Verify Friendship After Accept
8. Test Alternative Accept Method
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
USER1_EMAIL = "demo@loopync.com"
USER1_PASSWORD = "password123"

class FriendRequestDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.user1_token = None
        self.user1_id = None
        self.user1_data = None
        self.user2_token = None
        self.user2_id = None
        self.user2_data = None
        self.user2_email = None
        
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
    
    def step_1_login_user1(self):
        """STEP 1: Login User 1 (demo@loopync.com / password123)"""
        try:
            payload = {
                "email": USER1_EMAIL,
                "password": USER1_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user1_token = data['token']
                    self.user1_data = data['user']
                    self.user1_id = data['user']['id']
                    
                    self.log_result(
                        "STEP 1: Login User 1", 
                        True, 
                        f"Successfully logged in User 1: {self.user1_data['name']} ({self.user1_data['email']})",
                        f"User ID: {self.user1_id}, Friends: {len(self.user1_data.get('friends', []))}"
                    )
                else:
                    self.log_result(
                        "STEP 1: Login User 1", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "STEP 1: Login User 1", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 1: Login User 1", False, f"Exception occurred: {str(e)}")
    
    def step_2_create_user2(self):
        """STEP 2: Create/Login User 2 with different credentials"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.user2_email = f"testuser2_{timestamp}@example.com"
            
            payload = {
                "email": self.user2_email,
                "handle": f"testuser2_{timestamp}",
                "name": f"Test User 2 {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user2_token = data['token']
                    self.user2_data = data['user']
                    self.user2_id = data['user']['id']
                    
                    self.log_result(
                        "STEP 2: Create User 2", 
                        True, 
                        f"Successfully created User 2: {self.user2_data['name']} ({self.user2_data['email']})",
                        f"User ID: {self.user2_id}, Friends: {len(self.user2_data.get('friends', []))}"
                    )
                else:
                    self.log_result(
                        "STEP 2: Create User 2", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "STEP 2: Create User 2", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 2: Create User 2", False, f"Exception occurred: {str(e)}")
    
    def step_3_check_current_friend_status(self):
        """STEP 3: Check Current Friend Status"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 3: Check Friend Status", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check User 1's data
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.user1_id}")
            user1_current = None
            if response1.status_code == 200:
                user1_current = response1.json()
            
            # Check User 2's data
            response2 = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}")
            user2_current = None
            if response2.status_code == 200:
                user2_current = response2.json()
            
            if user1_current and user2_current:
                user1_friends = user1_current.get('friends', [])
                user1_sent = user1_current.get('friendRequestsSent', [])
                user1_received = user1_current.get('friendRequestsReceived', [])
                
                user2_friends = user2_current.get('friends', [])
                user2_sent = user2_current.get('friendRequestsSent', [])
                user2_received = user2_current.get('friendRequestsReceived', [])
                
                # Check if already friends
                already_friends = self.user2_id in user1_friends and self.user1_id in user2_friends
                
                self.log_result(
                    "STEP 3: Check Friend Status", 
                    True, 
                    f"Current friendship status checked",
                    f"Already friends: {already_friends}\n" +
                    f"User 1 - Friends: {len(user1_friends)}, Sent: {len(user1_sent)}, Received: {len(user1_received)}\n" +
                    f"User 2 - Friends: {len(user2_friends)}, Sent: {len(user2_sent)}, Received: {len(user2_received)}"
                )
            else:
                self.log_result(
                    "STEP 3: Check Friend Status", 
                    False, 
                    "Failed to retrieve user data",
                    f"User 1 status: {response1.status_code}, User 2 status: {response2.status_code}"
                )
                
        except Exception as e:
            self.log_result("STEP 3: Check Friend Status", False, f"Exception occurred: {str(e)}")
    
    def step_4_send_friend_request(self):
        """STEP 4: Send Friend Request (User 1 → User 2)"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 4: Send Friend Request", False, "Skipped - missing user IDs")
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
                        "STEP 4: Send Friend Request", 
                        True, 
                        f"Successfully sent friend request from User 1 to User 2",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "STEP 4: Send Friend Request", 
                        False, 
                        f"Friend request failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "STEP 4: Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 4: Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def step_5_check_pending_requests(self):
        """STEP 5: Check Pending Requests"""
        if not self.user2_id:
            self.log_result("STEP 5: Check Pending Requests", False, "Skipped - missing User 2 ID")
            return
            
        try:
            # Check User 2's friend requests received
            response = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}/friend-requests")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it's the expected format
                if 'received' in data and 'sent' in data:
                    received_requests = data['received']
                    # Look for request from User 1
                    user1_request = None
                    for req in received_requests:
                        if req.get('id') == self.user1_id:
                            user1_request = req
                            break
                    
                    if user1_request:
                        self.log_result(
                            "STEP 5: Check Pending Requests", 
                            True, 
                            f"Found pending friend request from User 1 in User 2's received requests",
                            f"Request from: {user1_request.get('name', 'Unknown')} ({user1_request.get('handle', 'Unknown')})"
                        )
                    else:
                        self.log_result(
                            "STEP 5: Check Pending Requests", 
                            False, 
                            "No pending friend request from User 1 found in User 2's received requests",
                            f"Received requests: {[req.get('name', 'Unknown') for req in received_requests]}"
                        )
                else:
                    # Try alternative format - direct user data
                    user_response = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}")
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        received_ids = user_data.get('friendRequestsReceived', [])
                        
                        if self.user1_id in received_ids:
                            self.log_result(
                                "STEP 5: Check Pending Requests", 
                                True, 
                                f"Found User 1 ID in User 2's friendRequestsReceived array",
                                f"Received request IDs: {received_ids}"
                            )
                        else:
                            self.log_result(
                                "STEP 5: Check Pending Requests", 
                                False, 
                                "User 1 ID not found in User 2's friendRequestsReceived array",
                                f"Received request IDs: {received_ids}"
                            )
                    else:
                        self.log_result(
                            "STEP 5: Check Pending Requests", 
                            False, 
                            "Could not retrieve User 2's data to check pending requests",
                            f"Response format: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                        )
            else:
                self.log_result(
                    "STEP 5: Check Pending Requests", 
                    False, 
                    f"Failed to get friend requests with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 5: Check Pending Requests", False, f"Exception occurred: {str(e)}")
    
    def step_6_accept_friend_request(self):
        """STEP 6: Accept Friend Request (User 2 Accepts)"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 6: Accept Friend Request", False, "Skipped - missing user IDs")
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
                        "STEP 6: Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "STEP 6: Accept Friend Request", 
                        False, 
                        f"Accept failed: {data.get('message', 'Unknown error')}",
                        f"Full response: {data}"
                    )
            else:
                # Capture exact error for debugging
                error_text = response.text
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No detail provided')
                except:
                    error_detail = error_text
                
                self.log_result(
                    "STEP 6: Accept Friend Request", 
                    False, 
                    f"Accept failed with status {response.status_code}: {error_detail}",
                    f"Full response: {error_text}"
                )
                
        except Exception as e:
            self.log_result("STEP 6: Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def step_7_debug_accept_endpoint(self):
        """STEP 7: Debug Accept Endpoint"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 7: Debug Accept Endpoint", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check what parameters the endpoint expects by examining the backend code
            # Test different parameter formats
            
            # Format 1: Query parameters
            params1 = {
                'userId': self.user2_id,
                'friendId': self.user1_id
            }
            response1 = self.session.post(f"{BACKEND_URL}/friends/accept", params=params1)
            
            # Format 2: JSON body
            payload2 = {
                'userId': self.user2_id,
                'friendId': self.user1_id
            }
            response2 = self.session.post(f"{BACKEND_URL}/friends/accept", json=payload2)
            
            # Format 3: Form data
            data3 = {
                'userId': self.user2_id,
                'friendId': self.user1_id
            }
            response3 = self.session.post(f"{BACKEND_URL}/friends/accept", data=data3)
            
            debug_info = f"Format 1 (params): {response1.status_code} - {response1.text[:100]}\n"
            debug_info += f"Format 2 (json): {response2.status_code} - {response2.text[:100]}\n"
            debug_info += f"Format 3 (form): {response3.status_code} - {response3.text[:100]}"
            
            # Check if any format worked
            success = any(r.status_code == 200 for r in [response1, response2, response3])
            
            self.log_result(
                "STEP 7: Debug Accept Endpoint", 
                success, 
                f"Tested different parameter formats for accept endpoint",
                debug_info
            )
                
        except Exception as e:
            self.log_result("STEP 7: Debug Accept Endpoint", False, f"Exception occurred: {str(e)}")
    
    def step_8_verify_friendship_after_accept(self):
        """STEP 8: Verify Friendship After Accept"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 8: Verify Friendship", False, "Skipped - missing user IDs")
            return
            
        try:
            # Get User 1's current data
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.user1_id}")
            user1_data = None
            if response1.status_code == 200:
                user1_data = response1.json()
            
            # Get User 2's current data
            response2 = self.session.get(f"{BACKEND_URL}/users/{self.user2_id}")
            user2_data = None
            if response2.status_code == 200:
                user2_data = response2.json()
            
            if user1_data and user2_data:
                user1_friends = user1_data.get('friends', [])
                user2_friends = user2_data.get('friends', [])
                
                user1_has_user2 = self.user2_id in user1_friends
                user2_has_user1 = self.user1_id in user2_friends
                
                # Check if pending request arrays are cleared
                user1_sent = user1_data.get('friendRequestsSent', [])
                user1_received = user1_data.get('friendRequestsReceived', [])
                user2_sent = user2_data.get('friendRequestsSent', [])
                user2_received = user2_data.get('friendRequestsReceived', [])
                
                requests_cleared = (
                    self.user2_id not in user1_sent and 
                    self.user1_id not in user2_received
                )
                
                if user1_has_user2 and user2_has_user1:
                    self.log_result(
                        "STEP 8: Verify Friendship", 
                        True, 
                        f"Bidirectional friendship successfully established",
                        f"User 1 friends: {len(user1_friends)}, User 2 friends: {len(user2_friends)}\n" +
                        f"Pending requests cleared: {requests_cleared}"
                    )
                else:
                    self.log_result(
                        "STEP 8: Verify Friendship", 
                        False, 
                        f"Friendship not properly established",
                        f"User 1 has User 2: {user1_has_user2}, User 2 has User 1: {user2_has_user1}\n" +
                        f"User 1 friends: {user1_friends}\n" +
                        f"User 2 friends: {user2_friends}"
                    )
            else:
                self.log_result(
                    "STEP 8: Verify Friendship", 
                    False, 
                    "Failed to retrieve user data for verification",
                    f"User 1 status: {response1.status_code}, User 2 status: {response2.status_code}"
                )
                
        except Exception as e:
            self.log_result("STEP 8: Verify Friendship", False, f"Exception occurred: {str(e)}")
    
    def step_9_test_alternative_accept_method(self):
        """STEP 9: Test Alternative Accept Method"""
        if not self.user1_id or not self.user2_id:
            self.log_result("STEP 9: Alternative Accept Method", False, "Skipped - missing user IDs")
            return
            
        try:
            # First, check if there are any friend requests in the friend_requests collection
            # This would be the alternative method mentioned in the review request
            
            # Try to find friend request ID from friend_requests collection
            # This is a hypothetical endpoint - we'll test if it exists
            response = self.session.get(f"{BACKEND_URL}/friend-requests", params={'userId': self.user2_id})
            
            if response.status_code == 200:
                data = response.json()
                request_id = None
                
                # Look for request from User 1 to User 2
                if isinstance(data, list):
                    for req in data:
                        if (req.get('fromUserId') == self.user1_id and 
                            req.get('toUserId') == self.user2_id and 
                            req.get('status') == 'pending'):
                            request_id = req.get('id')
                            break
                
                if request_id:
                    # Try alternative accept method
                    alt_response = self.session.post(f"{BACKEND_URL}/friend-requests/{request_id}/accept")
                    
                    if alt_response.status_code == 200:
                        alt_data = alt_response.json()
                        self.log_result(
                            "STEP 9: Alternative Accept Method", 
                            True, 
                            f"Alternative accept method successful using request ID",
                            f"Request ID: {request_id}, Response: {alt_data}"
                        )
                    else:
                        self.log_result(
                            "STEP 9: Alternative Accept Method", 
                            False, 
                            f"Alternative accept method failed with status {alt_response.status_code}",
                            f"Request ID: {request_id}, Response: {alt_response.text}"
                        )
                else:
                    self.log_result(
                        "STEP 9: Alternative Accept Method", 
                        False, 
                        "No pending friend request found in friend_requests collection",
                        f"Available requests: {data}"
                    )
            else:
                self.log_result(
                    "STEP 9: Alternative Accept Method", 
                    False, 
                    f"Could not access friend-requests endpoint (status {response.status_code})",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 9: Alternative Accept Method", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all debug tests in sequence"""
        print("=" * 80)
        print("FRIEND REQUEST ACCEPTANCE DEBUG TEST")
        print("Debug and Fix Friend Request Acceptance for Real Users")
        print("=" * 80)
        print()
        
        # Execute all steps in sequence
        self.step_1_login_user1()
        self.step_2_create_user2()
        self.step_3_check_current_friend_status()
        self.step_4_send_friend_request()
        self.step_5_check_pending_requests()
        self.step_6_accept_friend_request()
        self.step_7_debug_accept_endpoint()
        self.step_8_verify_friendship_after_accept()
        self.step_9_test_alternative_accept_method()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['message']}")
            print()
        
        print("CRITICAL FINDINGS:")
        print("- Exact failure point in friend accept flow will be identified")
        print("- Root cause of real user ID issues will be determined")
        print("- Specific fix recommendations will be provided")
        print()
        
        return self.test_results

if __name__ == "__main__":
    tester = FriendRequestDebugTester()
    results = tester.run_all_tests()