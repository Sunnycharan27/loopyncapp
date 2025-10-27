#!/usr/bin/env python3
"""
Video/Audio Call Initiation Test - After Duplicate Endpoint Removal
Tests the specific scenario mentioned in the review request.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"
EXPECTED_AGORA_APP_ID = "9d727260580f40d2ae8c131dbfd8ba08"

class CallInitiationTester:
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
    
    def test_1_login_demo_user(self):
        """Test 1: Login Demo User and Capture Demo User ID"""
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
                    
                    if self.demo_user_id:
                        self.log_result(
                            "Login Demo User", 
                            True, 
                            f"Successfully logged in and captured demo user ID",
                            f"Demo User ID: {self.demo_user_id}, Email: {user.get('email')}"
                        )
                    else:
                        self.log_result(
                            "Login Demo User", 
                            False, 
                            "Login successful but user ID not found",
                            f"User data: {user}"
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
    
    def test_2_verify_demo_user_has_friends(self):
        """Test 2: Verify Demo User Has Friends (should have u1, u2, u3 as friends)"""
        if not self.demo_user_id:
            self.log_result("Verify Demo User Has Friends", False, "Skipped - no demo user ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get('friends', [])
                
                if len(friends) > 0:
                    expected_friends = ['u1', 'u2', 'u3']
                    found_friends = [f for f in expected_friends if f in friends]
                    
                    if len(found_friends) >= 2:  # At least 2 friends for testing
                        self.log_result(
                            "Verify Demo User Has Friends", 
                            True, 
                            f"Demo user has {len(friends)} friends, including expected test users",
                            f"Friends: {friends}, Expected found: {found_friends}"
                        )
                    else:
                        self.log_result(
                            "Verify Demo User Has Friends", 
                            False, 
                            f"Demo user has friends but missing expected test users",
                            f"Friends: {friends}, Expected: {expected_friends}, Found: {found_friends}"
                        )
                else:
                    self.log_result(
                        "Verify Demo User Has Friends", 
                        False, 
                        "Demo user has no friends - cannot test call initiation",
                        f"Friends array: {friends}"
                    )
            else:
                self.log_result(
                    "Verify Demo User Has Friends", 
                    False, 
                    f"Failed to get demo user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Demo User Has Friends", False, f"Exception occurred: {str(e)}")
    
    def test_3_video_call_initiation(self):
        """Test 3: Test Video Call Initiation (POST /api/calls/initiate?callerId={demo_id}&recipientId=u1&callType=video)"""
        if not self.demo_user_id:
            self.log_result("Video Call Initiation", False, "Skipped - no demo user ID available")
            return
            
        try:
            params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'appId', 'callerToken', 'callerUid', 'recipientToken', 'recipientUid']
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check if all tokens are present and not empty
                    empty_fields = [field for field in required_fields if not data.get(field)]
                    
                    if not empty_fields:
                        self.log_result(
                            "Video Call Initiation", 
                            True, 
                            "Video call initiation successful with all required fields",
                            f"Call ID: {data['callId']}, Channel: {data['channelName']}, App ID: {data['appId']}"
                        )
                    else:
                        self.log_result(
                            "Video Call Initiation", 
                            False, 
                            f"Video call response has empty fields: {empty_fields}",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "Video Call Initiation", 
                        False, 
                        f"Video call response missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                data = response.json()
                if "only call friends" in data.get('detail', '').lower():
                    self.log_result(
                        "Video Call Initiation", 
                        False, 
                        "Video call failed - users are not friends",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Video Call Initiation", 
                        False, 
                        f"Video call failed with 403 status",
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
    
    def test_4_audio_call_initiation(self):
        """Test 4: Test Audio Call Initiation (POST /api/calls/initiate?callerId={demo_id}&recipientId=u2&callType=audio)"""
        if not self.demo_user_id:
            self.log_result("Audio Call Initiation", False, "Skipped - no demo user ID available")
            return
            
        try:
            params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u2',
                'callType': 'audio'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'appId', 'callerToken', 'callerUid', 'recipientToken', 'recipientUid']
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check if all tokens are present and not empty
                    empty_fields = [field for field in required_fields if not data.get(field)]
                    
                    if not empty_fields:
                        self.log_result(
                            "Audio Call Initiation", 
                            True, 
                            "Audio call initiation successful with all required fields",
                            f"Call ID: {data['callId']}, Channel: {data['channelName']}, App ID: {data['appId']}"
                        )
                    else:
                        self.log_result(
                            "Audio Call Initiation", 
                            False, 
                            f"Audio call response has empty fields: {empty_fields}",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "Audio Call Initiation", 
                        False, 
                        f"Audio call response missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                data = response.json()
                if "only call friends" in data.get('detail', '').lower():
                    self.log_result(
                        "Audio Call Initiation", 
                        False, 
                        "Audio call failed - users are not friends",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Audio Call Initiation", 
                        False, 
                        f"Audio call failed with 403 status",
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
    
    def test_5_verify_agora_app_id(self):
        """Test 5: Verify Agora App ID is Returned (appId: 9d727260580f40d2ae8c131dbfd8ba08)"""
        if not self.demo_user_id:
            self.log_result("Verify Agora App ID", False, "Skipped - no demo user ID available")
            return
            
        try:
            params = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                app_id = data.get('appId')
                
                if app_id == EXPECTED_AGORA_APP_ID:
                    self.log_result(
                        "Verify Agora App ID", 
                        True, 
                        f"Correct Agora App ID returned: {app_id}",
                        f"Expected: {EXPECTED_AGORA_APP_ID}, Got: {app_id}"
                    )
                elif app_id:
                    self.log_result(
                        "Verify Agora App ID", 
                        False, 
                        f"Incorrect Agora App ID returned",
                        f"Expected: {EXPECTED_AGORA_APP_ID}, Got: {app_id}"
                    )
                else:
                    self.log_result(
                        "Verify Agora App ID", 
                        False, 
                        "No Agora App ID in response",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Verify Agora App ID", 
                    False, 
                    f"Cannot verify App ID - call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Agora App ID", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("VIDEO/AUDIO CALL INITIATION TEST - AFTER DUPLICATE ENDPOINT REMOVAL")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"Expected Agora App ID: {EXPECTED_AGORA_APP_ID}")
        print("=" * 80)
        
        # Run tests in sequence
        self.test_1_login_demo_user()
        self.test_2_verify_demo_user_has_friends()
        self.test_3_video_call_initiation()
        self.test_4_audio_call_initiation()
        self.test_5_verify_agora_app_id()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if not result['success'] and result['details']:
                print(f"   Issue: {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Critical assessment
        critical_tests = ["Login Demo User", "Video Call Initiation", "Audio Call Initiation", "Verify Agora App ID"]
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print("🎉 SUCCESS: All critical call initiation tests passed!")
            print("✅ Call initiation succeeds without errors")
            print("✅ Response includes all required Agora data (appId, channelName, tokens, UIDs)")
            print("✅ Both video and audio calls work")
            print("✅ Correct Agora App ID is returned")
            print("✅ No 'generate_agora_token_internal' function errors")
        else:
            print("❌ FAILURE: Critical call initiation tests failed!")
            failed_critical = [result['test'] for result in self.test_results 
                             if result['test'] in critical_tests and not result['success']]
            print(f"Failed critical tests: {failed_critical}")
        
        return self.test_results

if __name__ == "__main__":
    tester = CallInitiationTester()
    results = tester.run_all_tests()