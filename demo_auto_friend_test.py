#!/usr/bin/env python3
"""
Demo User Auto-Friending Feature Test
Tests the auto-friending logic for demo@loopync.com user when they login.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class DemoAutoFriendTester:
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
    
    def test_1_seed_database(self):
        """Test 1: Seed the Database First"""
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'users' in data:
                    users_created = data.get('users', 0)
                    self.log_result(
                        "1. Seed Database", 
                        True, 
                        f"Successfully seeded database with {users_created} users",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "1. Seed Database", 
                        False, 
                        "Seed response missing expected fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "1. Seed Database", 
                    False, 
                    f"Seed operation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("1. Seed Database", False, f"Exception occurred: {str(e)}")
    
    def test_2_verify_seeded_users(self):
        """Test 2: Verify Seeded Users (u1, u2, u3) are Created"""
        try:
            seeded_user_ids = ['u1', 'u2', 'u3']
            verified_users = []
            
            for user_id in seeded_user_ids:
                response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    if 'id' in user_data and 'name' in user_data:
                        verified_users.append({
                            'id': user_data['id'],
                            'name': user_data['name'],
                            'handle': user_data.get('handle', 'Unknown')
                        })
                    else:
                        self.log_result(
                            "2. Verify Seeded Users", 
                            False, 
                            f"User {user_id} data incomplete",
                            f"User data: {user_data}"
                        )
                        return
                else:
                    self.log_result(
                        "2. Verify Seeded Users", 
                        False, 
                        f"Failed to get user {user_id} - status {response.status_code}",
                        f"Response: {response.text}"
                    )
                    return
            
            if len(verified_users) == len(seeded_user_ids):
                self.log_result(
                    "2. Verify Seeded Users", 
                    True, 
                    f"All {len(verified_users)} seeded users verified successfully",
                    f"Users: {[u['name'] + ' (' + u['id'] + ')' for u in verified_users]}"
                )
            else:
                self.log_result(
                    "2. Verify Seeded Users", 
                    False, 
                    f"Only {len(verified_users)} out of {len(seeded_user_ids)} users verified",
                    f"Verified: {verified_users}"
                )
                
        except Exception as e:
            self.log_result("2. Verify Seeded Users", False, f"Exception occurred: {str(e)}")
    
    def test_3_demo_user_login(self):
        """Test 3: Login as Demo User and Capture User ID"""
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
                    
                    if self.demo_user_id and user.get('email') == DEMO_EMAIL:
                        self.log_result(
                            "3. Demo User Login", 
                            True, 
                            f"Successfully logged in as {user.get('name', 'Demo User')}",
                            f"User ID: {self.demo_user_id}, Email: {user.get('email')}"
                        )
                    else:
                        self.log_result(
                            "3. Demo User Login", 
                            False, 
                            "Login successful but user data incomplete or incorrect",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "3. Demo User Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "3. Demo User Login", 
                    False, 
                    f"Demo user login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("3. Demo User Login", False, f"Exception occurred: {str(e)}")
    
    def test_4_check_demo_user_friends(self):
        """Test 4: Check Demo User's Friends Array"""
        if not self.demo_user_id:
            self.log_result("4. Check Demo User Friends", False, "Skipped - no demo user ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                friends = user_data.get('friends', [])
                
                if isinstance(friends, list):
                    if len(friends) > 0:
                        # Check if seeded users are in friends list
                        seeded_friends = [f for f in friends if f in ['u1', 'u2', 'u3']]
                        
                        if len(seeded_friends) > 0:
                            self.log_result(
                                "4. Check Demo User Friends", 
                                True, 
                                f"Demo user has {len(friends)} friends, including {len(seeded_friends)} seeded users",
                                f"All friends: {friends}, Seeded friends: {seeded_friends}"
                            )
                        else:
                            self.log_result(
                                "4. Check Demo User Friends", 
                                False, 
                                f"Demo user has {len(friends)} friends but none are seeded users (u1, u2, u3)",
                                f"Friends list: {friends}"
                            )
                    else:
                        self.log_result(
                            "4. Check Demo User Friends", 
                            False, 
                            "Demo user has no friends - auto-friending logic did not work",
                            "Friends array is empty"
                        )
                else:
                    self.log_result(
                        "4. Check Demo User Friends", 
                        False, 
                        "Friends field is not a list or missing",
                        f"Friends field: {friends}"
                    )
            else:
                self.log_result(
                    "4. Check Demo User Friends", 
                    False, 
                    f"Failed to get demo user data - status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("4. Check Demo User Friends", False, f"Exception occurred: {str(e)}")
    
    def test_5_verify_bidirectional_friendship(self):
        """Test 5: Verify Bidirectional Friendship"""
        if not self.demo_user_id:
            self.log_result("5. Verify Bidirectional Friendship", False, "Skipped - no demo user ID available")
            return
            
        try:
            seeded_user_ids = ['u1', 'u2', 'u3']
            bidirectional_friends = []
            
            for user_id in seeded_user_ids:
                response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    friends = user_data.get('friends', [])
                    
                    if self.demo_user_id in friends:
                        bidirectional_friends.append({
                            'id': user_id,
                            'name': user_data.get('name', 'Unknown'),
                            'has_demo_as_friend': True
                        })
                    else:
                        bidirectional_friends.append({
                            'id': user_id,
                            'name': user_data.get('name', 'Unknown'),
                            'has_demo_as_friend': False
                        })
                else:
                    self.log_result(
                        "5. Verify Bidirectional Friendship", 
                        False, 
                        f"Failed to get user {user_id} data - status {response.status_code}",
                        f"Response: {response.text}"
                    )
                    return
            
            # Count how many seeded users have demo user as friend
            mutual_friends = [f for f in bidirectional_friends if f['has_demo_as_friend']]
            
            if len(mutual_friends) > 0:
                self.log_result(
                    "5. Verify Bidirectional Friendship", 
                    True, 
                    f"Bidirectional friendship established with {len(mutual_friends)} seeded users",
                    f"Mutual friends: {[f['name'] + ' (' + f['id'] + ')' for f in mutual_friends]}"
                )
            else:
                self.log_result(
                    "5. Verify Bidirectional Friendship", 
                    False, 
                    "No bidirectional friendships found - demo user not in seeded users' friends lists",
                    f"Checked users: {[f'{f[\"name\"]} ({f[\"id\"]})' for f in bidirectional_friends]}"
                )
                
        except Exception as e:
            self.log_result("5. Verify Bidirectional Friendship", False, f"Exception occurred: {str(e)}")
    
    def test_6_friend_status_api(self):
        """Test 6: Test Friend Status API"""
        if not self.demo_user_id:
            self.log_result("6. Test Friend Status API", False, "Skipped - no demo user ID available")
            return
            
        try:
            seeded_user_ids = ['u1', 'u2', 'u3']
            friend_statuses = []
            
            for user_id in seeded_user_ids:
                response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/{user_id}")
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status', 'unknown')
                    friend_statuses.append({
                        'user_id': user_id,
                        'status': status,
                        'is_friends': status == 'friends'
                    })
                else:
                    friend_statuses.append({
                        'user_id': user_id,
                        'status': f'error_{response.status_code}',
                        'is_friends': False
                    })
            
            # Count how many return "friends" status
            friends_count = len([s for s in friend_statuses if s['is_friends']])
            
            if friends_count > 0:
                self.log_result(
                    "6. Test Friend Status API", 
                    True, 
                    f"Friend status API working - {friends_count} users show 'friends' status",
                    f"Statuses: {[(s['user_id'], s['status']) for s in friend_statuses]}"
                )
            else:
                self.log_result(
                    "6. Test Friend Status API", 
                    False, 
                    "Friend status API not returning 'friends' for any seeded users",
                    f"Statuses: {[(s['user_id'], s['status']) for s in friend_statuses]}"
                )
                
        except Exception as e:
            self.log_result("6. Test Friend Status API", False, f"Exception occurred: {str(e)}")
    
    def test_7_dm_thread_creation(self):
        """Test 7: Test DM Thread Creation"""
        if not self.demo_user_id:
            self.log_result("7. Test DM Thread Creation", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Try to create DM thread with u1
            payload = {
                'userId': self.demo_user_id,
                'peerUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    thread_id = data['threadId']
                    self.log_result(
                        "7. Test DM Thread Creation", 
                        True, 
                        f"Successfully created DM thread between demo user and u1",
                        f"Thread ID: {thread_id}"
                    )
                    return thread_id
                else:
                    self.log_result(
                        "7. Test DM Thread Creation", 
                        False, 
                        "DM thread response missing threadId",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # Check if it's because they're not friends
                error_data = response.json()
                error_detail = error_data.get('detail', '').lower()
                if 'friend' in error_detail:
                    self.log_result(
                        "7. Test DM Thread Creation", 
                        False, 
                        "DM thread creation failed - users are not friends",
                        f"Error: {error_data.get('detail', 'Unknown error')}"
                    )
                else:
                    self.log_result(
                        "7. Test DM Thread Creation", 
                        False, 
                        f"DM thread creation failed with 400 error",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "7. Test DM Thread Creation", 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("7. Test DM Thread Creation", False, f"Exception occurred: {str(e)}")
        
        return None
    
    def test_8_call_initiation(self):
        """Test 8: Test Call Initiation"""
        if not self.demo_user_id:
            self.log_result("8. Test Call Initiation", False, "Skipped - no demo user ID available")
            return
            
        try:
            # Try to initiate a voice call with u1
            payload = {
                'callerId': self.demo_user_id,
                'recipientId': 'u1',
                'callType': 'voice'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'callId' in data or 'token' in data:
                    self.log_result(
                        "8. Test Call Initiation", 
                        True, 
                        f"Successfully initiated voice call between demo user and u1",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "8. Test Call Initiation", 
                        False, 
                        "Call initiation response missing expected fields",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # Check if it's the "friends only" error
                error_data = response.json()
                error_detail = error_data.get('detail', '').lower()
                if 'friend' in error_detail or 'call' in error_detail:
                    self.log_result(
                        "8. Test Call Initiation", 
                        False, 
                        "Call initiation failed - 'You can only call friends' error",
                        f"Error: {error_data.get('detail', 'Unknown error')}"
                    )
                else:
                    self.log_result(
                        "8. Test Call Initiation", 
                        False, 
                        f"Call initiation failed with 400 error",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "8. Test Call Initiation", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("8. Test Call Initiation", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("DEMO USER AUTO-FRIENDING FEATURE TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Email: {DEMO_EMAIL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run tests in sequence
        self.test_1_seed_database()
        self.test_2_verify_seeded_users()
        self.test_3_demo_user_login()
        self.test_4_check_demo_user_friends()
        self.test_5_verify_bidirectional_friendship()
        self.test_6_friend_status_api()
        self.test_7_dm_thread_creation()
        self.test_8_call_initiation()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print("\nFAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['message']}")
        
        print("\nCRITICAL FINDINGS:")
        
        # Check if auto-friending worked
        demo_friends_test = next((t for t in self.test_results if t['test'] == '4. Check Demo User Friends'), None)
        if demo_friends_test and demo_friends_test['success']:
            print("✅ Demo user auto-friending logic is WORKING")
        else:
            print("❌ Demo user auto-friending logic is NOT WORKING")
        
        # Check if bidirectional friendship worked
        bidirectional_test = next((t for t in self.test_results if t['test'] == '5. Verify Bidirectional Friendship'), None)
        if bidirectional_test and bidirectional_test['success']:
            print("✅ Bidirectional friendship establishment is WORKING")
        else:
            print("❌ Bidirectional friendship establishment is NOT WORKING")
        
        # Check if friend status API works
        friend_status_test = next((t for t in self.test_results if t['test'] == '6. Test Friend Status API'), None)
        if friend_status_test and friend_status_test['success']:
            print("✅ Friend status API is WORKING")
        else:
            print("❌ Friend status API is NOT WORKING")
        
        # Check if DM and calls work
        dm_test = next((t for t in self.test_results if t['test'] == '7. Test DM Thread Creation'), None)
        call_test = next((t for t in self.test_results if t['test'] == '8. Test Call Initiation'), None)
        
        if dm_test and dm_test['success'] and call_test and call_test['success']:
            print("✅ DM and Call functionality is WORKING (no 'friends only' errors)")
        else:
            print("❌ DM and Call functionality has issues (likely 'friends only' errors)")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = DemoAutoFriendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)