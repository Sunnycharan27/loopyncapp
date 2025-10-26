#!/usr/bin/env python3
"""
VibeRooms Audio/Microphone Functionality Testing Suite
Tests the specific issue: Users invited to stage (speakers) cannot speak - microphone not working

Test Sequence:
1. Get Room Data - GET /api/rooms/{roomId} for an existing room
2. Test Role Permissions - Check participant roles (host, moderator, speaker, audience)
3. Test Agora Token Generation - POST /api/agora/token with different roles
4. Test Invite to Stage Flow - POST /api/rooms/{roomId}/invite-to-stage
5. Test Raise Hand - POST /api/rooms/{roomId}/raise-hand
6. Verify Room Participant States - Check role changes persist
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://parallels-ai.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class VibeRoomAudioTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.test_room_id = None
        self.test_user_id = "u2"  # Using seeded user u2 for testing (u1 will be host)
        
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
    
    def authenticate_demo_user(self):
        """Authenticate demo user and get token"""
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
                        "Demo User Authentication", 
                        True, 
                        f"Successfully authenticated as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Demo User Authentication", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo User Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Authentication", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def create_test_room(self):
        """Create a test VibeRoom for audio testing"""
        try:
            # Use seeded user u1 as host since demo user might not be in MongoDB
            host_user_id = "u1"
            
            payload = {
                "name": "Audio Test Room",
                "description": "Testing audio/microphone functionality",
                "category": "tech",
                "isPrivate": False,
                "tags": ["test", "audio"]
            }
            params = {"userId": host_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'agoraChannel' in data:
                    self.test_room_id = data['id']
                    # Update demo_user_id to the host that created the room
                    self.demo_user_id = host_user_id
                    self.log_result(
                        "Create Test Room", 
                        True, 
                        f"Successfully created test room: {data['name']}",
                        f"Room ID: {self.test_room_id}, Agora Channel: {data['agoraChannel']}, Host: {host_user_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Create Test Room", 
                        False, 
                        "Room creation response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create Test Room", 
                    False, 
                    f"Room creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create Test Room", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_get_room_data(self):
        """Test 1: Get Room Data - GET /api/rooms/{roomId}"""
        if not self.test_room_id:
            self.log_result("Get Room Data", False, "Skipped - no test room ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.test_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                if ('id' in data and 'participants' in data and 'hostId' in data and 
                    'agoraChannel' in data):
                    
                    participants = data['participants']
                    host_participant = next((p for p in participants if p['userId'] == self.demo_user_id), None)
                    
                    if host_participant and host_participant['role'] == 'host':
                        self.log_result(
                            "Get Room Data", 
                            True, 
                            f"Room data retrieved successfully with {len(participants)} participants",
                            f"Host role verified, Agora channel: {data['agoraChannel']}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Get Room Data", 
                            False, 
                            "Host participant not found or role incorrect",
                            f"Participants: {participants}"
                        )
                else:
                    self.log_result(
                        "Get Room Data", 
                        False, 
                        "Room data missing required fields",
                        f"Available fields: {list(data.keys())}"
                    )
            else:
                self.log_result(
                    "Get Room Data", 
                    False, 
                    f"Get room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Room Data", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_join_room_as_audience(self):
        """Join test user to room as audience member"""
        if not self.test_room_id:
            self.log_result("Join Room as Audience", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {"userId": self.test_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.test_room_id}/join", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'participant' in data and data['participant']['role'] == 'audience':
                    self.log_result(
                        "Join Room as Audience", 
                        True, 
                        f"User {self.test_user_id} joined as audience member",
                        f"Role: {data['participant']['role']}, Muted: {data['participant']['isMuted']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Join Room as Audience", 
                        False, 
                        "Join response missing participant data or incorrect role",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Join Room as Audience", 
                    False, 
                    f"Join room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Join Room as Audience", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_role_permissions(self):
        """Test 2: Test Role Permissions - Check participant roles"""
        if not self.test_room_id:
            self.log_result("Test Role Permissions", False, "Skipped - no test room ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.test_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                participants = data.get('participants', [])
                
                # Check for different roles
                roles_found = {}
                for participant in participants:
                    role = participant.get('role')
                    if role:
                        roles_found[role] = roles_found.get(role, 0) + 1
                
                # Verify host exists
                host_found = any(p['role'] == 'host' and p['userId'] == self.demo_user_id for p in participants)
                audience_found = any(p['role'] == 'audience' and p['userId'] == self.test_user_id for p in participants)
                
                if host_found and audience_found:
                    self.log_result(
                        "Test Role Permissions", 
                        True, 
                        f"Role permissions verified - found roles: {list(roles_found.keys())}",
                        f"Host: {host_found}, Audience: {audience_found}, Total participants: {len(participants)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Test Role Permissions", 
                        False, 
                        "Required roles not found",
                        f"Host found: {host_found}, Audience found: {audience_found}, Roles: {roles_found}"
                    )
            else:
                self.log_result(
                    "Test Role Permissions", 
                    False, 
                    f"Get room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Role Permissions", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_agora_token_generation_publisher(self):
        """Test 3a: Test Agora Token Generation - Publisher role (for speakers)"""
        if not self.test_room_id:
            self.log_result("Agora Token Generation (Publisher)", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {
                "channelName": self.test_room_id,
                "uid": 12345,
                "role": "publisher"
            }
            
            response = self.session.post(f"{BACKEND_URL}/agora/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if ('token' in data and 'appId' in data and 'channelName' in data and 
                    data.get('success') == True):
                    self.log_result(
                        "Agora Token Generation (Publisher)", 
                        True, 
                        "Successfully generated publisher token for speakers",
                        f"Channel: {data['channelName']}, UID: {data.get('uid')}, Token length: {len(data['token'])}"
                    )
                    return True
                else:
                    self.log_result(
                        "Agora Token Generation (Publisher)", 
                        False, 
                        "Token response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Agora Token Generation (Publisher)", 
                    False, 
                    f"Token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Agora Token Generation (Publisher)", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_agora_token_generation_subscriber(self):
        """Test 3b: Test Agora Token Generation - Subscriber role (for audience)"""
        if not self.test_room_id:
            self.log_result("Agora Token Generation (Subscriber)", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {
                "channelName": self.test_room_id,
                "uid": 67890,
                "role": "subscriber"
            }
            
            response = self.session.post(f"{BACKEND_URL}/agora/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if ('token' in data and 'appId' in data and 'channelName' in data and 
                    data.get('success') == True):
                    self.log_result(
                        "Agora Token Generation (Subscriber)", 
                        True, 
                        "Successfully generated subscriber token for audience",
                        f"Channel: {data['channelName']}, UID: {data.get('uid')}, Token length: {len(data['token'])}"
                    )
                    return True
                else:
                    self.log_result(
                        "Agora Token Generation (Subscriber)", 
                        False, 
                        "Token response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Agora Token Generation (Subscriber)", 
                    False, 
                    f"Token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Agora Token Generation (Subscriber)", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_raise_hand(self):
        """Test 4: Test Raise Hand - POST /api/rooms/{roomId}/raise-hand"""
        if not self.test_room_id:
            self.log_result("Test Raise Hand", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {"userId": self.test_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.test_room_id}/raise-hand", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'participants' in data:
                    # Check if user's raisedHand flag is set
                    participants = data['participants']
                    user_participant = next((p for p in participants if p['userId'] == self.test_user_id), None)
                    
                    if user_participant and user_participant.get('raisedHand') == True:
                        self.log_result(
                            "Test Raise Hand", 
                            True, 
                            f"Successfully raised hand for user {self.test_user_id}",
                            f"raisedHand flag: {user_participant['raisedHand']}, Role: {user_participant['role']}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Test Raise Hand", 
                            False, 
                            "Raise hand flag not set correctly",
                            f"User participant: {user_participant}"
                        )
                else:
                    self.log_result(
                        "Test Raise Hand", 
                        False, 
                        "Raise hand response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test Raise Hand", 
                    False, 
                    f"Raise hand failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Raise Hand", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_invite_to_stage(self):
        """Test 5: Test Invite to Stage Flow - POST /api/rooms/{roomId}/invite-to-stage"""
        if not self.test_room_id:
            self.log_result("Test Invite to Stage", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {
                "userId": self.demo_user_id,  # Host inviting
                "targetUserId": self.test_user_id  # Audience member being invited
            }
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.test_room_id}/invite-to-stage", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'participants' in data:
                    # Check if user's role changed to speaker
                    participants = data['participants']
                    user_participant = next((p for p in participants if p['userId'] == self.test_user_id), None)
                    
                    if (user_participant and user_participant.get('role') == 'speaker' and 
                        user_participant.get('isMuted') == False and 
                        user_participant.get('raisedHand') == False):
                        self.log_result(
                            "Test Invite to Stage", 
                            True, 
                            f"Successfully invited user {self.test_user_id} to stage as speaker",
                            f"New role: {user_participant['role']}, Muted: {user_participant['isMuted']}, RaisedHand: {user_participant['raisedHand']}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Test Invite to Stage", 
                            False, 
                            "User role not updated correctly after invite to stage",
                            f"User participant: {user_participant}"
                        )
                else:
                    self.log_result(
                        "Test Invite to Stage", 
                        False, 
                        "Invite to stage response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Test Invite to Stage", 
                    False, 
                    f"Invite to stage failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Test Invite to Stage", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_verify_room_participant_states(self):
        """Test 6: Verify Room Participant States - Check role changes persist"""
        if not self.test_room_id:
            self.log_result("Verify Room Participant States", False, "Skipped - no test room ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.test_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                participants = data.get('participants', [])
                
                # Find the test user who should now be a speaker
                user_participant = next((p for p in participants if p['userId'] == self.test_user_id), None)
                host_participant = next((p for p in participants if p['userId'] == self.demo_user_id), None)
                
                if (user_participant and user_participant.get('role') == 'speaker' and 
                    host_participant and host_participant.get('role') == 'host'):
                    
                    # Verify speaker has correct permissions
                    speaker_can_speak = (user_participant.get('role') == 'speaker' and 
                                       user_participant.get('isMuted') == False)
                    
                    # Verify audience members don't have publish permissions
                    audience_members = [p for p in participants if p.get('role') == 'audience']
                    audience_properly_muted = all(p.get('isMuted') == True for p in audience_members)
                    
                    if speaker_can_speak:
                        self.log_result(
                            "Verify Room Participant States", 
                            True, 
                            f"Role changes persisted correctly - speaker can speak, audience muted",
                            f"Speaker role: {user_participant['role']}, Speaker muted: {user_participant['isMuted']}, Audience members: {len(audience_members)}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Room Participant States", 
                            False, 
                            "Speaker permissions not set correctly",
                            f"Speaker can speak: {speaker_can_speak}, User participant: {user_participant}"
                        )
                else:
                    self.log_result(
                        "Verify Room Participant States", 
                        False, 
                        "Required participants not found or roles incorrect",
                        f"User participant: {user_participant}, Host participant: {host_participant}"
                    )
            else:
                self.log_result(
                    "Verify Room Participant States", 
                    False, 
                    f"Get room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Room Participant States", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def test_speaker_agora_token_generation(self):
        """Test 7: Verify speaker can get publisher token after role change"""
        if not self.test_room_id:
            self.log_result("Speaker Agora Token Generation", False, "Skipped - no test room ID available")
            return False
            
        try:
            params = {
                "channelName": self.test_room_id,
                "uid": int(self.test_user_id.replace('u', '')) if self.test_user_id.startswith('u') else 999,
                "role": "publisher"  # Speaker should be able to get publisher token
            }
            
            response = self.session.post(f"{BACKEND_URL}/agora/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if ('token' in data and 'appId' in data and 'channelName' in data and 
                    data.get('success') == True):
                    self.log_result(
                        "Speaker Agora Token Generation", 
                        True, 
                        "Speaker can successfully generate publisher token for microphone access",
                        f"Channel: {data['channelName']}, UID: {data.get('uid')}, Token generated for speaker role"
                    )
                    return True
                else:
                    self.log_result(
                        "Speaker Agora Token Generation", 
                        False, 
                        "Speaker token response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Speaker Agora Token Generation", 
                    False, 
                    f"Speaker token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Speaker Agora Token Generation", False, f"Exception occurred: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """Run all VibeRooms audio/microphone tests"""
        print("🎵 STARTING VIBEROOM AUDIO/MICROPHONE FUNCTIONALITY TESTING")
        print("=" * 70)
        
        # Setup
        if not self.authenticate_demo_user():
            print("❌ CRITICAL: Demo user authentication failed - cannot proceed with tests")
            return
        
        if not self.create_test_room():
            print("❌ CRITICAL: Test room creation failed - cannot proceed with tests")
            return
        
        if not self.test_join_room_as_audience():
            print("❌ CRITICAL: Cannot join room as audience - cannot proceed with tests")
            return
        
        # Core tests from the review request
        test_methods = [
            self.test_get_room_data,
            self.test_role_permissions,
            self.test_agora_token_generation_publisher,
            self.test_agora_token_generation_subscriber,
            self.test_raise_hand,
            self.test_invite_to_stage,
            self.test_verify_room_participant_states,
            self.test_speaker_agora_token_generation
        ]
        
        for test_method in test_methods:
            test_method()
        
        # Summary
        print("\n" + "=" * 70)
        print("🎵 VIBEROOM AUDIO/MICROPHONE TESTING SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n✅ ALL TESTS PASSED - VibeRooms audio/microphone functionality is working correctly")
            print("✅ Users invited to stage (speakers) CAN speak - microphone functionality verified")
        else:
            print(f"\n❌ {total - passed} TESTS FAILED - VibeRooms audio/microphone functionality has issues")
            print("❌ Users invited to stage (speakers) may NOT be able to speak - microphone issues detected")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result['success']]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = VibeRoomAudioTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)