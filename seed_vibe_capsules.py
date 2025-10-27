#!/usr/bin/env python3
"""
Seed Vibe Capsules for Testing
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BACKEND_URL = "https://chatvibes-7.preview.emergentagent.com/api"

print("=" * 80)
print("SEEDING VIBE CAPSULES")
print("=" * 80)

# Create a few test capsules for different users
capsules_to_create = [
    {
        "userId": "u1",
        "mediaType": "image",
        "mediaUrl": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400",
        "caption": "Good morning vibes! ☀️",
        "mood": "happy"
    },
    {
        "userId": "u2",
        "mediaType": "image", 
        "mediaUrl": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400",
        "caption": "Coding all night 💻",
        "mood": "focused"
    },
    {
        "userId": "u3",
        "mediaType": "image",
        "mediaUrl": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400",
        "caption": "Art in progress 🎨",
        "mood": "creative"
    }
]

created_count = 0
for capsule_data in capsules_to_create:
    try:
        print(f"\n📤 Creating capsule for user {capsule_data['userId']}...")
        user_id = capsule_data.pop('userId')
        response = requests.post(
            f"{BACKEND_URL}/capsules",
            params={"authorId": user_id},
            json=capsule_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Capsule created: {data.get('id')}")
            print(f"   Caption: {capsule_data['caption']}")
            created_count += 1
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
print(f"VIBE CAPSULES SEEDING COMPLETE - Created {created_count}/{len(capsules_to_create)} capsules")
print("=" * 80)
print("\n🎉 You can now view stories on the Home page!")
