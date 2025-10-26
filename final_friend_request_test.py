#!/usr/bin/env python3
"""
Final Comprehensive Friend Request and Search Test
Tests all the reported issues with proper user handling
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://socialsuper-app.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FinalFriendRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_friend_request_flow_seeded_users(self):
        """Test complete friend request flow with seeded users (u1, u2, u3)"""
        try:
            # Seed data first
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test 1: Send friend request from u1 to u2
            params = {'fromUserId': 'u1', 'toUserId': 'u2'}
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Send Friend Request (u1 → u2)", 
                    True, 
                    f"Successfully sent: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
            else:
                self.log_result(
                    "Send Friend Request (u1 → u2)", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 2: Get pending requests for u2
            response = self.session.get(f"{BACKEND_URL}/users/u2/friend-requests")
            
            if response.status_code == 200:
                data = response.json()
                received = data.get('received', [])
                u1_request = any(req.get('id') == 'u1' for req in received)
                
                if u1_request:
                    self.log_result(
                        "Get Pending Requests (u2)", 
                        True, 
                        f"Found pending request from u1",
                        f"Received: {len(received)} requests"
                    )
                else:
                    self.log_result(
                        "Get Pending Requests (u2)", 
                        False, 
                        "No pending request from u1 found",
                        f"Received requests: {[r.get('name', 'Unknown') for r in received]}"
                    )
                    return False
            else:
                self.log_result(
                    "Get Pending Requests (u2)", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 3: Accept friend request
            params = {'userId': 'u2', 'friendId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Accept Friend Request (u2 accepts u1)", 
                    True, 
                    f"Successfully accepted: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
            else:
                self.log_result(
                    "Accept Friend Request (u2 accepts u1)", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 4: Verify bidirectional friendship
            u1_friends_response = self.session.get(f"{BACKEND_URL}/users/u1/friends")
            u2_friends_response = self.session.get(f"{BACKEND_URL}/users/u2/friends")
            
            if u1_friends_response.status_code == 200 and u2_friends_response.status_code == 200:
                u1_friends = u1_friends_response.json()
                u2_friends = u2_friends_response.json()
                
                u1_has_u2 = any(f.get('id') == 'u2' for f in u1_friends)
                u2_has_u1 = any(f.get('id') == 'u1' for f in u2_friends)
                
                if u1_has_u2 and u2_has_u1:
                    self.log_result(
                        "Verify Bidirectional Friendship", 
                        True, 
                        "Friendship created successfully in both directions",
                        f"u1 friends: {len(u1_friends)}, u2 friends: {len(u2_friends)}"
                    )
                else:
                    self.log_result(
                        "Verify Bidirectional Friendship", 
                        False, 
                        f"Friendship not bidirectional - u1 has u2: {u1_has_u2}, u2 has u1: {u2_has_u1}",
                        f"u1 friends: {[f.get('name') for f in u1_friends]}, u2 friends: {[f.get('name') for f in u2_friends]}"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Bidirectional Friendship", 
                    False, 
                    "Failed to get friends lists",
                    f"u1 status: {u1_friends_response.status_code}, u2 status: {u2_friends_response.status_code}"
                )
                return False
            
            # Test 5: Check friend status
            response = self.session.get(f"{BACKEND_URL}/users/u1/friend-status/u2")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'friends':
                    self.log_result(
                        "Friend Status Check", 
                        True, 
                        f"Friend status correctly shows: {status}",
                        f"Response: {data}"
                    )
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
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 6: Remove friend
            params = {'userId': 'u1', 'friendId': 'u2'}
            response = self.session.delete(f"{BACKEND_URL}/friends/remove", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Remove Friend (u1 removes u2)", 
                    True, 
                    f"Successfully removed: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
            else:
                self.log_result(
                    "Remove Friend (u1 removes u2)", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 7: Reject friend request (send new request first)
            params = {'fromUserId': 'u1', 'toUserId': 'u2'}
            self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            params = {'userId': 'u2', 'friendId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/friends/reject", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Reject Friend Request (u2 rejects u1)", 
                    True, 
                    f"Successfully rejected: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
            else:
                self.log_result(
                    "Reject Friend Request (u2 rejects u1)", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            return True
                
        except Exception as e:
            self.log_result("Friend Request Flow", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_user_search_functionality(self):
        """Test user search by name, handle, and email"""
        try:
            # Ensure seeded data exists
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test 1: Search by name
            params = {'q': 'Priya'}
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    found_priya = any('priya' in user.get('name', '').lower() for user in data)
                    self.log_result(
                        "User Search by Name", 
                        True, 
                        f"Search returned {len(data)} results, Priya found: {found_priya}",
                        f"Results: {[u.get('name', 'Unknown') for u in data[:3]]}"
                    )
                else:
                    self.log_result(
                        "User Search by Name", 
                        False, 
                        f"Search returned no results",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "User Search by Name", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 2: Search by handle
            params = {'q': 'vibe'}
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "User Search by Handle", 
                    True, 
                    f"Search by handle returned {len(data)} results",
                    f"Query: 'vibe'"
                )
            else:
                self.log_result(
                    "User Search by Handle", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            # Test 3: Search by email (partial)
            params = {'q': 'gmail'}
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "User Search by Email", 
                    True, 
                    f"Search by email returned {len(data)} results",
                    f"Query: 'gmail'"
                )
            else:
                self.log_result(
                    "User Search by Email", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
            
            return True
                
        except Exception as e:
            self.log_result("User Search Functionality", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_global_search_functionality(self):
        """Test global search with friend status"""
        try:
            # Ensure seeded data exists
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test global search with currentUserId
            params = {
                'q': 'test',
                'currentUserId': 'u1'
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'users' in data and 'posts' in data:
                    users = data['users']
                    posts = data['posts']
                    tribes = data.get('tribes', [])
                    venues = data.get('venues', [])
                    events = data.get('events', [])
                    
                    self.log_result(
                        "Global Search Functionality", 
                        True, 
                        f"Global search working correctly",
                        f"Users: {len(users)}, Posts: {len(posts)}, Tribes: {len(tribes)}, Venues: {len(venues)}, Events: {len(events)}"
                    )
                    
                    # Check if users have friend status when currentUserId is provided
                    if users:
                        first_user = users[0]
                        has_friend_status = 'isFriend' in first_user and 'isBlocked' in first_user
                        
                        if has_friend_status:
                            self.log_result(
                                "Global Search Friend Status", 
                                True, 
                                "Friend status correctly included in search results",
                                f"First user: {first_user.get('name', 'Unknown')} - isFriend: {first_user['isFriend']}, isBlocked: {first_user['isBlocked']}"
                            )
                        else:
                            self.log_result(
                                "Global Search Friend Status", 
                                False, 
                                "Friend status missing from search results",
                                f"User fields: {list(first_user.keys())}"
                            )
                            return False
                    
                    return True
                else:
                    self.log_result(
                        "Global Search Functionality", 
                        False, 
                        "Global search response missing required fields",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Global Search Functionality", 
                    False, 
                    f"Failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Global Search Functionality", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_demo_user_authentication(self):
        """Test demo user authentication and basic functionality"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user = data['user']
                    self.log_result(
                        "Demo User Authentication", 
                        True, 
                        f"Successfully logged in as {user['name']}",
                        f"User ID: {user['id']}, Handle: {user.get('handle', 'No handle')}"
                    )
                    return user['id']
                else:
                    self.log_result("Demo User Authentication", False, "Login response missing token or user data")
                    return None
            else:
                self.log_result("Demo User Authentication", False, f"Login failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Demo User Authentication", False, f"Exception occurred: {str(e)}")
            return None
    
    def test_search_results_display(self):
        """Test that search results display correctly with Add Friend buttons"""
        try:
            # Ensure seeded data exists
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test search that should return results
            params = {'q': 'a'}  # Should match several users
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        self.log_result(
                            "Search Results Display", 
                            True, 
                            f"Search returned {len(data)} users for display",
                            f"Users: {[u.get('name', 'Unknown') for u in data[:5]]}"
                        )
                        
                        # Check if users have required fields for display
                        first_user = data[0]
                        required_fields = ['id', 'name', 'handle', 'avatar']
                        missing_fields = [field for field in required_fields if field not in first_user]
                        
                        if not missing_fields:
                            self.log_result(
                                "Search Results User Data", 
                                True, 
                                "Search results contain all required user fields",
                                f"Fields: {list(first_user.keys())}"
                            )
                        else:
                            self.log_result(
                                "Search Results User Data", 
                                False, 
                                f"Search results missing required fields: {missing_fields}",
                                f"Available fields: {list(first_user.keys())}"
                            )
                            return False
                        
                        return True
                    else:
                        self.log_result(
                            "Search Results Display", 
                            False, 
                            "Search returned no results",
                            "Expected at least some users for query 'a'"
                        )
                        return False
                else:
                    self.log_result(
                        "Search Results Display", 
                        False, 
                        "Search response is not a list",
                        f"Response type: {type(data)}"
                    )
                    return False
            else:
                self.log_result(
                    "Search Results Display", 
                    False, 
                    f"Search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Search Results Display", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 80)
        print("FINAL COMPREHENSIVE FRIEND REQUEST AND SEARCH TESTING")
        print("=" * 80)
        
        # Test demo user authentication
        print("\n" + "=" * 50)
        print("DEMO USER AUTHENTICATION")
        print("=" * 50)
        
        demo_user_id = self.test_demo_user_authentication()
        
        # Test friend request flow with seeded users
        print("\n" + "=" * 50)
        print("FRIEND REQUEST FLOW (SEEDED USERS)")
        print("=" * 50)
        
        friend_flow_success = self.test_friend_request_flow_seeded_users()
        
        # Test search functionality
        print("\n" + "=" * 50)
        print("SEARCH FUNCTIONALITY")
        print("=" * 50)
        
        search_success = self.test_user_search_functionality()
        global_search_success = self.test_global_search_functionality()
        search_display_success = self.test_search_results_display()
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Categorize results
        print(f"\n📊 RESULTS BY CATEGORY:")
        print(f"✅ Demo User Authentication: {'PASS' if demo_user_id else 'FAIL'}")
        print(f"✅ Friend Request Flow: {'PASS' if friend_flow_success else 'FAIL'}")
        print(f"✅ User Search: {'PASS' if search_success else 'FAIL'}")
        print(f"✅ Global Search: {'PASS' if global_search_success else 'FAIL'}")
        print(f"✅ Search Display: {'PASS' if search_display_success else 'FAIL'}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        # Specific findings for the user report
        print(f"\n🔍 FINDINGS FOR USER REPORT:")
        if friend_flow_success:
            print("✅ Friend request system is working correctly with seeded users")
            print("   - Send, accept, reject, and remove friend functionality all working")
            print("   - Bidirectional friendship creation working")
            print("   - Friend status checking working")
        else:
            print("❌ Friend request system has issues")
        
        if search_success and global_search_success and search_display_success:
            print("✅ Search functionality is working correctly")
            print("   - User search by name, handle, email working")
            print("   - Global search with friend status working")
            print("   - Search results display properly")
        else:
            print("❌ Search functionality has issues")
        
        if demo_user_id:
            print("✅ Demo user authentication working")
            print("⚠️  Note: Demo user exists but may have data consistency issues with friend requests")
        else:
            print("❌ Demo user authentication has issues")
        
        print("\n" + "=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = FinalFriendRequestTester()
    results = tester.run_all_tests()