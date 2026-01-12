#!/usr/bin/env python
import os
import django
import json
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User

client = Client()

# Register and login
print("=" * 80)
print("AUTHENTICATING...")
print("=" * 80)

register_data = {
    "email": f"testuser_debug@example.com",
    "password": "TestPass123!@#",
    "full_name": "Test User"
}
resp = client.post('/api/auth/register/', json.dumps(register_data), content_type='application/json')
print(f"Register: {resp.status_code}")

login_data = {"email": "testuser_debug@example.com", "password": "TestPass123!@#"}
resp = client.post('/api/auth/login/', json.dumps(login_data), content_type='application/json')
print(f"Login: {resp.status_code}")
if resp.status_code == 200:
    token = resp.json().get('access')
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
else:
    print(f"Login failed: {resp.json()}")
    exit(1)

# Test POST endpoints and capture errors
tests = [
    {
        "name": "Create Contract",
        "method": "POST",
        "url": "/api/contracts/",
        "data": {
            "title": "Test Contract",
            "description": "Test Description",
            "status": "draft"
        }
    },
    {
        "name": "Create Template",
        "method": "POST",
        "url": "/api/contract-templates/",
        "data": {
            "name": "Test Template",
            "description": "Test Template Description",
            "category": "Standard"
        }
    },
    {
        "name": "Create Notification",
        "method": "POST",
        "url": "/api/notifications/",
        "data": {
            "message": "Test notification",
            "notification_type": "email",
            "recipient": "test@example.com"
        }
    },
    {
        "name": "Create Workflow",
        "method": "POST",
        "url": "/api/workflows/",
        "data": {
            "name": "Test Workflow",
            "description": "Test workflow description",
            "steps": []
        }
    },
    {
        "name": "Create Metadata Field",
        "method": "POST",
        "url": "/api/metadata/fields/",
        "data": {
            "field_name": "test_field",
            "field_type": "string",
            "description": "Test field"
        }
    }
]

print("\n" + "=" * 80)
print("DEBUGGING POST ENDPOINTS - CAPTURING ERRORS")
print("=" * 80)

for test in tests:
    print(f"\n{test['name']}")
    print("-" * 40)
    
    if test['method'] == "POST":
        resp = client.post(
            test['url'],
            json.dumps(test['data']),
            content_type='application/json',
            **headers
        )
    
    print(f"Status Code: {resp.status_code}")
    try:
        response_data = resp.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response: {resp.content}")
    
    # If successful, try to get the ID for version/clone tests
    if resp.status_code in [200, 201] and 'contracts' in test['url']:
        contract_id = resp.json().get('id')
        if contract_id:
            # Test version creation
            print(f"\n  Create Version for Contract {contract_id}")
            print("  " + "-" * 36)
            version_resp = client.post(
                f"/api/contracts/{contract_id}/create-version/",
                json.dumps({"description": "Version 1"}),
                content_type='application/json',
                **headers
            )
            print(f"  Status Code: {version_resp.status_code}")
            try:
                print(f"  Response: {json.dumps(version_resp.json(), indent=2)}")
            except:
                print(f"  Response: {version_resp.content}")
            
            # Test clone
            print(f"\n  Clone Contract {contract_id}")
            print("  " + "-" * 36)
            clone_resp = client.post(
                f"/api/contracts/{contract_id}/clone/",
                json.dumps({"title": "Cloned Contract"}),
                content_type='application/json',
                **headers
            )
            print(f"  Status Code: {clone_resp.status_code}")
            try:
                print(f"  Response: {json.dumps(clone_resp.json(), indent=2)}")
            except:
                print(f"  Response: {clone_resp.content}")
