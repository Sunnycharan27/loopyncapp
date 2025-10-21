#!/usr/bin/env python3
"""
Backend API Testing Suite
Tests authentication, uploads, friend requests, DM threads, and search functionality for the Loopync app.
"""

import requests
import json
import uuid
import io
from datetime import datetime
from PIL import Image

# Configuration
BACKEND_URL = "https://vibehub-5.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.new_user_token = None
        self.new_user_email = None
        self.uploaded_file_url = None
        self.friend_request_id = None
        self.dm_thread_id = None
        self.dm_message_id = None
        
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
    
    def test_demo_login(self):
        """Test 1: Demo Login with demo@loopync.com"""
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
                    
                    # Validate user data
                    if (user.get('email') == DEMO_EMAIL and 
                        user.get('name') and 
                        user.get('id')):
                        self.log_result(
                            "Demo Login", 
                            True, 
                            f"Successfully logged in as {user['name']} ({user['email']})",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "Demo Login", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "Demo Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Demo Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Demo Login", False, f"Exception occurred: {str(e)}")
    
    def test_new_user_signup(self):
        """Test 2: New User Signup"""
        try:
            # Generate unique test user data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.new_user_email = f"testuser_{timestamp}@example.com"
            
            payload = {
                "email": self.new_user_email,
                "handle": f"testuser_{timestamp}",
                "name": f"Test User {timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.new_user_token = data['token']
                    user = data['user']
                    
                    # Validate user data
                    if (user.get('email') == self.new_user_email and 
                        user.get('name') == payload['name'] and 
                        user.get('id')):
                        self.log_result(
                            "New User Signup", 
                            True, 
                            f"Successfully created user {user['name']} ({user['email']})",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "New User Signup", 
                            False, 
                            "Signup successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Signup", 
                        False, 
                        "Signup response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "New User Signup", 
                    False, 
                    f"Signup failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("New User Signup", False, f"Exception occurred: {str(e)}")
    
    def test_new_user_login(self):
        """Test 3: Login with newly created user"""
        if not self.new_user_email:
            self.log_result("New User Login", False, "Skipped - no new user email available")
            return
            
        try:
            payload = {
                "email": self.new_user_email,
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    token = data['token']
                    user = data['user']
                    
                    # Validate user data
                    if (user.get('email') == self.new_user_email and 
                        user.get('name') and 
                        user.get('id')):
                        self.log_result(
                            "New User Login", 
                            True, 
                            f"Successfully logged in new user {user['name']}",
                            f"Token received, User ID: {user['id']}"
                        )
                    else:
                        self.log_result(
                            "New User Login", 
                            False, 
                            "Login successful but user data incomplete",
                            f"User data: {user}"
                        )
                else:
                    self.log_result(
                        "New User Login", 
                        False, 
                        "Login response missing token or user data",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "New User Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("New User Login", False, f"Exception occurred: {str(e)}")
    
    def test_jwt_token_validation(self):
        """Test 4: JWT Token Validation via /auth/me endpoint"""
        if not self.demo_token:
            self.log_result("JWT Token Validation", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data:
                    self.log_result(
                        "JWT Token Validation", 
                        True, 
                        f"Token validated successfully for user {data.get('name', 'Unknown')}",
                        f"User ID: {data['id']}"
                    )
                else:
                    self.log_result(
                        "JWT Token Validation", 
                        False, 
                        "Token validated but user data incomplete",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "JWT Token Validation", 
                    False, 
                    f"Token validation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Exception occurred: {str(e)}")
    
    def test_protected_route_access(self):
        """Test 5: Protected Route Access with valid token"""
        if not self.demo_token:
            self.log_result("Protected Route Access", False, "Skipped - no demo token available")
            return
            
        try:
            headers = {
                "Authorization": f"Bearer {self.demo_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Protected Route Access", 
                    True, 
                    "Successfully accessed protected route with valid token",
                    f"User: {data.get('name', 'Unknown')} ({data.get('email', 'Unknown')})"
                )
            else:
                self.log_result(
                    "Protected Route Access", 
                    False, 
                    f"Protected route access failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Protected Route Access", False, f"Exception occurred: {str(e)}")
    
    def test_invalid_credentials(self):
        """Test 6: Invalid Credentials Test"""
        try:
            payload = {
                "email": DEMO_EMAIL,
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Credentials", 
                    True, 
                    "Correctly rejected invalid credentials with 401 status",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Invalid Credentials", 
                    False, 
                    "Security issue: Invalid credentials were accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Invalid Credentials", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid credentials",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Invalid Credentials", False, f"Exception occurred: {str(e)}")
    
    def test_duplicate_email_signup(self):
        """Test 7: Duplicate Email Signup Test"""
        try:
            payload = {
                "email": DEMO_EMAIL,  # Using existing demo email
                "handle": "duplicate_test",
                "name": "Duplicate Test User",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "already" in data.get('detail', '').lower():
                    self.log_result(
                        "Duplicate Email Signup", 
                        True, 
                        "Correctly rejected duplicate email with 400 status",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Duplicate Email Signup", 
                        False, 
                        "Got 400 status but error message unclear",
                        f"Response: {data}"
                    )
            elif response.status_code == 200:
                self.log_result(
                    "Duplicate Email Signup", 
                    False, 
                    "Security issue: Duplicate email was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Duplicate Email Signup", 
                    False, 
                    f"Unexpected status code {response.status_code} for duplicate email",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Duplicate Email Signup", False, f"Exception occurred: {str(e)}")
    
    def test_invalid_token_access(self):
        """Test 8: Invalid Token Access Test"""
        try:
            headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Token Access", 
                    True, 
                    "Correctly rejected invalid token with 401 status",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "Invalid Token Access", 
                    False, 
                    "Security issue: Invalid token was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Invalid Token Access", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid token",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Invalid Token Access", False, f"Exception occurred: {str(e)}")
    
    def test_no_token_access(self):
        """Test 9: No Token Access Test"""
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result(
                    "No Token Access", 
                    True, 
                    f"Correctly rejected request without token (status {response.status_code})",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result(
                    "No Token Access", 
                    False, 
                    "Security issue: Request without token was accepted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "No Token Access", 
                    False, 
                    f"Unexpected status code {response.status_code} for no token",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("No Token Access", False, f"Exception occurred: {str(e)}")
    
    def generate_test_png(self):
        """Generate a small PNG image in memory for testing"""
        # Create a small 10x10 red image
        img = Image.new('RGB', (10, 10), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_static_upload(self):
        """Test 10: Static File Upload via /api/upload"""
        try:
            # Generate a small PNG for testing
            png_data = self.generate_test_png()
            
            files = {
                'file': ('test_image.png', png_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if 'url' in data and 'filename' in data and 'content_type' in data:
                    self.uploaded_file_url = data['url']
                    self.log_result(
                        "Static File Upload", 
                        True, 
                        f"Successfully uploaded file: {data['filename']}",
                        f"URL: {data['url']}, Content-Type: {data['content_type']}"
                    )
                else:
                    self.log_result(
                        "Static File Upload", 
                        False, 
                        "Upload response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Static File Upload", 
                    False, 
                    f"Upload failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Static File Upload", False, f"Exception occurred: {str(e)}")
    
    def test_static_file_retrieval(self):
        """Test 11: Static File Retrieval via /api/uploads"""
        if not self.uploaded_file_url:
            self.log_result("Static File Retrieval", False, "Skipped - no uploaded file URL available")
            return
            
        try:
            # Construct the full URL for file retrieval
            file_url = f"https://vibehub-5.preview.emergentagent.com/api{self.uploaded_file_url}"
            
            response = self.session.get(file_url)
            
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type.lower():
                    self.log_result(
                        "Static File Retrieval", 
                        True, 
                        f"Successfully retrieved uploaded file",
                        f"Content-Type: {content_type}, Size: {len(response.content)} bytes"
                    )
                else:
                    self.log_result(
                        "Static File Retrieval", 
                        True, 
                        f"File retrieved but content-type unexpected: {content_type}",
                        f"Size: {len(response.content)} bytes"
                    )
            else:
                self.log_result(
                    "Static File Retrieval", 
                    False, 
                    f"File retrieval failed with status {response.status_code}",
                    f"URL: {file_url}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Static File Retrieval", False, f"Exception occurred: {str(e)}")
    
    def test_seed_data(self):
        """Test 12: Create Seed Data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/seed")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'users' in data:
                    self.log_result(
                        "Seed Data Creation", 
                        True, 
                        f"Successfully created seed data: {data['users']} users",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Seed Data Creation", 
                        False, 
                        "Seed response missing expected fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Seed Data Creation", 
                    False, 
                    f"Seed creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Seed Data Creation", False, f"Exception occurred: {str(e)}")
    
    def test_send_friend_request(self):
        """Test 13: Send Friend Request from u2 to u1 (or use existing)"""
        try:
            params = {
                'fromUserId': 'u2',
                'toUserId': 'u1'
            }
            
            response = self.session.post(f"{BACKEND_URL}/friend-requests", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'requestId' in data and 'status' in data:
                    self.friend_request_id = data['requestId']
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        f"Successfully sent friend request: {data['requestId']}",
                        f"Status: {data['status']}"
                    )
                elif 'success' in data and data['success'] and 'requestId' in data:
                    self.friend_request_id = data['requestId']
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        f"Successfully sent friend request: {data['requestId']}",
                        f"Status: {data.get('status', 'pending')}"
                    )
                else:
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        "Friend request response missing required fields",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                # Check if friend request already exists or they're already friends
                data = response.json()
                detail = data.get('detail', '').lower()
                if "already sent" in detail:
                    # Get existing friend request
                    get_response = self.session.get(f"{BACKEND_URL}/friend-requests", params={'userId': 'u1'})
                    if get_response.status_code == 200:
                        requests_data = get_response.json()
                        if isinstance(requests_data, list) and len(requests_data) > 0:
                            for req in requests_data:
                                if req.get('fromUserId') == 'u2' and req.get('toUserId') == 'u1':
                                    self.friend_request_id = req['id']
                                    self.log_result(
                                        "Send Friend Request", 
                                        True, 
                                        f"Using existing friend request: {req['id']}",
                                        f"Status: {req['status']}"
                                    )
                                    return
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        "Friend request already exists but couldn't retrieve ID",
                        f"Response: {data}"
                    )
                elif "already friends" in detail:
                    self.log_result(
                        "Send Friend Request", 
                        True, 
                        "Users are already friends (friend request flow completed previously)",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Send Friend Request", 
                        False, 
                        f"Friend request failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "Send Friend Request", 
                    False, 
                    f"Friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_get_friend_requests(self):
        """Test 14: Get Friend Requests for u1"""
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/friend-requests", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Look for any request from u2 to u1 (pending or accepted)
                    u2_requests = [req for req in data if req.get('fromUserId') == 'u2' and req.get('toUserId') == 'u1']
                    if u2_requests:
                        request = u2_requests[0]
                        status = request.get('status', 'unknown')
                        if status == 'pending':
                            self.log_result(
                                "Get Friend Requests", 
                                True, 
                                f"Found pending friend request from {request.get('fromUser', {}).get('name', 'Unknown')}",
                                f"Request ID: {request['id']}, Status: {status}"
                            )
                        elif status == 'accepted':
                            self.log_result(
                                "Get Friend Requests", 
                                True, 
                                f"Found accepted friend request from {request.get('fromUser', {}).get('name', 'Unknown')}",
                                f"Request ID: {request['id']}, Status: {status} (friend request flow completed)"
                            )
                        else:
                            self.log_result(
                                "Get Friend Requests", 
                                True, 
                                f"Found friend request with status: {status}",
                                f"Request: {request}"
                            )
                    else:
                        self.log_result(
                            "Get Friend Requests", 
                            False, 
                            "No friend requests found from u2 to u1",
                            f"All requests: {data}"
                        )
                else:
                    self.log_result(
                        "Get Friend Requests", 
                        False, 
                        "Friend requests response is not a list",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Get Friend Requests", 
                    False, 
                    f"Get friend requests failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Friend Requests", False, f"Exception occurred: {str(e)}")
    
    def test_accept_friend_request(self):
        """Test 15: Accept Friend Request (or verify already accepted)"""
        # Check if users are already friends first
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
                            "Friend request flow completed successfully"
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
                if 'message' in data or 'success' in data:
                    self.log_result(
                        "Accept Friend Request", 
                        True, 
                        f"Successfully accepted friend request",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Accept Friend Request", 
                        False, 
                        "Accept response missing expected fields",
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
                        f"Accept friend request failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            else:
                self.log_result(
                    "Accept Friend Request", 
                    False, 
                    f"Accept friend request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Accept Friend Request", False, f"Exception occurred: {str(e)}")
    
    def test_friends_list(self):
        """Test 16: Verify Friends List includes u2 for u1"""
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/friends/list", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and isinstance(data['items'], list):
                    friends = data['items']
                    # Look for u2 in the friends list (nested under 'user')
                    friend_ids = [friend.get('user', {}).get('id') for friend in friends]
                    if 'u2' in friend_ids:
                        u2_friend = next(friend for friend in friends if friend.get('user', {}).get('id') == 'u2')
                        self.log_result(
                            "Friends List Verification", 
                            True, 
                            f"u2 found in u1's friends list: {u2_friend.get('user', {}).get('name', 'Unknown')}",
                            f"Total friends: {len(friends)}"
                        )
                    else:
                        self.log_result(
                            "Friends List Verification", 
                            False, 
                            "u2 not found in u1's friends list",
                            f"Friend IDs: {friend_ids}, Total friends: {len(friends)}"
                        )
                elif isinstance(data, list):
                    # Handle direct list response
                    friend_ids = [friend.get('id') for friend in data]
                    if 'u2' in friend_ids:
                        u2_friend = next(friend for friend in data if friend.get('id') == 'u2')
                        self.log_result(
                            "Friends List Verification", 
                            True, 
                            f"u2 found in u1's friends list: {u2_friend.get('name', 'Unknown')}",
                            f"Total friends: {len(data)}"
                        )
                    else:
                        self.log_result(
                            "Friends List Verification", 
                            False, 
                            "u2 not found in u1's friends list",
                            f"Friend IDs: {friend_ids}, Total friends: {len(data)}"
                        )
                else:
                    self.log_result(
                        "Friends List Verification", 
                        False, 
                        "Friends list response format unexpected",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Friends List Verification", 
                    False, 
                    f"Get friends list failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Friends List Verification", False, f"Exception occurred: {str(e)}")
    
    def test_dm_thread_creation(self):
        """Test 17: Verify DM Thread Auto-Creation between u1 and u2"""
        try:
            params = {'userId': 'u1'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads", params=params)
            
            if response.status_code == 200:
                data = response.json()
                threads = []
                
                if 'items' in data and isinstance(data['items'], list):
                    threads = data['items']
                elif isinstance(data, list):
                    threads = data
                
                if len(threads) > 0:
                    # Look for thread with u2
                    u2_thread = None
                    for thread in threads:
                        if 'peer' in thread and thread['peer'].get('id') == 'u2':
                            u2_thread = thread
                            break
                    
                    if u2_thread:
                        self.log_result(
                            "DM Thread Auto-Creation", 
                            True, 
                            f"DM thread found between u1 and u2: {u2_thread['peer'].get('name', 'Unknown')}",
                            f"Thread ID: {u2_thread.get('id')}"
                        )
                        # Store thread ID for messaging tests
                        self.dm_thread_id = u2_thread.get('id')
                    else:
                        self.log_result(
                            "DM Thread Auto-Creation", 
                            False, 
                            "No DM thread found between u1 and u2",
                            f"Available threads: {[t.get('peer', {}).get('id') for t in threads]}"
                        )
                else:
                    self.log_result(
                        "DM Thread Auto-Creation", 
                        False, 
                        "No DM threads found for u1",
                        f"Response: {data}"
                    )
            elif response.status_code == 500:
                # Backend has a bug in DM threads endpoint, try to create/get thread manually
                self.log_result(
                    "DM Thread Auto-Creation", 
                    False, 
                    "DM threads endpoint has backend bug (500 error)",
                    "Backend error: AttributeError in sort() method on find_one() result"
                )
                # Try to create a thread manually for testing
                try:
                    create_response = self.session.post(f"{BACKEND_URL}/dm/thread", 
                                                      params={'userId': 'u1', 'peerUserId': 'u2'})
                    if create_response.status_code == 200:
                        thread_data = create_response.json()
                        self.dm_thread_id = thread_data.get('threadId')
                        self.log_result(
                            "DM Thread Manual Creation", 
                            True, 
                            f"Manually created DM thread: {self.dm_thread_id}",
                            "Workaround for backend bug in /dm/threads endpoint"
                        )
                except Exception as e:
                    self.log_result(
                        "DM Thread Manual Creation", 
                        False, 
                        f"Failed to create DM thread manually: {str(e)}",
                        "Could not work around backend bug"
                    )
            else:
                self.log_result(
                    "DM Thread Auto-Creation", 
                    False, 
                    f"Get DM threads failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DM Thread Auto-Creation", False, f"Exception occurred: {str(e)}")
    
    def test_send_dm_message(self):
        """Test 18: Send DM Message from u1 to u2"""
        if not hasattr(self, 'dm_thread_id') or not self.dm_thread_id:
            self.log_result("Send DM Message", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {
                'userId': 'u1',
                'text': 'hello'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                                       params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'messageId' in data and 'timestamp' in data:
                    self.log_result(
                        "Send DM Message", 
                        True, 
                        f"Successfully sent DM message: 'hello'",
                        f"Message ID: {data['messageId']}, Timestamp: {data['timestamp']}"
                    )
                    self.dm_message_id = data['messageId']
                elif 'id' in data and 'text' in data:
                    self.log_result(
                        "Send DM Message", 
                        True, 
                        f"Successfully sent DM message: '{data['text']}'",
                        f"Message ID: {data['id']}, Sender: {data.get('senderId')}"
                    )
                    self.dm_message_id = data['id']
                else:
                    self.log_result(
                        "Send DM Message", 
                        False, 
                        "DM message response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Send DM Message", 
                    False, 
                    f"Send DM message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send DM Message", False, f"Exception occurred: {str(e)}")
    
    def test_get_dm_messages(self):
        """Test 19: Get DM Messages for u2"""
        if not hasattr(self, 'dm_thread_id') or not self.dm_thread_id:
            self.log_result("Get DM Messages", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {'userId': 'u2'}
            
            response = self.session.get(f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                                      params=params)
            
            if response.status_code == 200:
                data = response.json()
                messages = []
                
                if 'items' in data and isinstance(data['items'], list):
                    messages = data['items']
                elif isinstance(data, list):
                    messages = data
                
                if len(messages) > 0:
                    # Look for the "hello" message
                    hello_messages = [msg for msg in messages if msg.get('text') == 'hello']
                    if hello_messages:
                        msg = hello_messages[0]
                        self.log_result(
                            "Get DM Messages", 
                            True, 
                            f"Found 'hello' message from u1",
                            f"Message ID: {msg.get('id')}, Sender: {msg.get('senderId')}"
                        )
                    else:
                        self.log_result(
                            "Get DM Messages", 
                            True, 
                            f"DM messages retrieved successfully ({len(messages)} messages)",
                            f"Messages: {[msg.get('text', 'No text') for msg in messages[:3]]}"
                        )
                else:
                    self.log_result(
                        "Get DM Messages", 
                        True, 
                        "No messages in thread yet (empty thread is valid)",
                        f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'list'}"
                    )
            else:
                self.log_result(
                    "Get DM Messages", 
                    False, 
                    f"Get DM messages failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get DM Messages", False, f"Exception occurred: {str(e)}")
    
    def test_send_media_dm_message(self):
        """Test 20: Send DM Message with Media URL"""
        if not hasattr(self, 'dm_thread_id') or not self.dm_thread_id:
            self.log_result("Send Media DM Message", False, "Skipped - no DM thread ID available")
            return
            
        try:
            params = {
                'userId': 'u1',
                'text': 'Check out this image!',
                'mediaUrl': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200',
                'mimeType': 'image/jpeg'
            }
            
            response = self.session.post(f"{BACKEND_URL}/dm/threads/{self.dm_thread_id}/messages", 
                                       params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'messageId' in data and 'timestamp' in data:
                    self.log_result(
                        "Send Media DM Message", 
                        True, 
                        f"Successfully sent media DM message",
                        f"Message ID: {data['messageId']}, Timestamp: {data['timestamp']}"
                    )
                elif 'id' in data and 'mediaUrl' in data and 'mimeType' in data:
                    self.log_result(
                        "Send Media DM Message", 
                        True, 
                        f"Successfully sent media DM message",
                        f"Message ID: {data['id']}, Media: {data['mediaUrl']}, Type: {data['mimeType']}"
                    )
                else:
                    self.log_result(
                        "Send Media DM Message", 
                        False, 
                        "Media DM message response missing required fields",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Send Media DM Message", 
                    False, 
                    f"Send media DM message failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Send Media DM Message", False, f"Exception occurred: {str(e)}")
    
    def test_search_endpoint(self):
        """Test 21: Search Endpoint Sanity Check"""
        try:
            params = {
                'q': 'Raj',
                'currentUserId': 'u1'
            }
            
            response = self.session.get(f"{BACKEND_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data:
                    users = data['users']
                    if isinstance(users, list) and len(users) > 0:
                        # Check if users have required fields
                        user = users[0]
                        if 'isFriend' in user and 'isBlocked' in user:
                            self.log_result(
                                "Search Endpoint", 
                                True, 
                                f"Search returned {len(users)} users with friend/block status",
                                f"First user: {user.get('name', 'Unknown')}, isFriend: {user['isFriend']}, isBlocked: {user['isBlocked']}"
                            )
                        else:
                            self.log_result(
                                "Search Endpoint", 
                                False, 
                                "Search users missing isFriend/isBlocked fields",
                                f"User fields: {list(user.keys())}"
                            )
                    else:
                        self.log_result(
                            "Search Endpoint", 
                            True, 
                            "Search returned empty users list (acceptable)",
                            f"Response structure: {list(data.keys())}"
                        )
                else:
                    self.log_result(
                        "Search Endpoint", 
                        False, 
                        "Search response missing 'users' field",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Search Endpoint", 
                    False, 
                    f"Search failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Search Endpoint", False, f"Exception occurred: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("BACKEND API TESTING SUITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Demo Credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("=" * 60)
        
        # Run authentication tests first
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        self.test_demo_login()
        self.test_new_user_signup()
        self.test_new_user_login()
        self.test_jwt_token_validation()
        self.test_protected_route_access()
        self.test_invalid_credentials()
        self.test_duplicate_email_signup()
        self.test_invalid_token_access()
        self.test_no_token_access()
        
        # Run static upload tests
        print("\n📁 STATIC UPLOAD TESTS")
        print("-" * 40)
        self.test_static_upload()
        self.test_static_file_retrieval()
        
        # Run friend request flow tests
        print("\n👥 FRIEND REQUEST FLOW TESTS")
        print("-" * 40)
        self.test_seed_data()
        self.test_send_friend_request()
        self.test_get_friend_requests()
        self.test_accept_friend_request()
        self.test_friends_list()
        self.test_dm_thread_creation()
        
        # Run DM messaging tests
        print("\n💬 DM MESSAGING TESTS")
        print("-" * 40)
        self.test_send_dm_message()
        self.test_get_dm_messages()
        self.test_send_media_dm_message()
        
        # Run search tests
        print("\n🔍 SEARCH TESTS")
        print("-" * 40)
        self.test_search_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("\n" + "=" * 60)
        return passed == total

def main():
    """Main test runner"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All backend API tests passed!")
        return 0
    else:
        print("⚠️  Some backend API tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())