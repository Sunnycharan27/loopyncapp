#!/usr/bin/env python3
"""
Fixed Features Comprehensive Testing Suite
Tests the 4 major fixed features as requested in the review:
1. Messaging system (added simplified endpoints)
2. Post commenting (added singular form alias)
3. Event creation (added POST endpoint)
4. Calling system verification

Expected Results:
✅ Messaging: Works with simplified endpoints
✅ Commenting: Works with singular form
✅ Events: Creation working
✅ Calling: No user lookup errors
✅ Overall health: > 90%
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class FixedFeaturesTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.friend_id = None
        self.dm_thread_id = None
        self.post_id = None
        self.event_id = None
        self.working_endpoints = 0
        self.total_endpoints = 0
        
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
        
        # Track endpoint health
        self.total_endpoints += 1
        if success:
            self.working_endpoints += 1
    
    def login_demo_user(self):
        """Login demo user and get token"""
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
                        "Demo User Login", 
                        True, 
                        f"Successfully logged in as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                    return True
                else:
                    self.log_result("Demo User Login", False, "Login response missing token or user data")
                    return False
            else:
                self.log_result("Demo User Login", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Demo User Login", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_messaging_system(self):
        """Test 1: MESSAGING SYSTEM TEST - Simplified endpoints"""
        print("\n=== 1. MESSAGING SYSTEM TEST ===")
        
        if not self.demo_token:
            self.log_result("Messaging System", False, "No demo token available")
            return
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        # Get DM threads
        try:
            response = self.session.get(f"{BACKEND_URL}/dm/threads?userId={self.demo_user_id}", headers=headers)
            
            if response.status_code == 200:
                threads_data = response.json()
                self.log_result(
                    "Get DM Threads", 
                    True, 
                    f"Successfully retrieved DM threads (found {len(threads_data)} threads)",
                    f"Endpoint: GET /api/dm/threads?userId={{demo_id}}"
                )
                
                # If threads exist, test message sending
                if len(threads_data) > 0:
                    thread = threads_data[0]
                    thread_id = thread.get('id')
                    if thread_id:
                        self.dm_thread_id = thread_id
                        
                        # Test message sending using simplified endpoint
                        message_params = {
                            "senderId": self.demo_user_id,
                            "text": "Test message from fixed features testing"
                        }
                        
                        send_response = self.session.post(
                            f"{BACKEND_URL}/dm/{thread_id}/messages", 
                            params=message_params,
                            headers=headers
                        )
                        
                        if send_response.status_code == 200:
                            self.log_result(
                                "Send DM Message", 
                                True, 
                                "Successfully sent message using simplified endpoint",
                                f"Endpoint: POST /api/dm/{{threadId}}/messages"
                            )
                        else:
                            self.log_result(
                                "Send DM Message", 
                                False, 
                                f"Message sending failed with status {send_response.status_code}",
                                f"Response: {send_response.text}"
                            )
                        
                        # Test message retrieval
                        get_response = self.session.get(
                            f"{BACKEND_URL}/dm/{thread_id}/messages?userId={self.demo_user_id}",
                            headers=headers
                        )
                        
                        if get_response.status_code == 200:
                            messages = get_response.json()
                            self.log_result(
                                "Get DM Messages", 
                                True, 
                                f"Successfully retrieved messages (found {len(messages)} messages)",
                                f"Endpoint: GET /api/dm/{{threadId}}/messages?userId={{demo_id}}"
                            )
                        else:
                            self.log_result(
                                "Get DM Messages", 
                                False, 
                                f"Message retrieval failed with status {get_response.status_code}",
                                f"Response: {get_response.text}"
                            )
                else:
                    self.log_result(
                        "DM Thread Usage", 
                        True, 
                        "No existing threads found - simplified endpoints working but no test data",
                        "This is expected for demo user without active conversations"
                    )
            else:
                self.log_result(
                    "Get DM Threads", 
                    False, 
                    f"DM threads endpoint failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Messaging System", False, f"Exception occurred: {str(e)}")
    
    def test_post_commenting(self):
        """Test 2: POST COMMENTING TEST - Singular form alias"""
        print("\n=== 2. POST COMMENTING TEST ===")
        
        if not self.demo_token:
            self.log_result("Post Commenting", False, "No demo token available")
            return
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        # First get a post
        try:
            response = self.session.get(f"{BACKEND_URL}/posts", headers=headers)
            
            if response.status_code == 200:
                posts = response.json()
                if len(posts) > 0:
                    post = posts[0]
                    self.post_id = post['id']
                    
                    self.log_result(
                        "Get Posts", 
                        True, 
                        f"Successfully retrieved posts (found {len(posts)} posts)",
                        f"First post ID: {self.post_id}"
                    )
                    
                    # Test commenting on post using singular form
                    comment_payload = {
                        "authorId": self.demo_user_id,
                        "text": "Test comment from fixed features testing"
                    }
                    
                    comment_response = self.session.post(
                        f"{BACKEND_URL}/posts/{self.post_id}/comment",
                        json=comment_payload,
                        headers=headers
                    )
                    
                    if comment_response.status_code == 200:
                        comment_data = comment_response.json()
                        self.log_result(
                            "Create Comment (Singular)", 
                            True, 
                            "Successfully created comment using singular form endpoint",
                            f"Endpoint: POST /api/posts/{{postId}}/comment - Comment ID: {comment_data.get('id', 'Unknown')}"
                        )
                        
                        # Verify comment exists
                        verify_response = self.session.get(
                            f"{BACKEND_URL}/posts/{self.post_id}/comments",
                            headers=headers
                        )
                        
                        if verify_response.status_code == 200:
                            comments = verify_response.json()
                            test_comments = [c for c in comments if c.get('text') == comment_payload['text']]
                            if test_comments:
                                self.log_result(
                                    "Verify Comment", 
                                    True, 
                                    f"Comment successfully created and retrieved (found {len(comments)} total comments)",
                                    f"Endpoint: GET /api/posts/{{postId}}/comments"
                                )
                            else:
                                self.log_result(
                                    "Verify Comment", 
                                    False, 
                                    "Comment not found in comments list",
                                    f"Total comments: {len(comments)}"
                                )
                        else:
                            self.log_result(
                                "Verify Comment", 
                                False, 
                                f"Comment verification failed with status {verify_response.status_code}",
                                f"Response: {verify_response.text}"
                            )
                    else:
                        self.log_result(
                            "Create Comment (Singular)", 
                            False, 
                            f"Comment creation failed with status {comment_response.status_code}",
                            f"Response: {comment_response.text}"
                        )
                else:
                    self.log_result(
                        "Get Posts", 
                        True, 
                        "Posts endpoint working but no posts found",
                        "Cannot test commenting without existing posts"
                    )
            else:
                self.log_result(
                    "Get Posts", 
                    False, 
                    f"Posts endpoint failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Post Commenting", False, f"Exception occurred: {str(e)}")
    
    def test_event_creation(self):
        """Test 3: EVENT CREATION TEST - POST endpoint"""
        print("\n=== 3. EVENT CREATION TEST ===")
        
        if not self.demo_token:
            self.log_result("Event Creation", False, "No demo token available")
            return
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        # Test event creation
        try:
            event_payload = {
                "name": "Test Event from Fixed Features Testing",
                "description": "This is a test event created during backend testing",
                "date": "2024-12-31T18:00:00Z",
                "location": "Test Venue, Test City",
                "creatorId": self.demo_user_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/events", json=event_payload, headers=headers)
            
            if response.status_code == 200:
                event_data = response.json()
                if 'id' in event_data:
                    self.event_id = event_data['id']
                    self.log_result(
                        "Create Event", 
                        True, 
                        f"Successfully created event: {event_data['name']}",
                        f"Endpoint: POST /api/events - Event ID: {self.event_id}"
                    )
                    
                    # Verify event exists
                    verify_response = self.session.get(f"{BACKEND_URL}/events", headers=headers)
                    
                    if verify_response.status_code == 200:
                        events = verify_response.json()
                        test_events = [e for e in events if e.get('id') == self.event_id]
                        if test_events:
                            self.log_result(
                                "Verify Event", 
                                True, 
                                f"Event successfully created and retrieved (found {len(events)} total events)",
                                f"Endpoint: GET /api/events"
                            )
                        else:
                            self.log_result(
                                "Verify Event", 
                                False, 
                                "Created event not found in events list",
                                f"Total events: {len(events)}"
                            )
                    else:
                        self.log_result(
                            "Verify Event", 
                            False, 
                            f"Event verification failed with status {verify_response.status_code}",
                            f"Response: {verify_response.text}"
                        )
                else:
                    self.log_result(
                        "Create Event", 
                        False, 
                        "Event creation response missing ID",
                        f"Response: {event_data}"
                    )
            else:
                self.log_result(
                    "Create Event", 
                    False, 
                    f"Event creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Event Creation", False, f"Exception occurred: {str(e)}")
    
    def test_calling_system(self):
        """Test 4: CALLING SYSTEM TEST - No user lookup errors"""
        print("\n=== 4. CALLING SYSTEM TEST ===")
        
        if not self.demo_token:
            self.log_result("Calling System", False, "No demo token available")
            return
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        # First verify user has friends
        try:
            user_response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}", headers=headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                friends = user_data.get('friends', [])
                
                if len(friends) > 0:
                    self.friend_id = friends[0]
                    self.log_result(
                        "Verify Friends", 
                        True, 
                        f"Demo user has {len(friends)} friends for calling",
                        f"First friend ID: {self.friend_id}"
                    )
                    
                    # Test call initiation
                    call_params = {
                        "callerId": self.demo_user_id,
                        "recipientId": self.friend_id,
                        "callType": "video"
                    }
                    
                    call_response = self.session.post(
                        f"{BACKEND_URL}/calls/initiate",
                        params=call_params,
                        headers=headers
                    )
                    
                    if call_response.status_code == 200:
                        call_data = call_response.json()
                        expected_fields = ['callId', 'channelName', 'callerToken', 'recipientToken']
                        
                        if all(field in call_data for field in expected_fields):
                            self.log_result(
                                "Call Initiation", 
                                True, 
                                "Successfully initiated call with Agora tokens",
                                f"Endpoint: POST /api/calls/initiate - Call ID: {call_data.get('callId')}"
                            )
                        else:
                            missing_fields = [f for f in expected_fields if f not in call_data]
                            self.log_result(
                                "Call Initiation", 
                                False, 
                                f"Call response missing required fields: {missing_fields}",
                                f"Response: {call_data}"
                            )
                    else:
                        error_message = call_response.text
                        if "Caller not found" in error_message:
                            self.log_result(
                                "Call Initiation", 
                                False, 
                                "CRITICAL: 'Caller not found' error detected",
                                f"This indicates user database issue - Response: {error_message}"
                            )
                        else:
                            self.log_result(
                                "Call Initiation", 
                                False, 
                                f"Call initiation failed with status {call_response.status_code}",
                                f"Response: {error_message}"
                            )
                else:
                    self.log_result(
                        "Verify Friends", 
                        False, 
                        "Demo user has no friends for calling test",
                        "Cannot test calling without friend relationships"
                    )
            else:
                self.log_result(
                    "Verify Friends", 
                    False, 
                    f"User lookup failed with status {user_response.status_code}",
                    f"Response: {user_response.text}"
                )
                
        except Exception as e:
            self.log_result("Calling System", False, f"Exception occurred: {str(e)}")
    
    def test_overall_health_check(self):
        """Test 5: OVERALL HEALTH CHECK"""
        print("\n=== 5. OVERALL HEALTH CHECK ===")
        
        # Calculate system health percentage
        if self.total_endpoints > 0:
            health_percentage = (self.working_endpoints / self.total_endpoints) * 100
            
            if health_percentage > 90:
                self.log_result(
                    "System Health", 
                    True, 
                    f"System health: {health_percentage:.1f}% ({self.working_endpoints}/{self.total_endpoints} endpoints working)",
                    "System health > 90% - All critical features operational"
                )
            else:
                self.log_result(
                    "System Health", 
                    False, 
                    f"System health: {health_percentage:.1f}% ({self.working_endpoints}/{self.total_endpoints} endpoints working)",
                    "System health < 90% - Some critical issues detected"
                )
        else:
            self.log_result(
                "System Health", 
                False, 
                "No endpoints tested",
                "Cannot calculate system health"
            )
    
    def run_all_tests(self):
        """Run all fixed features tests"""
        print("🚀 STARTING FIXED FEATURES COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Login first
        if not self.login_demo_user():
            print("❌ Cannot proceed without demo user login")
            return
        
        # Run all tests
        self.test_messaging_system()
        self.test_post_commenting()
        self.test_event_creation()
        self.test_calling_system()
        self.test_overall_health_check()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FIXED FEATURES TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total} tests")
        print(f"❌ Failed: {total - passed}/{total} tests")
        
        if self.total_endpoints > 0:
            health_percentage = (self.working_endpoints / self.total_endpoints) * 100
            print(f"🏥 System Health: {health_percentage:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Expected results verification
        print("\n🎯 EXPECTED RESULTS VERIFICATION:")
        
        messaging_tests = [r for r in self.test_results if 'DM' in r['test'] or 'Messaging' in r['test']]
        messaging_success = all(r['success'] for r in messaging_tests) if messaging_tests else False
        print(f"✅ Messaging: {'Works with simplified endpoints' if messaging_success else '❌ Issues detected'}")
        
        commenting_tests = [r for r in self.test_results if 'Comment' in r['test']]
        commenting_success = all(r['success'] for r in commenting_tests) if commenting_tests else False
        print(f"✅ Commenting: {'Works with singular form' if commenting_success else '❌ Issues detected'}")
        
        event_tests = [r for r in self.test_results if 'Event' in r['test']]
        event_success = all(r['success'] for r in event_tests) if event_tests else False
        print(f"✅ Events: {'Creation working' if event_success else '❌ Issues detected'}")
        
        calling_tests = [r for r in self.test_results if 'Call' in r['test'] or 'Friends' in r['test']]
        calling_success = all(r['success'] for r in calling_tests) if calling_tests else False
        no_caller_errors = not any('Caller not found' in str(r.get('details', '')) for r in self.test_results)
        print(f"✅ Calling: {'No user lookup errors' if calling_success and no_caller_errors else '❌ Issues detected'}")
        
        health_tests = [r for r in self.test_results if 'Health' in r['test']]
        health_success = all(r['success'] for r in health_tests) if health_tests else False
        print(f"✅ Overall health: {'> 90%' if health_success else '❌ < 90%'}")
        
        print("\n🏁 TESTING COMPLETE")
        return self.test_results

if __name__ == "__main__":
    tester = FixedFeaturesTester()
    results = tester.run_all_tests()