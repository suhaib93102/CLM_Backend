#!/usr/bin/env python
"""
CLM Backend - Production Test Report with Error Capture
Enhanced version to capture and display detailed error messages
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_error_capture@example.com"
TEST_PASSWORD = "TestPassword123!"

# Colors
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    E = '\033[0m'   # End

def cleanup():
    try:
        User.objects.filter(email=TEST_EMAIL).delete()
    except:
        pass

def test_with_error_capture():
    """Test and capture detailed error responses"""
    cleanup()
    
    # Auth
    r1 = client.post(f'{BASE_URL}/auth/register/', data={'email': TEST_EMAIL, 'password': TEST_PASSWORD, 'full_name': 'Test'}, content_type='application/json')
    if r1.status_code != 201:
        print(f"{C.R}Registration failed: {r1.json()}{C.E}")
        return
    
    r2 = client.post(f'{BASE_URL}/auth/login/', data={'email': TEST_EMAIL, 'password': TEST_PASSWORD}, content_type='application/json')
    if r2.status_code != 200:
        print(f"{C.R}Login failed: {r2.json()}{C.E}")
        return
    
    token = r2.json().get('access')
    print(f"{C.G}✓ Authenticated{C.E}\n")
    
    # Test each POST endpoint
    endpoints = [
        ('Notification', f'{BASE_URL}/notifications/', {'title': 'Test', 'message': 'Test', 'notification_type': 'info'}),
        ('Workflow', f'{BASE_URL}/workflows/', {'name': 'Test', 'description': 'Test', 'steps': []}),
        ('Metadata Field', f'{BASE_URL}/metadata/fields/', {'name': 'Test', 'field_type': 'text', 'required': False}),
    ]
    
    for name, url, data in endpoints:
        print(f"\n{C.B}Testing {name} POST:{C.E}")
        print(f"  URL: {url}")
        print(f"  Data: {data}")
        
        r = client.post(url, data=data, HTTP_AUTHORIZATION=f'Bearer {token}', content_type='application/json')
        print(f"  Status: {r.status_code}")
        
        try:
            resp_data = r.json()
            print(f"  Response: {json.dumps(resp_data, indent=2)}")
        except:
            print(f"  Response (raw): {r.content}")
    
    cleanup()

if __name__ == '__main__':
    test_with_error_capture()
