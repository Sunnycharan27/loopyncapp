#!/usr/bin/env python3
"""
Test Friend Request and Search with Demo User (demo@loopync.com)
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class DemoUserFriendTester:
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
                        f"User ID: {self.demo_user_id}, Handle: {data['user'].get('handle', 'No handle')}"
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
    
    def test_demo_user_in_mongodb(self):
        """Check if demo user exists in MongoDB"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Demo User in MongoDB", 
                    True, 
                    f"Demo user found in MongoDB: {data.get('name', 'Unknown')}",
                    f"Handle: {data.get('handle', 'No handle')}, Email: {data.get('email', 'No email')}"
                )
                return True
            else:
                self.log_result(
                    "Demo User in MongoDB", 
                    False, 
                    f"Demo user not found in MongoDB - status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Demo User in MongoDB", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_send_friend_request_to_u1(self):
        """Send friend request from demo user to u1"""
        try:
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Send Friend Request (Demo -> u1)", 
                    True, 
                    f"Successfully sent friend request: {data.get('message', 'No message')}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Send Friend Request (Demo -> u1)", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Send Friend Request (Demo -> u1)", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_get_demo_friend_requests(self):
        """Get friend requests for demo user"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-requests")
            
            if response.status_code == 200:
                data = response.json()
                if 'received' in data and 'sent' in data:
                    received = data['received']
                    sent = data['sent']
                    
                    self.log_result(
                        "Get Demo Friend Requests", 
                        True, 
                        f"Successfully retrieved friend requests",
                        f"Received: {len(received)}, Sent: {len(sent)}"
                    )
                    
                    # Show details
                    if received:
                        print("   Received requests:")
                        for req in received:
                            print(f"     - From: {req.get('name', 'Unknown')} (ID: {req.get('id', 'Unknown')})")
                    
                    if sent:
                        print("   Sent requests:")
                        for req in sent:
                            print(f"     - To: {req.get('name', 'Unknown')} (ID: {req.get('id', 'Unknown')})")
                    
                    return True
                else:
                    self.log_result(
                        "Get Demo Friend Requests", 
                        False, 
                        "Response missing 'received' or 'sent' fields",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Get Demo Friend Requests", 
                    False, 
                    f"Get requests failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Get Demo Friend Requests", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_demo_friends_list(self):
        """Get demo user's friends list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friends")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Demo Friends List", 
                        True, 
                        f"Demo user has {len(data)} friends",
                        f"Friends: {[f.get('name', 'Unknown') for f in data]}"
                    )
                    return True
                else:
                    self.log_result(
                        "Demo Friends List", 
                        False, 
                        "Friends list response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Demo Friends List", 
                    False, 
                    f"Get friends failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Demo Friends List", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_search_for_demo_user(self):
        """Search for demo user by name"""
        try:
            params = {'q': 'Demo'}
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for demo user in results
                    demo_found = False
                    for user in data:
                        if user.get('id') == self.demo_user_id or 'demo' in user.get('name', '').lower():
                            demo_found = True
                            print(f"   Found demo user: {user.get('name', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
                            break
                    
                    self.log_result(
                        "Search for Demo User", 
                        True, 
                        f"Search returned {len(data)} results, Demo user found: {demo_found}",
                        f"Results: {[u.get('name', 'Unknown') for u in data[:5]]}"
                    )
                    return True
                else:
                    self.log_result(
                        "Search for Demo User", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Search for Demo User", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Search for Demo User", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_search_for_seeded_users(self):
        """Search for seeded users"""
        try:
            params = {'q': 'Priya'}  # Search for u1 (Priya Sharma)
            
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Search for Seeded Users", 
                        True, 
                        f"Search for 'Priya' returned {len(data)} results",
                        f"Results: {[u.get('name', 'Unknown') for u in data]}"
                    )
                    return True
                else:
                    self.log_result(
                        "Search for Seeded Users", 
                        False, 
                        "Search response is not a list",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Search for Seeded Users", 
                    False, 
                    f"User search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Search for Seeded Users", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_global_search_with_demo_user(self):
        """Test global search with demo user as currentUserId"""
        try:
            params = {
                'q': 'Priya',
                'currentUserId': self.demo_user_id
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data:
                    users = data['users']
                    
                    self.log_result(
                        "Global Search with Demo User", 
                        True, 
                        f"Global search returned {len(users)} users",
                        f"Search categories: {list(data.keys())}"
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
                        "Global Search with Demo User", 
                        False, 
                        "Global search response missing 'users' field",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Global Search with Demo User", 
                    False, 
                    f"Global search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Global Search with Demo User", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_friend_status_demo_to_u1(self):
        """Check friend status between demo user and u1"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/friend-status/u1")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                self.log_result(
                    "Friend Status (Demo -> u1)", 
                    True, 
                    f"Friend status: {status}",
                    f"Response: {data}"
                )
                return True
            else:
                self.log_result(
                    "Friend Status (Demo -> u1)", 
                    False, 
                    f"Friend status check failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Friend Status (Demo -> u1)", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all demo user tests"""
        print("=" * 80)
        print("DEMO USER FRIEND REQUEST AND SEARCH TESTING")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        # Seed data first
        try:
            self.session.post(f"{BACKEND_URL}/seed")
            print("✅ Seeded test data")
        except:
            print("⚠️  Could not seed data, continuing anyway")
        
        # Test demo user existence and functionality
        print("\n" + "=" * 50)
        print("DEMO USER VERIFICATION")
        print("=" * 50)
        
        self.test_demo_user_in_mongodb()
        
        # Friend Request Tests
        print("\n" + "=" * 50)
        print("FRIEND REQUEST TESTING")
        print("=" * 50)
        
        self.test_send_friend_request_to_u1()
        self.test_get_demo_friend_requests()
        self.test_demo_friends_list()
        self.test_friend_status_demo_to_u1()
        
        # Search Tests
        print("\n" + "=" * 50)
        print("SEARCH FUNCTIONALITY TESTING")
        print("=" * 50)
        
        self.test_search_for_demo_user()
        self.test_search_for_seeded_users()
        self.test_global_search_with_demo_user()
        
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
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print("\n" + "=" * 80)
        
        return self.test_results

if __name__ == "__main__":
    tester = DemoUserFriendTester()
    results = tester.run_all_tests()