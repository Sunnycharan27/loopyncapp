#!/usr/bin/env python3
"""
Debug User Lookup in MongoDB
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class UserLookupDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.demo_user_id = None
        
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
                    self.demo_user_id = data['user']['id']
                    print(f"✅ Demo User ID: {self.demo_user_id}")
                    return True
            return False
                
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False
    
    def test_user_lookup_direct(self):
        """Test direct user lookup"""
        try:
            print(f"\n🔍 Testing direct user lookup for ID: {self.demo_user_id}")
            
            response = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Direct lookup successful")
                print(f"   Name: {data.get('name', 'Unknown')}")
                print(f"   Handle: {data.get('handle', 'Unknown')}")
                print(f"   Email: {data.get('email', 'Unknown')}")
                print(f"   ID field: {data.get('id', 'MISSING!')}")
                return data
            else:
                print(f"❌ Direct lookup failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception in direct lookup: {str(e)}")
            return None
    
    def test_user_list_search(self):
        """Test finding user in user list"""
        try:
            print(f"\n🔍 Searching for demo user in user list")
            
            response = self.session.get(f"{BACKEND_URL}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Found {len(data)} users in database")
                    
                    # Look for demo user
                    demo_user = None
                    for user in data:
                        if (user.get('id') == self.demo_user_id or 
                            user.get('email') == DEMO_EMAIL or
                            'demo' in user.get('name', '').lower()):
                            demo_user = user
                            break
                    
                    if demo_user:
                        print(f"✅ Found demo user in list:")
                        print(f"   Name: {demo_user.get('name', 'Unknown')}")
                        print(f"   Handle: {demo_user.get('handle', 'Unknown')}")
                        print(f"   Email: {demo_user.get('email', 'Unknown')}")
                        print(f"   ID field: {demo_user.get('id', 'MISSING!')}")
                        print(f"   All fields: {list(demo_user.keys())}")
                        return demo_user
                    else:
                        print(f"❌ Demo user not found in list")
                        print(f"   Looking for ID: {self.demo_user_id}")
                        print(f"   Looking for email: {DEMO_EMAIL}")
                        print(f"   First 3 users:")
                        for i, user in enumerate(data[:3]):
                            print(f"     {i+1}. {user.get('name', 'Unknown')} (ID: {user.get('id', 'Unknown')}, Email: {user.get('email', 'Unknown')})")
                        return None
                else:
                    print(f"❌ User list response is not a list: {type(data)}")
                    return None
            else:
                print(f"❌ User list failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception in user list search: {str(e)}")
            return None
    
    def test_seeded_users(self):
        """Test with seeded users to compare"""
        try:
            print(f"\n🔍 Testing with seeded users for comparison")
            
            # Seed data first
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test direct lookup of u1
            response = self.session.get(f"{BACKEND_URL}/users/u1")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Seeded user u1 lookup successful")
                print(f"   Name: {data.get('name', 'Unknown')}")
                print(f"   Handle: {data.get('handle', 'Unknown')}")
                print(f"   ID field: {data.get('id', 'MISSING!')}")
                print(f"   All fields: {list(data.keys())}")
                
                # Now test friend request between seeded users
                params = {
                    'fromUserId': 'u1',
                    'toUserId': 'u2'
                }
                
                friend_response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
                
                if friend_response.status_code == 200:
                    print(f"✅ Friend request between seeded users successful")
                else:
                    print(f"❌ Friend request between seeded users failed: {friend_response.status_code}")
                    print(f"   Response: {friend_response.text}")
                
                return data
            else:
                print(f"❌ Seeded user u1 lookup failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception in seeded user test: {str(e)}")
            return None
    
    def test_friend_request_debug(self):
        """Debug the exact friend request issue"""
        try:
            print(f"\n🔍 Debugging friend request with demo user")
            
            # Ensure seeded data exists
            self.session.post(f"{BACKEND_URL}/seed")
            
            # Test friend request from demo user to u1
            params = {
                'fromUserId': self.demo_user_id,
                'toUserId': 'u1'
            }
            
            print(f"   Attempting friend request:")
            print(f"   From: {self.demo_user_id}")
            print(f"   To: u1")
            
            response = self.session.post(f"{BACKEND_URL}/friends/request", params=params)
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code != 200:
                # Let's check if both users exist
                print(f"\n   Checking if both users exist:")
                
                from_check = self.session.get(f"{BACKEND_URL}/users/{self.demo_user_id}")
                to_check = self.session.get(f"{BACKEND_URL}/users/u1")
                
                print(f"   From user ({self.demo_user_id}): {from_check.status_code}")
                print(f"   To user (u1): {to_check.status_code}")
                
                if from_check.status_code == 200:
                    from_data = from_check.json()
                    print(f"   From user data: ID={from_data.get('id')}, Name={from_data.get('name')}")
                
                if to_check.status_code == 200:
                    to_data = to_check.json()
                    print(f"   To user data: ID={to_data.get('id')}, Name={to_data.get('name')}")
            
            return response.status_code == 200
                
        except Exception as e:
            print(f"❌ Exception in friend request debug: {str(e)}")
            return False
    
    def run_debug(self):
        """Run all debug tests"""
        print("=" * 80)
        print("USER LOOKUP DEBUG SESSION")
        print("=" * 80)
        
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        # Test direct lookup
        user_data = self.test_user_lookup_direct()
        
        # Test user list search
        list_data = self.test_user_list_search()
        
        # Test seeded users
        seeded_data = self.test_seeded_users()
        
        # Debug friend request
        friend_success = self.test_friend_request_debug()
        
        print("\n" + "=" * 80)
        print("DEBUG SUMMARY")
        print("=" * 80)
        
        print(f"Direct user lookup: {'✅ SUCCESS' if user_data else '❌ FAILED'}")
        print(f"User list search: {'✅ SUCCESS' if list_data else '❌ FAILED'}")
        print(f"Seeded user test: {'✅ SUCCESS' if seeded_data else '❌ FAILED'}")
        print(f"Friend request: {'✅ SUCCESS' if friend_success else '❌ FAILED'}")
        
        if user_data and not friend_success:
            print("\n🔍 ANALYSIS:")
            print("   - User exists in MongoDB and can be retrieved directly")
            print("   - But friend request fails with 'User not found'")
            print("   - This suggests an issue in the friend request endpoint logic")
            print("   - Possible causes:")
            print("     1. Database query in friend endpoint is different")
            print("     2. User ID format mismatch")
            print("     3. Timing issue with database consistency")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    debugger = UserLookupDebugger()
    debugger.run_debug()