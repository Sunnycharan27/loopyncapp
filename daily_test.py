#!/usr/bin/env python3
"""
Daily.co Audio Integration Testing Suite
Tests Daily.co room creation, Vibe Room integration, and token generation for audio functionality.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://vibe-superapp.preview.emergentagent.com/api"
DEMO_USER_ID = "demo_user"
TEST_ROOM_NAME = "Test Audio Room"

class DailyTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.daily_room_url = None
        self.daily_room_name = None
        self.vibe_room_id = None
        
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
    
    def test_daily_room_creation(self):
        """Test 1: Daily.co Room Creation via /api/daily/rooms"""
        try:
            params = {
                'userId': DEMO_USER_ID,
                'roomName': TEST_ROOM_NAME
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/rooms", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'dailyRoomUrl' in data and 'dailyRoomName' in data and 'success' in data:
                    self.daily_room_url = data['dailyRoomUrl']
                    self.daily_room_name = data['dailyRoomName']
                    self.log_result(
                        "Daily.co Room Creation", 
                        True, 
                        f"Successfully created Daily.co room: {self.daily_room_name}",
                        f"URL: {self.daily_room_url}, Success: {data['success']}"
                    )
                else:
                    self.log_result(
                        "Daily.co Room Creation", 
                        False, 
                        "Daily room response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Daily.co Room Creation", 
                    False, 
                    f"Daily room creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily.co Room Creation", False, f"Exception occurred: {str(e)}")
    
    def test_vibe_room_with_audio(self):
        """Test 2: Create Vibe Room with Daily.co Audio Integration"""
        try:
            payload = {
                "name": "Test Audio Vibe Room",
                "description": "Testing audio integration",
                "category": "music",
                "isPrivate": False,
                "tags": ["test", "audio"]
            }
            params = {"userId": DEMO_USER_ID}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.vibe_room_id = data['id']
                    
                    # Check if Daily.co integration is working
                    if 'dailyRoomUrl' in data and 'dailyRoomName' in data:
                        self.log_result(
                            "Vibe Room with Audio", 
                            True, 
                            f"Successfully created Vibe Room with audio: {data['name']}",
                            f"Room ID: {self.vibe_room_id}, Daily URL: {data['dailyRoomUrl']}, Daily Name: {data['dailyRoomName']}"
                        )
                    else:
                        self.log_result(
                            "Vibe Room with Audio", 
                            False, 
                            f"Vibe Room created but missing Daily.co integration",
                            f"Room ID: {self.vibe_room_id}, Missing fields: dailyRoomUrl, dailyRoomName"
                        )
                else:
                    self.log_result(
                        "Vibe Room with Audio", 
                        False, 
                        "Vibe Room response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Vibe Room with Audio", 
                    False, 
                    f"Vibe Room creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Vibe Room with Audio", False, f"Exception occurred: {str(e)}")
    
    def test_get_room_details(self):
        """Test 3: Get Room Details to verify dailyRoomUrl field"""
        if not self.vibe_room_id:
            self.log_result("Get Room Details", False, "Skipped - no Vibe Room ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.vibe_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    if 'dailyRoomUrl' in data:
                        self.log_result(
                            "Get Room Details", 
                            True, 
                            f"Room details retrieved with Daily.co URL: {data['name']}",
                            f"Daily URL: {data['dailyRoomUrl']}, Participants: {len(data.get('participants', []))}"
                        )
                    else:
                        self.log_result(
                            "Get Room Details", 
                            False, 
                            "Room details missing dailyRoomUrl field",
                            f"Available fields: {list(data.keys())}"
                        )
                else:
                    self.log_result(
                        "Get Room Details", 
                        False, 
                        "Room details response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Get Room Details", 
                    False, 
                    f"Get room details failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Room Details", False, f"Exception occurred: {str(e)}")
    
    def test_daily_token_creation(self):
        """Test 4: Create Daily.co Token for joining rooms"""
        if not self.daily_room_name:
            self.log_result("Daily Token Creation", False, "Skipped - no Daily room name available")
            return
            
        try:
            params = {
                'roomName': self.daily_room_name,
                'userName': 'Demo User',
                'isOwner': True
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'success' in data:
                    self.log_result(
                        "Daily Token Creation", 
                        True, 
                        f"Successfully created Daily.co token for room: {self.daily_room_name}",
                        f"Token length: {len(data['token'])}, Success: {data['success']}"
                    )
                else:
                    self.log_result(
                        "Daily Token Creation", 
                        False, 
                        "Daily token response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Daily Token Creation", 
                    False, 
                    f"Daily token creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily Token Creation", False, f"Exception occurred: {str(e)}")
    
    def test_daily_api_key_validation(self):
        """Test 5: Validate Daily.co API Key is configured"""
        try:
            # Test with a simple room creation to validate API key
            params = {
                'userId': 'test_user',
                'roomName': 'API Key Test Room'
            }
            
            response = self.session.post(f"{BACKEND_URL}/daily/rooms", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result(
                        "Daily API Key Validation", 
                        True, 
                        "Daily.co API key is valid and working",
                        f"Successfully created test room"
                    )
                else:
                    self.log_result(
                        "Daily API Key Validation", 
                        False, 
                        "Daily.co API response indicates failure",
                        f"Response: {data}"
                    )
            elif response.status_code == 500:
                # Check if it's an API key issue
                error_text = response.text.lower()
                if 'api key' in error_text or 'authorization' in error_text or 'unauthorized' in error_text:
                    self.log_result(
                        "Daily API Key Validation", 
                        False, 
                        "Daily.co API key appears to be invalid or missing",
                        f"Error: {response.text}"
                    )
                else:
                    self.log_result(
                        "Daily API Key Validation", 
                        False, 
                        "Daily.co API error (not necessarily API key issue)",
                        f"Error: {response.text}"
                    )
            else:
                self.log_result(
                    "Daily API Key Validation", 
                    False, 
                    f"Daily.co API validation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Daily API Key Validation", False, f"Exception occurred: {str(e)}")
    
    def test_get_active_rooms(self):
        """Test 6: Get Active Vibe Rooms to verify audio rooms are listed"""
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    audio_rooms = [room for room in data if 'dailyRoomUrl' in room]
                    if len(audio_rooms) > 0:
                        self.log_result(
                            "Get Active Rooms", 
                            True, 
                            f"Found {len(audio_rooms)} active rooms with audio integration out of {len(data)} total rooms",
                            f"Audio rooms: {[room['name'] for room in audio_rooms[:3]]}"
                        )
                    else:
                        if len(data) > 0:
                            self.log_result(
                                "Get Active Rooms", 
                                False, 
                                f"Found {len(data)} rooms but none have Daily.co audio integration",
                                f"Room names: {[room.get('name', 'Unknown') for room in data[:3]]}"
                            )
                        else:
                            self.log_result(
                                "Get Active Rooms", 
                                True, 
                                "No active rooms found (acceptable for testing)",
                                "Empty rooms list"
                            )
                else:
                    self.log_result(
                        "Get Active Rooms", 
                        False, 
                        "Active rooms response is not a list",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Get Active Rooms", 
                    False, 
                    f"Get active rooms failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Active Rooms", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all Daily.co integration tests"""
        print("🎵 Starting Daily.co Audio Integration Tests...")
        print("=" * 60)
        
        # Test sequence
        self.test_daily_api_key_validation()
        self.test_daily_room_creation()
        self.test_vibe_room_with_audio()
        self.test_get_room_details()
        self.test_daily_token_creation()
        self.test_get_active_rooms()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DAILY.CO INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL DAILY.CO INTEGRATION TESTS PASSED!")
            print("✅ Daily.co audio integration is working correctly")
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED")
            print("❌ Daily.co audio integration has issues")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result['success']]
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        return self.test_results

def main():
    """Main function to run Daily.co integration tests"""
    tester = DailyTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    failed_count = sum(1 for result in results if not result['success'])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())