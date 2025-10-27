#!/usr/bin/env python3
"""
Comprehensive Demo User Calling Test
Verifies all expected results from the review request:
- ✅ Demo user has at least one friend (u1)
- ✅ Bidirectional friendship confirmed
- ✅ DM thread exists
- ✅ Call initiation succeeds without "Can only call friends" error
- ✅ Returns valid Agora tokens and channel info
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class ComprehensiveDemoCallingTester:
    def __init__(self):
        self.session = requests.Session()
        self.demo_user_id = None
        self.demo_token = None
        self.dm_thread_id = None
        self.test_results = []
        
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
        """Test 1: Check Demo User Login and ID"""
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
                    
                    # Check current friends array
                    current_friends = user.get('friends', [])
                    
                    self.log_result(
                        "Demo User Login and ID", 
                        True, 
                        f"Successfully logged in as {user['name']} (ID: {self.demo_user_id})",
                        f"Current friends: {len(current_friends)} - {current_friends}"
                    )
                    return True
                else:
                    self.log_result(
                        "Demo User Login and ID", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo User Login and ID", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Login and ID", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_2_demo_user_has_friends(self):
        """Test 2: Verify Demo User Has At Least One Friend (u1)"""
        if not self.demo_user_id:
            self.log_result("Demo User Has Friends", False, "Skipped - no demo user ID")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                user = response.json()
                friends = user.get('friends', [])
                
                if len(friends) > 0 and 'u1' in friends:
                    self.log_result(
                        "Demo User Has Friends", 
                        True, 
                        f"Demo user has {len(friends)} friends including u1",
                        f"Friends list: {friends}"
                    )
                    return True
                elif len(friends) > 0:
                    self.log_result(
                        "Demo User Has Friends", 
                        False, 
                        f"Demo user has {len(friends)} friends but u1 not included",
                        f"Friends list: {friends}"
                    )
                else:
                    self.log_result(
                        "Demo User Has Friends", 
                        False, 
                        "Demo user has no friends",
                        f"Friends list: {friends}"
                    )
            else:
                self.log_result(
                    "Demo User Has Friends", 
                    False, 
                    f"Failed to get user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Has Friends", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_3_bidirectional_friendship_confirmed(self):
        """Test 3: Verify Bidirectional Friendship Confirmed"""
        if not self.demo_user_id:
            self.log_result("Bidirectional Friendship Confirmed", False, "Skipped - no demo user ID")
            return False
            
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
                            "Bidirectional Friendship Confirmed", 
                            True, 
                            "Bidirectional friendship between demo user and u1 confirmed",
                            f"Demo user has u1: {demo_has_friend}, u1 has demo user: {friend_has_demo}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Bidirectional Friendship Confirmed", 
                            False, 
                            f"Friendship not bidirectional - Demo has u1: {demo_has_friend}, u1 has demo: {friend_has_demo}",
                            f"Demo friends: {demo_friends}, u1 friends: {friend_friends}"
                        )
                else:
                    self.log_result(
                        "Bidirectional Friendship Confirmed", 
                        False, 
                        f"Failed to get u1 user data with status {friend_response.status_code}",
                        f"Response: {friend_response.text}"
                    )
            else:
                self.log_result(
                    "Bidirectional Friendship Confirmed", 
                    False, 
                    f"Failed to get demo user data with status {demo_response.status_code}",
                    f"Response: {demo_response.text}"
                )
                
        except Exception as e:
            self.log_result("Bidirectional Friendship Confirmed", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_4_dm_thread_exists(self):
        """Test 4: Ensure DM Thread Exists"""
        if not self.demo_user_id:
            self.log_result("DM Thread Exists", False, "Skipped - no demo user ID")
            return False
            
        try:
            # Create/get DM thread between demo user and u1
            response = self.session.post(f"{BACKEND_URL}/dm/thread", 
                                       params={'userId': self.demo_user_id, 'peerUserId': 'u1'})
            
            if response.status_code == 200:
                data = response.json()
                self.dm_thread_id = data.get('threadId')
                
                if self.dm_thread_id:
                    self.log_result(
                        "DM Thread Exists", 
                        True, 
                        f"DM thread exists between demo user and u1: {self.dm_thread_id}",
                        f"Thread creation/retrieval successful"
                    )
                    return True
                else:
                    self.log_result(
                        "DM Thread Exists", 
                        False, 
                        "DM thread response missing threadId",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "DM Thread Exists", 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Thread Exists", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_5_call_initiation_succeeds(self):
        """Test 5: Call Initiation Succeeds Without 'Can Only Call Friends' Error"""
        if not self.demo_user_id:
            self.log_result("Call Initiation Succeeds", False, "Skipped - no demo user ID")
            return False
            
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
                
                # Check that there's no "Can only call friends" error
                error_message = video_data.get('error', '').lower()
                detail_message = video_data.get('detail', '').lower()
                
                if 'can only call friends' in error_message or 'can only call friends' in detail_message:
                    self.log_result(
                        "Call Initiation Succeeds", 
                        False, 
                        "Call initiation failed with 'Can only call friends' error",
                        f"Response: {video_data}"
                    )
                    return False
                else:
                    self.log_result(
                        "Call Initiation Succeeds", 
                        True, 
                        "Call initiation succeeded without 'Can only call friends' error",
                        f"Call ID: {video_data.get('callId', 'N/A')}"
                    )
                    return True
            else:
                # Check if the error is specifically about friendship
                try:
                    error_data = video_response.json()
                    error_detail = error_data.get('detail', '').lower()
                    if 'can only call friends' in error_detail:
                        self.log_result(
                            "Call Initiation Succeeds", 
                            False, 
                            "Call initiation failed with 'Can only call friends' error",
                            f"Status: {video_response.status_code}, Response: {error_data}"
                        )
                        return False
                except:
                    pass
                    
                self.log_result(
                    "Call Initiation Succeeds", 
                    False, 
                    f"Call initiation failed with status {video_response.status_code}",
                    f"Response: {video_response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation Succeeds", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def test_6_returns_valid_agora_tokens(self):
        """Test 6: Returns Valid Agora Tokens and Channel Info"""
        if not self.demo_user_id:
            self.log_result("Returns Valid Agora Tokens", False, "Skipped - no demo user ID")
            return False
            
        try:
            # Test call initiation to get Agora tokens
            params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required Agora fields
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken', 'appId']
                present_fields = [field for field in required_fields if field in data and data[field]]
                missing_fields = [field for field in required_fields if field not in data or not data[field]]
                
                if not missing_fields:
                    self.log_result(
                        "Returns Valid Agora Tokens", 
                        True, 
                        "All required Agora fields present and valid",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}, App ID: {data['appId']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Returns Valid Agora Tokens", 
                        False, 
                        f"Missing required Agora fields: {missing_fields}",
                        f"Present fields: {present_fields}, Response: {data}"
                    )
            else:
                self.log_result(
                    "Returns Valid Agora Tokens", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Returns Valid Agora Tokens", False, f"Exception occurred: {str(e)}")
            
        return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all expected results"""
        print("=" * 80)
        print("COMPREHENSIVE DEMO USER CALLING TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo User: {DEMO_EMAIL}")
        print("Testing all expected results from review request...")
        print("=" * 80)
        
        # Run all tests
        test_1 = self.test_1_demo_user_login_and_id()
        test_2 = self.test_2_demo_user_has_friends()
        test_3 = self.test_3_bidirectional_friendship_confirmed()
        test_4 = self.test_4_dm_thread_exists()
        test_5 = self.test_5_call_initiation_succeeds()
        test_6 = self.test_6_returns_valid_agora_tokens()
        
        # Summary
        print("\n" + "=" * 80)
        print("EXPECTED RESULTS VERIFICATION")
        print("=" * 80)
        
        expected_results = [
            ("✅ Demo user has at least one friend (u1)", test_2),
            ("✅ Bidirectional friendship confirmed", test_3),
            ("✅ DM thread exists", test_4),
            ("✅ Call initiation succeeds without 'Can only call friends' error", test_5),
            ("✅ Returns valid Agora tokens and channel info", test_6)
        ]
        
        all_passed = True
        for description, passed in expected_results:
            status = "✅ VERIFIED" if passed else "❌ FAILED"
            print(f"{status}: {description}")
            if not passed:
                all_passed = False
        
        # Final assessment
        print("\n" + "=" * 80)
        print("FINAL ASSESSMENT")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if all_passed:
            print(f"\n🎉 SUCCESS: All expected results verified!")
            print(f"✅ Demo user can successfully make calls to friends")
            print(f"✅ No 'Can only call friends' error")
            print(f"✅ Agora integration working properly")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Some expected results not met")
            print(f"❌ Demo user calling functionality needs attention")
        
        return all_passed

if __name__ == "__main__":
    tester = ComprehensiveDemoCallingTester()
    success = tester.run_comprehensive_test()