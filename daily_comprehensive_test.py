#!/usr/bin/env python3
"""
Comprehensive Daily.co Integration Test
Tests the exact scenario described in the review request.
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://socialsuper-app.preview.emergentagent.com/api"

class ComprehensiveDailyTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_step_1_daily_room_creation(self):
        """Step 1: Test Daily.co Room Creation"""
        print("🔸 STEP 1: Test Daily.co Room Creation")
        try:
            response = self.session.post(f"{BACKEND_URL}/daily/rooms?userId=demo_user&roomName=Test Audio Room")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['dailyRoomUrl', 'dailyRoomName', 'success']
                
                if all(field in data for field in required_fields):
                    self.daily_room_url = data['dailyRoomUrl']
                    self.daily_room_name = data['dailyRoomName']
                    self.log_result(
                        "Daily.co Room Creation", 
                        True, 
                        f"✅ Daily.co room created successfully",
                        f"Room Name: {self.daily_room_name}, URL: {self.daily_room_url}"
                    )
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result(
                        "Daily.co Room Creation", 
                        False, 
                        f"❌ Response missing required fields: {missing}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Daily.co Room Creation", 
                    False, 
                    f"❌ API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Daily.co Room Creation", False, f"❌ Exception: {str(e)}")
            return False
    
    def test_step_2_vibe_room_creation(self):
        """Step 2: Create a Vibe Room with Audio"""
        print("🔸 STEP 2: Create a Vibe Room with Audio")
        try:
            payload = {
                "name": "Test Audio Vibe Room",
                "description": "Testing audio",
                "category": "music",
                "isPrivate": False,
                "tags": ["test"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/rooms?userId=demo_user", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'name', 'dailyRoomUrl', 'dailyRoomName']
                
                if all(field in data for field in required_fields):
                    self.vibe_room_id = data['id']
                    self.vibe_daily_url = data['dailyRoomUrl']
                    self.vibe_daily_name = data['dailyRoomName']
                    self.log_result(
                        "Vibe Room with Audio", 
                        True, 
                        f"✅ Vibe Room created with Daily.co integration",
                        f"Room ID: {self.vibe_room_id}, Daily URL: {self.vibe_daily_url}"
                    )
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result(
                        "Vibe Room with Audio", 
                        False, 
                        f"❌ Response missing required fields: {missing}",
                        f"Available fields: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Vibe Room with Audio", 
                    False, 
                    f"❌ API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Vibe Room with Audio", False, f"❌ Exception: {str(e)}")
            return False
    
    def test_step_3_room_details(self):
        """Step 3: Get Room Details"""
        print("🔸 STEP 3: Get Room Details")
        if not hasattr(self, 'vibe_room_id'):
            self.log_result("Room Details Verification", False, "❌ No Vibe Room ID available from previous step")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/rooms/{self.vibe_room_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'dailyRoomUrl' in data:
                    self.log_result(
                        "Room Details Verification", 
                        True, 
                        f"✅ Room details contain dailyRoomUrl field",
                        f"Daily URL: {data['dailyRoomUrl']}, Participants: {len(data.get('participants', []))}"
                    )
                    return True
                else:
                    self.log_result(
                        "Room Details Verification", 
                        False, 
                        f"❌ Room details missing dailyRoomUrl field",
                        f"Available fields: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "Room Details Verification", 
                    False, 
                    f"❌ API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Room Details Verification", False, f"❌ Exception: {str(e)}")
            return False
    
    def test_step_4_daily_token(self):
        """Step 4: Create Daily Token"""
        print("🔸 STEP 4: Create Daily Token")
        if not hasattr(self, 'vibe_daily_name'):
            self.log_result("Daily Token Creation", False, "❌ No Daily room name available from previous step")
            return False
            
        try:
            response = self.session.post(f"{BACKEND_URL}/daily/token?roomName={self.vibe_daily_name}&userName=Demo User&isOwner=true")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'token' in data and 'success' in data:
                    self.log_result(
                        "Daily Token Creation", 
                        True, 
                        f"✅ Daily.co token created successfully",
                        f"Token length: {len(data['token'])}, Success: {data['success']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Daily Token Creation", 
                        False, 
                        f"❌ Response missing required fields",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Daily Token Creation", 
                    False, 
                    f"❌ API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Daily Token Creation", False, f"❌ Exception: {str(e)}")
            return False
    
    def test_api_key_validation(self):
        """Validate Daily.co API Key"""
        print("🔸 BONUS: Daily.co API Key Validation")
        try:
            # Test with the provided API key
            response = self.session.post(f"{BACKEND_URL}/daily/rooms?userId=test_validation&roomName=API Key Validation")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "API Key Validation", 
                        True, 
                        f"✅ Daily.co API key is valid and working",
                        f"API Key: c84172cc30949874adcdd45f4c8cf2819d6e9fc12628de00608f156662be0e79"
                    )
                    return True
            
            self.log_result(
                "API Key Validation", 
                False, 
                f"❌ Daily.co API key validation failed",
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
                
        except Exception as e:
            self.log_result("API Key Validation", False, f"❌ Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete test scenario from the review request"""
        print("🎵 COMPREHENSIVE DAILY.CO INTEGRATION TEST")
        print("Testing the exact scenario from the review request")
        print("=" * 70)
        print()
        
        # Run all test steps
        step1_success = self.test_step_1_daily_room_creation()
        step2_success = self.test_step_2_vibe_room_creation()
        step3_success = self.test_step_3_room_details()
        step4_success = self.test_step_4_daily_token()
        bonus_success = self.test_api_key_validation()
        
        # Summary
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        all_steps = [step1_success, step2_success, step3_success, step4_success]
        passed_steps = sum(all_steps)
        total_steps = len(all_steps)
        
        print(f"Core Test Steps: {passed_steps}/{total_steps} PASSED")
        print(f"Bonus Validation: {'PASSED' if bonus_success else 'FAILED'}")
        print()
        
        if passed_steps == total_steps:
            print("🎉 ALL CORE TESTS PASSED!")
            print("✅ Daily.co audio integration is working correctly")
            print("✅ User should no longer see 'Audio room not available' error")
            print()
            print("🔧 EXPECTED BEHAVIOR VERIFIED:")
            print("   ✓ Daily.co rooms are created successfully")
            print("   ✓ Vibe Rooms have dailyRoomUrl field populated")
            print("   ✓ Tokens are generated for joining rooms")
            print("   ✓ Complete audio integration flow is functional")
        else:
            print(f"⚠️  {total_steps - passed_steps} CORE TESTS FAILED")
            print("❌ Daily.co audio integration has issues")
            print("❌ User may still see 'Audio room not available' error")
            
            # Show failed steps
            step_names = ["Daily.co Room Creation", "Vibe Room with Audio", "Room Details", "Daily Token Creation"]
            for i, (step_name, success) in enumerate(zip(step_names, all_steps)):
                if not success:
                    print(f"   - Step {i+1}: {step_name} FAILED")
        
        return self.test_results

def main():
    """Main function"""
    tester = ComprehensiveDailyTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    core_tests = results[:4]  # First 4 are core tests
    failed_count = sum(1 for result in core_tests if not result['success'])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())