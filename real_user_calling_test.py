#!/usr/bin/env python3
"""
Real User Calling Test Suite
Tests calling functionality with real users (@Sunnycharan and Ram Charan) as specified in the review request.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

class RealUserCallingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.sunnycharan_id = None
        self.ram_charan_id = None
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
    
    def test_find_sunnycharan_user(self):
        """Test 1: Find Real User - @Sunnycharan"""
        try:
            # Search for user with handle "Sunnycharan" or name containing "Sunny"
            response = self.session.get(f"{BACKEND_URL}/users/search", params={'q': 'Sunnycharan'})
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 0:
                    # Look for exact match or close match
                    sunnycharan_user = None
                    for user in users:
                        if (user.get('handle', '').lower() == 'sunnycharan' or 
                            'sunny' in user.get('name', '').lower() or
                            'sunnycharan' in user.get('handle', '').lower()):
                            sunnycharan_user = user
                            break
                    
                    if sunnycharan_user:
                        self.sunnycharan_id = sunnycharan_user['id']
                        self.log_result(
                            "Find Sunnycharan User", 
                            True, 
                            f"Found @Sunnycharan: {sunnycharan_user.get('name', 'Unknown')} (@{sunnycharan_user.get('handle', 'Unknown')})",
                            f"User ID: {self.sunnycharan_id}"
                        )
                    else:
                        self.log_result(
                            "Find Sunnycharan User", 
                            False, 
                            "No user found matching 'Sunnycharan' criteria",
                            f"Search returned {len(users)} users: {[u.get('handle') for u in users]}"
                        )
                else:
                    self.log_result(
                        "Find Sunnycharan User", 
                        False, 
                        "Search for 'Sunnycharan' returned no results",
                        f"Response: {users}"
                    )
            else:
                self.log_result(
                    "Find Sunnycharan User", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Find Sunnycharan User", False, f"Exception occurred: {str(e)}")
    
    def test_find_ram_charan_user(self):
        """Test 2: Find Real User - Ram Charan"""
        try:
            # Search for "Ram Charan" or handle "Sunnyram"
            response = self.session.get(f"{BACKEND_URL}/users/search", params={'q': 'ram'})
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 0:
                    # Look for Ram Charan
                    ram_charan_user = None
                    for user in users:
                        name = user.get('name', '').lower()
                        handle = user.get('handle', '').lower()
                        if ('ram' in name and 'charan' in name) or 'sunnyram' in handle:
                            ram_charan_user = user
                            break
                    
                    if ram_charan_user:
                        self.ram_charan_id = ram_charan_user['id']
                        self.log_result(
                            "Find Ram Charan User", 
                            True, 
                            f"Found Ram Charan: {ram_charan_user.get('name', 'Unknown')} (@{ram_charan_user.get('handle', 'Unknown')})",
                            f"User ID: {self.ram_charan_id}"
                        )
                    else:
                        self.log_result(
                            "Find Ram Charan User", 
                            False, 
                            "No user found matching 'Ram Charan' criteria",
                            f"Search returned {len(users)} users: {[u.get('name') for u in users]}"
                        )
                else:
                    self.log_result(
                        "Find Ram Charan User", 
                        False, 
                        "Search for 'ram' returned no results",
                        f"Response: {users}"
                    )
            else:
                self.log_result(
                    "Find Ram Charan User", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Find Ram Charan User", False, f"Exception occurred: {str(e)}")
    
    def test_check_friendship_status(self):
        """Test 3: Check Current Friendship Status"""
        if not self.sunnycharan_id or not self.ram_charan_id:
            self.log_result("Check Friendship Status", False, "Skipped - missing user IDs")
            return
            
        try:
            # Check if Sunnycharan has Ram Charan in friends array
            response = self.session.get(f"{BACKEND_URL}/users/{self.sunnycharan_id}")
            
            if response.status_code == 200:
                sunnycharan_data = response.json()
                sunnycharan_friends = sunnycharan_data.get('friends', [])
                
                # Check if Ram Charan has Sunnycharan in friends array
                response2 = self.session.get(f"{BACKEND_URL}/users/{self.ram_charan_id}")
                
                if response2.status_code == 200:
                    ram_data = response2.json()
                    ram_friends = ram_data.get('friends', [])
                    
                    sunnycharan_has_ram = self.ram_charan_id in sunnycharan_friends
                    ram_has_sunnycharan = self.sunnycharan_id in ram_friends
                    
                    if sunnycharan_has_ram and ram_has_sunnycharan:
                        self.log_result(
                            "Check Friendship Status", 
                            True, 
                            "Users are already friends (bidirectional friendship exists)",
                            f"Sunnycharan friends: {len(sunnycharan_friends)}, Ram friends: {len(ram_friends)}"
                        )
                    elif sunnycharan_has_ram or ram_has_sunnycharan:
                        self.log_result(
                            "Check Friendship Status", 
                            False, 
                            "Friendship is unidirectional - needs fixing",
                            f"Sunnycharan has Ram: {sunnycharan_has_ram}, Ram has Sunnycharan: {ram_has_sunnycharan}"
                        )
                    else:
                        self.log_result(
                            "Check Friendship Status", 
                            False, 
                            "Users are not friends - friendship needs to be established",
                            f"Sunnycharan friends: {len(sunnycharan_friends)}, Ram friends: {len(ram_friends)}"
                        )
                else:
                    self.log_result(
                        "Check Friendship Status", 
                        False, 
                        f"Failed to get Ram Charan's data: {response2.status_code}",
                        f"Response: {response2.text}"
                    )
            else:
                self.log_result(
                    "Check Friendship Status", 
                    False, 
                    f"Failed to get Sunnycharan's data: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Check Friendship Status", False, f"Exception occurred: {str(e)}")
    
    def test_establish_friendship(self):
        """Test 4: Establish Friendship if Missing"""
        if not self.sunnycharan_id or not self.ram_charan_id:
            self.log_result("Establish Friendship", False, "Skipped - missing user IDs")
            return
            
        try:
            # Send friend request from Sunnycharan to Ram Charan
            response = self.session.post(f"{BACKEND_URL}/friends/request", 
                                       params={'fromUserId': self.sunnycharan_id, 'toUserId': self.ram_charan_id})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if data.get('nowFriends'):
                        self.log_result(
                            "Establish Friendship", 
                            True, 
                            "Friendship established automatically (mutual request)",
                            f"Response: {data}"
                        )
                    else:
                        # Accept the friend request
                        accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", 
                                                          params={'userId': self.ram_charan_id, 'friendId': self.sunnycharan_id})
                        
                        if accept_response.status_code == 200:
                            accept_data = accept_response.json()
                            if accept_data.get('success'):
                                self.log_result(
                                    "Establish Friendship", 
                                    True, 
                                    "Friendship established successfully",
                                    f"Friend request sent and accepted"
                                )
                            else:
                                self.log_result(
                                    "Establish Friendship", 
                                    False, 
                                    "Friend request sent but acceptance failed",
                                    f"Accept response: {accept_data}"
                                )
                        else:
                            self.log_result(
                                "Establish Friendship", 
                                False, 
                                f"Friend request sent but acceptance failed: {accept_response.status_code}",
                                f"Accept response: {accept_response.text}"
                            )
                else:
                    self.log_result(
                        "Establish Friendship", 
                        False, 
                        "Friend request failed",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Establish Friendship", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Establish Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_create_dm_thread(self):
        """Test 5: Create/Verify DM Thread"""
        if not self.sunnycharan_id or not self.ram_charan_id:
            self.log_result("Create DM Thread", False, "Skipped - missing user IDs")
            return
            
        try:
            # Create DM thread between Sunnycharan and Ram Charan
            response = self.session.post(f"{BACKEND_URL}/dm/thread", 
                                       params={'userId': self.sunnycharan_id, 'peerUserId': self.ram_charan_id})
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    self.dm_thread_id = data['threadId']
                    self.log_result(
                        "Create DM Thread", 
                        True, 
                        f"DM thread created/retrieved successfully",
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
    
    def test_call_initiation_sunnycharan_to_ram(self):
        """Test 6: Test Call Initiation Between Real Users (Sunnycharan → Ram Charan)"""
        if not self.sunnycharan_id or not self.ram_charan_id:
            self.log_result("Call Initiation (Sunnycharan → Ram)", False, "Skipped - missing user IDs")
            return
            
        try:
            # Test video call initiation
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                       params={
                                           'callerId': self.sunnycharan_id, 
                                           'recipientId': self.ram_charan_id, 
                                           'callType': 'video'
                                       })
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Call Initiation (Sunnycharan → Ram)", 
                        True, 
                        "Video call initiation successful - all Agora tokens returned",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Call Initiation (Sunnycharan → Ram)", 
                        False, 
                        f"Call initiation response missing fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Call Initiation (Sunnycharan → Ram)", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation (Sunnycharan → Ram)", False, f"Exception occurred: {str(e)}")
    
    def test_call_initiation_ram_to_sunnycharan(self):
        """Test 7: Test Call Initiation Between Real Users (Ram Charan → Sunnycharan)"""
        if not self.sunnycharan_id or not self.ram_charan_id:
            self.log_result("Call Initiation (Ram → Sunnycharan)", False, "Skipped - missing user IDs")
            return
            
        try:
            # Test audio call initiation
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                       params={
                                           'callerId': self.ram_charan_id, 
                                           'recipientId': self.sunnycharan_id, 
                                           'callType': 'audio'
                                       })
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Call Initiation (Ram → Sunnycharan)", 
                        True, 
                        "Audio call initiation successful - all Agora tokens returned",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Call Initiation (Ram → Sunnycharan)", 
                        False, 
                        f"Call initiation response missing fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Call Initiation (Ram → Sunnycharan)", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Call Initiation (Ram → Sunnycharan)", False, f"Exception occurred: {str(e)}")
    
    def test_create_additional_test_users(self):
        """Test 8: Create 2-3 New Test Accounts with Realistic Names"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_users = [
                {
                    "name": "Arjun Reddy",
                    "handle": f"arjun_reddy_{timestamp}",
                    "email": f"arjun.reddy.{timestamp}@example.com",
                    "password": "testpass123"
                },
                {
                    "name": "Priya Sharma",
                    "handle": f"priya_sharma_{timestamp}",
                    "email": f"priya.sharma.{timestamp}@example.com",
                    "password": "testpass123"
                },
                {
                    "name": "Vikram Singh",
                    "handle": f"vikram_singh_{timestamp}",
                    "email": f"vikram.singh.{timestamp}@example.com",
                    "password": "testpass123"
                }
            ]
            
            created_users = []
            
            for user_data in test_users:
                response = self.session.post(f"{BACKEND_URL}/auth/signup", json=user_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'user' in data and 'token' in data:
                        created_users.append({
                            'id': data['user']['id'],
                            'name': data['user']['name'],
                            'handle': data['user']['handle'],
                            'email': data['user']['email']
                        })
                
            if len(created_users) >= 2:
                self.log_result(
                    "Create Additional Test Users", 
                    True, 
                    f"Successfully created {len(created_users)} test users with realistic names",
                    f"Users: {[u['name'] for u in created_users]}"
                )
                
                # Store user IDs for friendship testing
                self.test_user_ids = [u['id'] for u in created_users]
                
            else:
                self.log_result(
                    "Create Additional Test Users", 
                    False, 
                    f"Only created {len(created_users)} users, expected at least 2",
                    f"Created users: {created_users}"
                )
                
        except Exception as e:
            self.log_result("Create Additional Test Users", False, f"Exception occurred: {str(e)}")
    
    def test_establish_friendships_between_test_users(self):
        """Test 9: Establish Friendships Between Test Users"""
        if not hasattr(self, 'test_user_ids') or len(self.test_user_ids) < 2:
            self.log_result("Establish Test User Friendships", False, "Skipped - insufficient test users")
            return
            
        try:
            successful_friendships = 0
            
            # Create friendships between all combinations of test users
            for i in range(len(self.test_user_ids)):
                for j in range(i + 1, len(self.test_user_ids)):
                    user1_id = self.test_user_ids[i]
                    user2_id = self.test_user_ids[j]
                    
                    # Send friend request
                    response = self.session.post(f"{BACKEND_URL}/friends/request", 
                                               params={'fromUserId': user1_id, 'toUserId': user2_id})
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            if not data.get('nowFriends'):
                                # Accept the friend request
                                accept_response = self.session.post(f"{BACKEND_URL}/friends/accept", 
                                                                  params={'userId': user2_id, 'friendId': user1_id})
                                
                                if accept_response.status_code == 200:
                                    accept_data = accept_response.json()
                                    if accept_data.get('success'):
                                        successful_friendships += 1
                            else:
                                successful_friendships += 1
            
            expected_friendships = len(self.test_user_ids) * (len(self.test_user_ids) - 1) // 2
            
            if successful_friendships >= expected_friendships:
                self.log_result(
                    "Establish Test User Friendships", 
                    True, 
                    f"Successfully established {successful_friendships} friendships between test users",
                    f"All {len(self.test_user_ids)} test users are now friends with each other"
                )
            else:
                self.log_result(
                    "Establish Test User Friendships", 
                    False, 
                    f"Only established {successful_friendships}/{expected_friendships} friendships",
                    f"Some friendship establishments failed"
                )
                
        except Exception as e:
            self.log_result("Establish Test User Friendships", False, f"Exception occurred: {str(e)}")
    
    def test_calling_between_all_test_users(self):
        """Test 10: Test Calling Between All Test User Combinations"""
        if not hasattr(self, 'test_user_ids') or len(self.test_user_ids) < 2:
            self.log_result("Test User Calling Combinations", False, "Skipped - insufficient test users")
            return
            
        try:
            successful_calls = 0
            total_combinations = 0
            
            # Test calling between all combinations
            for i in range(len(self.test_user_ids)):
                for j in range(len(self.test_user_ids)):
                    if i != j:  # Don't call yourself
                        caller_id = self.test_user_ids[i]
                        recipient_id = self.test_user_ids[j]
                        total_combinations += 1
                        
                        # Test call initiation
                        response = self.session.post(f"{BACKEND_URL}/calls/initiate", 
                                                   params={
                                                       'callerId': caller_id, 
                                                       'recipientId': recipient_id, 
                                                       'callType': 'video'
                                                   })
                        
                        if response.status_code == 200:
                            data = response.json()
                            required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                            
                            if all(field in data for field in required_fields):
                                successful_calls += 1
            
            if successful_calls == total_combinations:
                self.log_result(
                    "Test User Calling Combinations", 
                    True, 
                    f"All {successful_calls}/{total_combinations} call combinations successful",
                    f"System works with ANY registered users, not just seeded ones"
                )
            else:
                self.log_result(
                    "Test User Calling Combinations", 
                    False, 
                    f"Only {successful_calls}/{total_combinations} call combinations successful",
                    f"Some call initiations failed between test users"
                )
                
        except Exception as e:
            self.log_result("Test User Calling Combinations", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all real user calling tests"""
        print("=" * 80)
        print("REAL USER CALLING TEST SUITE - COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Date: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Execute all tests in sequence
        self.test_find_sunnycharan_user()
        self.test_find_ram_charan_user()
        self.test_check_friendship_status()
        self.test_establish_friendship()
        self.test_create_dm_thread()
        self.test_call_initiation_sunnycharan_to_ram()
        self.test_call_initiation_ram_to_sunnycharan()
        self.test_create_additional_test_users()
        self.test_establish_friendships_between_test_users()
        self.test_calling_between_all_test_users()
        
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
            ("Real users (@Sunnycharan and Ram Charan) are found in database", 
             any(r['test'] == 'Find Sunnycharan User' and r['success'] for r in self.test_results) and
             any(r['test'] == 'Find Ram Charan User' and r['success'] for r in self.test_results)),
            ("Friendship established between them", 
             any(r['test'] == 'Establish Friendship' and r['success'] for r in self.test_results)),
            ("DM thread exists", 
             any(r['test'] == 'Create DM Thread' and r['success'] for r in self.test_results)),
            ("Call initiation succeeds with real user IDs", 
             any(r['test'] == 'Call Initiation (Sunnycharan → Ram)' and r['success'] for r in self.test_results) and
             any(r['test'] == 'Call Initiation (Ram → Sunnycharan)' and r['success'] for r in self.test_results)),
            ("System works with any registered users, not just seeded ones", 
             any(r['test'] == 'Test User Calling Combinations' and r['success'] for r in self.test_results))
        ]
        
        for description, achieved in expected_results:
            status = "✅" if achieved else "❌"
            print(f"{status} {description}")
        
        return self.test_results

if __name__ == "__main__":
    tester = RealUserCallingTester()
    results = tester.run_all_tests()