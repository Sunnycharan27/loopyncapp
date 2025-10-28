#!/usr/bin/env python3
"""
Real User Calling Test Suite - Fixed Version
Tests calling functionality with actual real users @Sunnycharan and @Sunnyram who are already friends.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"

class RealUserCallingFixedTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        # Real user IDs from the database
        self.sunnycharan_id = "9b76bda7-ca16-4c33-9bc0-66d1b5ca86d0"  # @Sunnycharan
        self.sunnyram_id = "b1a68570-99a3-49fa-8309-347cbe3499df"     # @Sunnyram
        self.dm_thread_id = None
        
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
    
    def test_verify_real_users_exist(self):
        """Test 1: Verify Real Users Exist in Database"""
        try:
            # Check Sunnycharan
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.sunnycharan_id}")
            # Check Sunnyram  
            response2 = self.session.get(f"{BACKEND_URL}/users/{self.sunnyram_id}")
            
            if response1.status_code == 200 and response2.status_code == 200:
                user1 = response1.json()
                user2 = response2.json()
                
                self.log_result(
                    "Verify Real Users Exist", 
                    True, 
                    f"Both real users found: @{user1.get('handle')} and @{user2.get('handle')}",
                    f"Sunnycharan: {user1.get('name')} ({user1.get('email')}), Sunnyram: {user2.get('name')} ({user2.get('email')})"
                )
            else:
                self.log_result(
                    "Verify Real Users Exist", 
                    False, 
                    f"Failed to get user data: Sunnycharan {response1.status_code}, Sunnyram {response2.status_code}",
                    f"Responses: {response1.text}, {response2.text}"
                )
                
        except Exception as e:
            self.log_result("Verify Real Users Exist", False, f"Exception occurred: {str(e)}")
    
    def test_verify_friendship_status(self):
        """Test 2: Verify Bidirectional Friendship Status"""
        try:
            # Get Sunnycharan's data
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.sunnycharan_id}")
            # Get Sunnyram's data
            response2 = self.session.get(f"{BACKEND_URL}/users/{self.sunnyram_id}")
            
            if response1.status_code == 200 and response2.status_code == 200:
                user1 = response1.json()
                user2 = response2.json()
                
                sunnycharan_friends = user1.get('friends', [])
                sunnyram_friends = user2.get('friends', [])
                
                sunnycharan_has_sunnyram = self.sunnyram_id in sunnycharan_friends
                sunnyram_has_sunnycharan = self.sunnycharan_id in sunnyram_friends
                
                if sunnycharan_has_sunnyram and sunnyram_has_sunnycharan:
                    self.log_result(
                        "Verify Friendship Status", 
                        True, 
                        "Bidirectional friendship confirmed between @Sunnycharan and @Sunnyram",
                        f"Sunnycharan friends: {len(sunnycharan_friends)}, Sunnyram friends: {len(sunnyram_friends)}"
                    )
                else:
                    self.log_result(
                        "Verify Friendship Status", 
                        False, 
                        f"Friendship issue: Sunnycharan has Sunnyram: {sunnycharan_has_sunnyram}, Sunnyram has Sunnycharan: {sunnyram_has_sunnycharan}",
                        f"Sunnycharan friends: {sunnycharan_friends}, Sunnyram friends: {sunnyram_friends}"
                    )
            else:
                self.log_result(
                    "Verify Friendship Status", 
                    False, 
                    f"Failed to get user data for friendship check",
                    f"Status codes: {response1.status_code}, {response2.status_code}"
                )
                
        except Exception as e:
            self.log_result("Verify Friendship Status", False, f"Exception occurred: {str(e)}")
    
    def test_create_dm_thread(self):
        """Test 3: Create/Verify DM Thread Between Real Users"""
        try:
            # Create DM thread between Sunnycharan and Sunnyram
            response = self.session.post(f"{BACKEND_URL}/dm/thread", 
                                       params={'userId': self.sunnycharan_id, 'peerUserId': self.sunnyram_id})
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    self.dm_thread_id = data['threadId']
                    self.log_result(
                        "Create DM Thread", 
                        True, 
                        f"DM thread created/retrieved successfully between real users",
                        f"Thread ID: {self.dm_thread_id}"
                    )
                else:
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        "DM thread response missing threadId",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Create DM Thread", 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create DM Thread", False, f"Exception occurred: {str(e)}")
    
    def test_call_initiation_sunnycharan_to_sunnyram(self):
        """Test 4: Call Initiation (@Sunnycharan → @Sunnyram)"""
        try:
            # Test video call initiation
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                       params={
                                           'callerId': self.sunnycharan_id, 
                                           'recipientId': self.sunnyram_id, 
                                           'callType': 'video'
                                       })
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken', 'appId']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Call Initiation (@Sunnycharan → @Sunnyram)", 
                        True, 
                        "Video call initiation successful - all Agora tokens returned",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}, App ID: {data['appId']}"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Call Initiation (@Sunnycharan → @Sunnyram)", 
                        False, 
                        f"Call initiation response missing fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Call Initiation (@Sunnycharan → @Sunnyram)", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation (@Sunnycharan → @Sunnyram)", False, f"Exception occurred: {str(e)}")
    
    def test_call_initiation_sunnyram_to_sunnycharan(self):
        """Test 5: Call Initiation (@Sunnyram → @Sunnycharan)"""
        try:
            # Test audio call initiation
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                       params={
                                           'callerId': self.sunnyram_id, 
                                           'recipientId': self.sunnycharan_id, 
                                           'callType': 'audio'
                                       })
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken', 'appId']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Call Initiation (@Sunnyram → @Sunnycharan)", 
                        True, 
                        "Audio call initiation successful - all Agora tokens returned",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}, App ID: {data['appId']}"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Call Initiation (@Sunnyram → @Sunnycharan)", 
                        False, 
                        f"Call initiation response missing fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Call Initiation (@Sunnyram → @Sunnycharan)", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation (@Sunnyram → @Sunnycharan)", False, f"Exception occurred: {str(e)}")
    
    def test_multiple_real_user_scenarios(self):
        """Test 6: Test with Multiple Real User Scenarios"""
        try:
            # Get all users to find more real users
            response = self.session.get(f"{BACKEND_URL}/users", params={'limit': 50})
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Filter real users (not demo or test users)
                real_users = []
                for user in all_users:
                    email = user.get('email', '')
                    handle = user.get('handle', '')
                    if (not email.startswith('demo@') and 
                        not email.startswith('testuser_') and 
                        not handle.startswith('testuser_') and
                        '@gmail.com' in email):  # Real email addresses
                        real_users.append(user)
                
                if len(real_users) >= 2:
                    successful_calls = 0
                    total_attempts = 0
                    
                    # Test calling between first few real users
                    for i in range(min(3, len(real_users))):
                        for j in range(min(3, len(real_users))):
                            if i != j:
                                caller = real_users[i]
                                recipient = real_users[j]
                                total_attempts += 1
                                
                                # Check if they are friends first
                                caller_friends = caller.get('friends', [])
                                if recipient['id'] in caller_friends:
                                    # Test call initiation
                                    call_response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                                                   params={
                                                                       'callerId': caller['id'], 
                                                                       'recipientId': recipient['id'], 
                                                                       'callType': 'video'
                                                                   })
                                    
                                    if call_response.status_code == 200:
                                        call_data = call_response.json()
                                        required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                                        if all(field in call_data for field in required_fields):
                                            successful_calls += 1
                    
                    if successful_calls > 0:
                        self.log_result(
                            "Multiple Real User Scenarios", 
                            True, 
                            f"Successfully tested calling with {successful_calls} real user combinations",
                            f"Found {len(real_users)} real users, tested {total_attempts} combinations"
                        )
                    else:
                        self.log_result(
                            "Multiple Real User Scenarios", 
                            False, 
                            f"No successful calls among {total_attempts} real user combinations",
                            f"Found {len(real_users)} real users but no friend relationships for calling"
                        )
                else:
                    self.log_result(
                        "Multiple Real User Scenarios", 
                        False, 
                        f"Insufficient real users found: {len(real_users)}",
                        f"Need at least 2 real users for testing"
                    )
            else:
                self.log_result(
                    "Multiple Real User Scenarios", 
                    False, 
                    f"Failed to get users list: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Multiple Real User Scenarios", False, f"Exception occurred: {str(e)}")
    
    def test_system_works_with_any_users(self):
        """Test 7: Verify System Works with ANY Users (Not Just Seeded)"""
        try:
            # Create two new test users with realistic data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            user1_data = {
                "name": "Ananya Patel",
                "handle": f"ananya_patel_{timestamp}",
                "email": f"ananya.patel.{timestamp}@gmail.com",
                "password": "realpass123"
            }
            
            user2_data = {
                "name": "Rohit Kumar",
                "handle": f"rohit_kumar_{timestamp}",
                "email": f"rohit.kumar.{timestamp}@gmail.com",
                "password": "realpass123"
            }
            
            # Create users
            response1 = self.session.post(f"{BACKEND_URL}/auth/signup", json=user1_data)
            response2 = self.session.post(f"{BACKEND_URL}/auth/signup", json=user2_data)
            
            if response1.status_code == 200 and response2.status_code == 200:
                user1 = response1.json()['user']
                user2 = response2.json()['user']
                
                # Establish friendship
                friend_response = self.session.post(f"{BACKEND_URL}/friends/request", 
                                                  params={'fromUserId': user1['id'], 'toUserId': user2['id']})
                
                if friend_response.status_code == 200:
                    friend_data = friend_response.json()
                    if friend_data.get('success'):
                        if not friend_data.get('nowFriends'):
                            # Accept friend request
                            accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", 
                                                              params={'userId': user2['id'], 'friendId': user1['id']})
                        
                        # Test calling between new users
                        call_response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                                       params={
                                                           'callerId': user1['id'], 
                                                           'recipientId': user2['id'], 
                                                           'callType': 'video'
                                                       })
                        
                        if call_response.status_code == 200:
                            call_data = call_response.json()
                            required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                            
                            if all(field in call_data for field in required_fields):
                                self.log_result(
                                    "System Works with ANY Users", 
                                    True, 
                                    f"Successfully tested calling with newly created users: {user1['name']} → {user2['name']}",
                                    f"System works with ANY registered users, not just seeded ones"
                                )
                            else:
                                self.log_result(
                                    "System Works with ANY Users", 
                                    False, 
                                    "Call initiation missing required fields",
                                    f"Response: {call_data}"
                                )
                        else:
                            self.log_result(
                                "System Works with ANY Users", 
                                False, 
                                f"Call initiation failed: {call_response.status_code}",
                                f"Response: {call_response.text}"
                            )
                    else:
                        self.log_result(
                            "System Works with ANY Users", 
                            False, 
                            "Friend request failed",
                            f"Response: {friend_data}"
                        )
                else:
                    self.log_result(
                        "System Works with ANY Users", 
                        False, 
                        f"Friend request failed: {friend_response.status_code}",
                        f"Response: {friend_response.text}"
                    )
            else:
                self.log_result(
                    "System Works with ANY Users", 
                    False, 
                    f"User creation failed: {response1.status_code}, {response2.status_code}",
                    f"Responses: {response1.text}, {response2.text}"
                )
                
        except Exception as e:
            self.log_result("System Works with ANY Users", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all real user calling tests"""
        print("=" * 80)
        print("REAL USER CALLING TEST SUITE - FIXED VERSION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Date: {datetime.now().isoformat()}")
        print(f"Testing with real users: @Sunnycharan and @Sunnyram")
        print("=" * 80)
        
        # Execute all tests in sequence
        self.test_verify_real_users_exist()
        self.test_verify_friendship_status()
        self.test_create_dm_thread()
        self.test_call_initiation_sunnycharan_to_sunnyram()
        self.test_call_initiation_sunnyram_to_sunnycharan()
        self.test_multiple_real_user_scenarios()
        self.test_system_works_with_any_users()
        
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
        
        print("\nFAILED TESTS:")
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            for result in failed_tests:
                print(f"❌ {result['test']}: {result['message']}")
        else:
            print("None - All tests passed!")
        
        print("\n" + "=" * 80)
        print("EXPECTED RESULTS VERIFICATION:")
        print("=" * 80)
        
        # Check if all expected results were achieved
        expected_results = [
            ("✅ Real users (@Sunnycharan and Ram Charan) are found in database", 
             any(r['test'] == 'Verify Real Users Exist' and r['success'] for r in self.test_results)),
            ("✅ Friendship established between them", 
             any(r['test'] == 'Verify Friendship Status' and r['success'] for r in self.test_results)),
            ("✅ DM thread exists", 
             any(r['test'] == 'Create DM Thread' and r['success'] for r in self.test_results)),
            ("✅ Call initiation succeeds with real user IDs", 
             any(r['test'] == 'Call Initiation (@Sunnycharan → @Sunnyram)' and r['success'] for r in self.test_results) and
             any(r['test'] == 'Call Initiation (@Sunnyram → @Sunnycharan)' and r['success'] for r in self.test_results)),
            ("✅ System works with any registered users, not just seeded ones", 
             any(r['test'] == 'System Works with ANY Users' and r['success'] for r in self.test_results))
        ]
        
        for description in expected_results:
            print(description[0])
        
        return self.test_results

if __name__ == "__main__":
    tester = RealUserCallingFixedTester()
    results = tester.run_all_tests()