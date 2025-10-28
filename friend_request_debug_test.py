#!/usr/bin/env python3
"""
Friend Request Acceptance Debug Test
Debug and Fix Friend Request Acceptance for Real Users

This test follows the exact investigation sequence requested:
1. Login Real Users
2. Check Current Friend Status  
3. Send Friend Request (User 1 → User 2)
4. Check Pending Requests
5. Accept Friend Request (User 2 Accepts)
6. Debug Accept Endpoint
7. Verify Friendship After Accept
8. Test Alternative Accept Method
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
USER1_EMAIL = "demo@loopync.com"
USER1_PASSWORD = "password123"

class FriendRequestDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.user1_token = None
        self.user1_id = None
        self.user1_data = None
        self.user2_token = None
        self.user2_id = None
        self.user2_data = None
        self.user2_email = None
        
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def step_1_login_user1(self):
        """STEP 1: Login User 1 (demo@loopync.com / password123)"""
        try:
            payload = {
                "email": USER1_EMAIL,
                "password": USER1_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user1_token = data['token']
                    self.user1_data = data['user']
                    self.user1_id = data['user']['id']
                    
                    self.log_result(
                        "STEP 1: Login User 1", 
                        True, 
                        f"Successfully logged in User 1: {self.user1_data['name']} ({self.user1_data['email']})",
                        f"User ID: {self.user1_id}, Friends: {len(self.user1_data.get('friends', []))}"
                    )
                else:
                    self.log_result(
                        "STEP 1: Login User 1", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "STEP 1: Login User 1", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 1: Login User 1", False, f"Exception occurred: {str(e)}")
    
    def step_2_create_user2(self):
        """STEP 2: Create/Login User 2 with different credentials"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.user2_email = f"testuser2_{timestamp}@example.com"
            
            payload = {
                "email": self.user2_email,
                "handle": f"testuser2_{timestamp}",
                "name": f"Test User 2 {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user2_token = data['token']
                    self.user2_data = data['user']
                    self.user2_id = data['user']['id']
                    
                    self.log_result(
                        "STEP 2: Create User 2", 
                        True, 
                        f"Successfully created User 2: {self.user2_data['name']} ({self.user2_data['email']})",
                        f"User ID: {self.user2_id}, Friends: {len(self.user2_data.get('friends', []))}"
                    )
                else:
                    self.log_result(
                        "STEP 2: Create User 2", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "STEP 2: Create User 2", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("STEP 2: Create User 2", False, f"Exception occurred: {str(e)}")
                    self.log_result(
                        "Demo User Authentication", 
                        True, 
                        f"Successfully logged in as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                    return True
                else:
                    self.log_result("Demo User Authentication", False, "Login response missing token or user data")
                    return False
            else:
                self.log_result("Demo User Authentication", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Demo User Authentication", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_seed_data(self):
        """Seed test data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Seed Data", 
                    True, 
                    f"Successfully seeded data",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result("Seed Data", False, f"Seed failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Seed Data", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_list_users(self):
        """List all users to see what's available"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    user_info = []
                    for user in data[:10]:  # Show first 10 users
                        user_info.append(f"{user.get('id', 'No ID')} - {user.get('name', 'No Name')} ({user.get('handle', 'No Handle')})")
                    
                    self.log_result(
                        "List Users", 
                        True, 
                        f"Found {len(data)} users in database",
                        f"First 10 users:\n" + "\n".join(user_info)
                    )
                    return data
                else:
                    self.log_result("List Users", False, "Users response is not a list")
                    return []
            else:
                self.log_result("List Users", False, f"List users failed with status {response.status_code}")
                return []
                
        except Exception as e:
            self.log_result("List Users", False, f"Exception occurred: {str(e)}")
            return []
    
    def test_friend_request_with_seeded_users(self):
        """Test friend request between seeded users u1 and u2"""
        try:
            # Send friend request from u1 to u2
            params = {
                'fromUserId': 'u1',
                'toUserId': 'u2'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Friend Request (u1 -> u2)", 
                    True, 
                    f"Successfully sent friend request: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Friend Request (u1 -> u2)", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Friend Request (u1 -> u2)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_get_friend_requests_u2(self):
        """Get friend requests for u2"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/u2/friend-requests")
            
            if response.status_code == 200:
                data = response.json()
                if 'received' in data and 'sent' in data:
                    received = data['received']
                    sent = data['sent']
                    
                    self.log_result(
                        "Get Friend Requests (u2)", 
                        True, 
                        f"Successfully retrieved friend requests",
                        f"Received: {len(received)}, Sent: {len(sent)}"
                    )
                    
                    # Show details of received requests
                    if received:
                        print("   Received requests:")
                        for req in received:
                            print(f"     - From: {req.get('name', 'Unknown')} (ID: {req.get('id', 'Unknown')})")
                    
                    return True
                else:
                    self.log_result(
                        "Get Friend Requests (u2)", 
                        False, 
                        "Response missing 'received' or 'sent' fields",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Get Friend Requests (u2)", 
                    False, 
                    f"Get requests failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Get Friend Requests (u2)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_accept_friend_request_u2(self):
        """Accept friend request from u1 to u2"""
        try:
            params = {
                'userId': 'u2',
                'friendId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Accept Friend Request (u2 accepts u1)", 
                    True, 
                    f"Successfully accepted friend request: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Accept Friend Request (u2 accepts u1)", 
                    False, 
                    f"Accept failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Accept Friend Request (u2 accepts u1)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_verify_friendship_u1_u2(self):
        """Verify friendship between u1 and u2"""
        try:
            # Check u1's friends
            response1 = self.session.get(f"{BACKEND_URL}/users/u1/friends")
            
            if response1.status_code == 200:
                u1_friends = response1.json()
                u1_friend_ids = [f.get('id') for f in u1_friends]
                
                # Check u2's friends
                response2 = self.session.get(f"{BACKEND_URL}/users/u2/friends")
                
                if response2.status_code == 200:
                    u2_friends = response2.json()
                    u2_friend_ids = [f.get('id') for f in u2_friends]
                    
                    u1_has_u2 = 'u2' in u1_friend_ids
                    u2_has_u1 = 'u1' in u2_friend_ids
                    
                    if u1_has_u2 and u2_has_u1:
                        self.log_result(
                            "Verify Friendship (u1 <-> u2)", 
                            True, 
                            "Bidirectional friendship verified successfully",
                            f"u1 friends: {u1_friend_ids}, u2 friends: {u2_friend_ids}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Friendship (u1 <-> u2)", 
                            False, 
                            f"Friendship not bidirectional - u1 has u2: {u1_has_u2}, u2 has u1: {u2_has_u1}",
                            f"u1 friends: {u1_friend_ids}, u2 friends: {u2_friend_ids}"
                        )
                        return False
                else:
                    self.log_result(
                        "Verify Friendship (u1 <-> u2)", 
                        False, 
                        f"Failed to get u2 friends with status {response2.status_code}",
                        f"Response: {response2.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Friendship (u1 <-> u2)", 
                    False, 
                    f"Failed to get u1 friends with status {response1.status_code}",
                    f"Response: {response1.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Friendship (u1 <-> u2)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_friend_status_check_u1_u2(self):
        """Check friend status between u1 and u2"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/u1/friend-status/u2")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                self.log_result(
                    "Friend Status Check (u1 -> u2)", 
                    True, 
                    f"Friend status: {status}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Friend Status Check (u1 -> u2)", 
                    False, 
                    f"Friend status check failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Friend Status Check (u1 -> u2)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_search_functionality(self):
        """Test user search functionality"""
        try:
            # Search for users with 'a' (should find several)
            params = {'q': 'a'}
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "User Search Functionality", 
                        True, 
                        f"User search working - found {len(data)} users",
                        f"Search query: 'a', Results: {[u.get('name', 'Unknown') for u in data[:5]]}"
                    )
                    return True
                else:
                    self.log_result(
                        "User Search Functionality", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "User Search Functionality", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Search Functionality", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_global_search_functionality(self):
        """Test global search functionality"""
        try:
            params = {
                'q': 'test',
                'currentUserId': 'u1'
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data:
                    users = data['users']
                    posts = data.get('posts', [])
                    tribes = data.get('tribes', [])
                    venues = data.get('venues', [])
                    events = data.get('events', [])
                    
                    self.log_result(
                        "Global Search Functionality", 
                        True, 
                        f"Global search working",
                        f"Users: {len(users)}, Posts: {len(posts)}, Tribes: {len(tribes)}, Venues: {len(venues)}, Events: {len(events)}"
                    )
                    
                    # Check if users have friend status
                    if users:
                        first_user = users[0]
                        has_friend_status = 'isFriend' in first_user and 'isBlocked' in first_user
                        print(f"   Friend status in results: {has_friend_status}")
                        if has_friend_status:
                            print(f"   First user: {first_user.get('name', 'Unknown')} - isFriend: {first_user['isFriend']}, isBlocked: {first_user['isBlocked']}")
                    
                    return True
                else:
                    self.log_result(
                        "Global Search Functionality", 
                        False, 
                        "Global search response missing 'users' field",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Global Search Functionality", 
                    False, 
                    f"Global search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Global Search Functionality", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_remove_friend_u1_u2(self):
        """Test removing friendship between u1 and u2"""
        try:
            params = {
                'userId': 'u1',
                'friendId': 'u2'
            }
            
            response = self.session.delete(f"{BACKEND_URL}/friends/remove", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Remove Friend (u1 removes u2)", 
                    True, 
                    f"Successfully removed friend: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Remove Friend (u1 removes u2)", 
                    False, 
                    f"Remove friend failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Remove Friend (u1 removes u2)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_reject_friend_request(self):
        """Test rejecting a friend request"""
        try:
            # First send a new friend request from u1 to u2
            params = {
                'fromUserId': 'u1',
                'toUserId': 'u2'
            }
            
            send_response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if send_response.status_code == 200:
                # Now reject it
                reject_params = {
                    'userId': 'u2',
                    'friendId': 'u1'
                }
                
                reject_response = self.session.post(f"{BACKEND_URL}/friends/reject", params=reject_params)
                
                if reject_response.status_code == 200:
                    data = reject_response.json()
                    self.log_result(
                        "Reject Friend Request (u2 rejects u1)", 
                        True, 
                        f"Successfully rejected friend request: {data.get('message', 'No message')}",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Reject Friend Request (u2 rejects u1)", 
                        False, 
                        f"Reject failed with status {reject_response.status_code}",
                        f"Response: {reject_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Reject Friend Request (u2 rejects u1)", 
                    False, 
                    f"Could not send friend request for rejection test - status {send_response.status_code}",
                    f"Response: {send_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Reject Friend Request (u2 rejects u1)", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all debug tests"""
        print("=" * 80)
        print("FRIEND REQUEST AND SEARCH DEBUG TESTING")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        # Seed data and list users
        self.test_seed_data()
        users = self.test_list_users()
        
        # Friend Request Flow Tests with seeded users
        print("\n" + "=" * 50)
        print("FRIEND REQUEST FLOW TESTING (u1 <-> u2)")
        print("=" * 50)
        
        self.test_friend_request_with_seeded_users()
        self.test_get_friend_requests_u2()
        self.test_accept_friend_request_u2()
        self.test_verify_friendship_u1_u2()
        self.test_friend_status_check_u1_u2()
        self.test_remove_friend_u1_u2()
        self.test_reject_friend_request()
        
        # Search Tests
        print("\n" + "=" * 50)
        print("SEARCH FUNCTIONALITY TESTING")
        print("=" * 50)
        
        self.test_user_search_functionality()
        self.test_global_search_functionality()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = FriendRequestDebugTester()
    results = tester.run_all_tests()