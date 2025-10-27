#!/usr/bin/env python3
"""
Messenger Backend Functionality Testing Suite
Tests Trust Circles and DM functionality for the Complete Messenger Backend as requested.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"
DEMO_USER_ID = "demo_user"

class MessengerBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.trust_circle_id = None
        self.dm_thread_id = None
        self.test_user_id = None
        
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
    
    def test_trust_circles_get(self):
        """Test 1: GET /api/trust-circles?userId=demo_user"""
        try:
            params = {'userId': DEMO_USER_ID}
            response = self.session.get(f"{BACKEND_URL}/trust-circles", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Trust Circles GET", 
                        True, 
                        f"Successfully retrieved trust circles ({len(data)} circles)",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Trust Circles GET", 
                        False, 
                        "Trust circles response is not a list",
                        f"Response type: {type(data)}, Data: {data}"
                    )
            elif response.status_code == 404:
                # 404 is acceptable if endpoint doesn't exist yet
                self.log_result(
                    "Trust Circles GET", 
                    False, 
                    "Trust circles endpoint not found (404)",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Trust Circles GET", 
                    False, 
                    f"Trust circles GET failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Trust Circles GET", False, f"Exception occurred: {str(e)}")
    
    def test_trust_circles_create(self):
        """Test 2: POST /api/trust-circles?createdBy=demo_user"""
        try:
            params = {'createdBy': DEMO_USER_ID}
            payload = {
                "name": "Test Circle",
                "description": "Test circle for messaging",
                "icon": "🔵",
                "color": "from-blue-400 to-cyan-500",
                "members": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/trust-circles", params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.trust_circle_id = data['id']
                    self.log_result(
                        "Trust Circles CREATE", 
                        True, 
                        f"Successfully created trust circle: {data['name']}",
                        f"Circle ID: {data['id']}, Members: {len(data.get('members', []))}"
                    )
                else:
                    self.log_result(
                        "Trust Circles CREATE", 
                        False, 
                        "Trust circle creation response missing required fields",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                # 404 is acceptable if endpoint doesn't exist yet
                self.log_result(
                    "Trust Circles CREATE", 
                    False, 
                    "Trust circles create endpoint not found (404)",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Trust Circles CREATE", 
                    False, 
                    f"Trust circle creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Trust Circles CREATE", False, f"Exception occurred: {str(e)}")
    
    def test_dm_threads_get(self):
        """Test 3: GET /api/dm/threads?userId=demo_user"""
        try:
            params = {'userId': DEMO_USER_ID}
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "DM Threads GET", 
                        True, 
                        f"Successfully retrieved DM threads ({len(data)} threads)",
                        f"Response structure: list with {len(data)} items"
                    )
                elif isinstance(data, dict) and 'items' in data:
                    threads = data['items']
                    self.log_result(
                        "DM Threads GET", 
                        True, 
                        f"Successfully retrieved DM threads ({len(threads)} threads)",
                        f"Response structure: dict with items array"
                    )
                else:
                    self.log_result(
                        "DM Threads GET", 
                        False, 
                        "DM threads response format unexpected",
                        f"Response type: {type(data)}, Data: {data}"
                    )
            elif response.status_code == 500:
                # Known backend bug in DM threads endpoint
                self.log_result(
                    "DM Threads GET", 
                    False, 
                    "DM threads endpoint has backend bug (500 error)",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "DM Threads GET", 
                    False, 
                    f"DM threads GET failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Threads GET", False, f"Exception occurred: {str(e)}")
    
    def test_dm_thread_create(self):
        """Test 4: POST /api/dm/create-thread"""
        try:
            # First, create a test user to DM with
            test_user_email = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
            signup_payload = {
                "email": test_user_email,
                "handle": f"testuser_{datetime.now().strftime('%H%M%S')}",
                "name": "Test User for DM",
                "password": "testpassword123"
            }
            
            signup_response = self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.test_user_id = signup_data['user']['id']
                
                # Now try to create DM thread
                dm_payload = {
                    "user1Id": DEMO_USER_ID,
                    "user2Id": self.test_user_id
                }
                
                response = self.session.post(f"{BACKEND_URL}/dm/create-thread", json=dm_payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'threadId' in data or 'id' in data:
                        self.dm_thread_id = data.get('threadId') or data.get('id')
                        self.log_result(
                            "DM Thread CREATE", 
                            True, 
                            f"Successfully created DM thread between demo_user and test user",
                            f"Thread ID: {self.dm_thread_id}"
                        )
                    else:
                        self.log_result(
                            "DM Thread CREATE", 
                            False, 
                            "DM thread creation response missing thread ID",
                            f"Response: {data}"
                        )
                elif response.status_code == 404:
                    self.log_result(
                        "DM Thread CREATE", 
                        False, 
                        "DM thread create endpoint not found (404)",
                        f"Response: {response.text}"
                    )
                else:
                    self.log_result(
                        "DM Thread CREATE", 
                        False, 
                        f"DM thread creation failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "DM Thread CREATE", 
                    False, 
                    "Failed to create test user for DM thread testing",
                    f"Signup response: {signup_response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Thread CREATE", False, f"Exception occurred: {str(e)}")
    
    def test_dm_send_message(self):
        """Test 5: POST /api/dm/threads/{threadId}/messages"""
        if not self.dm_thread_id:
            self.log_result("DM Send Message", False, "Skipped - no DM thread ID available")
            return
            
        try:
            payload = {
                "text": "Hello from messenger backend test!"
            }
            params = {'userId': DEMO_USER_ID}
            
            response = self.session.post(
                f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                params=params, 
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'messageId' in data or 'id' in data:
                    message_id = data.get('messageId') or data.get('id')
                    self.log_result(
                        "DM Send Message", 
                        True, 
                        f"Successfully sent DM message",
                        f"Message ID: {message_id}, Text: {payload['text']}"
                    )
                else:
                    self.log_result(
                        "DM Send Message", 
                        False, 
                        "DM send message response missing message ID",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "DM Send Message", 
                    False, 
                    f"DM send message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Send Message", False, f"Exception occurred: {str(e)}")
    
    def test_dm_get_messages(self):
        """Test 6: GET /api/dm/threads/{threadId}/messages"""
        if not self.dm_thread_id:
            self.log_result("DM Get Messages", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {'userId': DEMO_USER_ID}
            
            response = self.session.get(
                f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = []
                
                if isinstance(data, list):
                    messages = data
                elif isinstance(data, dict) and 'items' in data:
                    messages = data['items']
                
                if len(messages) > 0:
                    # Look for our test message
                    test_messages = [msg for msg in messages if 'Hello from messenger backend test!' in msg.get('text', '')]
                    if test_messages:
                        msg = test_messages[0]
                        self.log_result(
                            "DM Get Messages", 
                            True, 
                            f"Successfully retrieved DM messages and found test message",
                            f"Message ID: {msg.get('id')}, Sender: {msg.get('senderId')}"
                        )
                    else:
                        self.log_result(
                            "DM Get Messages", 
                            True, 
                            f"Successfully retrieved DM messages ({len(messages)} messages)",
                            f"Messages: {[msg.get('text', 'No text')[:30] for msg in messages[:3]]}"
                        )
                else:
                    self.log_result(
                        "DM Get Messages", 
                        True, 
                        "Successfully retrieved DM messages (empty thread)",
                        "Empty message thread is acceptable"
                    )
            else:
                self.log_result(
                    "DM Get Messages", 
                    False, 
                    f"DM get messages failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Get Messages", False, f"Exception occurred: {str(e)}")
    
    def test_error_handling_invalid_requests(self):
        """Test 7: Error handling for invalid requests"""
        try:
            # Test invalid trust circle creation
            invalid_payload = {"invalid": "data"}
            response = self.session.post(f"{BACKEND_URL}/trust-circles", json=invalid_payload)
            
            if response.status_code in [400, 422, 404]:
                self.log_result(
                    "Error Handling - Invalid Trust Circle", 
                    True, 
                    f"Correctly rejected invalid trust circle data (status {response.status_code})",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Error Handling - Invalid Trust Circle", 
                    False, 
                    f"Unexpected status {response.status_code} for invalid data",
                    f"Response: {response.text}"
                )
            
            # Test invalid DM thread creation
            invalid_dm_payload = {"invalid": "data"}
            dm_response = self.session.post(f"{BACKEND_URL}/dm/create-thread", json=invalid_dm_payload)
            
            if dm_response.status_code in [400, 422, 404]:
                self.log_result(
                    "Error Handling - Invalid DM Thread", 
                    True, 
                    f"Correctly rejected invalid DM thread data (status {dm_response.status_code})",
                    f"Response: {dm_response.text}"
                )
            else:
                self.log_result(
                    "Error Handling - Invalid DM Thread", 
                    False, 
                    f"Unexpected status {dm_response.status_code} for invalid DM data",
                    f"Response: {dm_response.text}"
                )
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all messenger backend tests"""
        print("=" * 80)
        print("MESSENGER BACKEND FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo User ID: {DEMO_USER_ID}")
        print("=" * 80)
        
        # Run all tests in sequence
        self.test_trust_circles_get()
        self.test_trust_circles_create()
        self.test_dm_threads_get()
        self.test_dm_thread_create()
        self.test_dm_send_message()
        self.test_dm_get_messages()
        self.test_error_handling_invalid_requests()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']} - {result['message']}")
        
        print("\n" + "=" * 80)
        
        # Return summary for external use
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed/total)*100,
            'results': self.test_results
        }

def main():
    """Main function to run messenger backend tests"""
    tester = MessengerBackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary['failed'] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()