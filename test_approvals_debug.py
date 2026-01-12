#!/usr/bin/env python
"""Quick test to debug approvals endpoint"""
import os, django, json
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User

# Cleanup
User.objects.filter(email="testapproval@api.com").delete()

client = Client()

# Register and login
resp = client.post('/api/auth/register/', json.dumps({
    "email": "testapproval@api.com",
    "password": "Test123!@#",
    "full_name": "Test"
}), content_type='application/json')

token = resp.json()['access']
uid = resp.json()['user']['user_id']
h = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

# Try to create approval
print("Testing Approvals Endpoint:")
print("="*80)

resp = client.post('/api/approvals/', json.dumps({
    "entity_type": "contract",
    "entity_id": "00000000-0000-0000-0000-000000000000",
    "requester_id": uid,
    "status": "pending",
    "comment": "Test"
}), content_type='application/json', **h)

print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2)}")
