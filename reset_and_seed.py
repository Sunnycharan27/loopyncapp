#!/usr/bin/env python3
"""
Complete Database Reset and Fresh Seed
Clears all data and creates perfect user onboarding system
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"

print("=" * 80)
print("COMPLETE DATABASE RESET AND FRESH SEED")
print("=" * 80)

# Step 1: Seed the database (this will clear existing data first)
print("\n1️⃣ Clearing database and seeding fresh data...")
try:
    response = requests.post(f"{BACKEND_URL}/seed")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Database reset complete!")
        print(f"   - Created {data.get('users', 0)} users")
        print(f"   - Created {data.get('posts', 0)} posts")
        print(f"   - Created {data.get('reels', 0)} reels")
        print(f"   - Created {data.get('tribes', 0)} tribes")
    else:
        print(f"❌ Seed failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)

# Step 2: Test demo user login
print("\n2️⃣ Testing demo user login...")
try:
    login_payload = {
        "email": "demo@loopync.com",
        "password": "password123"
    }
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', {})
        print(f"✅ Demo user login successful!")
        print(f"   - User ID: {user.get('id')}")
        print(f"   - Name: {user.get('name')}")
        print(f"   - Email: {user.get('email')}")
        print(f"   - Friends: {len(user.get('friends', []))} friends")
        
        demo_token = data.get('token')
        demo_user_id = user.get('id')
    else:
        print(f"❌ Demo login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)

# Step 3: Test new user signup
print("\n3️⃣ Testing new user signup...")
try:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    signup_payload = {
        "email": f"testuser_{timestamp}@example.com",
        "password": "TestPass123!",
        "name": "Test User",
        "handle": f"testuser_{timestamp}",
        "phone_number": "+919876543210"
    }
    response = requests.post(f"{BACKEND_URL}/auth/signup", json=signup_payload)
    
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', {})
        print(f"✅ New user signup successful!")
        print(f"   - User ID: {user.get('id')}")
        print(f"   - Name: {user.get('name')}")
        print(f"   - Email: {user.get('email')}")
        print(f"   - Handle: @{user.get('handle')}")
    else:
        print(f"❌ Signup failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Step 4: Verify seeded users
print("\n4️⃣ Verifying seeded users...")
try:
    seeded_users = ['u1', 'u2', 'u3']
    for user_id in seeded_users:
        response = requests.get(f"{BACKEND_URL}/users/{user_id}")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User {user_id}: {user.get('name')} (@{user.get('handle')})")
        else:
            print(f"❌ User {user_id}: Not found")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
print("DATABASE RESET COMPLETE - READY FOR TESTING")
print("=" * 80)
print("\n📝 Test Credentials:")
print("   Email: demo@loopync.com")
print("   Password: password123")
print("\n🚀 You can now login and test the application!")
