#!/usr/bin/env python3
"""
DM Threads Testing Script - Focused test for the DM threads listing fix
Tests the specific scenario requested in the review.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"

class DMThreadsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.friend_request_id = None
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
    
    def test_seed_data(self):
        """Step 1: Seed data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'users' in data:
                    self.log_result(
                        "Seed Data", 
                        True, 
                        f"Successfully seeded {data['users']} users",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Seed Data", 
                        False, 
                        "Seed response missing expected fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Seed Data", 
                    False, 
                    f"Seed failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Seed Data", False, f"Exception occurred: {str(e)}")
    
    def test_send_friend_request(self):
        """Step 2: Send friend request u2->u1"""
        try:
            params = {
                'fromUserId': 'u2',
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friend-requests", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'requestId' in data:
                    self.friend_request_id = data['requestId']
                    self.log_result(
                        "Send Friend Request u2->u1", 
                        True, 
                        f"Successfully sent friend request: {data['requestId']}",
                        f"Status: {data.get('status', 'pending')}"
                    )
                else:
                    self.log_result(
                        "Send Friend Request u2->u1", 
                        False, 
                        "Friend request response missing requestId",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # Check if already friends or request exists
                data = response.json()
                detail = data.get('detail', '').lower()
                if "already friends" in detail:
                    self.log_result(
                        "Send Friend Request u2->u1", 
                        True, 
                        "Users are already friends (acceptable)",
                        f"Response: {data}"
                    )
                elif "already sent" in detail:
                    # Get existing request ID
                    get_response = self.session.get(f"{BACKEND_URL}/friend-requests", params={'userId': 'u1'})
                    if get_response.status_code == 200:
                        requests_data = get_response.json()
                        if isinstance(requests_data, list):
                            for req in requests_data:
                                if req.get('fromUserId') == 'u2' and req.get('toUserId') == 'u1':
                                    self.friend_request_id = req['id']
                                    self.log_result(
                                        "Send Friend Request u2->u1", 
                                        True, 
                                        f"Using existing friend request: {req['id']}",
                                        f"Status: {req['status']}"
                                    )
                                    return
                    self.log_result(
                        "Send Friend Request u2->u1", 
                        False, 
                        "Friend request already exists but couldn't retrieve ID",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Send Friend Request u2->u1", 
                        False, 
                        f"Friend request failed: {detail}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Send Friend Request u2->u1", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send Friend Request u2->u1", False, f"Exception occurred: {str(e)}")
    
    def test_accept_friend_request(self):
        """Step 3: Accept friend request"""
        # First check if already friends
        try:
            friends_response = self.session.get(f"{BACKEND_URL}/friends/list", params={'userId': 'u1'})
            if friends_response.status_code == 200:
                friends_data = friends_response.json()
                if 'items' in friends_data:
                    friend_ids = [friend.get('user', {}).get('id') for friend in friends_data['items']]
                    if 'u2' in friend_ids:
                        self.log_result(
                            "Accept Friend Request", 
                            True, 
                            "Friend request already accepted (users are friends)",
                            "Friendship already established"
                        )
                        return
        except:
            pass
            
        if not self.friend_request_id:
            self.log_result("Accept Friend Request", False, "Skipped - no friend request ID available")
            return
            
        try:
            response = self.session.post(f"{BACKEND_URL}/friend-requests/{self.friend_request_id}/accept")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Accept Friend Request", 
                    True, 
                    f"Successfully accepted friend request",
                    f"Response: {data}"
                )
            elif response.status_code == 400:
                data = response.json()
                if "already" in data.get('detail', '').lower():
                    self.log_result(
                        "Accept Friend Request", 
                        True, 
                        "Friend request already accepted",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Accept Friend Request", 
                        False, 
                        f"Accept failed: {data.get('detail', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Accept Friend Request", 
                    False, 
                    f"Accept failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_dm_threads_listing(self):
        """Step 4: Verify GET /api/dm/threads?userId=u1 returns 200 with items array and u2 thread"""
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'items' in data and isinstance(data['items'], list):
                    threads = data['items']
                    self.log_result(
                        "DM Threads Listing - Structure", 
                        True, 
                        f"GET /api/dm/threads returned 200 with items array ({len(threads)} threads)",
                        f"Response structure: {list(data.keys())}"
                    )
                    
                    # Look for thread with u2
                    u2_thread = None
                    for thread in threads:
                        if 'peer' in thread and thread['peer'].get('id') == 'u2':
                            u2_thread = thread
                            break
                    
                    if u2_thread:
                        self.dm_thread_id = u2_thread.get('id')
                        self.log_result(
                            "DM Threads Listing - u2 Thread", 
                            True, 
                            f"Found thread with u2: {u2_thread['peer'].get('name', 'Unknown')}",
                            f"Thread ID: {self.dm_thread_id}"
                        )
                    else:
                        self.log_result(
                            "DM Threads Listing - u2 Thread", 
                            False, 
                            "No thread found where peer.id === 'u2'",
                            f"Available peer IDs: {[t.get('peer', {}).get('id') for t in threads]}"
                        )
                elif isinstance(data, list):
                    # Handle direct list response
                    threads = data
                    self.log_result(
                        "DM Threads Listing - Structure", 
                        True, 
                        f"GET /api/dm/threads returned 200 with direct array ({len(threads)} threads)",
                        "Response is direct array"
                    )
                    
                    # Look for thread with u2
                    u2_thread = None
                    for thread in threads:
                        if 'peer' in thread and thread['peer'].get('id') == 'u2':
                            u2_thread = thread
                            break
                    
                    if u2_thread:
                        self.dm_thread_id = u2_thread.get('id')
                        self.log_result(
                            "DM Threads Listing - u2 Thread", 
                            True, 
                            f"Found thread with u2: {u2_thread['peer'].get('name', 'Unknown')}",
                            f"Thread ID: {self.dm_thread_id}"
                        )
                    else:
                        self.log_result(
                            "DM Threads Listing - u2 Thread", 
                            False, 
                            "No thread found where peer.id === 'u2'",
                            f"Available peer IDs: {[t.get('peer', {}).get('id') for t in threads]}"
                        )
                else:
                    self.log_result(
                        "DM Threads Listing - Structure", 
                        False, 
                        "Response structure unexpected (not items array or direct array)",
                        f"Response: {data}"
                    )
            elif response.status_code == 500:
                self.log_result(
                    "DM Threads Listing - 500 Error", 
                    False, 
                    "GET /api/dm/threads still returns 500 error - backend bug not fixed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "DM Threads Listing", 
                    False, 
                    f"GET /api/dm/threads failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Threads Listing", False, f"Exception occurred: {str(e)}")
    
    def test_send_hello_again_message(self):
        """Step 5: Send 'hello-again' message to the thread"""
        if not self.dm_thread_id:
            self.log_result("Send hello-again Message", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {
                'userId': 'u1',
                'text': 'hello-again'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                                       params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'messageId' in data or 'id' in data:
                    message_id = data.get('messageId') or data.get('id')
                    self.log_result(
                        "Send hello-again Message", 
                        True, 
                        f"Successfully sent 'hello-again' message",
                        f"Message ID: {message_id}, Thread: {self.dm_thread_id}"
                    )
                else:
                    self.log_result(
                        "Send hello-again Message", 
                        False, 
                        "Message response missing ID field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Send hello-again Message", 
                    False, 
                    f"Send message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send hello-again Message", False, f"Exception occurred: {str(e)}")
    
    def test_verify_hello_again_message(self):
        """Step 6: Verify GET messages returns the 'hello-again' message"""
        if not self.dm_thread_id:
            self.log_result("Verify hello-again Message", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                                      params=params)
            
            if response.status_code == 200:
                data = response.json()
                messages = []
                
                if 'items' in data and isinstance(data['items'], list):
                    messages = data['items']
                elif isinstance(data, list):
                    messages = data
                
                # Look for the "hello-again" message
                hello_again_messages = [msg for msg in messages if msg.get('text') == 'hello-again']
                if hello_again_messages:
                    msg = hello_again_messages[0]
                    self.log_result(
                        "Verify hello-again Message", 
                        True, 
                        f"Found 'hello-again' message in thread",
                        f"Message ID: {msg.get('id')}, Sender: {msg.get('senderId')}, Text: '{msg.get('text')}'"
                    )
                else:
                    # Show all messages for debugging
                    message_texts = [msg.get('text', 'No text') for msg in messages]
                    self.log_result(
                        "Verify hello-again Message", 
                        False, 
                        f"'hello-again' message not found in {len(messages)} messages",
                        f"Available messages: {message_texts}"
                    )
            else:
                self.log_result(
                    "Verify hello-again Message", 
                    False, 
                    f"Get messages failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Verify hello-again Message", False, f"Exception occurred: {str(e)}")
    
    def test_no_500_errors_final_check(self):
        """Step 7: Final check - confirm no 500 errors on /api/dm/threads"""
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                self.log_result(
                    "Final 500 Error Check", 
                    True, 
                    "GET /api/dm/threads returns 200 - no 500 errors",
                    f"Status: {response.status_code}"
                )
            elif response.status_code == 500:
                self.log_result(
                    "Final 500 Error Check", 
                    False, 
                    "GET /api/dm/threads still returns 500 error - backend bug persists",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Final 500 Error Check", 
                    False, 
                    f"GET /api/dm/threads returns unexpected status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Final 500 Error Check", False, f"Exception occurred: {str(e)}")
    
    def run_dm_threads_tests(self):
        """Run the specific DM threads tests as requested"""
        print("=" * 70)
        print("DM THREADS LISTING FIX - FOCUSED TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing scenario: u2->u1 friend request, accept, verify DM threads listing")
        print("=" * 70)
        
        # Run the specific test sequence
        print("\n📋 STEP 1: SEED DATA")
        print("-" * 40)
        self.test_seed_data()
        
        print("\n👥 STEP 2: SEND FRIEND REQUEST u2->u1")
        print("-" * 40)
        self.test_send_friend_request()
        
        print("\n✅ STEP 3: ACCEPT FRIEND REQUEST")
        print("-" * 40)
        self.test_accept_friend_request()
        
        print("\n💬 STEP 4: VERIFY DM THREADS LISTING")
        print("-" * 40)
        self.test_dm_threads_listing()
        
        print("\n📝 STEP 5: SEND 'hello-again' MESSAGE")
        print("-" * 40)
        self.test_send_hello_again_message()
        
        print("\n🔍 STEP 6: VERIFY MESSAGE RETRIEVAL")
        print("-" * 40)
        self.test_verify_hello_again_message()
        
        print("\n🚫 STEP 7: FINAL 500 ERROR CHECK")
        print("-" * 40)
        self.test_no_500_errors_final_check()
        
        # Summary
        print("\n" + "=" * 70)
        print("DM THREADS TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 70)
        return passed == total

def main():
    """Main test runner"""
    tester = DMThreadsTester()
    success = tester.run_dm_threads_tests()
    
    if success:
        print("🎉 All DM threads tests passed!")
        return 0
    else:
        print("⚠️  Some DM threads tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())