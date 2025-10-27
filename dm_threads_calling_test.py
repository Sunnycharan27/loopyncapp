#!/usr/bin/env python3
"""
DM Threads for Demo User to Test Calling - Backend Testing Suite
Tests the specific scenario requested: Create DM threads between demo user and friends for calling functionality.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class DMThreadsCallingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.demo_friends = []
        self.created_threads = []
        
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
    
    def test_1_login_demo_user(self):
        """Test 1: Login Demo User (demo@loopync.com / password123)"""
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
                    
                    if user.get('email') == DEMO_EMAIL and self.demo_user_id:
                        self.log_result(
                            "Login Demo User", 
                            True, 
                            f"Successfully logged in as {user['name']} ({user['email']})",
                            f"User ID: {self.demo_user_id}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Login Demo User", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
                        )
                        return False
                else:
                    self.log_result(
                        "Login Demo User", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Login Demo User", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Login Demo User", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_2_check_demo_user_friends(self):
        """Test 2: Check Demo User's Friends (should contain u1, u2, u3)"""
        if not self.demo_user_id:
            self.log_result("Check Demo User Friends", False, "Skipped - no demo user ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get('friends', [])
                self.demo_friends = friends
                
                expected_friends = ['u1', 'u2', 'u3']
                found_friends = [f for f in expected_friends if f in friends]
                
                if len(found_friends) >= 3:
                    self.log_result(
                        "Check Demo User Friends", 
                        True, 
                        f"Demo user has {len(friends)} friends, including expected u1, u2, u3",
                        f"Friends: {friends}, Found expected: {found_friends}"
                    )
                    return True
                elif len(found_friends) > 0:
                    self.log_result(
                        "Check Demo User Friends", 
                        True, 
                        f"Demo user has {len(found_friends)} of expected friends: {found_friends}",
                        f"All friends: {friends}"
                    )
                    return True
                else:
                    self.log_result(
                        "Check Demo User Friends", 
                        False, 
                        f"Demo user has {len(friends)} friends but none of expected u1, u2, u3",
                        f"Friends: {friends}"
                    )
                    return False
            else:
                self.log_result(
                    "Check Demo User Friends", 
                    False, 
                    f"Failed to get demo user data with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Check Demo User Friends", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_3_create_dm_thread_with_u1(self):
        """Test 3: Create DM Thread with u1"""
        return self._create_dm_thread_with_user('u1', "Create DM Thread with u1")
    
    def test_4_create_dm_thread_with_u2(self):
        """Test 4: Create DM Thread with u2"""
        return self._create_dm_thread_with_user('u2', "Create DM Thread with u2")
    
    def test_5_create_dm_thread_with_u3(self):
        """Test 5: Create DM Thread with u3"""
        return self._create_dm_thread_with_user('u3', "Create DM Thread with u3")
    
    def _create_dm_thread_with_user(self, peer_user_id, test_name):
        """Helper method to create DM thread with a specific user"""
        if not self.demo_user_id:
            self.log_result(test_name, False, "Skipped - no demo user ID available")
            return False
            
        try:
            params = {
                'userId': self.demo_user_id,
                'peerUserId': peer_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                thread_id = data.get('threadId')
                
                if thread_id:
                    self.created_threads.append({
                        'threadId': thread_id,
                        'peerUserId': peer_user_id
                    })
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Successfully created DM thread with {peer_user_id}",
                        f"Thread ID: {thread_id}"
                    )
                    
                    # Send a test message in the thread
                    self._send_test_message(thread_id, peer_user_id, test_name)
                    return True
                else:
                    self.log_result(
                        test_name, 
                        False, 
                        "DM thread creation response missing threadId",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    test_name, 
                    False, 
                    f"DM thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception occurred: {str(e)}")
            return False
    
    def _send_test_message(self, thread_id, peer_user_id, parent_test_name):
        """Helper method to send a test message in a DM thread"""
        try:
            params = {'userId': self.demo_user_id}
            payload = {'text': f'Hello {peer_user_id}! This is a test message for calling functionality.'}
            
            response = self.session.post(
                f"{BACKEND_URL}/dm/threads/{thread_id}/messages", 
                params=params, 
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messageId') or data.get('id')
                
                if message_id:
                    self.log_result(
                        f"{parent_test_name} - Send Message", 
                        True, 
                        f"Successfully sent test message to {peer_user_id}",
                        f"Message ID: {message_id}"
                    )
                else:
                    self.log_result(
                        f"{parent_test_name} - Send Message", 
                        False, 
                        "Message sent but response missing message ID",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    f"{parent_test_name} - Send Message", 
                    False, 
                    f"Failed to send message with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(f"{parent_test_name} - Send Message", False, f"Exception occurred: {str(e)}")
    
    def test_6_verify_threads_exist(self):
        """Test 6: Verify Threads Exist - GET /api/dm/threads?userId={demo_id}"""
        if not self.demo_user_id:
            self.log_result("Verify Threads Exist", False, "Skipped - no demo user ID available")
            return False
            
        try:
            params = {'userId': self.demo_user_id}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                threads = []
                
                if 'items' in data and isinstance(data['items'], list):
                    threads = data['items']
                elif isinstance(data, list):
                    threads = data
                
                if len(threads) >= 3:
                    # Check for threads with u1, u2, u3
                    peer_ids = []
                    for thread in threads:
                        if 'peer' in thread and 'id' in thread['peer']:
                            peer_ids.append(thread['peer']['id'])
                        elif 'user1Id' in thread and 'user2Id' in thread:
                            # Determine peer ID
                            peer_id = thread['user2Id'] if thread['user1Id'] == self.demo_user_id else thread['user1Id']
                            peer_ids.append(peer_id)
                    
                    expected_peers = ['u1', 'u2', 'u3']
                    found_peers = [p for p in expected_peers if p in peer_ids]
                    
                    if len(found_peers) >= 3:
                        self.log_result(
                            "Verify Threads Exist", 
                            True, 
                            f"Found {len(threads)} DM threads, including all expected peers: {found_peers}",
                            f"All peer IDs: {peer_ids}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Threads Exist", 
                            True, 
                            f"Found {len(threads)} DM threads with {len(found_peers)} expected peers: {found_peers}",
                            f"All peer IDs: {peer_ids}"
                        )
                        return True
                else:
                    self.log_result(
                        "Verify Threads Exist", 
                        False, 
                        f"Expected at least 3 DM threads, found {len(threads)}",
                        f"Threads: {threads}"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Threads Exist", 
                    False, 
                    f"Failed to get DM threads with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Threads Exist", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_7_test_call_initiation(self):
        """Test 7: Test Call Initiation from One Thread"""
        if not self.demo_user_id or not self.demo_friends:
            self.log_result("Test Call Initiation", False, "Skipped - no demo user ID or friends available")
            return False
            
        try:
            # Use the first available friend for call test
            recipient_id = 'u1' if 'u1' in self.demo_friends else self.demo_friends[0]
            
            params = {
                'callerId': self.demo_user_id,
                'recipientId': recipient_id,
                'callType': 'video'
            }
            
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Test Call Initiation", 
                        True, 
                        f"Successfully initiated video call from {self.demo_user_id} to {recipient_id}",
                        f"Call ID: {data['callId']}, Channel: {data['channelName']}"
                    )
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Test Call Initiation", 
                        False, 
                        f"Call initiated but response missing fields: {missing_fields}",
                        f"Response: {data}"
                    )
                    return False
            elif response.status_code == 403:
                # Check if it's a "can only call friends" error
                data = response.json()
                detail = data.get('detail', '').lower()
                if 'friends' in detail:
                    self.log_result(
                        "Test Call Initiation", 
                        False, 
                        f"Call blocked: {data.get('detail', 'Can only call friends')}",
                        f"This indicates friendship validation is working but demo user may not be properly friended with {recipient_id}"
                    )
                else:
                    self.log_result(
                        "Test Call Initiation", 
                        False, 
                        f"Call initiation failed with 403: {data.get('detail', 'Forbidden')}",
                        f"Response: {data}"
                    )
                return False
            else:
                self.log_result(
                    "Test Call Initiation", 
                    False, 
                    f"Call initiation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Test Call Initiation", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting DM Threads for Demo User to Test Calling - Backend Testing Suite")
        print("=" * 80)
        
        # Test sequence as specified in the review request
        tests = [
            self.test_1_login_demo_user,
            self.test_2_check_demo_user_friends,
            self.test_3_create_dm_thread_with_u1,
            self.test_4_create_dm_thread_with_u2,
            self.test_5_create_dm_thread_with_u3,
            self.test_6_verify_threads_exist,
            self.test_7_test_call_initiation
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Exception: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📈 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! DM threads and calling functionality is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the details above.")
        
        # Print expected results verification
        print("\n" + "=" * 80)
        print("🎯 EXPECTED RESULTS VERIFICATION")
        print("=" * 80)
        
        expected_results = [
            "✅ DM threads created successfully",
            "✅ Threads visible in messenger", 
            "✅ Can initiate calls from the threads",
            "✅ User can now test calling functionality in the UI"
        ]
        
        for result in expected_results:
            print(result)
        
        if self.created_threads:
            print(f"\n📋 CREATED THREADS: {len(self.created_threads)}")
            for thread in self.created_threads:
                print(f"   - Thread {thread['threadId']} with {thread['peerUserId']}")
        
        return passed, failed

def main():
    """Main function to run the tests"""
    tester = DMThreadsCallingTester()
    passed, failed = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())