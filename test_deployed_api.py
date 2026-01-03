#!/usr/bin/env python3
"""
Test script for CLM Backend API endpoints
Tests all available endpoints and saves responses to apiresponse.json
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "https://clm-backend-hfsi.onrender.com"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing {method} {endpoint}")
    if description:
        print(f"   {description}")

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}

        result = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "description": description,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
        }

        try:
            result["response_json"] = response.json()
        except:
            result["response_text"] = response.text

        if response.status_code >= 200 and response.status_code < 300:
            print(f"   ✅ Success: {response.status_code}")
        else:
            print(f"   ❌ Error: {response.status_code}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "description": description,
            "error": str(e)
        }

def test_file_upload():
    """Test file upload functionality"""
    print("\n📁 Testing file upload...")

    # Create a test .txt file
    test_content = "This is a test contract document.\nCreated for API testing purposes.\n\nContract terms:\n1. This is a sample contract\n2. For testing file upload functionality\n3. Generated on " + datetime.now().isoformat()

    files = {
        'file': ('test_contract.txt', test_content, 'text/plain')
    }

    # Test contract creation with file upload
    url = f"{BASE_URL}/api/contracts/"
    headers = {
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # This would need a valid token
    }

    try:
        response = requests.post(url, files=files, headers=headers, timeout=30)

        result = {
            "timestamp": datetime.now().isoformat(),
            "method": "POST",
            "endpoint": "/api/contracts/",
            "description": "File upload test with .txt file",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
        }

        try:
            result["response_json"] = response.json()
        except:
            result["response_text"] = response.text

        print(f"   📄 File upload result: {response.status_code}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"   ❌ File upload failed: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "method": "POST",
            "endpoint": "/api/contracts/",
            "description": "File upload test with .txt file",
            "error": str(e)
        }

def main():
    """Main test function"""
    print("🚀 Starting CLM Backend API Tests")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().isoformat()}")

    results = []

    # Test health endpoint (if exists)
    results.append(test_endpoint("GET", "/", description="Root endpoint check"))

    # Test authentication endpoints
    auth_endpoints = [
        ("GET", "/api/auth/me/", None, None, "Get current user (requires auth)"),
        ("POST", "/api/auth/login/", {
            "email": "test@example.com",
            "password": "testpass123"
        }, None, "User login"),
        ("POST", "/api/auth/register/", {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }, None, "User registration"),
        ("POST", "/api/auth/forgot-password/", {
            "email": "test@example.com"
        }, None, "Forgot password"),
    ]

    for method, endpoint, data, headers, description in auth_endpoints:
        results.append(test_endpoint(method, endpoint, data, headers, description))
        time.sleep(1)  # Rate limiting

    # Test contract-related endpoints (these might require authentication)
    contract_endpoints = [
        ("GET", "/api/contract-templates/", None, None, "List contract templates"),
        ("GET", "/api/clauses/", None, None, "List clauses"),
        ("GET", "/api/contracts/", None, None, "List contracts"),
        ("GET", "/api/generation-jobs/", None, None, "List generation jobs"),
    ]

    for method, endpoint, data, headers, description in contract_endpoints:
        results.append(test_endpoint(method, endpoint, data, headers, description))
        time.sleep(1)  # Rate limiting

    # Test file upload
    results.append(test_file_upload())

    # Save results to JSON file
    output_file = "apiresponse.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to {output_file}")
    print(f"📊 Total endpoints tested: {len(results)}")

    # Summary
    success_count = sum(1 for r in results if r.get('status_code', 0) >= 200 and r.get('status_code', 0) < 300)
    print(f"✅ Successful requests: {success_count}")
    print(f"❌ Failed requests: {len(results) - success_count}")

    print(f"\n🏁 Testing completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()