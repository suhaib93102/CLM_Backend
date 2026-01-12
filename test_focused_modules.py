#!/usr/bin/env python
"""
CLM BACKEND - FOCUSED PRODUCTION TEST SUITE
Tests: Templates, Versions, Contracts, Notifications, Admin, Document Storage
"""

import os
import sys
import django
import json
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
client = Client()

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "focused_test@example.com"
TEST_PASSWORD = "FocusedTest123!"

class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed):
    status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
    print(f"{status} {name}")

def cleanup():
    try:
        User.objects.filter(email=TEST_EMAIL).delete()
    except:
        pass

# Setup
print(f"\n{Colors.BOLD}='*80")
print("CLM BACKEND - FOCUSED PRODUCTION TEST")
print(f"{'='*80}{Colors.ENDC}\n")

cleanup()

# 1. AUTHENTICATION
print(f"{Colors.BOLD}AUTHENTICATION{Colors.ENDC}")
response = client.post(f'{BASE_URL}/auth/register/', 
    data={'email': TEST_EMAIL, 'password': TEST_PASSWORD, 'full_name': 'Test User'},
    content_type='application/json')
print_test("Register User", response.status_code == 201)

response = client.post(f'{BASE_URL}/auth/login/',
    data={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
    content_type='application/json')
access_token = response.json().get('access') if response.status_code == 200 else None
print_test("Login User", response.status_code == 200)

if not access_token:
    print("Authentication failed!")
    exit()

headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}', 'content_type': 'application/json'}

# 2. CONTRACTS - CRUD
print(f"\n{Colors.BOLD}CONTRACTS - CRUD OPERATIONS{Colors.ENDC}")
contract_id = None

response = client.get(f'{BASE_URL}/contracts/', **headers)
print_test("List Contracts (GET /contracts/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/contracts/', 
    data=json.dumps({'title': 'Test Contract', 'status': 'draft', 'counterparty': 'Test Vendor'}),
    **headers)
if response.status_code in [200, 201]:
    contract_id = response.json().get('id')
print_test("Create Contract (POST /contracts/)", response.status_code in [200, 201])

if contract_id:
    response = client.get(f'{BASE_URL}/contracts/{contract_id}/', **headers)
    print_test(f"Get Contract (GET /contracts/{contract_id}/)", response.status_code == 200)
    
    response = client.put(f'{BASE_URL}/contracts/{contract_id}/',
        data=json.dumps({'title': 'Updated Contract'}),
        **headers)
    print_test(f"Update Contract (PUT /contracts/{contract_id}/)", response.status_code in [200, 201])

# 3. CONTRACT VERSIONS
print(f"\n{Colors.BOLD}CONTRACT VERSIONS{Colors.ENDC}")
if contract_id:
    response = client.get(f'{BASE_URL}/contracts/{contract_id}/versions/', **headers)
    print_test(f"List Versions (GET /contracts/{contract_id}/versions/)", response.status_code == 200)
    
    response = client.post(f'{BASE_URL}/contracts/{contract_id}/create-version/',
        data=json.dumps({'change_summary': 'Version 2'}),
        **headers)
    print_test(f"Create Version (POST /contracts/{contract_id}/create-version/)", response.status_code in [200, 201])
    
    response = client.post(f'{BASE_URL}/contracts/{contract_id}/clone/',
        data=json.dumps({'title': 'Cloned Contract'}),
        **headers)
    print_test(f"Clone Contract (POST /contracts/{contract_id}/clone/)", response.status_code in [200, 201])

# 4. TEMPLATES - CRUD & VERSIONS
print(f"\n{Colors.BOLD}TEMPLATES - CRUD & VERSIONS{Colors.ENDC}")
template_id = None

response = client.get(f'{BASE_URL}/contract-templates/', **headers)
print_test("List Templates (GET /contract-templates/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/contract-templates/',
    data=json.dumps({'title': 'Test Template', 'status': 'draft'}),
    **headers)
if response.status_code in [200, 201]:
    template_id = response.json().get('id')
print_test("Create Template (POST /contract-templates/)", response.status_code in [200, 201])

if template_id:
    response = client.get(f'{BASE_URL}/contract-templates/{template_id}/', **headers)
    print_test(f"Get Template (GET /contract-templates/{template_id}/)", response.status_code == 200)
    
    response = client.put(f'{BASE_URL}/contract-templates/{template_id}/',
        data=json.dumps({'title': 'Updated Template'}),
        **headers)
    print_test(f"Update Template (PUT /contract-templates/{template_id}/)", response.status_code in [200, 201])
    
    response = client.get(f'{BASE_URL}/contract-templates/{template_id}/versions/', **headers)
    print_test(f"Template Versions (GET /contract-templates/{template_id}/versions/)", response.status_code == 200)
    
    response = client.post(f'{BASE_URL}/contract-templates/{template_id}/clone/',
        data=json.dumps({'title': 'Cloned Template'}),
        **headers)
    print_test(f"Clone Template (POST /contract-templates/{template_id}/clone/)", response.status_code in [200, 201])

