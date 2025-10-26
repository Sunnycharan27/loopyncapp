#!/usr/bin/env python3
"""
Comprehensive VibeRoom Testing
Tests room creation, retrieval, and all related functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://parallels-ai.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class ComprehensiveRoomTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.created_room_id = None
        
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
    
    def test_demo_login(self):
        """Test 1: Login as demo user"""
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
                        "Demo Login", 
                        True, 
                        f"Successfully logged in as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                else:
                    self.log_result(
                        "Demo Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo Login", False, f"Exception occurred: {str(e)}")
    
    def test_room_creation_exact_issue(self):
        """Test 2: Create room with exact parameters from issue"""
        try:
            payload = {
                "name": "sting",
                "description": "energy",
                "category": "General",
                "isPrivate": False
            }
            
            params = {"userId": "demo_user"}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data and 'agoraChannel' in data:
                    self.created_room_id = data['id']
                    self.log_result(
                        "Room Creation (Exact Issue)", 
                        True, 
                        f"Successfully created room: {data['name']} (ID: {data['id']})",
                        f"Agora Channel: {data['agoraChannel']}, Host: {data.get('hostName', 'Unknown')}"
                    )
                else:
                    self.log_result(
                        "Room Creation (Exact Issue)", 
                        False, 
                        "Room created but missing required fields",
                        f"Response fields: {list(data.keys())}"
                    )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Room Creation (Exact Issue)", 
                    False, 
                    f"Room creation failed with status {response.status_code}",
                    f"Error: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Room Creation (Exact Issue)", False, f"Exception occurred: {str(e)}")
    
    def test_room_retrieval(self):
        """Test 3: Retrieve the created room"""
        if not self.created_room_id:
            self.log_result("Room Retrieval", False, "Skipped - no room ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.created_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data and 'participants' in data:
                    self.log_result(
                        "Room Retrieval", 
                        True, 
                        f"Successfully retrieved room: {data['name']}",
                        f"Participants: {len(data['participants'])}, Status: {data.get('status', 'unknown')}"
                    )
                else:
                    self.log_result(
                        "Room Retrieval", 
                        False, 
                        "Room retrieved but missing required fields",
                        f"Response fields: {list(data.keys())}"
                    )
            else:
                self.log_result(
                    "Room Retrieval", 
                    False, 
                    f"Room retrieval failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Room Retrieval", False, f"Exception occurred: {str(e)}")
    
    def test_rooms_list(self):
        """Test 4: Get list of all active rooms"""
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for our created room
                    our_room = None
                    if self.created_room_id:
                        our_room = next((room for room in data if room.get('id') == self.created_room_id), None)
                    
                    if our_room:
                        self.log_result(
                            "Rooms List", 
                            True, 
                            f"Found {len(data)} rooms including our created room",
                            f"Our room: {our_room['name']} with {len(our_room.get('participants', []))} participants"
                        )
                    else:
                        self.log_result(
                            "Rooms List", 
                            True, 
                            f"Retrieved {len(data)} active rooms",
                            f"Room names: {[room.get('name', 'Unknown') for room in data[:3]]}"
                        )
                else:
                    self.log_result(
                        "Rooms List", 
                        False, 
                        "Rooms list response is not an array",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Rooms List", 
                    False, 
                    f"Rooms list failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Rooms List", False, f"Exception occurred: {str(e)}")
    
    def test_room_join(self):
        """Test 5: Join the created room"""
        if not self.created_room_id:
            self.log_result("Room Join", False, "Skipped - no room ID available")
            return
            
        try:
            params = {"userId": self.demo_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/rooms/{self.created_room_id}/join", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Room Join", 
                    True, 
                    "Successfully joined room",
                    f"Response: {data}"
                )
            elif response.status_code == 400:
                # User might already be in the room (as host)
                try:
                    error_data = response.json()
                    if "already" in error_data.get('detail', '').lower():
                        self.log_result(
                            "Room Join", 
                            True, 
                            "User already in room (expected as host)",
                            f"Response: {error_data}"
                        )
                    else:
                        self.log_result(
                            "Room Join", 
                            False, 
                            f"Room join failed: {error_data.get('detail', 'Unknown error')}",
                            f"Response: {error_data}"
                        )
                except:
                    self.log_result(
                        "Room Join", 
                        False, 
                        f"Room join failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "Room Join", 
                    False, 
                    f"Room join failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Room Join", False, f"Exception occurred: {str(e)}")
    
    def test_agora_token_generation(self):
        """Test 6: Test Agora token generation for the room"""
        if not self.created_room_id:
            self.log_result("Agora Token Generation", False, "Skipped - no room ID available")
            return
            
        try:
            params = {
                "roomName": self.created_room_id,
                "userName": "Demo User",
                "isOwner": "true"
            }
            
            response = self.session.post(f"{BACKEND_URL}/agora/token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.log_result(
                        "Agora Token Generation", 
                        True, 
                        "Successfully generated Agora token",
                        f"Token length: {len(data['token'])}"
                    )
                else:
                    self.log_result(
                        "Agora Token Generation", 
                        False, 
                        "Token response missing token field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Agora Token Generation", 
                    False, 
                    f"Agora token generation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Agora Token Generation", False, f"Exception occurred: {str(e)}")
    
    def test_room_with_different_categories(self):
        """Test 7: Test room creation with different categories"""
        categories = ["music", "tech", "gaming", "lifestyle", "business"]
        
        for category in categories:
            try:
                payload = {
                    "name": f"Test {category.title()} Room",
                    "description": f"Testing {category} category",
                    "category": category,
                    "isPrivate": False
                }
                
                params = {"userId": self.demo_user_id}
                
                response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        f"Room Creation ({category.title()})", 
                        True, 
                        f"Successfully created {category} room: {data['name']}",
                        f"Room ID: {data['id']}"
                    )
                else:
                    self.log_result(
                        f"Room Creation ({category.title()})", 
                        False, 
                        f"Failed to create {category} room with status {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"Room Creation ({category.title()})", False, f"Exception occurred: {str(e)}")
    
    def test_private_room_creation(self):
        """Test 8: Test private room creation"""
        try:
            payload = {
                "name": "Private Test Room",
                "description": "Testing private room functionality",
                "category": "General",
                "isPrivate": True
            }
            
            params = {"userId": self.demo_user_id}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('isPrivate') == True:
                    self.log_result(
                        "Private Room Creation", 
                        True, 
                        f"Successfully created private room: {data['name']}",
                        f"Room ID: {data['id']}, Private: {data['isPrivate']}"
                    )
                else:
                    self.log_result(
                        "Private Room Creation", 
                        False, 
                        "Private room created but isPrivate flag not set correctly",
                        f"isPrivate: {data.get('isPrivate')}"
                    )
            else:
                self.log_result(
                    "Private Room Creation", 
                    False, 
                    f"Private room creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Private Room Creation", False, f"Exception occurred: {str(e)}")
    
    def test_room_validation(self):
        """Test 9: Test room creation validation"""
        # Test with missing required fields
        test_cases = [
            {"payload": {}, "description": "empty payload"},
            {"payload": {"name": ""}, "description": "empty name"},
            {"payload": {"name": "Test", "category": "InvalidCategory"}, "description": "invalid category"},
        ]
        
        for case in test_cases:
            try:
                params = {"userId": self.demo_user_id}
                
                response = self.session.post(f"{BACKEND_URL}/rooms", json=case["payload"], params=params)
                
                if response.status_code == 422:  # Validation error
                    self.log_result(
                        f"Room Validation ({case['description']})", 
                        True, 
                        f"Correctly rejected {case['description']} with validation error",
                        f"Status: {response.status_code}"
                    )
                elif response.status_code == 200:
                    self.log_result(
                        f"Room Validation ({case['description']})", 
                        False, 
                        f"Validation issue: {case['description']} was accepted",
                        f"Response: {response.json()}"
                    )
                else:
                    self.log_result(
                        f"Room Validation ({case['description']})", 
                        True, 
                        f"Rejected {case['description']} with status {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"Room Validation ({case['description']})", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive room tests"""
        print("🧪 Starting Comprehensive VibeRoom Testing...")
        print("=" * 60)
        
        # Run tests in sequence
        self.test_demo_login()
        self.test_room_creation_exact_issue()
        self.test_room_retrieval()
        self.test_rooms_list()
        self.test_room_join()
        self.test_agora_token_generation()
        self.test_room_with_different_categories()
        self.test_private_room_creation()
        self.test_room_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
                    if result['details']:
                        print(f"    Details: {result['details']}")
        
        # Analysis
        print("\n🔍 ANALYSIS:")
        if failed_tests == 0:
            print("✅ All room creation and management functionality is working correctly")
            print("✅ The reported 'Failed to create room' issue is NOT reproducible in backend")
            print("🔍 Issue might be frontend-related or user-specific")
        else:
            print("❌ Found issues with room functionality")
            print("🔧 These issues need to be addressed")
        
        return self.test_results

if __name__ == "__main__":
    tester = ComprehensiveRoomTester()
    results = tester.run_all_tests()