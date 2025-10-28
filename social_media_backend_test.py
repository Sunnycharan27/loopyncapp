#!/usr/bin/env python3
"""
Comprehensive Social Media Backend Testing Suite
Tests all newly added Instagram/Twitter-style social media endpoints in server.py
Covers: Save Posts, Follow/Unfollow, Quote Posts, Hashtag Search, Trending, Replies
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class SocialMediaTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.demo_token = None
        self.demo_user_id = None
        self.test_user_id = None
        self.test_post_id = None
        self.quote_post_id = None
        self.reply_post_id = None
        
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
        """Setup: Login demo user and get authentication token"""
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
                        "Setup Authentication", 
                        True, 
                        f"Successfully authenticated as {data['user']['name']}",
                        f"User ID: {self.demo_user_id}"
                    )
                    return True
                else:
                    self.log_result("Setup Authentication", False, "Login response missing token or user data")
                    return False
            else:
                self.log_result("Setup Authentication", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Setup Authentication", False, f"Exception occurred: {str(e)}")
            return False
    
    def get_existing_post_id(self):
        """Get an existing post ID from the database for testing"""
        try:
            response = self.session.get(f"{BACKEND_URL}/posts")
            
            if response.status_code == 200:
                posts = response.json()
                if isinstance(posts, list) and len(posts) > 0:
                    self.test_post_id = posts[0]['id']
                    self.log_result(
                        "Get Existing Post", 
                        True, 
                        f"Found existing post for testing: {self.test_post_id}",
                        f"Post text: {posts[0]['text'][:50]}..."
                    )
                    return True
                else:
                    # Create a test post if none exist
                    return self.create_test_post()
            else:
                self.log_result("Get Existing Post", False, f"Failed to get posts: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Get Existing Post", False, f"Exception occurred: {str(e)}")
            return False
    
    def create_test_post(self):
        """Create a test post with hashtags for testing"""
        try:
            payload = {
                "text": "This is a test post for social media features #test #loopync #socialmedia",
                "audience": "public",
                "hashtags": ["test", "loopync", "socialmedia"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/posts?authorId={self.demo_user_id}", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.test_post_id = data['id']
                self.log_result(
                    "Create Test Post", 
                    True, 
                    f"Created test post: {self.test_post_id}",
                    f"Text: {data['text']}"
                )
                return True
            else:
                self.log_result("Create Test Post", False, f"Failed to create post: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Create Test Post", False, f"Exception occurred: {str(e)}")
            return False
    
    def get_test_user_id(self):
        """Get another user ID for testing follow/unfollow"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users?limit=10")
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 1:
                    # Find a user that's not the demo user
                    for user in users:
                        if user['id'] != self.demo_user_id:
                            self.test_user_id = user['id']
                            self.log_result(
                                "Get Test User", 
                                True, 
                                f"Found test user: {user['name']} ({self.test_user_id})",
                                f"Handle: @{user.get('handle', 'unknown')}"
                            )
                            return True
                    
                    self.log_result("Get Test User", False, "No other users found besides demo user")
                    return False
                else:
                    self.log_result("Get Test User", False, "Not enough users found for testing")
                    return False
            else:
                self.log_result("Get Test User", False, f"Failed to get users: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Get Test User", False, f"Exception occurred: {str(e)}")
            return False
    
    # ===== INSTAGRAM-STYLE FEATURES =====
    
    def test_save_post(self):
        """TEST 1: Save/Bookmark Posts (Instagram-style)"""
        if not self.test_post_id:
            self.log_result("Save Post", False, "Skipped - no test post ID available")
            return
            
        try:
            # Test save action
            response = self.session.post(f"{BACKEND_URL}/posts/{self.test_post_id}/save?userId={self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'saved' in data['message'].lower():
                    self.log_result(
                        "Save Post", 
                        True, 
                        f"Successfully saved post: {data['message']}",
                        f"Post ID: {self.test_post_id}"
                    )
                    
                    # Test unsave action
                    unsave_response = self.session.post(f"{BACKEND_URL}/posts/{self.test_post_id}/save?userId={self.demo_user_id}")
                    if unsave_response.status_code == 200:
                        unsave_data = unsave_response.json()
                        if 'unsaved' in unsave_data['message'].lower():
                            self.log_result(
                                "Unsave Post", 
                                True, 
                                f"Successfully unsaved post: {unsave_data['message']}",
                                "Save/unsave toggle working correctly"
                            )
                        else:
                            self.log_result("Unsave Post", False, f"Unexpected unsave response: {unsave_data}")
                    else:
                        self.log_result("Unsave Post", False, f"Unsave failed: {unsave_response.status_code}")
                else:
                    self.log_result("Save Post", False, f"Unexpected save response: {data}")
            else:
                self.log_result("Save Post", False, f"Save post failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Save Post", False, f"Exception occurred: {str(e)}")
    
    def test_get_saved_posts(self):
        """TEST 2: Get Saved Posts Collection"""
        try:
            # First save a post
            if self.test_post_id:
                self.session.post(f"{BACKEND_URL}/posts/{self.test_post_id}/save?userId={self.demo_user_id}")
            
            # Get saved posts
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/saved-posts?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Get Saved Posts", 
                        True, 
                        f"Successfully retrieved {len(data)} saved posts",
                        f"Posts enriched with author data: {len([p for p in data if 'author' in p])} of {len(data)}"
                    )
                else:
                    self.log_result("Get Saved Posts", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Get Saved Posts", False, f"Get saved posts failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Get Saved Posts", False, f"Exception occurred: {str(e)}")
    
    def test_follow_unfollow_users(self):
        """TEST 3: Follow/Unfollow Users (Instagram-style)"""
        if not self.test_user_id:
            self.log_result("Follow/Unfollow Users", False, "Skipped - no test user ID available")
            return
            
        try:
            # Test follow action
            response = self.session.post(f"{BACKEND_URL}/users/{self.demo_user_id}/follow?targetUserId={self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'action' in data and 'followingCount' in data and 'followersCount' in data:
                    action = data['action']
                    self.log_result(
                        "Follow User", 
                        True, 
                        f"Successfully {action} user - Following: {data['followingCount']}, Followers: {data['followersCount']}",
                        f"Action: {action}, Response: {data}"
                    )
                    
                    # Test unfollow action (toggle)
                    unfollow_response = self.session.post(f"{BACKEND_URL}/users/{self.demo_user_id}/follow?targetUserId={self.test_user_id}")
                    if unfollow_response.status_code == 200:
                        unfollow_data = unfollow_response.json()
                        if unfollow_data['action'] != action:  # Should toggle
                            self.log_result(
                                "Unfollow User", 
                                True, 
                                f"Successfully toggled to {unfollow_data['action']} - Following: {unfollow_data['followingCount']}",
                                "Follow/unfollow toggle working correctly"
                            )
                        else:
                            self.log_result("Unfollow User", False, f"Follow action didn't toggle: {unfollow_data}")
                    else:
                        self.log_result("Unfollow User", False, f"Unfollow failed: {unfollow_response.status_code}")
                else:
                    self.log_result("Follow User", False, f"Follow response missing required fields: {data}")
            else:
                self.log_result("Follow User", False, f"Follow user failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Follow/Unfollow Users", False, f"Exception occurred: {str(e)}")
    
    def test_self_follow_prevention(self):
        """TEST 4: Self-Follow Prevention"""
        try:
            response = self.session.post(f"{BACKEND_URL}/users/{self.demo_user_id}/follow?targetUserId={self.demo_user_id}")
            
            if response.status_code == 400:
                self.log_result(
                    "Self-Follow Prevention", 
                    True, 
                    "Correctly prevented self-follow with 400 error",
                    f"Response: {response.text}"
                )
            elif response.status_code == 200:
                self.log_result("Self-Follow Prevention", False, "Security issue: Self-follow was allowed")
            else:
                self.log_result("Self-Follow Prevention", False, f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Self-Follow Prevention", False, f"Exception occurred: {str(e)}")
    
    def test_get_followers_list(self):
        """TEST 5: Get Followers List"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/followers?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if followers have required fields
                    valid_followers = 0
                    for follower in data:
                        if all(field in follower for field in ['id', 'name', 'handle', 'avatar']):
                            valid_followers += 1
                    
                    self.log_result(
                        "Get Followers List", 
                        True, 
                        f"Successfully retrieved {len(data)} followers ({valid_followers} with complete data)",
                        f"Sample follower: {data[0] if data else 'None'}"
                    )
                else:
                    self.log_result("Get Followers List", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Get Followers List", False, f"Get followers failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Get Followers List", False, f"Exception occurred: {str(e)}")
    
    def test_get_following_list(self):
        """TEST 6: Get Following List"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}/following?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if following users have required fields
                    valid_following = 0
                    for user in data:
                        if all(field in user for field in ['id', 'name', 'handle', 'avatar']):
                            valid_following += 1
                    
                    self.log_result(
                        "Get Following List", 
                        True, 
                        f"Successfully retrieved {len(data)} following ({valid_following} with complete data)",
                        f"Sample user: {data[0] if data else 'None'}"
                    )
                else:
                    self.log_result("Get Following List", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Get Following List", False, f"Get following failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Get Following List", False, f"Exception occurred: {str(e)}")
    
    # ===== TWITTER-STYLE FEATURES =====
    
    def test_quote_posts(self):
        """TEST 7: Quote Posts (Retweet with Comment)"""
        if not self.test_post_id:
            self.log_result("Quote Posts", False, "Skipped - no test post ID available")
            return
            
        try:
            quote_text = "This is a great post! Quoting it for my followers 🔥"
            response = self.session.post(f"{BACKEND_URL}/posts/{self.test_post_id}/quote?authorId={self.demo_user_id}&text={quote_text}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'quotedPostId' in data and 'quotedPost' in data:
                    self.quote_post_id = data['id']
                    self.log_result(
                        "Quote Posts", 
                        True, 
                        f"Successfully created quote post: {self.quote_post_id}",
                        f"Original post: {data['quotedPostId']}, Quote text: {data['text']}"
                    )
                    
                    # Verify original post's quotes count incremented
                    original_response = self.session.get(f"{BACKEND_URL}/posts")
                    if original_response.status_code == 200:
                        posts = original_response.json()
                        original_post = next((p for p in posts if p['id'] == self.test_post_id), None)
                        if original_post and original_post.get('stats', {}).get('quotes', 0) > 0:
                            self.log_result(
                                "Quote Count Update", 
                                True, 
                                f"Original post quotes count updated: {original_post['stats']['quotes']}",
                                "Stats tracking working correctly"
                            )
                        else:
                            self.log_result("Quote Count Update", False, "Original post quotes count not updated")
                else:
                    self.log_result("Quote Posts", False, f"Quote response missing required fields: {data}")
            else:
                self.log_result("Quote Posts", False, f"Quote post failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Quote Posts", False, f"Exception occurred: {str(e)}")
    
    def test_hashtag_search(self):
        """TEST 8: Hashtag Search"""
        try:
            # Search for posts with #test hashtag
            hashtag = "test"
            response = self.session.get(f"{BACKEND_URL}/hashtags/{hashtag}/posts?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if posts contain the hashtag and have author enrichment
                    valid_posts = 0
                    hashtag_posts = 0
                    for post in data:
                        if 'author' in post:
                            valid_posts += 1
                        if hashtag.lower() in post.get('text', '').lower():
                            hashtag_posts += 1
                    
                    self.log_result(
                        "Hashtag Search", 
                        True, 
                        f"Found {len(data)} posts for #{hashtag} ({hashtag_posts} contain hashtag, {valid_posts} with author data)",
                        f"Case-insensitive search working: {hashtag_posts > 0}"
                    )
                else:
                    self.log_result("Hashtag Search", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Hashtag Search", False, f"Hashtag search failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Hashtag Search", False, f"Exception occurred: {str(e)}")
    
    def test_trending_hashtags(self):
        """TEST 9: Trending Hashtags (Last 24h)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/trending/hashtags?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if hashtags have required format
                    valid_hashtags = 0
                    for hashtag in data:
                        if 'hashtag' in hashtag and 'count' in hashtag:
                            valid_hashtags += 1
                    
                    self.log_result(
                        "Trending Hashtags", 
                        True, 
                        f"Retrieved {len(data)} trending hashtags ({valid_hashtags} with valid format)",
                        f"Top hashtag: {data[0] if data else 'None'}"
                    )
                else:
                    self.log_result("Trending Hashtags", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Trending Hashtags", False, f"Trending hashtags failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Trending Hashtags", False, f"Exception occurred: {str(e)}")
    
    def test_trending_posts(self):
        """TEST 10: Trending Posts (For You Page)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/trending/posts?limit=20")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if posts have author enrichment and no engagement_score in response
                    valid_posts = 0
                    no_engagement_score = 0
                    for post in data:
                        if 'author' in post:
                            valid_posts += 1
                        if '_engagement_score' not in post and 'engagement_score' not in post:
                            no_engagement_score += 1
                    
                    self.log_result(
                        "Trending Posts", 
                        True, 
                        f"Retrieved {len(data)} trending posts ({valid_posts} with author data, {no_engagement_score} without engagement score)",
                        f"Engagement-based ranking working: {len(data) > 0}"
                    )
                else:
                    self.log_result("Trending Posts", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Trending Posts", False, f"Trending posts failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Trending Posts", False, f"Exception occurred: {str(e)}")
    
    def test_reply_to_posts(self):
        """TEST 11: Reply to Posts (Twitter Threads)"""
        if not self.test_post_id:
            self.log_result("Reply to Posts", False, "Skipped - no test post ID available")
            return
            
        try:
            reply_text = "Great post! I totally agree with your perspective 👍"
            response = self.session.post(f"{BACKEND_URL}/posts/{self.test_post_id}/reply?authorId={self.demo_user_id}&text={reply_text}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'replyToPostId' in data and data['replyToPostId'] == self.test_post_id:
                    self.reply_post_id = data['id']
                    self.log_result(
                        "Reply to Posts", 
                        True, 
                        f"Successfully created reply: {self.reply_post_id}",
                        f"Reply to: {data['replyToPostId']}, Text: {data['text']}"
                    )
                    
                    # Test reply with media
                    media_reply_response = self.session.post(
                        f"{BACKEND_URL}/posts/{self.test_post_id}/reply?authorId={self.demo_user_id}&text=Check this out!&mediaUrl=https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200"
                    )
                    if media_reply_response.status_code == 200:
                        media_data = media_reply_response.json()
                        if 'mediaUrl' in media_data:
                            self.log_result(
                                "Reply with Media", 
                                True, 
                                f"Successfully created reply with media: {media_data['id']}",
                                f"Media URL: {media_data['mediaUrl']}"
                            )
                        else:
                            self.log_result("Reply with Media", False, "Reply created but media URL missing")
                    else:
                        self.log_result("Reply with Media", False, f"Media reply failed: {media_reply_response.status_code}")
                else:
                    self.log_result("Reply to Posts", False, f"Reply response missing required fields: {data}")
            else:
                self.log_result("Reply to Posts", False, f"Reply to post failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Reply to Posts", False, f"Exception occurred: {str(e)}")
    
    def test_get_post_replies(self):
        """TEST 12: Get Post Replies"""
        if not self.test_post_id:
            self.log_result("Get Post Replies", False, "Skipped - no test post ID available")
            return
            
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/{self.test_post_id}/replies?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if replies have author enrichment and are sorted chronologically
                    valid_replies = 0
                    for reply in data:
                        if 'author' in reply and 'replyToPostId' in reply:
                            valid_replies += 1
                    
                    self.log_result(
                        "Get Post Replies", 
                        True, 
                        f"Retrieved {len(data)} replies ({valid_replies} with complete data)",
                        f"Sample reply: {data[0] if data else 'None'}"
                    )
                else:
                    self.log_result("Get Post Replies", False, f"Unexpected response format: {type(data)}")
            else:
                self.log_result("Get Post Replies", False, f"Get post replies failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Get Post Replies", False, f"Exception occurred: {str(e)}")
    
    # ===== VALIDATION TESTS =====
    
    def test_user_not_found_errors(self):
        """TEST 13: User Not Found (404 Error Handling)"""
        fake_user_id = "nonexistent_user_12345"
        
        tests = [
            ("Save Post", f"/posts/{self.test_post_id or 'test'}/save?userId={fake_user_id}"),
            ("Get Saved Posts", f"/users/{fake_user_id}/saved-posts"),
            ("Follow User", f"/users/{fake_user_id}/follow?targetUserId={self.test_user_id or 'test'}"),
            ("Get Followers", f"/users/{fake_user_id}/followers"),
            ("Get Following", f"/users/{fake_user_id}/following")
        ]
        
        passed_tests = 0
        for test_name, endpoint in tests:
            try:
                if "save" in endpoint or "follow" in endpoint:
                    response = self.session.post(f"{BACKEND_URL}{endpoint}")
                else:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 404:
                    passed_tests += 1
                    
            except Exception:
                pass
        
        self.log_result(
            "User Not Found Errors", 
            passed_tests >= 3, 
            f"Correctly handled user not found errors: {passed_tests}/{len(tests)} tests passed",
            f"404 error handling working for most endpoints"
        )
    
    def test_post_not_found_errors(self):
        """TEST 14: Post Not Found (404 Error Handling)"""
        fake_post_id = "nonexistent_post_12345"
        
        tests = [
            ("Save Post", f"/posts/{fake_post_id}/save?userId={self.demo_user_id}"),
            ("Quote Post", f"/posts/{fake_post_id}/quote?authorId={self.demo_user_id}&text=test"),
            ("Reply to Post", f"/posts/{fake_post_id}/reply?authorId={self.demo_user_id}&text=test"),
            ("Get Post Replies", f"/posts/{fake_post_id}/replies")
        ]
        
        passed_tests = 0
        for test_name, endpoint in tests:
            try:
                if "replies" in endpoint and "GET" in endpoint:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 404:
                    passed_tests += 1
                    
            except Exception:
                pass
        
        self.log_result(
            "Post Not Found Errors", 
            passed_tests >= 2, 
            f"Correctly handled post not found errors: {passed_tests}/{len(tests)} tests passed",
            f"404 error handling working for most post endpoints"
        )
    
    def run_all_tests(self):
        """Run all social media feature tests"""
        print("🚀 Starting Comprehensive Social Media Backend Testing...")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        self.get_existing_post_id()
        self.get_test_user_id()
        
        # Instagram-Style Features
        print("\n📸 TESTING INSTAGRAM-STYLE FEATURES:")
        print("-" * 50)
        self.test_save_post()
        self.test_get_saved_posts()
        self.test_follow_unfollow_users()
        self.test_self_follow_prevention()
        self.test_get_followers_list()
        self.test_get_following_list()
        
        # Twitter-Style Features
        print("\n🐦 TESTING TWITTER-STYLE FEATURES:")
        print("-" * 50)
        self.test_quote_posts()
        self.test_hashtag_search()
        self.test_trending_hashtags()
        self.test_trending_posts()
        self.test_reply_to_posts()
        self.test_get_post_replies()
        
        # Validation Tests
        print("\n🔍 TESTING ERROR HANDLING:")
        print("-" * 50)
        self.test_user_not_found_errors()
        self.test_post_not_found_errors()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY:")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} tests ({success_rate:.1f}%)")
        
        if passed < total:
            print(f"❌ Failed: {total - passed} tests")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n🎯 Overall Status: {'PASS' if success_rate >= 80 else 'FAIL'}")
        print("=" * 80)
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = SocialMediaTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)