#!/usr/bin/env python3
"""
Test file upload with authenticated request
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://clm-backend-hfsi.onrender.com"

def test_file_upload():
    """Test file upload with authentication"""
    print("📁 Testing File Upload with Authentication...")

    # First, register and login to get access token
    register_data = {
        "email": f"upload_test_{int(datetime.now().timestamp())}@example.com",
        "password": "testpass123",
        "first_name": "Upload",
        "last_name": "Test"
    }

    # Register
    register_response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
    print(f"Registration: {register_response.status_code}")

    if register_response.status_code == 201:
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }

        login_response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        print(f"Login: {login_response.status_code}")

        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            headers = {'Authorization': f'Bearer {access_token}'}

            # Create test .txt file content
            test_content = """CONTRACT AGREEMENT

This is a test contract document created for API testing purposes.

PARTIES:
1. Test Company Inc.
2. Upload Test User

TERMS AND CONDITIONS:
1. This is a sample contract for testing file upload functionality
2. Generated automatically by API test script
3. Created on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

SIGNATURES:
___________________________    ___________________________
Test Company Inc.              Upload Test User
"""

            # Test file upload to contracts endpoint
            files = {
                'file': ('test_contract.txt', test_content, 'text/plain')
            }

            # Add any required form data for contract creation
            data = {
                'title': 'Test Contract Upload',
                'description': 'API test contract upload'
            }

            response = requests.post(
                f"{BASE_URL}/api/contracts/",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )

            result = {
                "timestamp": datetime.now().isoformat(),
                "method": "POST",
                "endpoint": "/api/contracts/",
                "description": "File upload test with .txt file and authentication",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "headers": dict(response.headers),
                "test_file_content": test_content[:100] + "..."  # First 100 chars
            }

            try:
                result["response_json"] = response.json()
            except:
                result["response_text"] = response.text

            print(f"📄 File upload result: {response.status_code}")
            if response.status_code >= 200 and response.status_code < 300:
                print("✅ File upload successful!")
            else:
                print("❌ File upload failed")

            return result

    return {
        "error": "Authentication failed",
        "registration_status": register_response.status_code,
        "login_status": login_response.status_code if 'login_response' in locals() else None
    }

def main():
    """Main function"""
    print("🚀 CLM Backend File Upload Test")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().isoformat()}")

    result = test_file_upload()

    # Save result
    with open('file_upload_test.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("💾 File upload test result saved to file_upload_test.json")

    # Summary
    if result.get('status_code') and result['status_code'] >= 200 and result['status_code'] < 300:
        print("✅ File upload test PASSED")
    else:
        print("❌ File upload test FAILED")
        print(f"   Status: {result.get('status_code', 'N/A')}")
        if 'response_json' in result:
            print(f"   Error: {result['response_json']}")

if __name__ == "__main__":
    main()