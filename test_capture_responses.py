#!/usr/bin/env python
"""
COMPREHENSIVE PRODUCTION TEST - CAPTURE REAL API RESPONSES
All endpoints tested with actual request/response data
"""
import os, django, json, sys
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User

# Cleanup
User.objects.filter(email="testuser@api.com").delete()

client = Client()
responses = []
passed_count = 0
failed_count = 0

def log_response(method, url, request_data, status_code, response_data, success):
    """Log API request and response"""
    global passed_count, failed_count
    
    status_indicator = "✓" if success else "✗"
    
    entry = f"\n{'='*100}\n{status_indicator} {method} {url}\nStatus: {status_code}\n"
    
    if request_data:
        entry += f"Request Body:\n{json.dumps(request_data, indent=2)}\n\n"
    
    entry += f"Response:\n{json.dumps(response_data, indent=2)}\n"
    
    responses.append(entry)
    
    if success:
        passed_count += 1
    else:
        failed_count += 1

def test_endpoint(method, url, data=None, headers=None, name=""):
    """Test endpoint and capture response"""
    try:
        if method == "GET":
            resp = client.get(url, **headers)
        elif method == "POST":
            resp = client.post(url, json.dumps(data), content_type='application/json', **headers)
        elif method == "PUT":
            resp = client.put(url, json.dumps(data), content_type='application/json', **headers)
        elif method == "DELETE":
            resp = client.delete(url, **headers)
        
        success = resp.status_code in [200, 201, 204]
        
        try:
            response_data = resp.json()
        except:
            response_data = {"status": "No JSON response", "status_code": resp.status_code}
        
        log_response(method, url, data, resp.status_code, response_data, success)
        
        return resp
    except Exception as e:
        log_response(method, url, data, "ERROR", {"error": str(e)}, False)
        return None

# Start logging
responses.append("="*100)
responses.append("CLM BACKEND - COMPREHENSIVE API TEST WITH ACTUAL RESPONSES")
responses.append("Generated: January 12, 2026")
responses.append("="*100)

print("\n" + "="*100)
print("CLM BACKEND - COMPREHENSIVE API TEST WITH ACTUAL RESPONSES")
print("="*100 + "\n")

# ===== AUTHENTICATION =====
print("Testing Authentication...")
responses.append("\n" + "="*100)
responses.append("SECTION 1: AUTHENTICATION")
responses.append("="*100)

resp = test_endpoint("POST", "/api/auth/register/", {
    "email": "testuser@api.com",
    "password": "TestPassword123!@#",
    "full_name": "Test API User"
}, {}, "Register")

resp = test_endpoint("POST", "/api/auth/login/", {
    "email": "testuser@api.com",
    "password": "TestPassword123!@#"
}, {}, "Login")

token = resp.json()['access']
uid = resp.json()['user']['user_id']
h = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

print(f"✓ Authenticated - User ID: {uid[:8]}...\n")

test_endpoint("GET", "/api/auth/me/", None, h, "Get Current User")
test_endpoint("POST", "/api/auth/refresh/", {"refresh": resp.json()['refresh']}, {}, "Refresh Token")

# ===== CONTRACTS =====
print("Testing Contracts...")
responses.append("\n" + "="*100)
responses.append("SECTION 2: CONTRACTS CRUD")
responses.append("="*100)

# Create contract
resp = test_endpoint("POST", "/api/contracts/", {
    "title": "Service Agreement with Acme Corp",
    "contract_type": "MSA",
    "status": "draft",
    "value": 50000.00,
    "counterparty": "Acme Corporation",
    "start_date": "2026-01-15",
    "end_date": "2027-01-14",
    "description": "Main service agreement"
}, h, "Create Contract")

contract_id = resp.json()['id'] if resp else None

# List contracts
test_endpoint("GET", "/api/contracts/", None, h, "List Contracts")
test_endpoint("GET", "/api/contracts/?limit=5&offset=0", None, h, "List with Pagination")
test_endpoint("GET", "/api/contracts/?status=draft", None, h, "Filter by Status")

