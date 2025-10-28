#!/usr/bin/env python3
"""
Complete VibeRooms Agora.io Audio Integration Test
Testing all requested endpoints and scenarios for Agora integration
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://loopconnect-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Demo user credentials
DEMO_EMAIL = "demo@loopync.com"
DEMO_PASSWORD = "password123"

class AgoraVibeRoomTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.demo_user_id = None
        self.test_room_id = None
        self.agora_channel = None
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def authenticate_demo_user(self):
        """Authenticate with demo user credentials"""
        self.log("🔐 Authenticating demo user...")
        
        response = self.session.post(f"{API_BASE}/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["token"]
            self.demo_user_id = data["user"]["id"]
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            self.log(f"✅ Demo user authenticated: {data['user']['name']} ({data['user']['email']})")
            return True
        else:
            self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def test_create_viberoom_with_agora(self):
        """Test 1: Create a new VibeRoom with Agora integration"""
        self.log("\n🎵 TEST 1: Create VibeRoom with Agora Integration")
        
        room_data = {
            "name": "Test Agora VibeRoom",
            "description": "Testing Agora.io audio integration",
            "category": "music",
            "isPrivate": False,
            "tags": ["test", "agora", "audio"]
        }
        
        response = self.session.post(f"{API_BASE}/rooms?userId={self.demo_user_id}", json=room_data)
        
        if response.status_code == 200:
            room = response.json()
            self.test_room_id = room["id"]
            self.agora_channel = room.get("agoraChannel")
            
            self.log(f"✅ VibeRoom created successfully")
            self.log(f"   Room ID: {room['id']}")
            self.log(f"   Room Name: {room['name']}")
            self.log(f"   Host ID: {room['hostId']}")
            self.log(f"   Agora Channel: {room.get('agoraChannel', 'NOT FOUND')}")
            
            # Verify required fields
            required_fields = ["id", "name", "hostId", "participants", "agoraChannel"]
            missing_fields = [field for field in required_fields if field not in room]
            
            if missing_fields:
                self.log(f"⚠️  Missing required fields: {missing_fields}")
                return False
            
            if not room.get("agoraChannel"):
                self.log("❌ agoraChannel field is missing or empty")
                return False
                
            return True
        else:
            self.log(f"❌ Room creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_verify_room_agora_field(self):
        """Test 2: Verify the room has agoraChannel field"""
        self.log("\n🔍 TEST 2: Verify Room has Agora Channel Field")
        
        if not self.test_room_id:
            self.log("❌ No test room ID available")
            return False
        
        response = self.session.get(f"{API_BASE}/rooms/{self.test_room_id}")
        
        if response.status_code == 200:
            room = response.json()
            agora_channel = room.get("agoraChannel")
            
            if agora_channel:
                self.log(f"✅ Room has agoraChannel field: {agora_channel}")
                self.agora_channel = agora_channel
                return True
            else:
                self.log("❌ Room missing agoraChannel field")
                return False
        else:
            self.log(f"❌ Failed to get room details: {response.status_code} - {response.text}")
            return False
    
    def test_generate_agora_token_publisher(self):
        """Test 3: Generate an Agora token for joining as a host/publisher"""
        self.log("\n🎤 TEST 3: Generate Agora Token for Publisher (Host)")
        
        if not self.agora_channel:
            self.log("❌ No Agora channel available")
            return False
        
        params = {
            "channelName": self.agora_channel,
            "uid": 12345,
            "role": "publisher"
        }
        
        response = self.session.post(f"{API_BASE}/agora/token", params=params)
        
        if response.status_code == 200:
            token_data = response.json()
            
            self.log(f"✅ Publisher token generated successfully")
            self.log(f"   App ID: {token_data.get('appId', 'NOT FOUND')}")
            self.log(f"   Channel: {token_data.get('channelName', 'NOT FOUND')}")
            self.log(f"   UID: {token_data.get('uid', 'NOT FOUND')}")
            self.log(f"   Token Length: {len(token_data.get('token', ''))}")
            
            # Verify required properties
            required_props = ["token", "appId", "channelName", "uid", "success"]
            missing_props = [prop for prop in required_props if prop not in token_data]
            
            if missing_props:
                self.log(f"⚠️  Missing token properties: {missing_props}")
                return False
            
            if not token_data.get("token"):
                self.log("❌ Token is empty")
                return False
                
            return True
        else:
            self.log(f"❌ Publisher token generation failed: {response.status_code} - {response.text}")
            return False
    
    def test_generate_agora_token_subscriber(self):
        """Test 4: Generate an Agora token for joining as an audience/subscriber"""
        self.log("\n👂 TEST 4: Generate Agora Token for Subscriber (Audience)")
        
        if not self.agora_channel:
            self.log("❌ No Agora channel available")
            return False
        
        params = {
            "channelName": self.agora_channel,
            "uid": 67890,
            "role": "subscriber"
        }
        
        response = self.session.post(f"{API_BASE}/agora/token", params=params)
        
        if response.status_code == 200:
            token_data = response.json()
            
            self.log(f"✅ Subscriber token generated successfully")
            self.log(f"   App ID: {token_data.get('appId', 'NOT FOUND')}")
            self.log(f"   Channel: {token_data.get('channelName', 'NOT FOUND')}")
            self.log(f"   UID: {token_data.get('uid', 'NOT FOUND')}")
            self.log(f"   Token Length: {len(token_data.get('token', ''))}")
            
            # Verify tokens are different for different roles
            # (We can't easily compare without storing the previous token, but we can verify structure)
            if not token_data.get("token"):
                self.log("❌ Subscriber token is empty")
                return False
                
            return True
        else:
            self.log(f"❌ Subscriber token generation failed: {response.status_code} - {response.text}")
            return False
    
    def test_verify_tokens_different_roles(self):
        """Test 5: Verify tokens are different for publisher vs subscriber"""
        self.log("\n🔄 TEST 5: Verify Token Differences for Different Roles")
        
        if not self.agora_channel:
            self.log("❌ No Agora channel available")
            return False
        
        # Generate publisher token
        pub_response = self.session.post(f"{API_BASE}/agora/token", params={
            "channelName": self.agora_channel,
            "uid": 11111,
            "role": "publisher"
        })
        
        # Generate subscriber token
        sub_response = self.session.post(f"{API_BASE}/agora/token", params={
            "channelName": self.agora_channel,
            "uid": 22222,
            "role": "subscriber"
        })
        
        if pub_response.status_code == 200 and sub_response.status_code == 200:
            pub_token = pub_response.json().get("token", "")
            sub_token = sub_response.json().get("token", "")
            
            if pub_token and sub_token and pub_token != sub_token:
                self.log("✅ Publisher and subscriber tokens are different (role differentiation working)")
                return True
            else:
                self.log("❌ Tokens are identical or empty (role differentiation not working)")
                return False
        else:
            self.log("❌ Failed to generate tokens for comparison")
            return False
    
    def test_join_room(self):
        """Test 6: Test that room joining works correctly"""
        self.log("\n🚪 TEST 6: Join VibeRoom")
        
        if not self.test_room_id:
            self.log("❌ No test room ID available")
            return False
        
        response = self.session.post(f"{API_BASE}/rooms/{self.test_room_id}/join?userId={self.demo_user_id}")
        
        if response.status_code == 200:
            result = response.json()
            self.log(f"✅ Successfully joined room")
            self.log(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            self.log(f"❌ Room join failed: {response.status_code} - {response.text}")
            return False
    
    def test_all_responses_200_ok(self):
        """Test 7: Verify all responses are 200 OK"""
        self.log("\n✅ TEST 7: Verify All Responses are 200 OK")
        
        test_endpoints = [
            ("POST", f"/rooms?userId={self.demo_user_id}", {"name": "Status Test Room", "category": "test"}),
            ("GET", f"/rooms/{self.test_room_id}" if self.test_room_id else "/rooms", None),
            ("POST", f"/agora/token?channelName=test_channel&uid=99999&role=publisher", None),
            ("POST", f"/rooms/{self.test_room_id}/join?userId={self.demo_user_id}" if self.test_room_id else None, None)
        ]
        
        all_200 = True
        for method, endpoint, data in test_endpoints:
            if endpoint is None:
                continue
                
            if method == "POST":
                if data:
                    response = self.session.post(f"{API_BASE}{endpoint}", json=data)
                else:
                    response = self.session.post(f"{API_BASE}{endpoint}")
            else:
                response = self.session.get(f"{API_BASE}{endpoint}")
            
            if response.status_code == 200:
                self.log(f"✅ {method} {endpoint}: 200 OK")
            else:
                self.log(f"❌ {method} {endpoint}: {response.status_code}")
                all_200 = False
        
        return all_200
    
    def run_comprehensive_test(self):
        """Run all Agora VibeRoom integration tests"""
        self.log("🎵 STARTING COMPLETE VIBEROOM AGORA.IO AUDIO INTEGRATION TESTING")
        self.log("=" * 80)
        
        # Test results tracking
        test_results = []
        
        # Authentication
        if not self.authenticate_demo_user():
            self.log("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            ("Create VibeRoom with Agora Integration", self.test_create_viberoom_with_agora),
            ("Verify Room has agoraChannel Field", self.test_verify_room_agora_field),
            ("Generate Agora Token for Publisher", self.test_generate_agora_token_publisher),
            ("Generate Agora Token for Subscriber", self.test_generate_agora_token_subscriber),
            ("Verify Token Role Differentiation", self.test_verify_tokens_different_roles),
            ("Join VibeRoom", self.test_join_room),
            ("Verify All Responses 200 OK", self.test_all_responses_200_ok)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                self.log(f"❌ {test_name} failed with exception: {str(e)}")
                test_results.append((test_name, False))
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("🎯 AGORA VIBEROOM INTEGRATION TEST SUMMARY")
        self.log("=" * 80)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{status}: {test_name}")
        
        self.log(f"\n📊 OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL AGORA VIBEROOM INTEGRATION TESTS PASSED!")
            self.log("🚀 Agora.io audio integration is fully functional and production-ready")
            return True
        else:
            self.log(f"⚠️  {total - passed} test(s) failed - Agora integration needs attention")
            return False

def main():
    """Main test execution"""
    tester = AgoraVibeRoomTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()