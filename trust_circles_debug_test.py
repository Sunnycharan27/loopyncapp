#!/usr/bin/env python3
"""
Debug test for Trust Circles endpoint to understand the backend issue
"""

import requests
import json

BACKEND_URL = "https://loopsuite.preview.emergentagent.com/api"
DEMO_USER_ID = "demo_user"

def test_trust_circles_debug():
    """Debug the trust circles creation issue"""
    
    # Test GET first
    print("Testing GET /api/trust-circles...")
    params = {'userId': DEMO_USER_ID}
    response = requests.get(f"{BACKEND_URL}/trust-circles", params=params)
    print(f"GET Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"GET Response: {data}")
        print(f"Number of circles: {len(data)}")
    else:
        print(f"GET Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test POST with minimal data
    print("Testing POST /api/trust-circles with minimal data...")
    params = {'createdBy': DEMO_USER_ID}
    payload = {
        "name": "Debug Test Circle",
        "description": "Testing trust circle creation",
        "icon": "🔵",
        "color": "from-blue-400 to-cyan-500",
        "members": []
    }
    
    response = requests.post(f"{BACKEND_URL}/trust-circles", params=params, json=payload)
    print(f"POST Status: {response.status_code}")
    print(f"POST Response: {response.text}")
    
    if response.status_code != 200:
        print("Trust circles creation has a backend bug (ObjectId serialization issue)")
        print("This is a known issue with MongoDB _id field not being excluded properly")

if __name__ == "__main__":
    test_trust_circles_debug()