# Get single contract
if contract_id:
    test_endpoint("GET", f"/api/contracts/{contract_id}/", None, h, "Get Contract Details")
    
    # Update contract
    test_endpoint("PUT", f"/api/contracts/{contract_id}/", {
        "status": "pending",
        "value": 55000.00
    }, h, "Update Contract")
    
    # Clone contract
    test_endpoint("POST", f"/api/contracts/{contract_id}/clone/", {
        "title": "Cloned Service Agreement"
    }, h, "Clone Contract")
    
    # Get statistics
    test_endpoint("GET", "/api/contracts/statistics/", None, h, "Get Statistics")
    
    # Get recent
    test_endpoint("GET", "/api/contracts/recent/", None, h, "Get Recent")

# ===== TEMPLATES =====
print("Testing Templates...")
responses.append("\n" + "="*100)
responses.append("SECTION 3: CONTRACT TEMPLATES")
responses.append("="*100)

# Create template
resp = test_endpoint("POST", "/api/contract-templates/", {
    "name": "Standard NDA Template",
    "contract_type": "NDA",
    "r2_key": "templates/nda_2024.docx",
    "description": "Standard NDA for vendor agreements",
    "status": "draft",
    "merge_fields": ["company_name", "date", "parties"]
}, h, "Create Template")

template_id = resp.json()['id'] if resp else None

# List templates
test_endpoint("GET", "/api/contract-templates/", None, h, "List Templates")

# Get template details
if template_id:
    test_endpoint("GET", f"/api/contract-templates/{template_id}/", None, h, "Get Template Details")
    
    # Update template
    test_endpoint("PUT", f"/api/contract-templates/{template_id}/", {
        "status": "published",
        "description": "Updated NDA template"
    }, h, "Update Template")

# ===== WORKFLOWS =====
print("Testing Workflows...")
responses.append("\n" + "="*100)
responses.append("SECTION 4: WORKFLOWS")
responses.append("="*100)

# Create workflow
resp = test_endpoint("POST", "/api/workflows/", {
    "name": "Contract Approval Workflow",
    "description": "Multi-step approval process for contracts",
    "status": "active",
    "steps": [
        {
            "step_number": 1,
            "name": "Initial Review",
            "assigned_to": ["role:manager"],
            "required_approval": True
        }
    ]
}, h, "Create Workflow")

workflow_id = resp.json()['id'] if resp else None

# List workflows
test_endpoint("GET", "/api/workflows/", None, h, "List Workflows")

# Get workflow
if workflow_id:
    test_endpoint("GET", f"/api/workflows/{workflow_id}/", None, h, "Get Workflow Details")
    
    # Update workflow
    test_endpoint("PUT", f"/api/workflows/{workflow_id}/", {
        "status": "active",
        "description": "Updated approval workflow"
    }, h, "Update Workflow")

# ===== APPROVALS =====
print("Testing Approvals...")
responses.append("\n" + "="*100)
responses.append("SECTION 5: APPROVALS")
responses.append("="*100)

test_endpoint("GET", "/api/approvals/", None, h, "List Approvals")

if contract_id:
    test_endpoint("POST", f"/api/contracts/{contract_id}/approve/", {
        "reviewed": True,
        "comments": "Contract approved after legal review"
    }, h, "Approve Contract")

# ===== ADMIN PANEL =====
print("Testing Admin Panel...")
responses.append("\n" + "="*100)
responses.append("SECTION 6: ADMIN PANEL")
responses.append("="*100)

test_endpoint("GET", "/api/roles/", None, h, "List Roles")
test_endpoint("GET", "/api/permissions/", None, h, "List Permissions")
test_endpoint("GET", "/api/users/", None, h, "List Users")
test_endpoint("GET", "/api/admin/sla-rules/", None, h, "List SLA Rules")
test_endpoint("GET", "/api/admin/sla-breaches/", None, h, "List SLA Breaches")
test_endpoint("GET", "/api/admin/users/roles/", None, h, "List User Roles")
test_endpoint("GET", "/api/admin/tenants/", None, h, "List Tenants")

# ===== AUDIT LOGS =====
print("Testing Audit Logs...")
responses.append("\n" + "="*100)
responses.append("SECTION 7: AUDIT LOGS & HISTORY")
responses.append("="*100)

test_endpoint("GET", "/api/audit-logs/", None, h, "List Audit Logs")
test_endpoint("GET", "/api/audit-logs/stats/", None, h, "Audit Statistics")

