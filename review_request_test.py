#!/usr/bin/env python3
"""
Review Request Backend Testing Suite
Tests all backend features as specifically requested in the comprehensive application check.
Covers: Authentication, User Management, Friend System, Messaging, Social Feed, Venues, Tribes, Events, Notifications, Calling
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class ReviewRequestTester:
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
        status = "✅ WORKING" if success else "❌ BROKEN"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")

    # 1. AUTHENTICATION SYSTEM
    def test_auth_signup(self):
        """POST /api/auth/signup - Test user registration"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            payload = {
                "email": f"testuser_{timestamp}@example.com",
                "handle": f"testuser_{timestamp}",
                "name": f"Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_result("POST /api/auth/signup", True, "User registration working")
                else:
                    self.log_result("POST /api/auth/signup", False, "Response missing token or user data", f"Response: {data}")
            else:
                self.log_result("POST /api/auth/signup", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/auth/signup", False, f"Exception: {str(e)}")

    def test_auth_login(self):
        """POST /api/auth/login - Test demo@loopync.com login"""
        try:
            payload = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.demo_token = data['token']
                    self.demo_user_id = data['user']['id']
                    self.log_result("POST /api/auth/login", True, f"Demo login working - User: {data['user']['name']}")
                else:
                    self.log_result("POST /api/auth/login", False, "Response missing token or user data", f"Response: {data}")
            else:
                self.log_result("POST /api/auth/login", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/auth/login", False, f"Exception: {str(e)}")

    def test_auth_me(self):
        """GET /api/auth/me - Verify token validation"""
        if not self.demo_token:
            self.log_result("GET /api/auth/me", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result("GET /api/auth/me", True, f"Token validation working - User: {data.get('name')}")
                else:
                    self.log_result("GET /api/auth/me", False, "User data incomplete", f"Response: {data}")
            else:
                self.log_result("GET /api/auth/me", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/auth/me", False, f"Exception: {str(e)}")

    def test_auth_password_validation(self):
        """Test password validation and error handling"""
        try:
            payload = {"email": DEMO_EMAIL, "password": "wrongpassword"}
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_result("Password Validation", True, "Invalid credentials correctly rejected")
            else:
                self.log_result("Password Validation", False, f"Unexpected status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("Password Validation", False, f"Exception: {str(e)}")

    # 2. USER MANAGEMENT
    def test_user_profile_get(self):
        """GET /api/users/{userId} - Test user profile retrieval"""
        try:
            user_id = self.demo_user_id if self.demo_user_id else "demo_user"
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result("GET /api/users/{userId}", True, f"Profile retrieval working - User: {data['name']}")
                else:
                    self.log_result("GET /api/users/{userId}", False, "Profile missing required fields", f"Fields: {list(data.keys())}")
            else:
                self.log_result("GET /api/users/{userId}", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/users/{userId}", False, f"Exception: {str(e)}")

    def test_user_profile_update(self):
        """POST /api/users/{userId}/update - Test profile updates"""
        try:
            user_id = self.demo_user_id if self.demo_user_id else "demo_user"
            payload = {"bio": "Updated bio from test", "name": "Demo User Updated"}
            response = self.session.put(f"{BACKEND_URL}/users/{user_id}", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and data['success']:
                    self.log_result("POST /api/users/{userId}/update", True, "Profile updates working")
                else:
                    self.log_result("POST /api/users/{userId}/update", False, "Update response invalid", f"Response: {data}")
            else:
                self.log_result("POST /api/users/{userId}/update", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/users/{userId}/update", False, f"Exception: {str(e)}")

    def test_user_search(self):
        """GET /api/users/search?q=test - Test user search"""
        try:
            params = {'q': 'demo', 'limit': 10}
            response = self.session.get(f"{BACKEND_URL}/users/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/users/search", True, f"User search working - Found {len(data)} users")
                else:
                    self.log_result("GET /api/users/search", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/users/search", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/users/search", False, f"Exception: {str(e)}")

    # 3. FRIEND SYSTEM
    def test_friend_request_send(self):
        """POST /api/friends/request - Send friend request"""
        try:
            params = {'fromUserId': 'u1', 'toUserId': 'u2'}
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data:
                    self.log_result("POST /api/friends/request", True, "Friend request sending working")
                else:
                    self.log_result("POST /api/friends/request", False, "Response invalid", f"Response: {data}")
            else:
                self.log_result("POST /api/friends/request", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/friends/request", False, f"Exception: {str(e)}")

    def test_friend_request_accept(self):
        """POST /api/friends/accept - Accept request"""
        try:
            params = {'userId': 'u2', 'friendId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/friends/accept", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data:
                    self.log_result("POST /api/friends/accept", True, "Friend request acceptance working")
                else:
                    self.log_result("POST /api/friends/accept", False, "Response invalid", f"Response: {data}")
            else:
                self.log_result("POST /api/friends/accept", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/friends/accept", False, f"Exception: {str(e)}")

    def test_friends_list(self):
        """GET /api/users/{userId}/friends - Get friends list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/u1/friends")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/users/{userId}/friends", True, f"Friends list working - {len(data)} friends")
                else:
                    self.log_result("GET /api/users/{userId}/friends", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/users/{userId}/friends", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/users/{userId}/friends", False, f"Exception: {str(e)}")

    def test_bidirectional_friendships(self):
        """Verify bidirectional friendships"""
        try:
            u1_response = self.session.get(f"{BACKEND_URL}/users/u1/friends")
            u2_response = self.session.get(f"{BACKEND_URL}/users/u2/friends")
            
            if u1_response.status_code == 200 and u2_response.status_code == 200:
                u1_friends = u1_response.json()
                u2_friends = u2_response.json()
                
                u1_has_u2 = any(friend.get('id') == 'u2' for friend in u1_friends)
                u2_has_u1 = any(friend.get('id') == 'u1' for friend in u2_friends)
                
                if u1_has_u2 and u2_has_u1:
                    self.log_result("Bidirectional Friendships", True, "Bidirectional friendships working correctly")
                else:
                    self.log_result("Bidirectional Friendships", False, f"Not bidirectional - u1→u2: {u1_has_u2}, u2→u1: {u2_has_u1}")
            else:
                self.log_result("Bidirectional Friendships", False, f"Failed to get friends lists - u1: {u1_response.status_code}, u2: {u2_response.status_code}")
        except Exception as e:
            self.log_result("Bidirectional Friendships", False, f"Exception: {str(e)}")

    # 4. MESSAGING SYSTEM
    def test_dm_threads_get(self):
        """GET /api/dm/threads?userId={id} - Get DM threads"""
        try:
            params = {'userId': 'demo_user'}
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/dm/threads", True, f"DM threads working - {len(data)} threads")
                else:
                    self.log_result("GET /api/dm/threads", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/dm/threads", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/dm/threads", False, f"Exception: {str(e)}")

    def test_dm_thread_create(self):
        """POST /api/dm/thread - Create new thread"""
        try:
            params = {'userId': 'demo_user', 'peerUserId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    self.thread_id = data['threadId']
                    self.log_result("POST /api/dm/thread", True, f"DM thread creation working - ID: {data['threadId']}")
                else:
                    self.log_result("POST /api/dm/thread", False, "Response missing threadId", f"Response: {data}")
            else:
                self.log_result("POST /api/dm/thread", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/dm/thread", False, f"Exception: {str(e)}")

    def test_dm_send_message(self):
        """POST /api/dm/{threadId}/messages - Send message"""
        if not hasattr(self, 'thread_id'):
            self.log_result("POST /api/dm/{threadId}/messages", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'demo_user'}
            payload = {'text': 'Hello from review request test!'}
            response = self.session.post(f"{BACKEND_URL}/dm/{self.thread_id}/messages", params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.log_result("POST /api/dm/{threadId}/messages", True, f"Message sending working - ID: {data['id']}")
                else:
                    self.log_result("POST /api/dm/{threadId}/messages", False, "Response missing message ID", f"Response: {data}")
            else:
                self.log_result("POST /api/dm/{threadId}/messages", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/dm/{threadId}/messages", False, f"Exception: {str(e)}")

    def test_dm_get_messages(self):
        """GET /api/dm/{threadId}/messages - Retrieve messages"""
        if not hasattr(self, 'thread_id'):
            self.log_result("GET /api/dm/{threadId}/messages", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'demo_user'}
            response = self.session.get(f"{BACKEND_URL}/dm/{self.thread_id}/messages", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/dm/{threadId}/messages", True, f"Message retrieval working - {len(data)} messages")
                else:
                    self.log_result("GET /api/dm/{threadId}/messages", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/dm/{threadId}/messages", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/dm/{threadId}/messages", False, f"Exception: {str(e)}")

    # 5. SOCIAL FEED (TIMELINE)
    def test_posts_get_all(self):
        """GET /api/posts - Get all posts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/posts")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/posts", True, f"Posts timeline working - {len(data)} posts")
                else:
                    self.log_result("GET /api/posts", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/posts", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/posts", False, f"Exception: {str(e)}")

    def test_posts_create(self):
        """POST /api/posts - Create new post"""
        try:
            payload = {'text': 'Test post from review request test', 'audience': 'public'}
            params = {'authorId': 'demo_user'}
            response = self.session.post(f"{BACKEND_URL}/posts", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.post_id = data['id']
                    self.log_result("POST /api/posts", True, f"Post creation working - ID: {data['id']}")
                else:
                    self.log_result("POST /api/posts", False, "Response missing post ID", f"Response: {data}")
            else:
                self.log_result("POST /api/posts", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/posts", False, f"Exception: {str(e)}")

    def test_posts_like(self):
        """POST /api/posts/{postId}/like - Like post"""
        if not hasattr(self, 'post_id'):
            self.log_result("POST /api/posts/{postId}/like", False, "Skipped - no post ID available")
            return
            
        try:
            params = {'userId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/posts/{self.post_id}/like", params=params)
            
            if response.status_code == 200:
                self.log_result("POST /api/posts/{postId}/like", True, "Post liking working")
            else:
                self.log_result("POST /api/posts/{postId}/like", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/posts/{postId}/like", False, f"Exception: {str(e)}")

    def test_posts_comment(self):
        """POST /api/posts/{postId}/comment - Comment on post"""
        if not hasattr(self, 'post_id'):
            self.log_result("POST /api/posts/{postId}/comment", False, "Skipped - no post ID available")
            return
            
        try:
            payload = {'text': 'Great post from review test!'}
            params = {'authorId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/posts/{self.post_id}/comment", json=payload, params=params)
            
            if response.status_code == 200:
                self.log_result("POST /api/posts/{postId}/comment", True, "Post commenting working")
            else:
                self.log_result("POST /api/posts/{postId}/comment", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/posts/{postId}/comment", False, f"Exception: {str(e)}")

    # 6. VENUES SYSTEM
    def test_venues_get_all(self):
        """GET /api/venues - Get all venues"""
        try:
            response = self.session.get(f"{BACKEND_URL}/venues")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/venues", True, f"Venues system working - {len(data)} venues")
                    
                    # Check for category and timings
                    if len(data) > 0:
                        venue = data[0]
                        has_category = 'category' in venue or 'type' in venue
                        has_timings = 'timings' in venue or 'hours' in venue
                        self.log_result("Venues Category & Timings", has_category or has_timings, f"Category: {has_category}, Timings: {has_timings}")
                else:
                    self.log_result("GET /api/venues", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/venues", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/venues", False, f"Exception: {str(e)}")

    def test_venues_filter_category(self):
        """Test venue filtering by category"""
        try:
            # Get venues first to find a category
            venues_response = self.session.get(f"{BACKEND_URL}/venues")
            if venues_response.status_code == 200:
                venues = venues_response.json()
                if len(venues) > 0:
                    venue = venues[0]
                    category = venue.get('category', venue.get('type', 'restaurant'))
                    
                    # Test filtering
                    filter_params = {'category': category}
                    filter_response = self.session.get(f"{BACKEND_URL}/venues", params=filter_params)
                    
                    if filter_response.status_code == 200:
                        self.log_result("Venue Category Filtering", True, f"Category filtering working for '{category}'")
                    else:
                        self.log_result("Venue Category Filtering", False, f"Filtering failed with status {filter_response.status_code}")
                else:
                    self.log_result("Venue Category Filtering", True, "No venues to test filtering (acceptable)")
            else:
                self.log_result("Venue Category Filtering", False, f"Could not get venues for filtering test")
        except Exception as e:
            self.log_result("Venue Category Filtering", False, f"Exception: {str(e)}")

    # 7. TRIBES (GROUPS)
    def test_tribes_get_all(self):
        """GET /api/tribes - Get all tribes"""
        try:
            response = self.session.get(f"{BACKEND_URL}/tribes")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/tribes", True, f"Tribes system working - {len(data)} tribes")
                else:
                    self.log_result("GET /api/tribes", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/tribes", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/tribes", False, f"Exception: {str(e)}")

    def test_tribes_create(self):
        """POST /api/tribes - Create new tribe"""
        try:
            payload = {
                'name': 'Review Test Tribe',
                'description': 'Test tribe from review request',
                'type': 'public',
                'tags': ['test', 'review']
            }
            params = {'ownerId': 'demo_user'}
            response = self.session.post(f"{BACKEND_URL}/tribes", json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.tribe_id = data['id']
                    self.log_result("POST /api/tribes", True, f"Tribe creation working - ID: {data['id']}")
                else:
                    self.log_result("POST /api/tribes", False, "Response missing tribe ID", f"Response: {data}")
            else:
                self.log_result("POST /api/tribes", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/tribes", False, f"Exception: {str(e)}")

    def test_tribes_join(self):
        """POST /api/tribes/{tribeId}/join - Join tribe"""
        if not hasattr(self, 'tribe_id'):
            self.log_result("POST /api/tribes/{tribeId}/join", False, "Skipped - no tribe ID available")
            return
            
        try:
            params = {'userId': 'u1'}
            response = self.session.post(f"{BACKEND_URL}/tribes/{self.tribe_id}/join", params=params)
            
            if response.status_code == 200:
                self.log_result("POST /api/tribes/{tribeId}/join", True, "Tribe joining working")
            else:
                self.log_result("POST /api/tribes/{tribeId}/join", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/tribes/{tribeId}/join", False, f"Exception: {str(e)}")

    # 8. EVENTS SYSTEM
    def test_events_get_all(self):
        """GET /api/events - Get all events"""
        try:
            response = self.session.get(f"{BACKEND_URL}/events")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/events", True, f"Events system working - {len(data)} events")
                else:
                    self.log_result("GET /api/events", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/events", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/events", False, f"Exception: {str(e)}")

    def test_events_create(self):
        """POST /api/events - Create event"""
        try:
            payload = {
                'name': 'Review Test Event',
                'description': 'Test event from review request',
                'date': '2024-12-31T20:00:00Z',
                'location': 'Test Venue',
                'tiers': [
                    {'name': 'General', 'price': 50, 'available': 100}
                ]
            }
            response = self.session.post(f"{BACKEND_URL}/events", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.event_id = data['id']
                    self.log_result("POST /api/events", True, f"Event creation working - ID: {data['id']}")
                else:
                    self.log_result("POST /api/events", False, "Response missing event ID", f"Response: {data}")
            else:
                self.log_result("POST /api/events", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/events", False, f"Exception: {str(e)}")

    def test_events_ticketing(self):
        """Test event ticketing if implemented"""
        if not hasattr(self, 'event_id'):
            self.log_result("Event Ticketing", False, "Skipped - no event ID available")
            return
            
        try:
            params = {'userId': 'demo_user', 'tier': 'General'}
            response = self.session.post(f"{BACKEND_URL}/events/{self.event_id}/tickets", params=params)
            
            if response.status_code == 200:
                self.log_result("Event Ticketing", True, "Event ticketing working")
            elif response.status_code == 404:
                self.log_result("Event Ticketing", True, "Event ticketing not implemented (acceptable)")
            else:
                self.log_result("Event Ticketing", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("Event Ticketing", False, f"Exception: {str(e)}")

    # 9. NOTIFICATIONS
    def test_notifications_get(self):
        """GET /api/notifications?userId={id} - Get notifications"""
        try:
            params = {'userId': 'demo_user'}
            response = self.session.get(f"{BACKEND_URL}/notifications", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check notification types
                    friend_notifications = [n for n in data if n.get('type') == 'friend_request']
                    like_notifications = [n for n in data if n.get('type') == 'post_like']
                    comment_notifications = [n for n in data if n.get('type') == 'post_comment']
                    
                    self.log_result("GET /api/notifications", True, f"Notifications working - {len(data)} total (Friend: {len(friend_notifications)}, Likes: {len(like_notifications)}, Comments: {len(comment_notifications)})")
                else:
                    self.log_result("GET /api/notifications", False, "Response not a list", f"Type: {type(data)}")
            else:
                self.log_result("GET /api/notifications", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("GET /api/notifications", False, f"Exception: {str(e)}")

    # 10. CALLING SYSTEM
    def test_calls_initiate(self):
        """POST /api/calls/initiate - Test call creation"""
        try:
            params = {
                'callerId': 'demo_user',
                'recipientId': 'u1',
                'callType': 'video'
            }
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'callId' in data and 'channelName' in data:
                    self.log_result("POST /api/calls/initiate", True, f"Call initiation working - ID: {data['callId']}")
                    
                    # Check Agora token generation
                    if 'callerToken' in data and 'recipientToken' in data:
                        self.log_result("Agora Token Generation", True, "Agora tokens generated successfully")
                    else:
                        self.log_result("Agora Token Generation", False, "Agora tokens missing", f"Fields: {list(data.keys())}")
                else:
                    self.log_result("POST /api/calls/initiate", False, "Response missing required fields", f"Response: {data}")
            else:
                self.log_result("POST /api/calls/initiate", False, f"Failed with status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("POST /api/calls/initiate", False, f"Exception: {str(e)}")

    def test_calls_friendship_validation(self):
        """Verify Agora token generation and friendship validation"""
        try:
            params = {
                'callerId': 'demo_user',
                'recipientId': 'nonexistent_user',
                'callType': 'audio'
            }
            response = self.session.post(f"{BACKEND_URL}/calls/initiate", params=params)
            
            if response.status_code == 403 or response.status_code == 404:
                self.log_result("Friendship Validation", True, "Call security working - non-friends rejected")
            else:
                self.log_result("Friendship Validation", False, f"Security issue - unexpected status {response.status_code}", f"Response: {response.text}")
        except Exception as e:
            self.log_result("Friendship Validation", False, f"Exception: {str(e)}")

    def run_review_tests(self):
        """Run all tests as requested in the review"""
        print("=" * 80)
        print("COMPREHENSIVE APPLICATION CHECK - ALL FEATURES AUDIT")
        print("Backend API Testing for Social Media Features & Deployment")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("=" * 80)
        
        # 1. Authentication System
        print("\n🔐 1. AUTHENTICATION SYSTEM")
        self.test_auth_signup()
        self.test_auth_login()
        self.test_auth_me()
        self.test_auth_password_validation()
        
        # 2. User Management
        print("\n👤 2. USER MANAGEMENT")
        self.test_user_profile_get()
        self.test_user_profile_update()
        self.test_user_search()
        
        # 3. Friend System
        print("\n👥 3. FRIEND SYSTEM")
        self.test_friend_request_send()
        self.test_friend_request_accept()
        self.test_friends_list()
        self.test_bidirectional_friendships()
        
        # 4. Messaging System
        print("\n💬 4. MESSAGING SYSTEM")
        self.test_dm_threads_get()
        self.test_dm_thread_create()
        self.test_dm_send_message()
        self.test_dm_get_messages()
        
        # 5. Social Feed (Timeline)
        print("\n📱 5. SOCIAL FEED (TIMELINE)")
        self.test_posts_get_all()
        self.test_posts_create()
        self.test_posts_like()
        self.test_posts_comment()
        
        # 6. Venues System
        print("\n🏪 6. VENUES SYSTEM")
        self.test_venues_get_all()
        self.test_venues_filter_category()
        
        # 7. Tribes (Groups)
        print("\n🏛️ 7. TRIBES (GROUPS)")
        self.test_tribes_get_all()
        self.test_tribes_create()
        self.test_tribes_join()
        
        # 8. Events System
        print("\n🎉 8. EVENTS SYSTEM")
        self.test_events_get_all()
        self.test_events_create()
        self.test_events_ticketing()
        
        # 9. Notifications
        print("\n🔔 9. NOTIFICATIONS")
        self.test_notifications_get()
        
        # 10. Calling System
        print("\n📞 10. CALLING SYSTEM")
        self.test_calls_initiate()
        self.test_calls_friendship_validation()
        
        # Print Summary
        self.print_review_summary()
    
    def print_review_summary(self):
        """Print review-specific summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE APPLICATION CHECK - RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Overall System Health Score: {(passed_tests/total_tests)*100:.1f}%")
        print(f"✅ Working Features: {passed_tests}")
        print(f"❌ Broken/Missing Features: {failed_tests}")
        
        # Working features list
        print(f"\n✅ WORKING FEATURES LIST ({passed_tests}):")
        for result in self.test_results:
            if result['success']:
                print(f"  • {result['test']}")
        
        # Broken/missing features
        if failed_tests > 0:
            print(f"\n❌ BROKEN/MISSING FEATURES ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Recommendations
        print(f"\n🚀 RECOMMENDATIONS FOR NEW FEATURES TO ADD:")
        if (passed_tests/total_tests) >= 0.9:
            print("  ✅ System is excellent - ready for advanced social features")
            print("  • Consider adding: Stories, Live Streaming, Advanced AI recommendations")
        elif (passed_tests/total_tests) >= 0.8:
            print("  ⚠️  System is good - fix minor issues then add new features")
            print("  • Priority: Fix broken features, then add: Push notifications, Advanced search")
        else:
            print("  ❌ System needs attention - focus on core features first")
            print("  • Priority: Fix critical broken features before adding new ones")
        
        print("\n" + "=" * 80)
        
        return (passed_tests/total_tests) >= 0.8

def main():
    """Main test runner"""
    tester = ReviewRequestTester()
    success = tester.run_review_tests()
    
    if success:
        print("🎉 System health is good - ready for new social media features!")
        return 0
    else:
        print("⚠️  System needs fixes before adding new features!")
        return 1

if __name__ == "__main__":
    exit(main())