# 5. NOTIFICATIONS - CRUD
print(f"\n{Colors.BOLD}NOTIFICATIONS - CRUD{Colors.ENDC}")
notif_id = None

response = client.get(f'{BASE_URL}/notifications/', **headers)
print_test("List Notifications (GET /notifications/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/notifications/',
    data=json.dumps({'title': 'Test Notification', 'message': 'Test message', 'notification_type': 'info'}),
    **headers)
if response.status_code in [200, 201]:
    notif_id = response.json().get('id')
print_test("Create Notification (POST /notifications/)", response.status_code in [200, 201])

if notif_id:
    response = client.get(f'{BASE_URL}/notifications/{notif_id}/', **headers)
    print_test(f"Get Notification (GET /notifications/{notif_id}/)", response.status_code == 200)
    
    response = client.put(f'{BASE_URL}/notifications/{notif_id}/',
        data=json.dumps({'title': 'Updated Notification'}),
        **headers)
    print_test(f"Update Notification (PUT /notifications/{notif_id}/)", response.status_code in [200, 201])
    
    response = client.delete(f'{BASE_URL}/notifications/{notif_id}/', **headers)
    print_test(f"Delete Notification (DELETE /notifications/{notif_id}/)", response.status_code in [200, 204])

# 6. DOCUMENT STORAGE & RETRIEVAL
print(f"\n{Colors.BOLD}DOCUMENT STORAGE & RETRIEVAL{Colors.ENDC}")

response = client.get(f'{BASE_URL}/documents/', **headers)
print_test("List Documents (GET /documents/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/repository/', **headers)
print_test("Repository Contents (GET /repository/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/repository/folders/', **headers)
print_test("Repository Folders (GET /repository/folders/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/repository/folders/',
    data=json.dumps({'name': 'Test Folder'}),
    **headers)
print_test("Create Folder (POST /repository/folders/)", response.status_code in [200, 201])

# 7. ADMIN PANEL
print(f"\n{Colors.BOLD}ADMIN PANEL{Colors.ENDC}")

response = client.get(f'{BASE_URL}/admin/sla-rules/', **headers)
print_test("SLA Rules (GET /admin/sla-rules/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/admin/sla-breaches/', **headers)
print_test("SLA Breaches (GET /admin/sla-breaches/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/admin/users/roles/', **headers)
print_test("User Roles (GET /admin/users/roles/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/roles/', **headers)
print_test("List Roles (GET /roles/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/permissions/', **headers)
print_test("List Permissions (GET /permissions/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/tenants/', **headers)
print_test("List Tenants (GET /tenants/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/users/', **headers)
print_test("List Users (GET /users/)", response.status_code == 200)

# 8. WORKFLOWS & APPROVALS
print(f"\n{Colors.BOLD}WORKFLOWS & APPROVALS{Colors.ENDC}")

response = client.get(f'{BASE_URL}/workflows/', **headers)
print_test("List Workflows (GET /workflows/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/workflows/',
    data=json.dumps({'name': 'Test Workflow', 'steps': []}),
    **headers)
print_test("Create Workflow (POST /workflows/)", response.status_code in [200, 201])

response = client.get(f'{BASE_URL}/approvals/', **headers)
print_test("List Approvals (GET /approvals/)", response.status_code == 200)

if contract_id:
    response = client.post(f'{BASE_URL}/contracts/{contract_id}/approve/',
        data=json.dumps({}),
        **headers)
    print_test(f"Approve Contract (POST /contracts/{contract_id}/approve/)", response.status_code in [200, 201])

# 9. METADATA & CUSTOM FIELDS
print(f"\n{Colors.BOLD}METADATA & CUSTOM FIELDS{Colors.ENDC}")

response = client.get(f'{BASE_URL}/metadata/fields/', **headers)
print_test("List Metadata Fields (GET /metadata/fields/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/metadata/fields/',
    data=json.dumps({'name': 'Test Field', 'field_type': 'text'}),
    **headers)
print_test("Create Metadata Field (POST /metadata/fields/)", response.status_code in [200, 201])

# 10. AUDIT LOGS
print(f"\n{Colors.BOLD}AUDIT LOGS{Colors.ENDC}")

response = client.get(f'{BASE_URL}/audit-logs/', **headers)
print_test("List Audit Logs (GET /audit-logs/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/audit-logs/stats/', **headers)
print_test("Audit Statistics (GET /audit-logs/stats/)", response.status_code == 200)

# 11. SEARCH
print(f"\n{Colors.BOLD}SEARCH{Colors.ENDC}")

response = client.get(f'{BASE_URL}/search/?q=test', **headers)
print_test("Full-text Search (GET /search/)", response.status_code == 200)

response = client.get(f'{BASE_URL}/search/semantic/?q=test', **headers)
print_test("Semantic Search (GET /search/semantic/)", response.status_code == 200)

response = client.post(f'{BASE_URL}/search/advanced/',
    data=json.dumps({'query': 'test'}),
    **headers)
print_test("Advanced Search (POST /search/advanced/)", response.status_code in [200, 201])

# CLEANUP
cleanup()
print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
