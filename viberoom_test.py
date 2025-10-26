#!/usr/bin/env python3
"""
VibeRoom Creation Issue Testing
Tests the specific issue where user gets "Failed to create room" error
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://socialsuper-app.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class VibeRoomTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        
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
        """Test 1: Login as demo user to get authentication"""
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
    
    def test_demo_user_exists(self):
        """Test 2: Check if demo_user exists and has proper data"""
        try:
            # Check if demo_user exists in the system
            response = self.session.get(f"{BACKEND_URL}/users/demo_user")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "Demo User Exists", 
                        True, 
                        f"demo_user found: {data['name']} (ID: {data['id']})",
                        f"User data: {data}"
                    )
                else:
                    self.log_result(
                        "Demo User Exists", 
                        False, 
                        "demo_user found but missing required fields",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Demo User Exists", 
                    False, 
                    "demo_user not found in system",
                    "This could be the root cause of room creation failure"
                )
            else:
                self.log_result(
                    "Demo User Exists", 
                    False, 
                    f"Error checking demo_user: status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo User Exists", False, f"Exception occurred: {str(e)}")
    
    def test_room_creation_original_issue(self):
        """Test 3: Test the exact room creation that's failing"""
        try:
            # The exact room data that's causing the issue
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
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "Room Creation (Original Issue)", 
                        True, 
                        f"Successfully created room: {data['name']} (ID: {data['id']})",
                        f"Room data: {data}"
                    )
                else:
                    self.log_result(
                        "Room Creation (Original Issue)", 
                        False, 
                        "Room created but response missing required fields",
                        f"Response: {data}"
                    )
            else:
                # This is the expected failure - capture the exact error
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Room Creation (Original Issue)", 
                    False, 
                    f"Room creation failed with status {response.status_code}",
                    f"Error message: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Room Creation (Original Issue)", False, f"Exception occurred: {str(e)}")
    
    def test_room_creation_with_auth_token(self):
        """Test 4: Test room creation with proper authentication token"""
        if not self.demo_token:
            self.log_result("Room Creation (With Auth)", False, "Skipped - no demo token available")
            return
            
        try:
            payload = {
                "name": "sting",
                "description": "energy",
                "category": "General",
                "isPrivate": False
            }
            
            params = {"userId": "demo_user"}
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "Room Creation (With Auth)", 
                        True, 
                        f"Successfully created room with auth: {data['name']} (ID: {data['id']})",
                        f"Room data: {data}"
                    )
                else:
                    self.log_result(
                        "Room Creation (With Auth)", 
                        False, 
                        "Room created but response missing required fields",
                        f"Response: {data}"
                    )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Room Creation (With Auth)", 
                    False, 
                    f"Room creation with auth failed with status {response.status_code}",
                    f"Error message: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Room Creation (With Auth)", False, f"Exception occurred: {str(e)}")
    
    def test_room_creation_with_logged_in_user_id(self):
        """Test 5: Test room creation using the actual logged-in user ID"""
        if not self.demo_user_id:
            self.log_result("Room Creation (Logged User ID)", False, "Skipped - no demo user ID available")
            return
            
        try:
            payload = {
                "name": "sting",
                "description": "energy",
                "category": "General",
                "isPrivate": False
            }
            
            params = {"userId": self.demo_user_id}
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "Room Creation (Logged User ID)", 
                        True, 
                        f"Successfully created room with logged user ID: {data['name']} (ID: {data['id']})",
                        f"Room data: {data}"
                    )
                else:
                    self.log_result(
                        "Room Creation (Logged User ID)", 
                        False, 
                        "Room created but response missing required fields",
                        f"Response: {data}"
                    )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Room Creation (Logged User ID)", 
                    False, 
                    f"Room creation with logged user ID failed with status {response.status_code}",
                    f"Error message: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Room Creation (Logged User ID)", False, f"Exception occurred: {str(e)}")
    
    def test_simple_room_creation(self):
        """Test 6: Test with simpler room data"""
        if not self.demo_user_id:
            self.log_result("Simple Room Creation", False, "Skipped - no demo user ID available")
            return
            
        try:
            payload = {
                "name": "Test Room",
                "description": "Test",
                "category": "General"
            }
            
            params = {"userId": self.demo_user_id}
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            
            response = self.session.post(f"{BACKEND_URL}/rooms", json=payload, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "Simple Room Creation", 
                        True, 
                        f"Successfully created simple room: {data['name']} (ID: {data['id']})",
                        f"Room data: {data}"
                    )
                else:
                    self.log_result(
                        "Simple Room Creation", 
                        False, 
                        "Simple room created but response missing required fields",
                        f"Response: {data}"
                    )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Simple Room Creation", 
                    False, 
                    f"Simple room creation failed with status {response.status_code}",
                    f"Error message: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Simple Room Creation", False, f"Exception occurred: {str(e)}")
    
    def test_agora_integration_check(self):
        """Test 7: Check if Agora integration is working"""
        try:
            # Check if there's a Daily.co rooms endpoint (mentioned in backend code)
            response = self.session.post(f"{BACKEND_URL}/daily/rooms", params={"userId": "demo_user", "roomName": "Test Audio Room"})
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Agora Integration Check", 
                    True, 
                    "Daily.co integration working",
                    f"Response: {data}"
                )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Unknown error')
                except:
                    error_message = response.text
                
                self.log_result(
                    "Agora Integration Check", 
                    False, 
                    f"Daily.co integration failed with status {response.status_code}",
                    f"Error message: {error_message}"
                )
                
        except Exception as e:
            self.log_result("Agora Integration Check", False, f"Exception occurred: {str(e)}")
    
    def check_backend_logs(self):
        """Test 8: Check backend logs for any errors"""
        try:
            # This is a placeholder - in a real scenario we'd check server logs
            # For now, we'll just report what we've found
            failed_tests = [result for result in self.test_results if not result['success']]
            
            if failed_tests:
                error_summary = []
                for test in failed_tests:
                    error_summary.append(f"{test['test']}: {test['message']}")
                
                self.log_result(
                    "Backend Error Analysis", 
                    False, 
                    f"Found {len(failed_tests)} failing tests",
                    f"Errors: {'; '.join(error_summary)}"
                )
            else:
                self.log_result(
                    "Backend Error Analysis", 
                    True, 
                    "No errors found in testing",
                    "All room creation tests passed"
                )
                
        except Exception as e:
            self.log_result("Backend Error Analysis", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all VibeRoom creation tests"""
        print("🧪 Starting VibeRoom Creation Issue Testing...")
        print("=" * 60)
        
        # Run tests in sequence
        self.test_demo_login()
        self.test_demo_user_exists()
        self.test_room_creation_original_issue()
        self.test_room_creation_with_auth_token()
        self.test_room_creation_with_logged_in_user_id()
        self.test_simple_room_creation()
        self.test_agora_integration_check()
        self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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
        
        return self.test_results

if __name__ == "__main__":
    tester = VibeRoomTester()
    results = tester.run_all_tests()