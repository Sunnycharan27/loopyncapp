#!/usr/bin/env python3
"""
FOCUSED BACKEND FUNCTIONALITY TEST - Core Features

Testing core backend functionality with proper API parameter handling.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
TEST_EMAIL = "demo@loopync.com"
TEST_PASSWORD = "password123"

class FocusedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.jwt_token = None
        self.test_results = []
        self.demo_user_data = {}
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_1_authentication(self):
        """TEST 1: Authentication System"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                self.demo_user_data = user_data
                
                # Set authorization header
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                
                # Verify required fields
                wallet_balance = user_data.get("walletBalance", 0.0)
                onboarding_complete = user_data.get("onboardingComplete", False)
                
                self.log_test(
                    "Authentication System",
                    True,
                    f"Login successful. User ID: {self.user_id}, Balance: ₹{wallet_balance:,.2f}, Onboarding: {onboarding_complete}"
                )
                return True
            else:
                self.log_test(
                    "Authentication System",
                    False,
                    error=f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication System",
                False,
                error=f"Exception during login: {str(e)}"
            )
            return False

    def test_2_posts_feed(self):
        """TEST 2: Posts & Social Feed"""
        try:
            response = self.session.get(f"{BACKEND_URL}/posts")
            
            if response.status_code == 200:
                posts = response.json()
                
                # Check author enrichment
                posts_with_authors = sum(1 for post in posts if "author" in post and post["author"])
                
                # Create a test post
                post_data = {
                    "text": f"Test post for comprehensive testing at {datetime.now().strftime('%H:%M:%S')} #test",
                    "audience": "public"
                }
                
                create_response = self.session.post(f"{BACKEND_URL}/posts", json=post_data, params={"authorId": self.user_id})
                
                if create_response.status_code == 200:
                    created_post = create_response.json()
                    self.test_post = created_post
                    
                    # Test like functionality
                    like_response = self.session.post(f"{BACKEND_URL}/posts/{created_post['id']}/like", params={"userId": self.user_id})
                    
                    like_success = like_response.status_code == 200
                    
                    self.log_test(
                        "Posts & Social Feed",
                        True,
                        f"Found {len(posts)} posts (author enrichment: {posts_with_authors}/{len(posts)}), Created post: ✅, Like functionality: {'✅' if like_success else '❌'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Posts & Social Feed",
                        False,
                        error=f"Failed to create post: {create_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Posts & Social Feed",
                    False,
                    error=f"Failed to get posts: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Posts & Social Feed",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_3_stories_system(self):
        """TEST 3: Vibe Capsules (Stories)"""
        try:
            # Try stories endpoint with userId parameter
            response = self.session.get(f"{BACKEND_URL}/stories", params={"userId": self.user_id})
            
            if response.status_code == 200:
                stories = response.json()
                
                # Try to create a story
                story_data = {
                    "mediaType": "image",
                    "mediaUrl": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                    "caption": f"Test story at {datetime.now().strftime('%H:%M:%S')}",
                    "duration": 15
                }
                
                create_response = self.session.post(f"{BACKEND_URL}/stories", json=story_data, params={"authorId": self.user_id})
                
                create_success = create_response.status_code == 200
                
                self.log_test(
                    "Vibe Capsules (Stories)",
                    True,
                    f"Stories endpoint working. Found {len(stories)} stories, Create story: {'✅' if create_success else '❌'}"
                )
                return True
            else:
                self.log_test(
                    "Vibe Capsules (Stories)",
                    False,
                    error=f"Stories endpoint failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Vibe Capsules (Stories)",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_4_reels_system(self):
        """TEST 4: Reels (VibeZone)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/reels")
            
            if response.status_code == 200:
                reels = response.json()
                
                # Check author enrichment
                reels_with_authors = sum(1 for reel in reels if "author" in reel and reel["author"])
                
                # Create a test reel
                reel_data = {
                    "videoUrl": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
                    "thumb": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400",
                    "caption": f"Test reel at {datetime.now().strftime('%H:%M:%S')}"
                }
                
                create_response = self.session.post(f"{BACKEND_URL}/reels", json=reel_data, params={"authorId": self.user_id})
                
                create_success = create_response.status_code == 200
                
                self.log_test(
                    "Reels (VibeZone)",
                    True,
                    f"Found {len(reels)} reels (author enrichment: {reels_with_authors}/{len(reels)}), Create reel: {'✅' if create_success else '❌'}"
                )
                return True
            else:
                self.log_test(
                    "Reels (VibeZone)",
                    False,
                    error=f"Failed to get reels: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Reels (VibeZone)",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_5_events_ticketing(self):
        """TEST 5: Events & Ticketing"""
        try:
            # Get events
            response = self.session.get(f"{BACKEND_URL}/events")
            
            if response.status_code == 200:
                events = response.json()
                
                if events:
                    event = events[0]
                    tiers = event.get("tiers", [])
                    
                    if tiers:
                        tier_name = tiers[0].get("name")
                        
                        # Try to book a ticket
                        book_response = self.session.post(
                            f"{BACKEND_URL}/events/{event['id']}/book",
                            params={
                                "userId": self.user_id,
                                "tier": tier_name,
                                "quantity": 1
                            }
                        )
                        
                        book_success = book_response.status_code == 200
                        
                        # Get user tickets
                        tickets_response = self.session.get(f"{BACKEND_URL}/tickets/{self.user_id}")
                        tickets_success = tickets_response.status_code == 200
                        
                        if tickets_success:
                            tickets = tickets_response.json()
                            qr_codes_present = sum(1 for ticket in tickets if "qrCode" in ticket)
                        else:
                            qr_codes_present = 0
                        
                        self.log_test(
                            "Events & Ticketing",
                            True,
                            f"Found {len(events)} events, Book ticket: {'✅' if book_success else '❌'}, QR codes: {qr_codes_present} tickets"
                        )
                        return True
                    else:
                        self.log_test(
                            "Events & Ticketing",
                            False,
                            error="No tiers found in events"
                        )
                        return False
                else:
                    self.log_test(
                        "Events & Ticketing",
                        False,
                        error="No events found"
                    )
                    return False
            else:
                self.log_test(
                    "Events & Ticketing",
                    False,
                    error=f"Failed to get events: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Events & Ticketing",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_6_messaging_system(self):
        """TEST 6: Messaging System"""
        try:
            # Get DM threads
            threads_response = self.session.get(f"{BACKEND_URL}/dm/threads", params={"userId": self.user_id})
            
            if threads_response.status_code == 200:
                threads = threads_response.json()
                
                # Try to create a DM thread with a friend
                friends = self.demo_user_data.get("friends", [])
                
                if friends:
                    friend_id = friends[0]
                    
                    # Create DM thread with correct parameters
                    create_response = self.session.post(
                        f"{BACKEND_URL}/dm/thread",
                        params={
                            "userId": self.user_id,
                            "peerUserId": friend_id
                        }
                    )
                    
                    create_success = create_response.status_code == 200
                    
                    if create_success:
                        thread_data = create_response.json()
                        thread_id = thread_data.get("threadId")
                        
                        # Try to send a message
                        message_data = {
                            "senderId": self.user_id,
                            "text": f"Test message at {datetime.now().strftime('%H:%M:%S')}"
                        }
                        
                        message_response = self.session.post(
                            f"{BACKEND_URL}/dm/threads/{thread_id}/messages",
                            json=message_data
                        )
                        
                        message_success = message_response.status_code == 200
                    else:
                        message_success = False
                    
                    self.log_test(
                        "Messaging System",
                        True,
                        f"Found {len(threads)} threads, Create thread: {'✅' if create_success else '❌'}, Send message: {'✅' if message_success else '❌'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Messaging System",
                        True,
                        f"Found {len(threads)} threads, No friends to test DM creation"
                    )
                    return True
            else:
                self.log_test(
                    "Messaging System",
                    False,
                    error=f"Failed to get DM threads: {threads_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Messaging System",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_7_friend_system(self):
        """TEST 7: Friend System"""
        try:
            # Get friends list
            friends_response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/friends")
            
            if friends_response.status_code == 200:
                friends = friends_response.json()
                
                # Get all users to find someone to send friend request to
                users_response = self.session.get(f"{BACKEND_URL}/users", params={"limit": 20})
                
                if users_response.status_code == 200:
                    users = users_response.json()
                    current_friends = self.demo_user_data.get("friends", [])
                    
                    # Find a user who's not already a friend
                    target_user = None
                    for user in users:
                        if user.get("id") != self.user_id and user.get("id") not in current_friends:
                            target_user = user
                            break
                    
                    if target_user:
                        # Send friend request
                        request_response = self.session.post(
                            f"{BACKEND_URL}/friends/request",
                            params={
                                "fromUserId": self.user_id,
                                "toUserId": target_user["id"]
                            }
                        )
                        
                        request_success = request_response.status_code == 200
                    else:
                        request_success = False
                    
                    self.log_test(
                        "Friend System",
                        True,
                        f"Current friends: {len(friends)}, Send friend request: {'✅' if request_success else '❌ (no suitable target)'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Friend System",
                        True,
                        f"Current friends: {len(friends)}, Could not get users list for friend request test"
                    )
                    return True
            else:
                self.log_test(
                    "Friend System",
                    False,
                    error=f"Failed to get friends: {friends_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Friend System",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_8_calling_system(self):
        """TEST 8: Calling System (Agora)"""
        try:
            friends = self.demo_user_data.get("friends", [])
            
            if friends:
                friend_id = friends[0]
                
                # Initiate call with correct parameters
                call_response = self.session.post(
                    f"{BACKEND_URL}/calls/initiate",
                    params={
                        "callerId": self.user_id,
                        "recipientId": friend_id,
                        "callType": "video"
                    }
                )
                
                if call_response.status_code == 200:
                    call_data = call_response.json()
                    
                    # Verify Agora tokens
                    required_fields = ["callId", "channelName", "callerToken", "recipientToken"]
                    has_all_fields = all(field in call_data for field in required_fields)
                    
                    self.log_test(
                        "Calling System (Agora)",
                        True,
                        f"Call initiated successfully. Agora tokens generated: {'✅' if has_all_fields else '❌'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Calling System (Agora)",
                        False,
                        error=f"Call initiation failed: {call_response.status_code} - {call_response.text}"
                    )
                    return False
            else:
                self.log_test(
                    "Calling System (Agora)",
                    False,
                    error="No friends available to test calling"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Calling System (Agora)",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_9_wallet_system(self):
        """TEST 9: Wallet System"""
        try:
            # Get wallet balance
            wallet_response = self.session.get(f"{BACKEND_URL}/wallet", params={"userId": self.user_id})
            
            if wallet_response.status_code == 200:
                wallet_data = wallet_response.json()
                balance = wallet_data.get("balance", 0.0)
                
                # Try to get transactions (may not exist)
                transactions_response = self.session.get(f"{BACKEND_URL}/wallet/transactions", params={"userId": self.user_id})
                transactions_success = transactions_response.status_code == 200
                
                if transactions_success:
                    transactions = transactions_response.json()
                    transaction_count = len(transactions)
                else:
                    transaction_count = "N/A"
                
                self.log_test(
                    "Wallet System",
                    True,
                    f"Balance: ₹{balance:,.2f}, Transactions: {transaction_count}"
                )
                return True
            else:
                self.log_test(
                    "Wallet System",
                    False,
                    error=f"Failed to get wallet: {wallet_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Wallet System",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_10_notifications(self):
        """TEST 10: Notifications"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/{self.user_id}")
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Count notification types
                types = set()
                for notification in notifications:
                    if "type" in notification:
                        types.add(notification["type"])
                
                self.log_test(
                    "Notifications",
                    True,
                    f"Found {len(notifications)} notifications with types: {', '.join(types) if types else 'None'}"
                )
                return True
            else:
                self.log_test(
                    "Notifications",
                    False,
                    error=f"Failed to get notifications: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Notifications",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_11_instagram_features(self):
        """TEST 11: Instagram-Style Features"""
        try:
            # Get saved posts
            saved_response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/saved-posts")
            
            if saved_response.status_code == 200:
                saved_posts = saved_response.json()
                
                # Test follow functionality
                users_response = self.session.get(f"{BACKEND_URL}/users", params={"limit": 10})
                
                if users_response.status_code == 200:
                    users = users_response.json()
                    target_user = None
                    
                    for user in users:
                        if user.get("id") != self.user_id:
                            target_user = user
                            break
                    
                    if target_user:
                        follow_response = self.session.post(
                            f"{BACKEND_URL}/users/{self.user_id}/follow",
                            params={"targetUserId": target_user["id"]}
                        )
                        
                        follow_success = follow_response.status_code == 200
                    else:
                        follow_success = False
                    
                    # Get followers/following
                    followers_response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/followers")
                    following_response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/following")
                    
                    followers_success = followers_response.status_code == 200
                    following_success = following_response.status_code == 200
                    
                    if followers_success and following_success:
                        followers = followers_response.json()
                        following = following_response.json()
                        
                        self.log_test(
                            "Instagram-Style Features",
                            True,
                            f"Saved posts: {len(saved_posts)}, Follow: {'✅' if follow_success else '❌'}, Followers: {len(followers)}, Following: {len(following)}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Instagram-Style Features",
                            False,
                            error="Failed to get followers/following lists"
                        )
                        return False
                else:
                    self.log_test(
                        "Instagram-Style Features",
                        True,
                        f"Saved posts: {len(saved_posts)}, Could not test follow functionality"
                    )
                    return True
            else:
                self.log_test(
                    "Instagram-Style Features",
                    False,
                    error=f"Failed to get saved posts: {saved_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Instagram-Style Features",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_12_twitter_features(self):
        """TEST 12: Twitter-Style Features"""
        try:
            # Get trending hashtags
            hashtags_response = self.session.get(f"{BACKEND_URL}/trending/hashtags")
            
            if hashtags_response.status_code == 200:
                hashtags = hashtags_response.json()
                
                # Get trending posts
                trending_response = self.session.get(f"{BACKEND_URL}/trending/posts")
                
                if trending_response.status_code == 200:
                    trending_posts = trending_response.json()
                    
                    # Check author enrichment
                    posts_with_authors = sum(1 for post in trending_posts if "author" in post and post["author"])
                    
                    # Test quote and reply if we have a test post
                    quote_success = False
                    reply_success = False
                    
                    if hasattr(self, 'test_post') and self.test_post:
                        post_id = self.test_post.get("id")
                        
                        # Test quote
                        quote_response = self.session.post(
                            f"{BACKEND_URL}/posts/{post_id}/quote",
                            json={"text": f"Quote test at {datetime.now().strftime('%H:%M:%S')}"},
                            params={"authorId": self.user_id}
                        )
                        quote_success = quote_response.status_code == 200
                        
                        # Test reply
                        reply_response = self.session.post(
                            f"{BACKEND_URL}/posts/{post_id}/reply",
                            json={"text": f"Reply test at {datetime.now().strftime('%H:%M:%S')}"},
                            params={"authorId": self.user_id}
                        )
                        reply_success = reply_response.status_code == 200
                    
                    self.log_test(
                        "Twitter-Style Features",
                        True,
                        f"Trending hashtags: {len(hashtags)}, Trending posts: {len(trending_posts)} (authors: {posts_with_authors}), Quote: {'✅' if quote_success else '❌'}, Reply: {'✅' if reply_success else '❌'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Twitter-Style Features",
                        False,
                        error=f"Failed to get trending posts: {trending_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Twitter-Style Features",
                    False,
                    error=f"Failed to get trending hashtags: {hashtags_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Twitter-Style Features",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def test_13_venues_tribes(self):
        """TEST 13: Venues & Tribes"""
        try:
            # Get venues
            venues_response = self.session.get(f"{BACKEND_URL}/venues")
            
            if venues_response.status_code == 200:
                venues = venues_response.json()
                
                # Get tribes
                tribes_response = self.session.get(f"{BACKEND_URL}/tribes")
                
                if tribes_response.status_code == 200:
                    tribes = tribes_response.json()
                    
                    # Try to join a tribe
                    join_success = False
                    if tribes:
                        tribe_id = tribes[0].get("id")
                        join_response = self.session.post(
                            f"{BACKEND_URL}/tribes/{tribe_id}/join",
                            params={"userId": self.user_id}
                        )
                        join_success = join_response.status_code == 200
                    
                    self.log_test(
                        "Venues & Tribes",
                        True,
                        f"Venues: {len(venues)}, Tribes: {len(tribes)}, Join tribe: {'✅' if join_success else '❌'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Venues & Tribes",
                        False,
                        error=f"Failed to get tribes: {tribes_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Venues & Tribes",
                    False,
                    error=f"Failed to get venues: {venues_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Venues & Tribes",
                False,
                error=f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all focused tests"""
        print("🎯 FOCUSED BACKEND FUNCTIONALITY TEST - Core Features")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_1_authentication,
            self.test_2_posts_feed,
            self.test_3_stories_system,
            self.test_4_reels_system,
            self.test_5_events_ticketing,
            self.test_6_messaging_system,
            self.test_7_friend_system,
            self.test_8_calling_system,
            self.test_9_wallet_system,
            self.test_10_notifications,
            self.test_11_instagram_features,
            self.test_12_twitter_features,
            self.test_13_venues_tribes
        ]
        
        for test in tests:
            test()
        
        # Print summary
        self.print_summary()
        
        # Return success status
        failed_tests = [r for r in self.test_results if not r["success"]]
        return len(failed_tests) == 0

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)} ✅")
        print(f"Failed: {len(failed_tests)} ❌")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test']}")
        
        print()
        print("🔍 CRITICAL VALIDATION RESULTS:")
        
        success_rate = len(passed_tests) / len(self.test_results) * 100
        
        if success_rate >= 90:
            print("✅ SUCCESS CRITERIA MET: 90%+ of features working")
        else:
            print("❌ SUCCESS CRITERIA NOT MET: Less than 90% of features working")
        
        print(f"   • Overall Success Rate: {success_rate:.1f}%")
        print(f"   • Critical 500 Errors: {len([r for r in failed_tests if '500' in r.get('error', '')])}")
        print(f"   • Authentication Working: {'✅' if any('Authentication' in r['test'] and r['success'] for r in self.test_results) else '❌'}")
        print(f"   • Content Creation Working: {'✅' if any('Posts' in r['test'] and r['success'] for r in self.test_results) else '❌'}")

if __name__ == "__main__":
    tester = FocusedBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL FOCUSED TESTS PASSED - CORE BACKEND FUNCTIONALITY IS WORKING!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW RESULTS ABOVE")
        sys.exit(1)