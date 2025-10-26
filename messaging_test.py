#!/usr/bin/env python3
"""
Messaging Functionality Testing Suite
Focused testing of DM threads and messaging endpoints as requested in the review.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://tribe-messenger.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class MessagingTester:
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
        if details:
            print(f"   Details: {details}")
    
    def authenticate_demo_user(self):
        """Authenticate as demo user"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.demo_token = data.get('token')
                self.demo_user_id = data.get('user', {}).get('id', 'demo_user')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.demo_token}',
                    'Content-Type': 'application/json'
                })
                
                self.log_result(
                    "Demo User Authentication", 
                    True, 
                    f"Successfully authenticated as {data.get('user', {}).get('name', 'Demo User')}"
                )
                return True
            else:
                self.log_result(
                    "Demo User Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Demo User Authentication", 
                False, 
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_get_dm_threads(self):
        """Test 1: GET /api/dm/threads?userId=demo_user - Get DM threads"""
        try:
            params = {"userId": self.demo_user_id}
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                threads = []
                if isinstance(data, list):
                    threads = data
                elif isinstance(data, dict):
                    if 'items' in data:
                        threads = data['items']
                    elif 'threads' in data:
                        threads = data['threads']
                    else:
                        threads = [data] if data else []
                
                self.log_result(
                    "Get DM Threads", 
                    True, 
                    f"Successfully retrieved {len(threads)} DM threads",
                    f"Threads: {[t.get('peer', {}).get('name', 'Unknown') for t in threads]}"
                )
                return threads
            else:
                self.log_result(
                    "Get DM Threads", 
                    False, 
                    f"Failed to get DM threads - Status {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Get DM Threads", 
                False, 
                f"Error getting DM threads: {str(e)}"
            )
            return []
    
    def test_get_thread_messages(self, thread_id):
        """Test 2: GET /api/dm/threads/{threadId}/messages - Get messages in a thread"""
        try:
            params = {"userId": self.demo_user_id}
            response = self.session.get(f"{BACKEND_URL}/dm/threads/{thread_id}/messages", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                messages = []
                if isinstance(data, list):
                    messages = data
                elif isinstance(data, dict):
                    if 'messages' in data:
                        messages = data['messages']
                    elif 'items' in data:
                        messages = data['items']
                
                self.log_result(
                    "Get Thread Messages", 
                    True, 
                    f"Successfully retrieved {len(messages)} messages from thread {thread_id}",
                    f"Recent messages: {[m.get('text', 'Media message')[:50] for m in messages[-3:]]}"
                )
                return messages
            else:
                self.log_result(
                    "Get Thread Messages", 
                    False, 
                    f"Failed to get messages - Status {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Get Thread Messages", 
                False, 
                f"Error getting thread messages: {str(e)}"
            )
            return []
    
    def test_send_message(self, thread_id):
        """Test 3: POST /api/dm/threads/{threadId}/messages - Send a message"""
        try:
            test_message = f"Test message from messaging test - {datetime.now().strftime('%H:%M:%S')}"
            
            # Try body payload format first
            payload = {
                "text": test_message
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/threads/{thread_id}/messages", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('id')
                
                self.log_result(
                    "Send Message", 
                    True, 
                    f"Successfully sent message to thread {thread_id}",
                    f"Message ID: {message_id}, Text: {test_message}"
                )
                return message_id
            else:
                # Try query parameter format as fallback
                params = {"userId": self.demo_user_id}
                response = self.session.post(
                    f"{BACKEND_URL}/dm/threads/{thread_id}/messages", 
                    params=params,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get('id')
                    
                    self.log_result(
                        "Send Message", 
                        True, 
                        f"Successfully sent message to thread {thread_id} (with userId param)",
                        f"Message ID: {message_id}, Text: {test_message}"
                    )
                    return message_id
                else:
                    self.log_result(
                        "Send Message", 
                        False, 
                        f"Failed to send message - Status {response.status_code}",
                        response.text
                    )
                    return None
                
        except Exception as e:
            self.log_result(
                "Send Message", 
                False, 
                f"Error sending message: {str(e)}"
            )
            return None
    
    def test_create_dm_thread(self):
        """Test 4: POST /api/dm/threads - Create a new DM thread between two users"""
        return self.test_create_dm_thread_between_users(self.demo_user_id, "u1")
    
    def test_create_dm_thread_between_users(self, user1_id, user2_id):
        """Create DM thread between specific users"""
        try:
            # Try to create thread between specified users
            payload = {
                "user1Id": user1_id,
                "user2Id": user2_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/threads", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                thread_id = data.get('id')
                
                self.log_result(
                    "Create DM Thread", 
                    True, 
                    f"Successfully created DM thread between {user1_id} and {user2_id}",
                    f"Thread ID: {thread_id}"
                )
                return thread_id
            elif response.status_code == 400:
                # Thread might already exist
                error_data = response.json()
                if "already exists" in error_data.get('detail', '').lower():
                    self.log_result(
                        "Create DM Thread", 
                        True, 
                        "DM thread already exists between users (expected behavior)",
                        f"Response: {error_data.get('detail')}"
                    )
                    return "existing"
                else:
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        f"Failed to create DM thread - Status {response.status_code}",
                        response.text
                    )
                    return None
            else:
                # Try alternative endpoint format
                params = {"userId": user1_id, "peerUserId": user2_id}
                response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    thread_id = data.get('id')
                    
                    self.log_result(
                        "Create DM Thread", 
                        True, 
                        f"Successfully created DM thread using alternative endpoint",
                        f"Thread ID: {thread_id}"
                    )
                    return thread_id
                else:
                    self.log_result(
                        "Create DM Thread", 
                        False, 
                        f"Failed to create DM thread - Status {response.status_code}",
                        response.text
                    )
                    return None
                
        except Exception as e:
            self.log_result(
                "Create DM Thread", 
                False, 
                f"Error creating DM thread: {str(e)}"
            )
            return None
    
    def run_messaging_tests(self):
        """Run the complete messaging test sequence as requested"""
        print("=" * 80)
        print("MESSAGING FUNCTIONALITY TESTING - FOCUSED TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("=" * 80)
        print()
        
        # Step 0: Seed data to ensure we have users and friendships
        print("0. Seeding baseline data...")
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Seed Data", 
                    True, 
                    f"Successfully seeded data: {data.get('users', 0)} users, {data.get('messages', 0)} messages"
                )
            else:
                self.log_result("Seed Data", False, f"Seeding failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Seed Data", False, f"Seeding error: {str(e)}")
        
        # Step 1: Authenticate
        if not self.authenticate_demo_user():
            print("❌ Authentication failed - cannot proceed with messaging tests")
            return False
        
        print("\n🔍 MESSAGING TEST SEQUENCE:")
        print("-" * 50)
        
        # Test with seeded user u1 who has existing threads
        print("1. Getting DM threads for seeded user u1 (who has friends)...")
        original_user_id = self.demo_user_id
        self.demo_user_id = "u1"  # Switch to u1 for testing
        threads = self.test_get_dm_threads()
        
        if threads:
            # Step 3: If threads exist, get messages from first thread
            print(f"\n2. Found {len(threads)} threads - testing first thread...")
            first_thread = threads[0]
            thread_id = first_thread.get('id')
            peer_name = first_thread.get('peer', {}).get('name', 'Unknown')
            
            print(f"   Testing thread with {peer_name} (ID: {thread_id})")
            
            # Get messages from the thread
            messages = self.test_get_thread_messages(thread_id)
            
            # Step 4: Try to send a message to the existing thread
            print(f"\n3. Sending test message to existing thread...")
            message_id = self.test_send_message(thread_id)
            
            if message_id:
                # Verify the message was sent by getting messages again
                print(f"\n4. Verifying message was sent...")
                updated_messages = self.test_get_thread_messages(thread_id)
                
                if len(updated_messages) > len(messages):
                    self.log_result(
                        "Message Verification", 
                        True, 
                        f"Message successfully added to thread (was {len(messages)}, now {len(updated_messages)})"
                    )
                else:
                    self.log_result(
                        "Message Verification", 
                        False, 
                        f"Message count didn't increase (still {len(updated_messages)})"
                    )
        else:
            # Step 5: If no threads, try to create a new thread between u1 and u2
            print("\n2. No existing threads found - attempting to create new thread between u1 and u2...")
            # Switch to u2 for thread creation test
            self.demo_user_id = "u2"
            thread_id = self.test_create_dm_thread_between_users("u1", "u2")
            
            if thread_id and thread_id != "existing":
                print(f"\n3. Successfully created thread - testing messaging...")
                self.test_send_message(thread_id)
                self.test_get_thread_messages(thread_id)
        
        # Test with demo_user as well
        print(f"\n5. Testing DM threads for original demo_user...")
        self.demo_user_id = original_user_id
        demo_threads = self.test_get_dm_threads()
        
        # Summary
        print("\n" + "=" * 80)
        print("MESSAGING TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if total - passed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        return success_rate == 100.0

if __name__ == "__main__":
    tester = MessagingTester()
    success = tester.run_messaging_tests()
    
    if success:
        print("✅ All messaging functionality tests passed!")
        exit(0)
    else:
        print("❌ Some messaging tests failed!")
        exit(1)