"""
Quick test script to verify Gemini API integration
"""
import requests
import json
import sys

# Force UTF-8 for output if possible, but use safe chars
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("=" * 60)
print("Testing Mental Wellness Journal - Gemini API Integration")
print("=" * 60)

# Test 1: Start a chat session
print("\n1. Testing /api/chat/start endpoint...")
try:
    response = session.post(f"{BASE_URL}/api/chat/start", json={})
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [SUCCESS]")
        print(f"   Message: {data.get('message', '')[:100]}...")
    else:
        print(f"   [ERROR]: {response.text}")
except Exception as e:
    print(f"   [EXCEPTION]: {str(e)}")

# Test 2: Send a message
print("\n2. Testing /api/chat/message endpoint...")
try:
    response = session.post(
        f"{BASE_URL}/api/chat/message",
        json={"message": "Oggi e stata una bella giornata"}
    )
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [SUCCESS]")
        print(f"   Response: {data.get('response', '')[:150]}...")
    else:
        print(f"   [ERROR]: {response.text}")
except Exception as e:
    print(f"   [EXCEPTION]: {str(e)}")

# Test 3: Get wellness suggestions
print("\n3. Testing /api/wellness/suggestions endpoint...")
try:
    response = session.get(f"{BASE_URL}/api/wellness/suggestions")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [SUCCESS]")
        if 'summary' in data:
            print(f"   Summary: {data['summary'][:100]}...")
    else:
        print(f"   [ERROR]: {response.text}")
except Exception as e:
    print(f"   [EXCEPTION]: {str(e)}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
