#!/usr/bin/env python3
"""
DM Send/Receive Regression Test
Tests the specific DM functionality post-fix with body payload changes.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

class DMRegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.thread_id = None
        
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
    
    def test_1_seed_data(self):
        """Step 1: Ensure seed data exists"""
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data and data['users'] >= 2:
                    self.log_result(
                        "1. Seed Data", 
                        True, 
                        f"Successfully seeded {data['users']} users",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "1. Seed Data", 
                        False, 
                        "Seed data incomplete",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "1. Seed Data", 
                    False, 
                    f"Seed failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("1. Seed Data", False, f"Exception occurred: {str(e)}")
    
    def test_2_send_friend_request(self):
        """Step 2: Send friend request from u2 to u1"""
        try:
            params = {
                'fromUserId': 'u2',
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friend-requests", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "2. Send Friend Request", 
                    True, 
                    "Friend request sent successfully (or already exists)",
                    f"Response: {data}"
                )
            elif response.status_code == 400:
                data = response.json()
                detail = data.get('detail', '').lower()
                if "already" in detail:
                    self.log_result(
                        "2. Send Friend Request", 
                        True, 
                        "Friend request already exists or users already friends",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "2. Send Friend Request", 
                        False, 
                        f"Friend request failed: {data.get('detail', 'Unknown error')}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "2. Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("2. Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_3_accept_friend_request(self):
        """Step 3: Accept friend request (idempotent)"""
        try:
            # First get the friend request ID
            get_response = self.session.get(f"{BACKEND_URL}/friend-requests", params={'userId': 'u1'})
            
            if get_response.status_code == 200:
                requests_data = get_response.json()
                if isinstance(requests_data, list) and len(requests_data) > 0:
                    # Find request from u2 to u1
                    u2_request = None
                    for req in requests_data:
                        if req.get('fromUserId') == 'u2' and req.get('toUserId') == 'u1':
                            u2_request = req
                            break
                    
                    if u2_request:
                        request_id = u2_request['id']
                        
                        # Accept the friend request
                        accept_response = self.session.post(f"{BACKEND_URL}/friend-requests/{request_id}/accept")
                        
                        if accept_response.status_code == 200:
                            data = accept_response.json()
                            self.log_result(
                                "3. Accept Friend Request", 
                                True, 
                                "Friend request accepted successfully",
                                f"Response: {data}"
                            )
                        elif accept_response.status_code == 400:
                            data = accept_response.json()
                            if "already" in data.get('detail', '').lower():
                                self.log_result(
                                    "3. Accept Friend Request", 
                                    True, 
                                    "Friend request already accepted (idempotent)",
                                    f"Response: {data}"
                                )
                            else:
                                self.log_result(
                                    "3. Accept Friend Request", 
                                    False, 
                                    f"Accept failed: {data.get('detail', 'Unknown error')}",
                                    f"Response: {data}"
                                )
                        else:
                            self.log_result(
                                "3. Accept Friend Request", 
                                False, 
                                f"Accept failed with status {accept_response.status_code}",
                                f"Response: {accept_response.text}"
                            )
                    else:
                        # Check if they're already friends
                        friends_response = self.session.get(f"{BACKEND_URL}/friends/list", params={'userId': 'u1'})
                        if friends_response.status_code == 200:
                            friends_data = friends_response.json()
                            if 'items' in friends_data:
                                friend_ids = [friend.get('user', {}).get('id') for friend in friends_data['items']]
                                if 'u2' in friend_ids:
                                    self.log_result(
                                        "3. Accept Friend Request", 
                                        True, 
                                        "Users are already friends (idempotent)",
                                        "Friend request flow completed previously"
                                    )
                                    return
                        
                        self.log_result(
                            "3. Accept Friend Request", 
                            False, 
                            "No friend request found from u2 to u1",
                            f"Available requests: {[req.get('fromUserId') for req in requests_data]}"
                        )
                else:
                    self.log_result(
                        "3. Accept Friend Request", 
                        False, 
                        "No friend requests found",
                        f"Response: {requests_data}"
                    )
            else:
                self.log_result(
                    "3. Accept Friend Request", 
                    False, 
                    f"Get friend requests failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                
        except Exception as e:
            self.log_result("3. Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_4_retrieve_create_thread(self):
        """Step 4: Retrieve/create DM thread between u1 and u2"""
        try:
            params = {
                'userId': 'u1',
                'peerUserId': 'u2'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/thread", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'threadId' in data:
                    self.thread_id = data['threadId']
                    self.log_result(
                        "4. Retrieve/Create Thread", 
                        True, 
                        f"DM thread retrieved/created successfully",
                        f"Thread ID: {self.thread_id}"
                    )
                else:
                    self.log_result(
                        "4. Retrieve/Create Thread", 
                        False, 
                        "Thread response missing threadId",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "4. Retrieve/Create Thread", 
                    False, 
                    f"Thread creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("4. Retrieve/Create Thread", False, f"Exception occurred: {str(e)}")
    
    def test_5_send_text_message_body(self):
        """Step 5: Send message via Body with JSON payload"""
        if not self.thread_id:
            self.log_result("5. Send Text Message (Body)", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'u1'}
            json_payload = {"text": "body hello"}
            
            response = self.session.post(
                f"{BACKEND_URL}/dm/threads/{self.thread_id}/messages", 
                params=params,
                json=json_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data or 'messageId' in data:
                    message_id = data.get('id') or data.get('messageId')
                    self.log_result(
                        "5. Send Text Message (Body)", 
                        True, 
                        f"Successfully sent message via JSON body: 'body hello'",
                        f"Message ID: {message_id}"
                    )
                else:
                    self.log_result(
                        "5. Send Text Message (Body)", 
                        False, 
                        "Message response missing ID field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "5. Send Text Message (Body)", 
                    False, 
                    f"Send message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("5. Send Text Message (Body)", False, f"Exception occurred: {str(e)}")
    
    def test_6_verify_message_received(self):
        """Step 6: Verify message appears for u2"""
        if not self.thread_id:
            self.log_result("6. Verify Message Received", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'u2'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads/{self.thread_id}/messages", params=params)
            
            if response.status_code == 200:
                data = response.json()
                messages = []
                
                if 'items' in data and isinstance(data['items'], list):
                    messages = data['items']
                elif isinstance(data, list):
                    messages = data
                
                # Look for the "body hello" message
                body_hello_messages = [msg for msg in messages if msg.get('text') == 'body hello']
                
                if body_hello_messages:
                    msg = body_hello_messages[0]
                    self.log_result(
                        "6. Verify Message Received", 
                        True, 
                        f"Message 'body hello' found in u2's thread",
                        f"Message ID: {msg.get('id')}, Sender: {msg.get('senderId')}"
                    )
                else:
                    # Check if any messages contain "body hello"
                    containing_messages = [msg for msg in messages if 'body hello' in msg.get('text', '')]
                    if containing_messages:
                        msg = containing_messages[0]
                        self.log_result(
                            "6. Verify Message Received", 
                            True, 
                            f"Message containing 'body hello' found: '{msg.get('text')}'",
                            f"Message ID: {msg.get('id')}, Sender: {msg.get('senderId')}"
                        )
                    else:
                        self.log_result(
                            "6. Verify Message Received", 
                            False, 
                            "Message 'body hello' not found in thread",
                            f"Available messages: {[msg.get('text', 'No text') for msg in messages]}"
                        )
            else:
                self.log_result(
                    "6. Verify Message Received", 
                    False, 
                    f"Get messages failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("6. Verify Message Received", False, f"Exception occurred: {str(e)}")
    
    def test_7_send_media_message_body(self):
        """Step 7: Send media message via Body with JSON payload"""
        if not self.thread_id:
            self.log_result("7. Send Media Message (Body)", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'u1'}
            json_payload = {
                "mediaUrl": "https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?w=200",
                "mimeType": "image/jpeg"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/dm/threads/{self.thread_id}/messages", 
                params=params,
                json=json_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data or 'messageId' in data:
                    message_id = data.get('id') or data.get('messageId')
                    self.log_result(
                        "7. Send Media Message (Body)", 
                        True, 
                        f"Successfully sent media message via JSON body",
                        f"Message ID: {message_id}, Media: {json_payload['mediaUrl']}"
                    )
                else:
                    self.log_result(
                        "7. Send Media Message (Body)", 
                        False, 
                        "Media message response missing ID field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "7. Send Media Message (Body)", 
                    False, 
                    f"Send media message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("7. Send Media Message (Body)", False, f"Exception occurred: {str(e)}")
    
    def test_8_verify_media_message_received(self):
        """Step 8: Verify media message appears for u2"""
        if not self.thread_id:
            self.log_result("8. Verify Media Message Received", False, "Skipped - no thread ID available")
            return
            
        try:
            params = {'userId': 'u2'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads/{self.thread_id}/messages", params=params)
            
            if response.status_code == 200:
                data = response.json()
                messages = []
                
                if 'items' in data and isinstance(data['items'], list):
                    messages = data['items']
                elif isinstance(data, list):
                    messages = data
                
                # Look for the media message
                media_messages = [msg for msg in messages if msg.get('mediaUrl') and 'unsplash.com' in msg.get('mediaUrl', '')]
                
                if media_messages:
                    msg = media_messages[0]
                    self.log_result(
                        "8. Verify Media Message Received", 
                        True, 
                        f"Media message found in u2's thread",
                        f"Message ID: {msg.get('id')}, Media: {msg.get('mediaUrl')}, Type: {msg.get('mimeType')}"
                    )
                else:
                    # Check for any media messages
                    any_media_messages = [msg for msg in messages if msg.get('mediaUrl')]
                    if any_media_messages:
                        msg = any_media_messages[0]
                        self.log_result(
                            "8. Verify Media Message Received", 
                            True, 
                            f"Media message found (different URL): {msg.get('mediaUrl')}",
                            f"Message ID: {msg.get('id')}, Type: {msg.get('mimeType')}"
                        )
                    else:
                        self.log_result(
                            "8. Verify Media Message Received", 
                            False, 
                            "Media message not found in thread",
                            f"Total messages: {len(messages)}, Media URLs: {[msg.get('mediaUrl') for msg in messages if msg.get('mediaUrl')]}"
                        )
            else:
                self.log_result(
                    "8. Verify Media Message Received", 
                    False, 
                    f"Get messages failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("8. Verify Media Message Received", False, f"Exception occurred: {str(e)}")
    
    def run_regression_tests(self):
        """Run DM send/receive regression tests"""
        print("=" * 70)
        print("DM SEND/RECEIVE REGRESSION TESTS (Body Payload Change)")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing DM functionality with JSON body payloads")
        print("=" * 70)
        
        # Run the regression test sequence
        self.test_1_seed_data()
        self.test_2_send_friend_request()
        self.test_3_accept_friend_request()
        self.test_4_retrieve_create_thread()
        self.test_5_send_text_message_body()
        self.test_6_verify_message_received()
        self.test_7_send_media_message_body()
        self.test_8_verify_media_message_received()
        
        # Summary
        print("\n" + "=" * 70)
        print("REGRESSION TEST SUMMARY")
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
        else:
            print("\n🎉 All DM regression tests passed!")
        
        print("\n" + "=" * 70)
        return passed == total

def main():
    """Main test runner"""
    tester = DMRegressionTester()
    success = tester.run_regression_tests()
    
    if success:
        print("✅ DM send/receive regression tests completed successfully!")
        return 0
    else:
        print("❌ Some DM regression tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())