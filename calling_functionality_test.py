#!/usr/bin/env python3
"""
Calling Functionality Comprehensive Test
Tests various calling scenarios to ensure the user database fix is working properly.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class CallingFunctionalityTester:
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
    
    def setup_demo_user(self):
        """Setup demo user for testing"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.demo_token = data['token']
                self.demo_user_id = data['user']['id']
                return True
            return False
        except:
            return False
    
    def test_call_initiation_video(self):
        """Test 1: Video Call Initiation"""
        if not self.setup_demo_user():
            self.log_result("Video Call Initiation", False, "Failed to setup demo user")
            return
            
        try:
            # Get user's friends
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if user_response.status_code != 200:
                self.log_result("Video Call Initiation", False, "Cannot get user data")
                return
                
            friends = user_response.json().get('friends', [])
            if len(friends) == 0:
                self.log_result("Video Call Initiation", False, "User has no friends for calling")
                return
            
            # Test video call with first friend
            recipient_id = friends[0]
            params = {
                'callerId': self.demo_user_id,
                'recipientId': recipient_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ['callId', 'channelName', 'callerToken', 'recipientToken']):
                    self.log_result(
                        "Video Call Initiation", 
                        True, 
                        f"Video call initiated successfully",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    self.log_result(
                        "Video Call Initiation", 
                        False, 
                        "Video call response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Video Call Initiation", 
                    False, 
                    f"Video call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Video Call Initiation", False, f"Exception occurred: {str(e)}")
    
    def test_call_initiation_audio(self):
        """Test 2: Audio Call Initiation"""
        try:
            # Get user's friends
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if user_response.status_code != 200:
                self.log_result("Audio Call Initiation", False, "Cannot get user data")
                return
                
            friends = user_response.json().get('friends', [])
            if len(friends) == 0:
                self.log_result("Audio Call Initiation", False, "User has no friends for calling")
                return
            
            # Test audio call with second friend (if available)
            recipient_id = friends[1] if len(friends) > 1 else friends[0]
            params = {
                'callerId': self.demo_user_id,
                'recipientId': recipient_id,
                'callType': 'audio'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ['callId', 'channelName', 'callerToken', 'recipientToken']):
                    self.log_result(
                        "Audio Call Initiation", 
                        True, 
                        f"Audio call initiated successfully",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    self.log_result(
                        "Audio Call Initiation", 
                        False, 
                        "Audio call response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Audio Call Initiation", 
                    False, 
                    f"Audio call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Audio Call Initiation", False, f"Exception occurred: {str(e)}")
    
    def test_call_with_non_friend(self):
        """Test 3: Call with Non-Friend (should fail)"""
        try:
            # Try to call a user who is not a friend
            non_friend_id = "non_existent_user_123"
            params = {
                'callerId': self.demo_user_id,
                'recipientId': non_friend_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 400 or response.status_code == 404:
                # Should fail with appropriate error
                self.log_result(
                    "Call with Non-Friend", 
                    True, 
                    f"Correctly rejected call to non-friend with status {response.status_code}",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Call with Non-Friend", 
                    False, 
                    "Security issue: Call to non-friend was allowed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Call with Non-Friend", 
                    False, 
                    f"Unexpected status code {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call with Non-Friend", False, f"Exception occurred: {str(e)}")
    
    def test_call_with_invalid_caller(self):
        """Test 4: Call with Invalid Caller ID (should fail)"""
        try:
            # Try to call with invalid caller ID
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if user_response.status_code != 200:
                self.log_result("Call with Invalid Caller", False, "Cannot get user data")
                return
                
            friends = user_response.json().get('friends', [])
            if len(friends) == 0:
                self.log_result("Call with Invalid Caller", False, "User has no friends for testing")
                return
            
            params = {
                'callerId': 'invalid_caller_123',
                'recipientId': friends[0],
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 404:
                # Should fail with "Caller not found"
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if "Caller not found" in str(error_data):
                    self.log_result(
                        "Call with Invalid Caller", 
                        True, 
                        f"Correctly rejected invalid caller with 'Caller not found' error",
                        f"Response: {error_data}"
                    )
                else:
                    self.log_result(
                        "Call with Invalid Caller", 
                        True, 
                        f"Correctly rejected invalid caller with 404 status",
                        f"Response: {error_data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Call with Invalid Caller", 
                    False, 
                    "Security issue: Call with invalid caller was allowed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Call with Invalid Caller", 
                    False, 
                    f"Unexpected status code {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call with Invalid Caller", False, f"Exception occurred: {str(e)}")
    
    def test_multiple_friends_calling(self):
        """Test 5: Multiple Friends Calling Capability"""
        try:
            # Get user's friends
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if user_response.status_code != 200:
                self.log_result("Multiple Friends Calling", False, "Cannot get user data")
                return
                
            friends = user_response.json().get('friends', [])
            if len(friends) < 2:
                self.log_result("Multiple Friends Calling", False, f"User has only {len(friends)} friends, need at least 2")
                return
            
            successful_calls = 0
            
            # Test calling multiple friends
            for i, friend_id in enumerate(friends[:3]):  # Test up to 3 friends
                params = {
                    'callerId': self.demo_user_id,
                    'recipientId': friend_id,
                    'callType': 'video'
                }
                
                response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
                
                if response.status_code == 200:
                    successful_calls += 1
                    print(f"   Call {i+1} to {friend_id}: SUCCESS")
                else:
                    print(f"   Call {i+1} to {friend_id}: FAILED ({response.status_code})")
            
            if successful_calls >= 2:
                self.log_result(
                    "Multiple Friends Calling", 
                    True, 
                    f"Successfully initiated calls to {successful_calls} different friends",
                    f"Tested {len(friends[:3])} friends total"
                )
            else:
                self.log_result(
                    "Multiple Friends Calling", 
                    False, 
                    f"Only {successful_calls} calls succeeded out of {len(friends[:3])} attempts",
                    "Expected at least 2 successful calls"
                )
                
        except Exception as e:
            self.log_result("Multiple Friends Calling", False, f"Exception occurred: {str(e)}")
    
    def test_agora_integration(self):
        """Test 6: Agora Integration Verification"""
        try:
            # Get user's friends
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            if user_response.status_code != 200:
                self.log_result("Agora Integration", False, "Cannot get user data")
                return
                
            friends = user_response.json().get('friends', [])
            if len(friends) == 0:
                self.log_result("Agora Integration", False, "User has no friends for testing")
                return
            
            params = {
                'callerId': self.demo_user_id,
                'recipientId': friends[0],
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for Agora-specific fields
                agora_fields = ['appId', 'callerToken', 'recipientToken', 'channelName', 'callerUid', 'recipientUid']
                missing_fields = [field for field in agora_fields if field not in data]
                
                if len(missing_fields) == 0:
                    self.log_result(
                        "Agora Integration", 
                        True, 
                        f"All Agora fields present in call response",
                        f"App ID: {data.get('appId')}, Channel: {data.get('channelName')}"
                    )
                else:
                    self.log_result(
                        "Agora Integration", 
                        False, 
                        f"Missing Agora fields: {missing_fields}",
                        f"Available fields: {list(data.keys())}"
                    )
            else:
                self.log_result(
                    "Agora Integration", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Agora Integration", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all calling functionality tests"""
        print("=" * 80)
        print("CALLING FUNCTIONALITY COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {DEMO_EMAIL}")
        print("=" * 80)
        
        # Run tests in sequence
        self.test_call_initiation_video()
        self.test_call_initiation_audio()
        self.test_call_with_non_friend()
        self.test_call_with_invalid_caller()
        self.test_multiple_friends_calling()
        self.test_agora_integration()
        
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
        
        return self.test_results

if __name__ == "__main__":
    tester = CallingFunctionalityTester()
    results = tester.run_all_tests()