if contract_id:
    test_endpoint("GET", f"/api/contracts/{contract_id}/history/", None, h, "Contract History")

# ===== SEARCH =====
print("Testing Search...")
responses.append("\n" + "="*100)
responses.append("SECTION 8: SEARCH")
responses.append("="*100)

test_endpoint("GET", "/api/search/?q=contract", None, h, "Full-text Search")
test_endpoint("GET", "/api/search/semantic/?q=agreement", None, h, "Semantic Search")
test_endpoint("POST", "/api/search/advanced/", {
    "query": "contract",
    "filters": {"status": "draft"}
}, h, "Advanced Search")

# ===== NOTIFICATIONS =====
print("Testing Notifications...")
responses.append("\n" + "="*100)
responses.append("SECTION 9: NOTIFICATIONS")
responses.append("="*100)

test_endpoint("POST", "/api/notifications/", {
    "message": "Contract approval required",
    "notification_type": "email",
    "subject": "Contract Review Needed",
    "body": "Please review the attached contract",
    "recipient_id": uid
}, h, "Create Notification")

test_endpoint("GET", "/api/notifications/", None, h, "List Notifications")

# ===== DOCUMENTS & REPOSITORY =====
print("Testing Documents & Repository...")
responses.append("\n" + "="*100)
responses.append("SECTION 10: DOCUMENTS & REPOSITORY")
responses.append("="*100)

test_endpoint("GET", "/api/documents/", None, h, "List Documents")
test_endpoint("GET", "/api/repository/", None, h, "List Repository")
test_endpoint("GET", "/api/repository/folders/", None, h, "List Folders")
test_endpoint("POST", "/api/repository/folders/", {
    "name": "Legal Documents",
    "parent_id": None
}, h, "Create Folder")

# ===== METADATA =====
print("Testing Metadata...")
responses.append("\n" + "="*100)
responses.append("SECTION 11: METADATA")
responses.append("="*100)

test_endpoint("POST", "/api/metadata/fields/", {
    "name": "contract_value",
    "field_type": "number",
    "description": "Total contract value in USD"
}, h, "Create Metadata Field")

test_endpoint("GET", "/api/metadata/fields/", None, h, "List Metadata Fields")

# ===== HEALTH CHECKS =====
print("Testing Health Checks...")
responses.append("\n" + "="*100)
responses.append("SECTION 12: HEALTH & MONITORING")
responses.append("="*100)

test_endpoint("GET", "/api/health/", None, h, "System Health")
test_endpoint("GET", "/api/health/database/", None, h, "Database Health")
test_endpoint("GET", "/api/health/cache/", None, h, "Cache Health")
test_endpoint("GET", "/api/health/metrics/", None, h, "System Metrics")

# ===== FINAL SUMMARY =====
responses.append("\n" + "="*100)
responses.append("TEST EXECUTION SUMMARY")
responses.append("="*100)

responses.append(f"\nTotal Endpoints Tested: {passed_count + failed_count}")
responses.append(f"Passed: {passed_count} ✓")
responses.append(f"Failed: {failed_count} ✗")

if (passed_count + failed_count) > 0:
    success_rate = (passed_count / (passed_count + failed_count)) * 100
    responses.append(f"Success Rate: {success_rate:.1f}%")

responses.append("\n" + "="*100)
responses.append("END OF TEST REPORT")
responses.append("="*100)

# Print summary
print("\n" + "="*100)
print("TEST SUMMARY")
print("="*100)
print(f"Total Endpoints Tested: {passed_count + failed_count}")
print(f"Passed: {passed_count} ✓")
print(f"Failed: {failed_count} ✗")
if (passed_count + failed_count) > 0:
    success_rate = (passed_count / (passed_count + failed_count)) * 100
    print(f"Success Rate: {success_rate:.1f}%")
print("="*100 + "\n")

# Save all responses to file
output_file = '/Users/vishaljha/CLM_Backend/API_RESPONSES_ACTUAL.txt'
with open(output_file, 'w') as f:
    f.write('\n'.join(responses))

print(f"✓ All responses saved to: API_RESPONSES_ACTUAL.txt")
