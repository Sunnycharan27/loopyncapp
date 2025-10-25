#!/usr/bin/env python3
"""
Daily.co VibeRooms Audio Integration Testing Suite
Tests the complete VibeRooms audio connection flow with Daily.co integration.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://vibe-connect-26.preview.emergentagent.com/api"
DEMO_USER_ID = "demo_user"

class DailyVibeRoomTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.room_id = None
        self.daily_room_name = None
        self.daily_room_url = None
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
    
    def test_create_vibe_room_with_audio(self):
        """Test 1: Create a new VibeRoom with Daily.co integration"""
        try:
            payload = {
                "name": "Test Audio VibeRoom",
                "description": "Testing Daily.co audio integration",
                "category": "music",
                "isPrivate": False,
                "tags": ["test", "audio", "daily"]
            }
            
            params = {"userId": DEMO_USER_ID}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if room has required fields
                required_fields = ['id', 'name', 'dailyRoomUrl', 'dailyRoomName', 'hostId', 'participants']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.room_id = data['id']
                    self.daily_room_url = data['dailyRoomUrl']
                    self.daily_room_name = data['dailyRoomName']
                    
                    # Verify Daily.co fields are not empty
                    if self.daily_room_url and self.daily_room_name:
                        self.log_result(
                            "Create VibeRoom with Daily.co Integration", 
                            True, 
                            f"Successfully created VibeRoom with audio: {data['name']}",
                            f"Room ID: {self.room_id}, Daily Room: {self.daily_room_name}, URL: {self.daily_room_url}"
                        )
                    else:
                        self.log_result(
                            "Create VibeRoom with Daily.co Integration", 
                            False, 
                            "VibeRoom created but Daily.co fields are empty",
                            f"dailyRoomUrl: {self.daily_room_url}, dailyRoomName: {self.daily_room_name}"
                        )
                else:
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
    
    def test_verify_room_daily_properties(self):
        """Test 2: Verify the room has dailyRoomUrl and dailyRoomName"""
        if not self.room_id:
            self.log_result("Verify Room Daily.co Properties", False, "Skipped - no room ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.room_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for Daily.co properties
                daily_url = data.get('dailyRoomUrl')
                daily_name = data.get('dailyRoomName')
                
                if daily_url and daily_name:
                    # Verify URL format
                    if daily_url.startswith('https://') and 'daily.co' in daily_url:
                        self.log_result(
                            "Verify Room Daily.co Properties", 
                            True, 
                            f"Room has valid Daily.co properties",
                            f"dailyRoomUrl: {daily_url}, dailyRoomName: {daily_name}"
                        )
                    else:
                        self.log_result(
                            "Verify Room Daily.co Properties", 
                            False, 
                            f"Invalid Daily.co URL format: {daily_url}",
                            f"Expected https://...daily.co/... format"
                        )
                else:
                    self.log_result(
                        "Verify Room Daily.co Properties", 
                        False, 
                        "Room missing Daily.co properties",
                        f"dailyRoomUrl: {daily_url}, dailyRoomName: {daily_name}"
                    )
            else:
                self.log_result(
                    "Verify Room Daily.co Properties", 
                    False, 
                    f"Get room details failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Room Daily.co Properties", False, f"Exception occurred: {str(e)}")
    
    def test_generate_meeting_token_owner(self):
        """Test 3: Generate a meeting token for joining the room as owner"""
        if not self.daily_room_name:
            self.log_result("Generate Meeting Token (Owner)", False, "Skipped - no Daily room name available")
            return
            
        try:
            params = {
                "roomName": self.daily_room_name,
                "userName": "Test User",
                "isOwner": "true"
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'token' in data:
                    self.meeting_token = data['token']
                    
                    # Verify token is a valid JWT format (basic check)
                    token_parts = self.meeting_token.split('.')
                    if len(token_parts) == 3 and len(self.meeting_token) > 100:
                        self.log_result(
                            "Generate Meeting Token (Owner)", 
                            True, 
                            f"Successfully generated meeting token",
                            f"Token length: {len(self.meeting_token)} characters, Format: JWT"
                        )
                    else:
                        self.log_result(
                            "Generate Meeting Token (Owner)", 
                            False, 
                            f"Invalid token format received",
                            f"Token: {self.meeting_token[:50]}... (length: {len(self.meeting_token)})"
                        )
                else:
                    self.log_result(
                        "Generate Meeting Token (Owner)", 
                        False, 
                        "Token generation response missing 'token' field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Generate Meeting Token (Owner)", 
                    False, 
                    f"Token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Generate Meeting Token (Owner)", False, f"Exception occurred: {str(e)}")
    
    def test_generate_meeting_token_participant(self):
        """Test 4: Generate a meeting token for joining the room as participant"""
        if not self.daily_room_name:
            self.log_result("Generate Meeting Token (Participant)", False, "Skipped - no Daily room name available")
            return
            
        try:
            params = {
                "roomName": self.daily_room_name,
                "userName": "Test Participant",
                "isOwner": "false"
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'token' in data:
                    participant_token = data['token']
                    
                    # Verify token is different from owner token and valid format
                    token_parts = participant_token.split('.')
                    if len(token_parts) == 3 and len(participant_token) > 100:
                        if participant_token != self.meeting_token:
                            self.log_result(
                                "Generate Meeting Token (Participant)", 
                                True, 
                                f"Successfully generated participant token (different from owner)",
                                f"Token length: {len(participant_token)} characters"
                            )
                        else:
                            self.log_result(
                                "Generate Meeting Token (Participant)", 
                                False, 
                                "Participant token is identical to owner token",
                                "Tokens should be different for different roles"
                            )
                    else:
                        self.log_result(
                            "Generate Meeting Token (Participant)", 
                            False, 
                            f"Invalid participant token format",
                            f"Token: {participant_token[:50]}..."
                        )
                else:
                    self.log_result(
                        "Generate Meeting Token (Participant)", 
                        False, 
                        "Participant token response missing 'token' field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Generate Meeting Token (Participant)", 
                    False, 
                    f"Participant token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Generate Meeting Token (Participant)", False, f"Exception occurred: {str(e)}")
    
    def test_join_room(self):
        """Test 5: Join the VibeRoom"""
        if not self.room_id:
            self.log_result("Join VibeRoom", False, "Skipped - no room ID available")
            return
            
        try:
            params = {"userId": DEMO_USER_ID}
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.room_id}/join", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'success' in data and data['success']:
                    self.log_result(
                        "Join VibeRoom", 
                        True, 
                        f"Successfully joined VibeRoom",
                        f"Response: {data}"
                    )
                elif 'message' in data:
                    # Check if already joined
                    if "already" in data['message'].lower():
                        self.log_result(
                            "Join VibeRoom", 
                            True, 
                            f"User already in room: {data['message']}",
                            "Already joined is acceptable"
                        )
                    else:
                        self.log_result(
                            "Join VibeRoom", 
                            True, 
                            f"Room join response: {data['message']}",
                            f"Full response: {data}"
                        )
                else:
                    self.log_result(
                        "Join VibeRoom", 
                        False, 
                        "Join room response format unexpected",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Join VibeRoom", 
                    False, 
                    f"Join room failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Join VibeRoom", False, f"Exception occurred: {str(e)}")
    
    def test_daily_api_endpoints(self):
        """Test 6: Test Daily.co API endpoints directly"""
        try:
            # Test direct Daily.co room creation
            params = {
                "userId": DEMO_USER_ID,
                "roomName": "Direct Test Room"
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/rooms", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'dailyRoomUrl' in data and 'dailyRoomName' in data and 'success' in data:
                    if data['success']:
                        self.log_result(
                            "Daily.co API Endpoints", 
                            True, 
                            f"Direct Daily.co room creation successful",
                            f"Room: {data['dailyRoomName']}, URL: {data['dailyRoomUrl']}"
                        )
                    else:
                        self.log_result(
                            "Daily.co API Endpoints", 
                            False, 
                            "Daily.co room creation returned success=false",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "Daily.co API Endpoints", 
                        False, 
                        "Daily.co room creation response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Daily.co API Endpoints", 
                    False, 
                    f"Daily.co room creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily.co API Endpoints", False, f"Exception occurred: {str(e)}")
    
    def test_room_participants_list(self):
        """Test 7: Verify room participants list includes joined user"""
        if not self.room_id:
            self.log_result("Room Participants List", False, "Skipped - no room ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.room_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'participants' in data:
                    participants = data['participants']
                    
                    if isinstance(participants, list):
                        # Look for demo user in participants
                        demo_participant = None
                        for participant in participants:
                            if participant.get('userId') == DEMO_USER_ID:
                                demo_participant = participant
                                break
                        
                        if demo_participant:
                            # Check participant properties
                            required_props = ['userId', 'role', 'joinedAt']
                            missing_props = [prop for prop in required_props if prop not in demo_participant]
                            
                            if not missing_props:
                                self.log_result(
                                    "Room Participants List", 
                                    True, 
                                    f"Demo user found in participants with role: {demo_participant['role']}",
                                    f"Participant: {demo_participant}"
                                )
                            else:
                                self.log_result(
                                    "Room Participants List", 
                                    False, 
                                    f"Participant missing properties: {missing_props}",
                                    f"Participant: {demo_participant}"
                                )
                        else:
                            self.log_result(
                                "Room Participants List", 
                                False, 
                                f"Demo user not found in participants list",
                                f"Participants: {[p.get('userId') for p in participants]}"
                            )
                    else:
                        self.log_result(
                            "Room Participants List", 
                            False, 
                            "Participants field is not a list",
                            f"Participants type: {type(participants)}"
                        )
                else:
                    self.log_result(
                        "Room Participants List", 
                        False, 
                        "Room response missing participants field",
                        f"Available fields: {list(data.keys())}"
                    )
            else:
                self.log_result(
                    "Room Participants List", 
                    False, 
                    f"Get room details failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Room Participants List", False, f"Exception occurred: {str(e)}")
    
    def test_all_rooms_list(self):
        """Test 8: Verify created room appears in rooms list"""
        if not self.room_id:
            self.log_result("All Rooms List", False, "Skipped - no room ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Look for our created room
                    created_room = None
                    for room in data:
                        if room.get('id') == self.room_id:
                            created_room = room
                            break
                    
                    if created_room:
                        # Verify room has Daily.co properties in list
                        if 'dailyRoomUrl' in created_room and 'dailyRoomName' in created_room:
                            self.log_result(
                                "All Rooms List", 
                                True, 
                                f"Created room found in list with Daily.co properties",
                                f"Room: {created_room['name']}, Total rooms: {len(data)}"
                            )
                        else:
                            self.log_result(
                                "All Rooms List", 
                                False, 
                                "Created room found but missing Daily.co properties in list",
                                f"Room fields: {list(created_room.keys())}"
                            )
                    else:
                        self.log_result(
                            "All Rooms List", 
                            False, 
                            f"Created room not found in rooms list",
                            f"Available room IDs: {[r.get('id') for r in data]}"
                        )
                else:
                    self.log_result(
                        "All Rooms List", 
                        False, 
                        "Rooms list response is not an array",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "All Rooms List", 
                    False, 
                    f"Get rooms list failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("All Rooms List", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all Daily.co VibeRooms integration tests"""
        print("🎵 Starting Daily.co VibeRooms Audio Integration Tests...")
        print("=" * 70)
        
        # Run tests in sequence
        self.test_create_vibe_room_with_audio()
        self.test_verify_room_daily_properties()
        self.test_generate_meeting_token_owner()
        self.test_generate_meeting_token_participant()
        self.test_join_room()
        self.test_daily_api_endpoints()
        self.test_room_participants_list()
        self.test_all_rooms_list()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎵 Daily.co VibeRooms Integration Test Summary")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL DAILY.CO VIBEROOM INTEGRATION TESTS PASSED!")
            print("✅ Audio room creation working correctly")
            print("✅ Daily.co properties properly set")
            print("✅ Meeting token generation functional")
            print("✅ Room joining flow operational")
            print("✅ All Daily.co endpoints working")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Daily.co integration needs attention.")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result['success']]
            for failed in failed_tests:
                print(f"❌ {failed['test']}: {failed['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = DailyVibeRoomTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)