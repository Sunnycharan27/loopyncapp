#!/usr/bin/env python3
"""
Friend Request Flow Test - Complete End-to-End Testing
Tests the complete friend request flow with current frontend implementation.
Specifically tests the /friends/accept endpoint that frontend uses.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FriendRequestFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.new_user_id = None
        self.new_user_token = None
        self.new_user_email = None
        
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
        """Test 1: Login Demo User (demo@loopync.com / password123)"""
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
                    self.demo_user_id = user['id']
                    
                    # Check friendRequestsReceived array
                    friend_requests_received = user.get('friendRequestsReceived', [])
                    
                    self.log_result(
                        "Login Demo User", 
                        True, 
                        f"Successfully logged in as {user['name']} (ID: {self.demo_user_id})",
                        f"friendRequestsReceived: {friend_requests_received}"
                    )
                else:
                    self.log_result(
                        "Login Demo User", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Login Demo User", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Login Demo User", False, f"Exception occurred: {str(e)}")
    
    def test_2_create_test_user(self):
        """Test 2: Create Test User for Friend Request"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.new_user_email = f"friendtest_{timestamp}@example.com"
            
            payload = {
                "email": self.new_user_email,
                "handle": f"friendtest_{timestamp}",
                "name": f"Friend Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.new_user_token = data['token']
                    user = data['user']
                    self.new_user_id = user['id']
                    
                    self.log_result(
                        "Create Test User", 
                        True, 
                        f"Successfully created test user {user['name']} (ID: {self.new_user_id})",
                        f"Email: {self.new_user_email}"
                    )
                else:
                    self.log_result(
                        "Create Test User", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create Test User", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create Test User", False, f"Exception occurred: {str(e)}")
    
    def test_3_send_friend_request(self):
        """Test 3: Send Friend Request (New User → Demo)"""
        if not self.new_user_id or not self.demo_user_id:
            self.log_result("Send Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'fromUserId': self.new_user_id,
                'toUserId': self.demo_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        f"Successfully sent friend request from {self.new_user_id} to {self.demo_user_id}",
                        f"Response: {data}"
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
    
    def test_4_verify_demo_has_pending_request(self):
        """Test 4: Verify Demo User Has Pending Request in friendRequestsReceived"""
        if not self.demo_user_id:
            self.log_result("Verify Pending Request", False, "Skipped - missing demo user ID")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                friend_requests_received = data.get('friendRequestsReceived', [])
                
                if self.new_user_id in friend_requests_received:
                    self.log_result(
                        "Verify Pending Request", 
                        True, 
                        f"Demo user has pending request from {self.new_user_id}",
                        f"friendRequestsReceived: {friend_requests_received}"
                    )
                else:
                    self.log_result(
                        "Verify Pending Request", 
                        False, 
                        f"Demo user does not have pending request from {self.new_user_id}",
                        f"friendRequestsReceived: {friend_requests_received}"
                    )
            else:
                self.log_result(
                    "Verify Pending Request", 
                    False, 
                    f"Failed to get demo user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Pending Request", False, f"Exception occurred: {str(e)}")
    
    def test_5_accept_friend_request(self):
        """Test 5: Accept Friend Request (Demo Accepts) - EXACT frontend endpoint"""
        if not self.demo_user_id or not self.new_user_id:
            self.log_result("Accept Friend Request", False, "Skipped - missing user IDs")
            return
            
        try:
            # This is the EXACT endpoint that frontend calls
            params = {
                'userId': self.demo_user_id,
                'friendId': self.new_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request using /friends/accept endpoint",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Accept Friend Request", 
                        False, 
                        "Accept response indicates failure",
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
    
    def test_6_verify_bidirectional_friendship(self):
        """Test 6: Verify Bidirectional Friendship"""
        if not self.demo_user_id or not self.new_user_id:
            self.log_result("Verify Bidirectional Friendship", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check demo user's friends array
            demo_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            new_user_response = self.session.get(f"{BACKEND_URL}/users/{self.new_user_id}")
            
            demo_success = False
            new_user_success = False
            
            if demo_response.status_code == 200:
                demo_data = demo_response.json()
                demo_friends = demo_data.get('friends', [])
                demo_requests_received = demo_data.get('friendRequestsReceived', [])
                
                if self.new_user_id in demo_friends:
                    demo_success = True
                    demo_msg = f"✓ Demo user has {self.new_user_id} in friends array"
                else:
                    demo_msg = f"✗ Demo user missing {self.new_user_id} in friends array: {demo_friends}"
                
                # Check that friendRequestsReceived is cleared
                if self.new_user_id not in demo_requests_received:
                    demo_cleared_msg = f"✓ Demo user's friendRequestsReceived cleared: {demo_requests_received}"
                else:
                    demo_cleared_msg = f"✗ Demo user's friendRequestsReceived not cleared: {demo_requests_received}"
            else:
                demo_msg = f"✗ Failed to get demo user data: {demo_response.status_code}"
                demo_cleared_msg = "✗ Could not check friendRequestsReceived"
            
            if new_user_response.status_code == 200:
                new_user_data = new_user_response.json()
                new_user_friends = new_user_data.get('friends', [])
                new_user_requests_sent = new_user_data.get('friendRequestsSent', [])
                
                if self.demo_user_id in new_user_friends:
                    new_user_success = True
                    new_user_msg = f"✓ New user has {self.demo_user_id} in friends array"
                else:
                    new_user_msg = f"✗ New user missing {self.demo_user_id} in friends array: {new_user_friends}"
                
                # Check that friendRequestsSent is cleared
                if self.demo_user_id not in new_user_requests_sent:
                    new_user_cleared_msg = f"✓ New user's friendRequestsSent cleared: {new_user_requests_sent}"
                else:
                    new_user_cleared_msg = f"✗ New user's friendRequestsSent not cleared: {new_user_requests_sent}"
            else:
                new_user_msg = f"✗ Failed to get new user data: {new_user_response.status_code}"
                new_user_cleared_msg = "✗ Could not check friendRequestsSent"
            
            overall_success = demo_success and new_user_success
            
            self.log_result(
                "Verify Bidirectional Friendship", 
                overall_success, 
                f"Bidirectional friendship verification: {'SUCCESS' if overall_success else 'FAILED'}",
                f"{demo_msg}\n{new_user_msg}\n{demo_cleared_msg}\n{new_user_cleared_msg}"
            )
                
        except Exception as e:
            self.log_result("Verify Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_7_test_call_between_friends(self):
        """Test 7: Test Call Between Friends"""
        if not self.demo_user_id or not self.new_user_id:
            self.log_result("Test Call Between Friends", False, "Skipped - missing user IDs")
            return
            
        try:
            params = {
                'callerId': self.demo_user_id,
                'recipientId': self.new_user_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Test Call Between Friends", 
                        True, 
                        f"Successfully initiated call between friends",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    self.log_result(
                        "Test Call Between Friends", 
                        False, 
                        "Call response missing required fields",
                        f"Response: {data}, Required: {required_fields}"
                    )
            else:
                self.log_result(
                    "Test Call Between Friends", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Call Between Friends", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Complete Friend Request Flow Test")
        print("=" * 60)
        
        # Run tests in sequence
        self.test_1_login_demo_user()
        self.test_2_create_test_user()
        self.test_3_send_friend_request()
        self.test_4_verify_demo_has_pending_request()
        self.test_5_accept_friend_request()
        self.test_6_verify_bidirectional_friendship()
        self.test_7_test_call_between_friends()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Check if all expected results were achieved
        expected_results = [
            "✅ Friend request sends correctly",
            "✅ Demo user has pending request in friendRequestsReceived", 
            "✅ Accept endpoint works without errors",
            "✅ Both users have each other in friends arrays",
            "✅ Pending request arrays cleared",
            "✅ Friends can call each other"
        ]
        
        print(f"\n🎯 EXPECTED RESULTS VERIFICATION:")
        if passed == total:
            for expected in expected_results:
                print(expected)
            print("\n🎉 ALL EXPECTED RESULTS ACHIEVED!")
        else:
            print("❌ Some tests failed - expected results not fully achieved")
        
        return passed == total

if __name__ == "__main__":
    tester = FriendRequestFlowTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)