#!/usr/bin/env python3
"""
Friend Request and Search Issues Investigation
Tests the specific friend request and search functionality reported by the user.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FriendRequestSearchTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_user_email = None
        
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
    
    def setup_authentication(self):
        """Setup authentication for demo user"""
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
    
    def create_test_user(self):
        """Create a second test user for friend request testing"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"friendtest_{timestamp}@example.com"
            
            payload = {
                "email": self.test_user_email,
                "handle": f"friendtest_{timestamp}",
                "name": f"Friend Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.test_user_token = data['token']
                    self.test_user_id = data['user']['id']
                    self.log_result(
                        "Test User Creation", 
                        True, 
                        f"Successfully created test user {data['user']['name']}",
                        f"User ID: {self.test_user_id}"
                    )
                    return True
                else:
                    self.log_result("Test User Creation", False, "Signup response missing token or user data")
                    return False
            else:
                self.log_result("Test User Creation", False, f"Signup failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Test User Creation", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_send_friend_request(self):
        """Test 1: Send friend request from Test User to Demo User"""
        if not self.test_user_id or not self.demo_user_id:
            self.log_result("Send Friend Request", False, "Skipped - missing user IDs")
            return False
            
        try:
            params = {
                'fromUserId': self.test_user_id,
                'toUserId': self.demo_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        f"Successfully sent friend request: {data.get('message', 'No message')}",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        f"Friend request failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Send Friend Request", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_get_pending_requests(self):
        """Test 2: Get pending friend requests for Demo User"""
        if not self.demo_user_id:
            self.log_result("Get Pending Requests", False, "Skipped - missing demo user ID")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-requests")
            
            if response.status_code == 200:
                data = response.json()
                if 'received' in data and 'sent' in data:
                    received = data['received']
                    sent = data['sent']
                    
                    # Look for request from test user
                    test_user_request = None
                    for req in received:
                        if req.get('id') == self.test_user_id:
                            test_user_request = req
                            break
                    
                    if test_user_request:
                        self.log_result(
                            "Get Pending Requests", 
                            True, 
                            f"Found pending request from {test_user_request.get('name', 'Unknown')}",
                            f"Received: {len(received)}, Sent: {len(sent)}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Get Pending Requests", 
                            False, 
                            "No pending request found from test user",
                            f"Received requests: {[r.get('name', 'Unknown') for r in received]}"
                        )
                        return False
                else:
                    self.log_result(
                        "Get Pending Requests", 
                        False, 
                        "Response missing 'received' or 'sent' fields",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Get Pending Requests", 
                    False, 
                    f"Get requests failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Get Pending Requests", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_accept_friend_request(self):
        """Test 3: Accept friend request"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("Accept Friend Request", False, "Skipped - missing user IDs")
            return False
            
        try:
            params = {
                'userId': self.demo_user_id,
                'friendId': self.test_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request: {data.get('message', 'No message')}",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Accept Friend Request", 
                        False, 
                        f"Accept failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Accept Friend Request", 
                    False, 
                    f"Accept failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Accept Friend Request", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_verify_friendship(self):
        """Test 4: Verify bidirectional friendship was created"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("Verify Friendship", False, "Skipped - missing user IDs")
            return False
            
        try:
            # Check demo user's friends list
            response1 = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friends")
            
            if response1.status_code == 200:
                demo_friends = response1.json()
                demo_friend_ids = [f.get('id') for f in demo_friends]
                
                # Check test user's friends list
                response2 = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/friends")
                
                if response2.status_code == 200:
                    test_friends = response2.json()
                    test_friend_ids = [f.get('id') for f in test_friends]
                    
                    # Verify bidirectional friendship
                    demo_has_test = self.test_user_id in demo_friend_ids
                    test_has_demo = self.demo_user_id in test_friend_ids
                    
                    if demo_has_test and test_has_demo:
                        self.log_result(
                            "Verify Friendship", 
                            True, 
                            "Bidirectional friendship verified successfully",
                            f"Demo friends: {len(demo_friends)}, Test friends: {len(test_friends)}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Friendship", 
                            False, 
                            f"Friendship not bidirectional - Demo has Test: {demo_has_test}, Test has Demo: {test_has_demo}",
                            f"Demo friend IDs: {demo_friend_ids}, Test friend IDs: {test_friend_ids}"
                        )
                        return False
                else:
                    self.log_result(
                        "Verify Friendship", 
                        False, 
                        f"Failed to get test user friends with status {response2.status_code}",
                        f"Response: {response2.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Friendship", 
                    False, 
                    f"Failed to get demo user friends with status {response1.status_code}",
                    f"Response: {response1.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Friendship", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_friend_status_check(self):
        """Test 5: Check friend status between users"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("Friend Status Check", False, "Skipped - missing user IDs")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'friends':
                    self.log_result(
                        "Friend Status Check", 
                        True, 
                        f"Friend status correctly shows 'friends'",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Friend Status Check", 
                        False, 
                        f"Friend status shows '{status}' instead of 'friends'",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Friend Status Check", 
                    False, 
                    f"Friend status check failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Friend Status Check", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_remove_friend(self):
        """Test 6: Remove friend (unfriend)"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("Remove Friend", False, "Skipped - missing user IDs")
            return False
            
        try:
            params = {
                'userId': self.demo_user_id,
                'friendId': self.test_user_id
            }
            
            response = self.session.delete(f"{BACKEND_URL}/friends/remove", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Remove Friend", 
                        True, 
                        f"Successfully removed friend: {data.get('message', 'No message')}",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Remove Friend", 
                        False, 
                        f"Remove friend failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Remove Friend", 
                    False, 
                    f"Remove friend failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Remove Friend", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_reject_friend_request(self):
        """Test 7: Test rejecting friend request (send new request first)"""
        if not self.test_user_id or not self.demo_user_id:
            self.log_result("Reject Friend Request", False, "Skipped - missing user IDs")
            return False
            
        try:
            # First send a new friend request
            params = {
                'fromUserId': self.test_user_id,
                'toUserId': self.demo_user_id
            }
            
            send_response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if send_response.status_code == 200:
                # Now reject it
                reject_params = {
                    'userId': self.demo_user_id,
                    'friendId': self.test_user_id
                }
                
                reject_response = self.session.post(f"{BACKEND_URL}/friends/reject", params=reject_params)
                
                if reject_response.status_code == 200:
                    data = reject_response.json()
                    if data.get('success'):
                        self.log_result(
                            "Reject Friend Request", 
                            True, 
                            f"Successfully rejected friend request: {data.get('message', 'No message')}",
                            f"Response: {data}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Reject Friend Request", 
                            False, 
                            f"Reject failed: {data.get('message', 'Unknown error')}",
                            f"Response: {data}"
                        )
                        return False
                else:
                    self.log_result(
                        "Reject Friend Request", 
                        False, 
                        f"Reject failed with status {reject_response.status_code}",
                        f"Response: {reject_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Reject Friend Request", 
                    False, 
                    f"Could not send friend request for rejection test - status {send_response.status_code}",
                    f"Response: {send_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Reject Friend Request", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_search_by_name(self):
        """Test 8: Search users by name"""
        try:
            params = {
                'q': 'Demo'  # Search for demo user
            }
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for demo user in results
                    demo_found = False
                    for user in data:
                        if user.get('id') == self.demo_user_id or 'demo' in user.get('name', '').lower():
                            demo_found = True
                            break
                    
                    if demo_found:
                        self.log_result(
                            "User Search by Name", 
                            True, 
                            f"Successfully found users by name search - {len(data)} results",
                            f"Demo user found in results"
                        )
                        return True
                    else:
                        self.log_result(
                            "User Search by Name", 
                            False, 
                            f"Search returned {len(data)} results but demo user not found",
                            f"Results: {[u.get('name', 'Unknown') for u in data[:3]]}"
                        )
                        return False
                else:
                    self.log_result(
                        "User Search by Name", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "User Search by Name", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Search by Name", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_search_by_handle(self):
        """Test 9: Search users by handle"""
        try:
            params = {
                'q': 'demo'  # Search for demo user handle
            }
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "User Search by Handle", 
                        True, 
                        f"Successfully searched users by handle - {len(data)} results",
                        f"Search query: 'demo'"
                    )
                    return True
                else:
                    self.log_result(
                        "User Search by Handle", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "User Search by Handle", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Search by Handle", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_search_by_email(self):
        """Test 10: Search users by email"""
        try:
            params = {
                'q': 'loopync'  # Search for part of demo email
            }
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "User Search by Email", 
                        True, 
                        f"Successfully searched users by email - {len(data)} results",
                        f"Search query: 'loopync'"
                    )
                    return True
                else:
                    self.log_result(
                        "User Search by Email", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "User Search by Email", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Search by Email", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_global_search(self):
        """Test 11: Global search functionality"""
        try:
            params = {
                'q': 'test',
                'currentUserId': self.demo_user_id
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data and 'posts' in data:
                    users = data['users']
                    posts = data['posts']
                    
                    # Check if users have friend status
                    friend_status_present = True
                    if users:
                        for user in users[:3]:  # Check first 3 users
                            if 'isFriend' not in user or 'isBlocked' not in user:
                                friend_status_present = False
                                break
                    
                    if friend_status_present:
                        self.log_result(
                            "Global Search", 
                            True, 
                            f"Global search working correctly - {len(users)} users, {len(posts)} posts",
                            f"Friend status included in user results"
                        )
                        return True
                    else:
                        self.log_result(
                            "Global Search", 
                            False, 
                            f"Global search missing friend status in user results",
                            f"Users: {len(users)}, Posts: {len(posts)}"
                        )
                        return False
                else:
                    self.log_result(
                        "Global Search", 
                        False, 
                        "Global search response missing 'users' or 'posts' fields",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Global Search", 
                    False, 
                    f"Global search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Global Search", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_search_with_friend_status(self):
        """Test 12: Verify search results show correct friend status"""
        if not self.demo_user_id or not self.test_user_id:
            self.log_result("Search Friend Status", False, "Skipped - missing user IDs")
            return False
            
        try:
            # First make sure users are friends again
            params = {
                'fromUserId': self.test_user_id,
                'toUserId': self.demo_user_id
            }
            self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            accept_params = {
                'userId': self.demo_user_id,
                'friendId': self.test_user_id
            }
            self.session.post(f"{BACKEND_URL}/friends/accept", params=accept_params)
            
            # Now search and check friend status
            search_params = {
                'q': 'Friend Test',  # Search for test user
                'currentUserId': self.demo_user_id
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=search_params)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data:
                    users = data['users']
                    
                    # Look for test user in results
                    test_user_found = False
                    for user in users:
                        if user.get('id') == self.test_user_id:
                            test_user_found = True
                            is_friend = user.get('isFriend', False)
                            
                            if is_friend:
                                self.log_result(
                                    "Search Friend Status", 
                                    True, 
                                    f"Search correctly shows friend status for test user",
                                    f"isFriend: {is_friend}, isBlocked: {user.get('isBlocked', False)}"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Search Friend Status", 
                                    False, 
                                    f"Search shows incorrect friend status for test user",
                                    f"isFriend: {is_friend}, expected: True"
                                )
                                return False
                    
                    if not test_user_found:
                        self.log_result(
                            "Search Friend Status", 
                            False, 
                            "Test user not found in search results",
                            f"Search returned {len(users)} users"
                        )
                        return False
                else:
                    self.log_result(
                        "Search Friend Status", 
                        False, 
                        "Search response missing 'users' field",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Search Friend Status", 
                    False, 
                    f"Search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Search Friend Status", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all friend request and search tests"""
        print("=" * 80)
        print("FRIEND REQUEST AND SEARCH ISSUES INVESTIGATION")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return
        
        # Seed data for testing
        try:
            self.session.post(f"{BACKEND_URL}/seed")
            print("✅ Seeded test data")
        except:
            print("⚠️  Could not seed data, continuing anyway")
        
        # Friend Request Flow Tests
        print("\n" + "=" * 50)
        print("PART 1: FRIEND REQUEST FLOW TESTING")
        print("=" * 50)
        
        self.test_send_friend_request()
        self.test_get_pending_requests()
        self.test_accept_friend_request()
        self.test_verify_friendship()
        self.test_friend_status_check()
        self.test_remove_friend()
        self.test_reject_friend_request()
        
        # Search Tests
        print("\n" + "=" * 50)
        print("PART 2: FRIEND SEARCH TESTING")
        print("=" * 50)
        
        self.test_user_search_by_name()
        self.test_user_search_by_handle()
        self.test_user_search_by_email()
        self.test_global_search()
        self.test_search_with_friend_status()
        
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
    tester = FriendRequestSearchTester()
    results = tester.run_all_tests()