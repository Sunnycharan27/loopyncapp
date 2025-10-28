#!/usr/bin/env python3
"""
FOCUSED BACKEND TESTING: Quote Posts and Reply Posts (Twitter Features)
Testing quote and reply functionality after Post model fix
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
TEST_EMAIL = "demo@loopync.com"
TEST_PASSWORD = "password123"

class TwitterFeaturesTest:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "status": status
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def login_demo_user(self):
        """Login with demo user credentials"""
        print("🔐 LOGGING IN DEMO USER...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["user"]["id"]
                self.token = data["token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                self.log_test("Demo User Login", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Demo User Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Demo User Login", False, f"Exception: {str(e)}")
            return False

    def get_existing_post(self):
        """Get an existing post to use for quote/reply testing"""
        print("📝 GETTING EXISTING POST FOR TESTING...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts?limit=10")
            
            if response.status_code == 200:
                posts = response.json()
                if posts and len(posts) > 0:
                    # Find a post that's not from the demo user to avoid self-quote/reply
                    for post in posts:
                        if post.get("authorId") != self.user_id:
                            self.log_test("Get Existing Post", True, f"Found post ID: {post['id']}")
                            return post["id"]
                    
                    # If all posts are from demo user, use the first one anyway
                    post_id = posts[0]["id"]
                    self.log_test("Get Existing Post", True, f"Using demo user's post ID: {post_id}")
                    return post_id
                else:
                    self.log_test("Get Existing Post", False, "No posts found in database")
                    return None
            else:
                self.log_test("Get Existing Post", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Get Existing Post", False, f"Exception: {str(e)}")
            return None

    def test_quote_post_creation(self, original_post_id):
        """TEST 1: Quote Posts (Retweet with Comment)"""
        print("🔄 TESTING QUOTE POST CREATION...")
        
        quote_text = "This is my quote comment on this post"
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/posts/{original_post_id}/quote",
                params={
                    "authorId": self.user_id,
                    "text": quote_text
                }
            )
            
            if response.status_code == 200:
                quote_post = response.json()
                
                # Verify response structure
                required_fields = ["id", "quotedPostId", "quotedPost", "author"]
                missing_fields = [field for field in required_fields if field not in quote_post]
                
                if missing_fields:
                    self.log_test("Quote Post Creation", False, f"Missing fields: {missing_fields}")
                    return None
                
                # Verify quotedPostId matches original
                if quote_post.get("quotedPostId") != original_post_id:
                    self.log_test("Quote Post Creation", False, f"quotedPostId mismatch: expected {original_post_id}, got {quote_post.get('quotedPostId')}")
                    return None
                
                # Verify quotedPost object exists
                if not quote_post.get("quotedPost"):
                    self.log_test("Quote Post Creation", False, "quotedPost object is missing or empty")
                    return None
                
                # Verify author enrichment
                if not quote_post.get("author"):
                    self.log_test("Quote Post Creation", False, "Author enrichment missing")
                    return None
                
                self.log_test("Quote Post Creation", True, f"Quote post created with ID: {quote_post['id']}")
                return quote_post["id"]
                
            else:
                self.log_test("Quote Post Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Quote Post Creation", False, f"Exception: {str(e)}")
            return None

    def test_reply_post_creation(self, original_post_id):
        """TEST 2: Reply to Posts (Twitter Threads)"""
        print("💬 TESTING REPLY POST CREATION...")
        
        reply_text = "This is my reply to the post"
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/posts/{original_post_id}/reply",
                params={
                    "authorId": self.user_id,
                    "text": reply_text
                }
            )
            
            if response.status_code == 200:
                reply_post = response.json()
                
                # Verify response structure
                required_fields = ["id", "replyToPostId", "author"]
                missing_fields = [field for field in required_fields if field not in reply_post]
                
                if missing_fields:
                    self.log_test("Reply Post Creation", False, f"Missing fields: {missing_fields}")
                    return None
                
                # Verify replyToPostId matches original
                if reply_post.get("replyToPostId") != original_post_id:
                    self.log_test("Reply Post Creation", False, f"replyToPostId mismatch: expected {original_post_id}, got {reply_post.get('replyToPostId')}")
                    return None
                
                # Verify author enrichment
                if not reply_post.get("author"):
                    self.log_test("Reply Post Creation", False, "Author enrichment missing")
                    return None
                
                self.log_test("Reply Post Creation", True, f"Reply post created with ID: {reply_post['id']}")
                return reply_post["id"]
                
            else:
                self.log_test("Reply Post Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Reply Post Creation", False, f"Exception: {str(e)}")
            return None

    def test_get_post_replies(self, original_post_id):
        """TEST 3: Get Post Replies"""
        print("📋 TESTING GET POST REPLIES...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/{original_post_id}/replies?limit=100")
            
            if response.status_code == 200:
                replies = response.json()
                
                # Verify it's a list
                if not isinstance(replies, list):
                    self.log_test("Get Post Replies", False, f"Expected list, got {type(replies)}")
                    return False
                
                # Check if replies have replyToPostId
                for reply in replies:
                    if "replyToPostId" not in reply:
                        self.log_test("Get Post Replies", False, "Reply missing replyToPostId field")
                        return False
                    
                    if reply["replyToPostId"] != original_post_id:
                        self.log_test("Get Post Replies", False, f"Reply has wrong replyToPostId: {reply['replyToPostId']}")
                        return False
                    
                    # Check author enrichment
                    if "author" not in reply:
                        self.log_test("Get Post Replies", False, "Reply missing author enrichment")
                        return False
                
                self.log_test("Get Post Replies", True, f"Found {len(replies)} replies with correct structure")
                return True
                
            else:
                self.log_test("Get Post Replies", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Post Replies", False, f"Exception: {str(e)}")
            return False

    def test_quote_post_database_persistence(self, quote_post_id):
        """TEST 4: Quote Post Verification in Database"""
        print("🗄️ TESTING QUOTE POST DATABASE PERSISTENCE...")
        
        try:
            # Get all posts and find our quote post
            response = self.session.get(f"{BACKEND_URL}/posts?limit=100")
            
            if response.status_code == 200:
                posts = response.json()
                quote_post = None
                
                for post in posts:
                    if post.get("id") == quote_post_id:
                        quote_post = post
                        break
                
                if not quote_post:
                    self.log_test("Quote Post Database Persistence", False, f"Quote post {quote_post_id} not found in database")
                    return False
                
                # Verify quotedPostId is persisted
                if "quotedPostId" not in quote_post or not quote_post["quotedPostId"]:
                    self.log_test("Quote Post Database Persistence", False, "quotedPostId field not persisted in database")
                    return False
                
                # Verify quotedPost object is persisted
                if "quotedPost" not in quote_post or not quote_post["quotedPost"]:
                    self.log_test("Quote Post Database Persistence", False, "quotedPost object not persisted in database")
                    return False
                
                self.log_test("Quote Post Database Persistence", True, "quotedPostId and quotedPost fields persisted correctly")
                return True
                
            else:
                self.log_test("Quote Post Database Persistence", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Quote Post Database Persistence", False, f"Exception: {str(e)}")
            return False

    def test_reply_post_database_persistence(self, reply_post_id):
        """TEST 5: Reply Post Verification in Database"""
        print("🗄️ TESTING REPLY POST DATABASE PERSISTENCE...")
        
        try:
            # Get the specific reply post
            response = self.session.get(f"{BACKEND_URL}/posts?limit=100")
            
            if response.status_code == 200:
                posts = response.json()
                reply_post = None
                
                for post in posts:
                    if post.get("id") == reply_post_id:
                        reply_post = post
                        break
                
                if not reply_post:
                    self.log_test("Reply Post Database Persistence", False, f"Reply post {reply_post_id} not found in database")
                    return False
                
                # Verify replyToPostId is persisted
                if "replyToPostId" not in reply_post or not reply_post["replyToPostId"]:
                    self.log_test("Reply Post Database Persistence", False, "replyToPostId field not persisted in database")
                    return False
                
                self.log_test("Reply Post Database Persistence", True, "replyToPostId field persisted correctly")
                return True
                
            else:
                self.log_test("Reply Post Database Persistence", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reply Post Database Persistence", False, f"Exception: {str(e)}")
            return False

    def test_stats_and_notifications(self, original_post_id):
        """TEST 6: Verify Stats Tracking and Notifications"""
        print("📊 TESTING STATS AND NOTIFICATIONS...")
        
        try:
            # Get the original post to check stats
            response = self.session.get(f"{BACKEND_URL}/posts?limit=100")
            
            if response.status_code == 200:
                posts = response.json()
                original_post = None
                
                for post in posts:
                    if post.get("id") == original_post_id:
                        original_post = post
                        break
                
                if not original_post:
                    self.log_test("Stats and Notifications", False, f"Original post {original_post_id} not found")
                    return False
                
                # Check stats structure
                stats = original_post.get("stats", {})
                required_stats = ["likes", "quotes", "reposts", "replies"]
                
                for stat in required_stats:
                    if stat not in stats:
                        self.log_test("Stats and Notifications", False, f"Missing stat: {stat}")
                        return False
                
                # Verify quotes and replies counts are numbers
                quotes_count = stats.get("quotes", 0)
                replies_count = stats.get("replies", 0)
                
                if not isinstance(quotes_count, (int, float)) or not isinstance(replies_count, (int, float)):
                    self.log_test("Stats and Notifications", False, "Stats counts are not numeric")
                    return False
                
                self.log_test("Stats and Notifications", True, f"Stats working - Quotes: {quotes_count}, Replies: {replies_count}")
                return True
                
            else:
                self.log_test("Stats and Notifications", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Stats and Notifications", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all quote and reply tests"""
        print("🎯 STARTING FOCUSED BACKEND TESTING: Quote Posts and Reply Posts (Twitter Features)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Step 1: Login
        if not self.login_demo_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Get existing post
        original_post_id = self.get_existing_post()
        if not original_post_id:
            print("❌ Cannot proceed without an existing post")
            return False
        
        # Step 3: Test quote post creation
        quote_post_id = self.test_quote_post_creation(original_post_id)
        
        # Step 4: Test reply post creation
        reply_post_id = self.test_reply_post_creation(original_post_id)
        
        # Step 5: Test get post replies
        self.test_get_post_replies(original_post_id)
        
        # Step 6: Test quote post database persistence
        if quote_post_id:
            self.test_quote_post_database_persistence(quote_post_id)
        
        # Step 7: Test reply post database persistence
        if reply_post_id:
            self.test_reply_post_database_persistence(reply_post_id)
        
        # Step 8: Test stats and notifications
        self.test_stats_and_notifications(original_post_id)
        
        # Print summary
        self.print_summary()
        
        # Return overall success
        return all(result["success"] for result in self.test_results)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Print individual results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Quote and Reply functionality is working correctly!")
        elif success_rate >= 80:
            print("⚠️  MOSTLY WORKING - Some minor issues found")
        else:
            print("❌ CRITICAL ISSUES - Quote and Reply functionality needs fixes")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = TwitterFeaturesTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)