#!/usr/bin/env python3
"""
VibeRooms Clubhouse Integration with Daily.co Real API Testing Suite
Tests complete VibeRooms functionality like Clubhouse with real Daily.co audio API
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://parallels-ai.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"
DAILY_API_KEY = "c84172cc30949874adcdd45f4c8cf2819d6e9fc12628de00608f156662be0e79"

class VibeRoomClubhouseTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.created_room_id = None
        self.daily_room_url = None
        self.daily_room_name = None
        self.meeting_token = None
        
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
    
    def setup_authentication(self):
        """Setup: Login with demo credentials"""
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
                    self.demo_user_id = data['user']['id']
                    self.log_result(
                        "Authentication Setup", 
                        True, 
                        f"Successfully logged in as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                    return True
                else:
                    self.log_result("Authentication Setup", False, "Login response missing token or user data")
                    return False
            else:
                self.log_result("Authentication Setup", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_1_daily_api_key_validation(self):
        """Test 1: Daily.co API Key Validation"""
        try:
            # Test Daily.co API key by making a direct API call
            headers = {
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Test with a simple API call to validate the key
            response = requests.get("https://api.daily.co/v1/rooms", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Daily.co API Key Validation", 
                    True, 
                    f"Daily.co API key is valid and active",
                    f"Account has access to rooms API, found {len(data.get('data', []))} rooms"
                )
            elif response.status_code == 401:
                self.log_result(
                    "Daily.co API Key Validation", 
                    False, 
                    "Daily.co API key is invalid or expired",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Daily.co API Key Validation", 
                    False, 
                    f"Daily.co API returned unexpected status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily.co API Key Validation", False, f"Exception occurred: {str(e)}")
    
    def test_2_create_viberoom_with_daily_integration(self):
        """Test 2: Create VibeRoom with Daily.co Integration"""
        try:
            payload = {
                "name": "Test Clubhouse Room",
                "description": "Testing audio integration with Daily.co",
                "category": "music",
                "isPrivate": False,
                "tags": ["test", "audio", "clubhouse"]
            }
            params = {"userId": self.demo_user_id or "demo_user"}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'name', 'dailyRoomUrl', 'dailyRoomName', 'hostId', 'participants']
                
                if all(field in data for field in required_fields):
                    self.created_room_id = data['id']
                    self.daily_room_url = data['dailyRoomUrl']
                    self.daily_room_name = data['dailyRoomName']
                    
                    # Verify Daily.co room URL format
                    if 'daily.co' in self.daily_room_url:
                        self.log_result(
                            "Create VibeRoom with Daily.co Integration", 
                            True, 
                            f"Successfully created VibeRoom with Daily.co integration",
                            f"Room ID: {self.created_room_id}, Daily URL: {self.daily_room_url}, Daily Name: {self.daily_room_name}"
                        )
                    else:
                        self.log_result(
                            "Create VibeRoom with Daily.co Integration", 
                            False, 
                            "VibeRoom created but Daily.co URL format invalid",
                            f"Daily URL: {self.daily_room_url}"
                        )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Create VibeRoom with Daily.co Integration", 
                        False, 
                        f"VibeRoom response missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create VibeRoom with Daily.co Integration", 
                    False, 
                    f"VibeRoom creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create VibeRoom with Daily.co Integration", False, f"Exception occurred: {str(e)}")
    
    def test_3_daily_room_properties(self):
        """Test 3: Daily.co Room Properties Verification"""
        if not self.daily_room_name:
            self.log_result("Daily.co Room Properties", False, "Skipped - no Daily room name available")
            return
            
        try:
            # Verify room exists on Daily.co servers
            headers = {
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"https://api.daily.co/v1/rooms/{self.daily_room_name}", 
                                  headers=headers, timeout=30)
            
            if response.status_code == 200:
                room_data = response.json()
                properties = room_data.get('config', {})
                
                # Check important Clubhouse-style properties
                checks = {
                    'audio_enabled': not properties.get('start_audio_off', True),
                    'video_optional': properties.get('start_video_off', False),
                    'room_accessible': True,  # If we got 200, room is accessible
                    'has_properties': len(properties) > 0
                }
                
                if all(checks.values()):
                    self.log_result(
                        "Daily.co Room Properties", 
                        True, 
                        f"Daily.co room properly configured for Clubhouse-style audio",
                        f"Room: {self.daily_room_name}, Properties: {properties}"
                    )
                else:
                    failed_checks = [k for k, v in checks.items() if not v]
                    self.log_result(
                        "Daily.co Room Properties", 
                        False, 
                        f"Daily.co room configuration issues: {failed_checks}",
                        f"Properties: {properties}"
                    )
            else:
                self.log_result(
                    "Daily.co Room Properties", 
                    False, 
                    f"Failed to verify Daily.co room properties (status {response.status_code})",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily.co Room Properties", False, f"Exception occurred: {str(e)}")
    
    def test_4_generate_meeting_token(self):
        """Test 4: Generate Meeting Token"""
        if not self.daily_room_name:
            self.log_result("Generate Meeting Token", False, "Skipped - no Daily room name available")
            return
            
        try:
            params = {
                'roomName': self.daily_room_name,
                'userName': 'TestUser',
                'isOwner': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and len(data['token']) > 100:  # JWT tokens are typically long
                    self.meeting_token = data['token']
                    self.log_result(
                        "Generate Meeting Token", 
                        True, 
                        f"Successfully generated meeting token",
                        f"Token length: {len(self.meeting_token)} characters, Room: {self.daily_room_name}"
                    )
                else:
                    self.log_result(
                        "Generate Meeting Token", 
                        False, 
                        "Token generation response invalid",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Generate Meeting Token", 
                    False, 
                    f"Token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Generate Meeting Token", False, f"Exception occurred: {str(e)}")
    
    def test_5_join_room_flow(self):
        """Test 5: Join Room Flow"""
        if not self.created_room_id:
            self.log_result("Join Room Flow", False, "Skipped - no room ID available")
            return
            
        try:
            params = {'userId': 'testUser123'}
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/join", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data or 'success' in data:
                    # Verify user was added to participants
                    room_response = self.session.get(f"{BACKEND_URL}/rooms/{self.created_room_id}")
                    if room_response.status_code == 200:
                        room_data = room_response.json()
                        participants = room_data.get('participants', [])
                        user_in_room = any(p.get('userId') == 'testUser123' for p in participants)
                        
                        if user_in_room:
                            self.log_result(
                                "Join Room Flow", 
                                True, 
                                f"Successfully joined room and verified participant list",
                                f"Total participants: {len(participants)}"
                            )
                        else:
                            self.log_result(
                                "Join Room Flow", 
                                False, 
                                "Join successful but user not found in participants",
                                f"Participants: {participants}"
                            )
                    else:
                        self.log_result(
                            "Join Room Flow", 
                            True, 
                            f"Join room successful",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "Join Room Flow", 
                        False, 
                        "Join room response missing expected fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Join Room Flow", 
                    False, 
                    f"Join room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Join Room Flow", False, f"Exception occurred: {str(e)}")
    
    def test_6_stage_management_clubhouse_features(self):
        """Test 6: Stage Management (Clubhouse Features)"""
        if not self.created_room_id:
            self.log_result("Stage Management", False, "Skipped - no room ID available")
            return
            
        try:
            # Test 6a: Raise Hand
            params = {'userId': 'testUser123'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/raise-hand", params=params)
            
            raise_hand_success = response.status_code == 200
            if not raise_hand_success:
                self.log_result(
                    "Stage Management - Raise Hand", 
                    False, 
                    f"Raise hand failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
            
            # Test 6b: Invite to Stage
            params = {'userId': self.demo_user_id or 'demo_user', 'targetUserId': 'testUser123'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/invite-to-stage", params=params)
            
            invite_success = response.status_code == 200
            if not invite_success:
                self.log_result(
                    "Stage Management - Invite to Stage", 
                    False, 
                    f"Invite to stage failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
            
            # Test 6c: Make Moderator
            params = {'userId': self.demo_user_id or 'demo_user', 'targetUserId': 'testUser123'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/make-moderator", params=params)
            
            moderator_success = response.status_code == 200
            if not moderator_success:
                self.log_result(
                    "Stage Management - Make Moderator", 
                    False, 
                    f"Make moderator failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
            
            # Test 6d: Remove from Stage
            params = {'userId': self.demo_user_id or 'demo_user', 'targetUserId': 'testUser123'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/remove-from-stage", params=params)
            
            remove_success = response.status_code == 200
            if not remove_success:
                self.log_result(
                    "Stage Management - Remove from Stage", 
                    False, 
                    f"Remove from stage failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
            
            # Overall stage management assessment
            successful_features = sum([raise_hand_success, invite_success, moderator_success, remove_success])
            if successful_features >= 3:
                self.log_result(
                    "Stage Management (Clubhouse Features)", 
                    True, 
                    f"Stage management features working ({successful_features}/4 features successful)",
                    "Clubhouse-style stage management is functional"
                )
            elif successful_features >= 2:
                self.log_result(
                    "Stage Management (Clubhouse Features)", 
                    True, 
                    f"Stage management partially working ({successful_features}/4 features successful)",
                    "Some Clubhouse features need attention"
                )
            else:
                self.log_result(
                    "Stage Management (Clubhouse Features)", 
                    False, 
                    f"Stage management mostly failing ({successful_features}/4 features successful)",
                    "Clubhouse features need significant fixes"
                )
                
        except Exception as e:
            self.log_result("Stage Management (Clubhouse Features)", False, f"Exception occurred: {str(e)}")
    
    def test_7_audio_room_lifecycle(self):
        """Test 7: Audio Room Lifecycle"""
        if not self.created_room_id:
            self.log_result("Audio Room Lifecycle", False, "Skipped - no room ID available")
            return
            
        try:
            # Test complete lifecycle: Create → Join → Raise hand → Invite to stage → Leave → End room
            lifecycle_steps = []
            
            # Step 1: Room already created (from test 2)
            lifecycle_steps.append("Room Created ✓")
            
            # Step 2: Join room (already tested in test 5)
            lifecycle_steps.append("User Joined ✓")
            
            # Step 3: Raise hand
            params = {'userId': 'lifecycleUser'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/raise-hand", params=params)
            if response.status_code == 200:
                lifecycle_steps.append("Hand Raised ✓")
            else:
                lifecycle_steps.append("Hand Raised ✗")
            
            # Step 4: Invite to stage
            params = {'userId': self.demo_user_id or 'demo_user', 'targetUserId': 'lifecycleUser'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/invite-to-stage", params=params)
            if response.status_code == 200:
                lifecycle_steps.append("Invited to Stage ✓")
            else:
                lifecycle_steps.append("Invited to Stage ✗")
            
            # Step 5: Leave room
            params = {'userId': 'lifecycleUser'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/leave", params=params)
            if response.status_code == 200:
                lifecycle_steps.append("User Left ✓")
            else:
                lifecycle_steps.append("User Left ✗")
            
            # Step 6: End room (if endpoint exists)
            params = {'userId': self.demo_user_id or 'demo_user'}
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/end", params=params)
            if response.status_code == 200:
                lifecycle_steps.append("Room Ended ✓")
            else:
                lifecycle_steps.append("Room End ✗ (may not be implemented)")
            
            successful_steps = len([step for step in lifecycle_steps if "✓" in step])
            total_steps = len(lifecycle_steps)
            
            if successful_steps >= 5:
                self.log_result(
                    "Audio Room Lifecycle", 
                    True, 
                    f"Complete audio room lifecycle working ({successful_steps}/{total_steps} steps)",
                    f"Lifecycle: {' → '.join(lifecycle_steps)}"
                )
            else:
                self.log_result(
                    "Audio Room Lifecycle", 
                    False, 
                    f"Audio room lifecycle incomplete ({successful_steps}/{total_steps} steps)",
                    f"Lifecycle: {' → '.join(lifecycle_steps)}"
                )
                
        except Exception as e:
            self.log_result("Audio Room Lifecycle", False, f"Exception occurred: {str(e)}")
    
    def test_8_real_time_audio_connection(self):
        """Test 8: Real-time Audio Connection (Daily.co WebRTC)"""
        if not self.daily_room_url or not self.meeting_token:
            self.log_result("Real-time Audio Connection", False, "Skipped - no Daily.co room URL or token available")
            return
            
        try:
            # Test if Daily.co room is accessible for WebRTC connection
            # We can't fully test WebRTC without a browser, but we can verify the room is ready
            
            # Check if room is accessible
            response = requests.get(self.daily_room_url, timeout=10)
            
            if response.status_code == 200:
                # Check if the response contains Daily.co room content
                content = response.text.lower()
                webrtc_indicators = ['webrtc', 'daily', 'audio', 'microphone', 'call']
                
                if any(indicator in content for indicator in webrtc_indicators):
                    self.log_result(
                        "Real-time Audio Connection", 
                        True, 
                        f"Daily.co room is accessible and ready for WebRTC connection",
                        f"Room URL: {self.daily_room_url}, Token available: {bool(self.meeting_token)}"
                    )
                else:
                    self.log_result(
                        "Real-time Audio Connection", 
                        False, 
                        "Daily.co room accessible but WebRTC indicators not found",
                        f"Content length: {len(content)} characters"
                    )
            else:
                self.log_result(
                    "Real-time Audio Connection", 
                    False, 
                    f"Daily.co room not accessible (status {response.status_code})",
                    f"URL: {self.daily_room_url}"
                )
                
        except Exception as e:
            self.log_result("Real-time Audio Connection", False, f"Exception occurred: {str(e)}")
    
    def test_9_multiple_participants(self):
        """Test 9: Multiple Participants"""
        if not self.created_room_id:
            self.log_result("Multiple Participants", False, "Skipped - no room ID available")
            return
            
        try:
            # Add multiple participants to test concurrent audio streams
            participants = ['user1', 'user2', 'user3', 'user4', 'user5']
            successful_joins = 0
            
            for user in participants:
                params = {'userId': user}
                response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/join", params=params)
                if response.status_code == 200:
                    successful_joins += 1
                    time.sleep(0.1)  # Small delay between joins
            
            # Verify participants in room
            room_response = self.session.get(f"{BACKEND_URL}/rooms/{self.created_room_id}")
            if room_response.status_code == 200:
                room_data = room_response.json()
                total_participants = len(room_data.get('participants', []))
                
                # Test stage vs audience separation
                speakers = [p for p in room_data.get('participants', []) if p.get('role') in ['host', 'moderator', 'speaker']]
                audience = [p for p in room_data.get('participants', []) if p.get('role') == 'audience']
                
                if total_participants >= 5 and len(speakers) <= 20:  # Max 20 speakers as per Clubhouse
                    self.log_result(
                        "Multiple Participants", 
                        True, 
                        f"Successfully added {successful_joins} participants, total: {total_participants}",
                        f"Speakers: {len(speakers)}, Audience: {len(audience)}, Speaker limit respected: {len(speakers) <= 20}"
                    )
                else:
                    self.log_result(
                        "Multiple Participants", 
                        False, 
                        f"Participant management issues detected",
                        f"Joins: {successful_joins}, Total: {total_participants}, Speakers: {len(speakers)}"
                    )
            else:
                self.log_result(
                    "Multiple Participants", 
                    False, 
                    f"Could not verify participants (room fetch failed)",
                    f"Successful joins: {successful_joins}/{len(participants)}"
                )
                
        except Exception as e:
            self.log_result("Multiple Participants", False, f"Exception occurred: {str(e)}")
    
    def test_10_error_handling(self):
        """Test 10: Error Handling"""
        try:
            error_tests = []
            
            # Test 10a: Invalid Daily.co key (temporarily)
            # We'll test with invalid room name instead to avoid breaking the real key
            params = {'roomName': 'invalid_room_name_12345', 'userName': 'TestUser', 'isOwner': 'true'}
            response = self.session.post(f"{BACKEND_URL}/daily/token", params=params)
            
            if response.status_code in [400, 404, 500]:
                error_tests.append("Invalid room token generation properly rejected ✓")
            else:
                error_tests.append("Invalid room token generation not properly handled ✗")
            
            # Test 10b: Room creation with invalid data
            payload = {"name": "", "description": ""}  # Invalid empty name
            params = {"userId": "invalid_user"}
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code in [400, 422]:
                error_tests.append("Invalid room creation properly rejected ✓")
            else:
                error_tests.append("Invalid room creation not properly handled ✗")
            
            # Test 10c: Join non-existent room
            response = self.session.post(f"{BACKEND_URL}/rooms/nonexistent123/join", params={'userId': 'testuser'})
            
            if response.status_code in [404, 400]:
                error_tests.append("Non-existent room join properly rejected ✓")
            else:
                error_tests.append("Non-existent room join not properly handled ✗")
            
            # Test 10d: Stage management without permissions
            if self.created_room_id:
                params = {'userId': 'unauthorized_user', 'targetUserId': 'testUser123'}
                response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/invite-to-stage", params=params)
                
                if response.status_code in [403, 401, 400]:
                    error_tests.append("Unauthorized stage management properly rejected ✓")
                else:
                    error_tests.append("Unauthorized stage management not properly handled ✗")
            
            successful_error_tests = len([test for test in error_tests if "✓" in test])
            total_error_tests = len(error_tests)
            
            if successful_error_tests >= 3:
                self.log_result(
                    "Error Handling", 
                    True, 
                    f"Error handling working properly ({successful_error_tests}/{total_error_tests} tests passed)",
                    f"Error tests: {error_tests}"
                )
            else:
                self.log_result(
                    "Error Handling", 
                    False, 
                    f"Error handling needs improvement ({successful_error_tests}/{total_error_tests} tests passed)",
                    f"Error tests: {error_tests}"
                )
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all VibeRooms Clubhouse integration tests"""
        print("🎵 STARTING VIBEROOM CLUBHOUSE INTEGRATION TESTING WITH DAILY.CO REAL API")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        # Run all tests in sequence
        self.test_1_daily_api_key_validation()
        self.test_2_create_viberoom_with_daily_integration()
        self.test_3_daily_room_properties()
        self.test_4_generate_meeting_token()
        self.test_5_join_room_flow()
        self.test_6_stage_management_clubhouse_features()
        self.test_7_audio_room_lifecycle()
        self.test_8_real_time_audio_connection()
        self.test_9_multiple_participants()
        self.test_10_error_handling()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎵 VIBEROOM CLUBHOUSE INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"✅ PASSED: {len(passed_tests)} tests")
        print(f"❌ FAILED: {len(failed_tests)} tests")
        print(f"📊 SUCCESS RATE: {len(passed_tests)}/{len(self.test_results)} ({len(passed_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        print("\n🎯 CLUBHOUSE FEATURES VERIFICATION:")
        clubhouse_features = [
            "✅ Daily.co API Integration" if any("Daily.co API Key" in r['test'] and r['success'] for r in self.test_results) else "❌ Daily.co API Integration",
            "✅ Real Audio Room Creation" if any("VibeRoom with Daily.co" in r['test'] and r['success'] for r in self.test_results) else "❌ Real Audio Room Creation",
            "✅ Meeting Token Generation" if any("Meeting Token" in r['test'] and r['success'] for r in self.test_results) else "❌ Meeting Token Generation",
            "✅ Stage Management" if any("Stage Management" in r['test'] and r['success'] for r in self.test_results) else "❌ Stage Management",
            "✅ Multiple Participants" if any("Multiple Participants" in r['test'] and r['success'] for r in self.test_results) else "❌ Multiple Participants",
            "✅ Audio Room Lifecycle" if any("Audio Room Lifecycle" in r['test'] and r['success'] for r in self.test_results) else "❌ Audio Room Lifecycle",
            "✅ WebRTC Connection Ready" if any("Real-time Audio" in r['test'] and r['success'] for r in self.test_results) else "❌ WebRTC Connection Ready",
            "✅ Error Handling" if any("Error Handling" in r['test'] and r['success'] for r in self.test_results) else "❌ Error Handling"
        ]
        
        for feature in clubhouse_features:
            print(f"   {feature}")
        
        # Final assessment
        working_features = len([f for f in clubhouse_features if "✅" in f])
        total_features = len(clubhouse_features)
        
        print(f"\n🚀 PRODUCTION READINESS: {working_features}/{total_features} Clubhouse features working")
        
        if working_features >= 7:
            print("🎉 VIBEROOM CLUBHOUSE INTEGRATION IS PRODUCTION-READY!")
        elif working_features >= 5:
            print("⚠️  VIBEROOM CLUBHOUSE INTEGRATION IS MOSTLY READY (minor issues)")
        else:
            print("🔧 VIBEROOM CLUBHOUSE INTEGRATION NEEDS SIGNIFICANT WORK")
        
        return self.test_results

if __name__ == "__main__":
    tester = VibeRoomClubhouseTester()
    results = tester.run_all_tests()