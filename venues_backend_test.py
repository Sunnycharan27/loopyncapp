#!/usr/bin/env python3
"""
Backend Test Suite for Venues Update - Temples with Timings and More Information Button
Testing the venue data structure to ensure proper categorization and timing information.
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

class VenuesBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_1_reseed_database(self):
        """Test 1: Reseed Database - POST /api/seed"""
        try:
            print("🔄 TEST 1: Reseeding Database...")
            response = self.session.post(f"{self.backend_url}/seed")
            
            if response.status_code == 200:
                data = response.json()
                venues_count = data.get('venues', 0)
                
                if venues_count > 0:
                    self.log_test(
                        "Reseed Database", 
                        True, 
                        f"Database reseeded successfully with {venues_count} venues",
                        {"venues_count": venues_count, "response": data}
                    )
                    return True
                else:
                    self.log_test(
                        "Reseed Database", 
                        False, 
                        "Database seeded but no venues found",
                        {"response": data}
                    )
                    return False
            else:
                self.log_test(
                    "Reseed Database", 
                    False, 
                    f"Seed endpoint failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Reseed Database", 
                False, 
                f"Exception during seeding: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def test_2_get_all_venues(self):
        """Test 2: Get All Venues - GET /api/venues"""
        try:
            print("🔄 TEST 2: Getting All Venues...")
            response = self.session.get(f"{self.backend_url}/venues")
            
            if response.status_code == 200:
                venues = response.json()
                
                if isinstance(venues, list) and len(venues) > 0:
                    # Check if venues have required fields
                    required_fields = ['id', 'name', 'category', 'timings']
                    venues_with_all_fields = []
                    venues_missing_fields = []
                    
                    for venue in venues:
                        missing_fields = [field for field in required_fields if field not in venue]
                        if missing_fields:
                            venues_missing_fields.append({
                                "venue_id": venue.get('id', 'unknown'),
                                "venue_name": venue.get('name', 'unknown'),
                                "missing_fields": missing_fields
                            })
                        else:
                            venues_with_all_fields.append(venue)
                    
                    if len(venues_missing_fields) == 0:
                        self.log_test(
                            "Get All Venues", 
                            True, 
                            f"Retrieved {len(venues)} venues, all have required fields (id, name, category, timings)",
                            {
                                "total_venues": len(venues),
                                "venues_with_all_fields": len(venues_with_all_fields),
                                "sample_venue": venues[0] if venues else None
                            }
                        )
                        return venues
                    else:
                        self.log_test(
                            "Get All Venues", 
                            False, 
                            f"Retrieved {len(venues)} venues, but {len(venues_missing_fields)} venues missing required fields",
                            {
                                "total_venues": len(venues),
                                "venues_missing_fields": venues_missing_fields[:3]  # Show first 3
                            }
                        )
                        return venues  # Return anyway for further testing
                else:
                    self.log_test(
                        "Get All Venues", 
                        False, 
                        "No venues found in response",
                        {"response": venues}
                    )
                    return []
            else:
                self.log_test(
                    "Get All Venues", 
                    False, 
                    f"Venues endpoint failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return []
                
        except Exception as e:
            self.log_test(
                "Get All Venues", 
                False, 
                f"Exception during venues retrieval: {str(e)}",
                {"exception": str(e)}
            )
            return []

    def test_3_verify_temple_venues(self, venues: List[Dict]):
        """Test 3: Verify Temple Venues Have Timings"""
        try:
            print("🔄 TEST 3: Verifying Temple Venues...")
            
            # Expected temple venues from the review request
            expected_temples = [
                {"id": "v7", "name": "Birla Mandir"},
                {"id": "v8", "name": "Chilkur Balaji Temple"},
                {"id": "v9", "name": "Jagannath Temple"}
            ]
            
            temple_venues = [v for v in venues if v.get('category') == 'temple']
            temple_test_results = []
            
            for expected_temple in expected_temples:
                temple_venue = next((v for v in temple_venues if v.get('id') == expected_temple['id']), None)
                
                if temple_venue:
                    # Check required fields for temples
                    has_category = temple_venue.get('category') == 'temple'
                    has_timings = 'timings' in temple_venue and temple_venue['timings']
                    has_name_match = expected_temple['name'].lower() in temple_venue.get('name', '').lower()
                    
                    temple_test_results.append({
                        "temple_id": expected_temple['id'],
                        "temple_name": temple_venue.get('name'),
                        "has_category": has_category,
                        "has_timings": has_timings,
                        "has_name_match": has_name_match,
                        "timings": temple_venue.get('timings'),
                        "category": temple_venue.get('category'),
                        "all_checks_passed": has_category and has_timings and has_name_match
                    })
                else:
                    temple_test_results.append({
                        "temple_id": expected_temple['id'],
                        "temple_name": expected_temple['name'],
                        "found": False,
                        "all_checks_passed": False
                    })
            
            # Check overall results
            all_temples_passed = all(result.get('all_checks_passed', False) for result in temple_test_results)
            temples_found = len([r for r in temple_test_results if r.get('found', True)])
            
            if all_temples_passed and temples_found == len(expected_temples):
                self.log_test(
                    "Verify Temple Venues", 
                    True, 
                    f"All {len(expected_temples)} temple venues found with correct category and timings",
                    {
                        "total_temples_in_db": len(temple_venues),
                        "expected_temples_found": temples_found,
                        "temple_details": temple_test_results
                    }
                )
                return True
            else:
                failed_temples = [r for r in temple_test_results if not r.get('all_checks_passed', False)]
                self.log_test(
                    "Verify Temple Venues", 
                    False, 
                    f"Temple verification failed. {len(failed_temples)} temples have issues",
                    {
                        "total_temples_in_db": len(temple_venues),
                        "expected_temples_found": temples_found,
                        "failed_temples": failed_temples,
                        "all_temple_results": temple_test_results
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Temple Venues", 
                False, 
                f"Exception during temple verification: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def test_4_verify_mosque_venues(self, venues: List[Dict]):
        """Test 4: Verify Mosque Has Timings"""
        try:
            print("🔄 TEST 4: Verifying Mosque Venues...")
            
            # Expected mosque from the review request
            expected_mosque = {"id": "v19", "name": "Mecca Masjid"}
            
            mosque_venues = [v for v in venues if v.get('category') == 'mosque']
            mosque_venue = next((v for v in mosque_venues if v.get('id') == expected_mosque['id']), None)
            
            if mosque_venue:
                has_category = mosque_venue.get('category') == 'mosque'
                has_timings = 'timings' in mosque_venue and mosque_venue['timings']
                has_name_match = expected_mosque['name'].lower() in mosque_venue.get('name', '').lower()
                
                mosque_details = {
                    "mosque_id": expected_mosque['id'],
                    "mosque_name": mosque_venue.get('name'),
                    "has_category": has_category,
                    "has_timings": has_timings,
                    "has_name_match": has_name_match,
                    "timings": mosque_venue.get('timings'),
                    "category": mosque_venue.get('category'),
                    "all_checks_passed": has_category and has_timings and has_name_match
                }
                
                if mosque_details['all_checks_passed']:
                    self.log_test(
                        "Verify Mosque Venues", 
                        True, 
                        f"Mosque venue {mosque_venue.get('name')} found with correct category and timings",
                        {
                            "total_mosques_in_db": len(mosque_venues),
                            "mosque_details": mosque_details
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Verify Mosque Venues", 
                        False, 
                        f"Mosque venue found but missing required fields",
                        {
                            "total_mosques_in_db": len(mosque_venues),
                            "mosque_details": mosque_details
                        }
                    )
                    return False
            else:
                self.log_test(
                    "Verify Mosque Venues", 
                    False, 
                    f"Expected mosque {expected_mosque['name']} (ID: {expected_mosque['id']}) not found",
                    {
                        "total_mosques_in_db": len(mosque_venues),
                        "available_mosques": [{"id": m.get('id'), "name": m.get('name')} for m in mosque_venues]
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Mosque Venues", 
                False, 
                f"Exception during mosque verification: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def test_5_verify_cafe_venues(self, venues: List[Dict]):
        """Test 5: Verify Cafes Have Timings"""
        try:
            print("🔄 TEST 5: Verifying Cafe Venues...")
            
            # Expected cafe from the review request
            expected_cafe = {"id": "v1", "name": "Concu Bakery"}
            
            cafe_venues = [v for v in venues if v.get('category') == 'cafe']
            cafe_venue = next((v for v in cafe_venues if v.get('id') == expected_cafe['id']), None)
            
            if cafe_venue:
                has_category = cafe_venue.get('category') == 'cafe'
                has_timings = 'timings' in cafe_venue and cafe_venue['timings']
                has_name_match = expected_cafe['name'].lower() in cafe_venue.get('name', '').lower()
                
                cafe_details = {
                    "cafe_id": expected_cafe['id'],
                    "cafe_name": cafe_venue.get('name'),
                    "has_category": has_category,
                    "has_timings": has_timings,
                    "has_name_match": has_name_match,
                    "timings": cafe_venue.get('timings'),
                    "category": cafe_venue.get('category'),
                    "all_checks_passed": has_category and has_timings and has_name_match
                }
                
                if cafe_details['all_checks_passed']:
                    self.log_test(
                        "Verify Cafe Venues", 
                        True, 
                        f"Cafe venue {cafe_venue.get('name')} found with correct category and timings",
                        {
                            "total_cafes_in_db": len(cafe_venues),
                            "cafe_details": cafe_details
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Verify Cafe Venues", 
                        False, 
                        f"Cafe venue found but missing required fields",
                        {
                            "total_cafes_in_db": len(cafe_venues),
                            "cafe_details": cafe_details
                        }
                    )
                    return False
            else:
                self.log_test(
                    "Verify Cafe Venues", 
                    False, 
                    f"Expected cafe {expected_cafe['name']} (ID: {expected_cafe['id']}) not found",
                    {
                        "total_cafes_in_db": len(cafe_venues),
                        "available_cafes": [{"id": c.get('id'), "name": c.get('name')} for c in cafe_venues]
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Cafe Venues", 
                False, 
                f"Exception during cafe verification: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def test_6_verify_restaurant_venues(self, venues: List[Dict]):
        """Test 6: Verify Restaurant Has Timings"""
        try:
            print("🔄 TEST 6: Verifying Restaurant Venues...")
            
            # Expected restaurant from the review request
            expected_restaurant = {"id": "v4", "name": "Paradise Biryani"}
            
            restaurant_venues = [v for v in venues if v.get('category') == 'restaurant']
            restaurant_venue = next((v for v in restaurant_venues if v.get('id') == expected_restaurant['id']), None)
            
            if restaurant_venue:
                has_category = restaurant_venue.get('category') == 'restaurant'
                has_timings = 'timings' in restaurant_venue and restaurant_venue['timings']
                has_name_match = expected_restaurant['name'].lower() in restaurant_venue.get('name', '').lower()
                
                restaurant_details = {
                    "restaurant_id": expected_restaurant['id'],
                    "restaurant_name": restaurant_venue.get('name'),
                    "has_category": has_category,
                    "has_timings": has_timings,
                    "has_name_match": has_name_match,
                    "timings": restaurant_venue.get('timings'),
                    "category": restaurant_venue.get('category'),
                    "all_checks_passed": has_category and has_timings and has_name_match
                }
                
                if restaurant_details['all_checks_passed']:
                    self.log_test(
                        "Verify Restaurant Venues", 
                        True, 
                        f"Restaurant venue {restaurant_venue.get('name')} found with correct category and timings",
                        {
                            "total_restaurants_in_db": len(restaurant_venues),
                            "restaurant_details": restaurant_details
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Verify Restaurant Venues", 
                        False, 
                        f"Restaurant venue found but missing required fields",
                        {
                            "total_restaurants_in_db": len(restaurant_venues),
                            "restaurant_details": restaurant_details
                        }
                    )
                    return False
            else:
                self.log_test(
                    "Verify Restaurant Venues", 
                    False, 
                    f"Expected restaurant {expected_restaurant['name']} (ID: {expected_restaurant['id']}) not found",
                    {
                        "total_restaurants_in_db": len(restaurant_venues),
                        "available_restaurants": [{"id": r.get('id'), "name": r.get('name')} for r in restaurant_venues]
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Restaurant Venues", 
                False, 
                f"Exception during restaurant verification: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def test_7_verify_all_venues_structure(self, venues: List[Dict]):
        """Test 7: Verify All Venues Have Required Fields"""
        try:
            print("🔄 TEST 7: Verifying All Venues Data Structure...")
            
            required_fields = ['category', 'timings']
            venues_analysis = {
                'total_venues': len(venues),
                'venues_with_category': 0,
                'venues_with_timings': 0,
                'venues_with_both': 0,
                'category_breakdown': {},
                'venues_missing_fields': []
            }
            
            for venue in venues:
                has_category = 'category' in venue and venue['category']
                has_timings = 'timings' in venue and venue['timings']
                
                if has_category:
                    venues_analysis['venues_with_category'] += 1
                    category = venue['category']
                    venues_analysis['category_breakdown'][category] = venues_analysis['category_breakdown'].get(category, 0) + 1
                
                if has_timings:
                    venues_analysis['venues_with_timings'] += 1
                
                if has_category and has_timings:
                    venues_analysis['venues_with_both'] += 1
                else:
                    missing_fields = []
                    if not has_category:
                        missing_fields.append('category')
                    if not has_timings:
                        missing_fields.append('timings')
                    
                    venues_analysis['venues_missing_fields'].append({
                        'id': venue.get('id'),
                        'name': venue.get('name'),
                        'missing_fields': missing_fields
                    })
            
            # Check if all venues have required fields
            all_venues_compliant = venues_analysis['venues_with_both'] == venues_analysis['total_venues']
            
            if all_venues_compliant:
                self.log_test(
                    "Verify All Venues Structure", 
                    True, 
                    f"All {venues_analysis['total_venues']} venues have required 'category' and 'timings' fields",
                    venues_analysis
                )
                return True
            else:
                missing_count = len(venues_analysis['venues_missing_fields'])
                self.log_test(
                    "Verify All Venues Structure", 
                    False, 
                    f"{missing_count} out of {venues_analysis['total_venues']} venues missing required fields",
                    venues_analysis
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify All Venues Structure", 
                False, 
                f"Exception during venues structure verification: {str(e)}",
                {"exception": str(e)}
            )
            return False

    def run_all_tests(self):
        """Run all venue tests in sequence"""
        print("🚀 Starting Venues Backend Testing...")
        print("=" * 80)
        
        # Test 1: Reseed Database
        if not self.test_1_reseed_database():
            print("❌ Critical: Database seeding failed. Cannot continue with venue tests.")
            return False
        
        # Test 2: Get All Venues
        venues = self.test_2_get_all_venues()
        if not venues:
            print("❌ Critical: No venues retrieved. Cannot continue with venue verification tests.")
            return False
        
        # Test 3-7: Venue verification tests
        test_results = []
        test_results.append(self.test_3_verify_temple_venues(venues))
        test_results.append(self.test_4_verify_mosque_venues(venues))
        test_results.append(self.test_5_verify_cafe_venues(venues))
        test_results.append(self.test_6_verify_restaurant_venues(venues))
        test_results.append(self.test_7_verify_all_venues_structure(venues))
        
        # Summary
        print("=" * 80)
        print("📊 VENUES BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['message']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   - {result['test']}: {result['message']}")
        
        print("=" * 80)
        
        # Return overall success
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = VenuesBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL VENUES BACKEND TESTS PASSED!")
        sys.exit(0)
    else:
        print("💥 SOME VENUES BACKEND TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()