#!/usr/bin/env python3
"""
Fix Demo User Friendship Test
Addresses the bidirectional friendship issue found in the previous test.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FixDemoFriendshipTester:
    def __init__(self):
        self.session = requests.Session()
        self.demo_user_id = None
        self.demo_token = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def login_demo_user(self):
        """Login demo user and get ID"""
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
                        f"Successfully logged in as {user['name']} (ID: {self.demo_user_id})",
                        f"Current friends: {user.get('friends', [])}"
                    )
                    return True
                    
        except Exception as e:
            self.log_result("Demo User Login", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def fix_bidirectional_friendship(self):
        """Fix bidirectional friendship between demo user and u1"""
        if not self.demo_user_id:
            return False
            
        try:
            # First, remove existing friendship to start clean
            self.session.delete(f"{BACKEND_URL}/friends/remove", 
                              params={'userId': self.demo_user_id, 'friendId': 'u1'})
            self.session.delete(f"{BACKEND_URL}/friends/remove", 
                              params={'userId': 'u1', 'friendId': self.demo_user_id})
            
            # Send friend request from demo user to u1
            request_response = self.session.post(f"{BACKEND_URL}/friends/request", 
                                               params={'fromUserId': self.demo_user_id, 'toUserId': 'u1'})
            
            if request_response.status_code == 200:
                request_data = request_response.json()
                
                if request_data.get('success'):
                    if request_data.get('nowFriends'):
                        self.log_result(
                            "Fix Bidirectional Friendship", 
                            True, 
                            "Friend request automatically accepted - users are now friends",
                            f"Response: {request_data}"
                        )
                        return True
                    else:
                        # Accept the friend request from u1's side
                        accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", 
                                                          params={'userId': 'u1', 'friendId': self.demo_user_id})
                        
                        if accept_response.status_code == 200:
                            accept_data = accept_response.json()
                            self.log_result(
                                "Fix Bidirectional Friendship", 
                                True, 
                                "Friend request sent and accepted successfully",
                                f"Accept response: {accept_data}"
                            )
                            return True
                        else:
                            self.log_result(
                                "Fix Bidirectional Friendship", 
                                False, 
                                f"Friend request sent but accept failed with status {accept_response.status_code}",
                                f"Accept response: {accept_response.text}"
                            )
                else:
                    self.log_result(
                        "Fix Bidirectional Friendship", 
                        False, 
                        "Friend request failed",
                        f"Response: {request_data}"
                    )
            else:
                self.log_result(
                    "Fix Bidirectional Friendship", 
                    False, 
                    f"Friend request failed with status {request_response.status_code}",
                    f"Response: {request_response.text}"
                )
                
        except Exception as e:
            self.log_result("Fix Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def verify_friendship(self):
        """Verify bidirectional friendship"""
        try:
            # Check demo user's friends array
            demo_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if demo_response.status_code == 200:
                demo_user = demo_response.json()
                demo_friends = demo_user.get('friends', [])
                
                # Check u1's friends array
                friend_response = self.session.get(f"{BACKEND_URL}/users/u1")
                
                if friend_response.status_code == 200:
                    friend_user = friend_response.json()
                    friend_friends = friend_user.get('friends', [])
                    
                    # Verify bidirectional friendship
                    demo_has_friend = 'u1' in demo_friends
                    friend_has_demo = self.demo_user_id in friend_friends
                    
                    if demo_has_friend and friend_has_demo:
                        self.log_result(
                            "Verify Bidirectional Friendship", 
                            True, 
                            "Bidirectional friendship confirmed",
                            f"Demo user friends: {len(demo_friends)} total, Friend user friends: {len(friend_friends)} total"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Bidirectional Friendship", 
                            False, 
                            f"Friendship not bidirectional - Demo has u1: {demo_has_friend}, u1 has demo: {friend_has_demo}",
                            f"Demo friends: {demo_friends}, u1 friends: {friend_friends}"
                        )
                        return False
                        
        except Exception as e:
            self.log_result("Verify Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_call_functionality(self):
        """Test call functionality"""
        try:
            # Test video call initiation
            video_params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'video'
            }
            
            video_response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=video_params)
            
            if video_response.status_code == 200:
                video_data = video_response.json()
                
                # Check for required Agora fields
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                missing_fields = [field for field in required_fields if field not in video_data]
                
                if not missing_fields:
                    self.log_result(
                        "Test Call Functionality", 
                        True, 
                        "Call initiation successful - no 'Can only call friends' error",
                        f"Call ID: {video_data.get('callId')}, Channel: {video_data.get('channelName')}, App ID: {video_data.get('appId')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Test Call Functionality", 
                        False, 
                        f"Call response missing fields: {missing_fields}",
                        f"Response: {video_data}"
                    )
            else:
                self.log_result(
                    "Test Call Functionality", 
                    False, 
                    f"Call initiation failed with status {video_response.status_code}",
                    f"Response: {video_response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Call Functionality", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def run_fix_test(self):
        """Run the fix test"""
        print("=" * 80)
        print("FIX DEMO USER FRIENDSHIP AND CALLING TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo User: {DEMO_EMAIL}")
        print("=" * 80)
        
        # Step 1: Login
        if not self.login_demo_user():
            print("❌ CRITICAL: Cannot proceed without demo user login")
            return False
        
        # Step 2: Fix friendship
        if not self.fix_bidirectional_friendship():
            print("❌ CRITICAL: Failed to establish friendship")
            return False
        
        # Step 3: Verify friendship
        if not self.verify_friendship():
            print("❌ CRITICAL: Friendship verification failed")
            return False
        
        # Step 4: Test calling
        if not self.test_call_functionality():
            print("❌ CRITICAL: Call functionality test failed")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 SUCCESS: All tests passed!")
        print("✅ Demo user has bidirectional friendship with u1")
        print("✅ Demo user can successfully initiate calls")
        print("✅ No 'Can only call friends' error")
        print("=" * 80)
        
        return True

if __name__ == "__main__":
    tester = FixDemoFriendshipTester()
    success = tester.run_fix_test()
    
    if success:
        print("\n🎯 CONCLUSION: Demo user friendship and calling issue has been RESOLVED")
    else:
        print("\n⚠️  CONCLUSION: Demo user friendship and calling issue still needs attention")