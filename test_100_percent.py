#!/usr/bin/env python
"""
COMPREHENSIVE 100% ENDPOINT TEST - ALL REAL VALUES
Test all 48+ endpoints with real request/response data
Target: 100% PASS RATE
"""
import os, django, json, sys
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User
from contracts.models import Contract, ContractTemplate
from approvals.models import ApprovalModel
from workflows.models import Workflow

# Cleanup
User.objects.filter(email="test100percent@api.com").delete()

client = Client()
responses = []
results = {"total": 0, "passed": 0, "failed": 0, "details": []}

def test_endpoint(method, url, data=None, headers=None, description=""):
    """Test endpoint with real data and capture response"""
    results["total"] += 1
    
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
            response_data = resp.json() if resp.status_code != 204 else {}
        except:
            response_data = {"status": "No JSON", "http_code": resp.status_code}
        
        if success:
            results["passed"] += 1
            status_icon = "✓"
        else:
            results["failed"] += 1
            status_icon = "✗"
        
        results["details"].append({
            "endpoint": url,
            "method": method,
            "status_code": resp.status_code,
            "success": success,
            "description": description
        })
        
        # Log response
        entry = f"\n{'='*100}\n{status_icon} {method} {url} [{resp.status_code}]\nDescription: {description}\n"
        if data:
            entry += f"\nRequest:\n{json.dumps(data, indent=2)}\n"
        entry += f"\nResponse:\n{json.dumps(response_data, indent=2)}\n"
        
        responses.append(entry)
        
        return resp, success
    except Exception as e:
        results["failed"] += 1
        results["details"].append({
            "endpoint": url,
            "method": method,
            "error": str(e)
        })
        responses.append(f"\n✗ {method} {url}\nError: {str(e)}\n")
        return None, False

# ===== START TEST =====
print("\n" + "="*100)
print("COMPREHENSIVE 100% ENDPOINT TEST - ALL REAL VALUES")
print("="*100 + "\n")

responses.append("="*100)
responses.append("COMPREHENSIVE TEST - ALL ENDPOINTS WITH REAL VALUES")
responses.append(f"Generated: January 12, 2026")
responses.append("="*100)

# ===== SECTION 1: AUTHENTICATION (5 endpoints) =====
print("1. Testing Authentication (5/5)...")
responses.append("\n" + "="*100)
responses.append("SECTION 1: AUTHENTICATION")
responses.append("="*100)

# Register
resp, _ = test_endpoint("POST", "/api/auth/register/", {
    "email": "test100percent@api.com",
    "password": "TestPassword123!@#$",
    "full_name": "100 Percent Test User"
}, {}, "User registration with real credentials")

token = None
uid = None
if resp:
    token = resp.json()['access']
    uid = resp.json()['user']['user_id']

h = {'HTTP_AUTHORIZATION': f'Bearer {token}'} if token else {}

# Login
test_endpoint("POST", "/api/auth/login/", {
    "email": "test100percent@api.com",
    "password": "TestPassword123!@#$"
}, {}, "User login")

# Get current user
test_endpoint("GET", "/api/auth/me/", None, h, "Get current user info")

# Refresh token
if resp:
    refresh = resp.json().get('refresh')
    test_endpoint("POST", "/api/auth/refresh/", {
        "refresh": refresh
    }, {}, "Refresh JWT token")

# Logout
test_endpoint("POST", "/api/auth/logout/", {}, h, "User logout")

# ===== SECTION 2: CONTRACTS (11 endpoints) =====
print("2. Testing Contracts (11/11)...")
responses.append("\n" + "="*100)
responses.append("SECTION 2: CONTRACTS CRUD")
responses.append("="*100)

contract_id = None

# Create contract
resp, _ = test_endpoint("POST", "/api/contracts/", {
    "title": "Enterprise MSA with Global Tech Corp",
    "contract_type": "MSA",
    "status": "draft",
    "value": 750000.00,
    "counterparty": "Global Tech Corporation",
    "start_date": "2026-02-01",
    "end_date": "2027-01-31",
    "description": "Master Service Agreement with payment terms and SLAs"
}, h, "Create new contract with full details")

if resp and resp.status_code == 201:
    contract_id = resp.json()['id']

# List contracts
test_endpoint("GET", "/api/contracts/", None, h, "List all contracts")

# Get contract by ID
if contract_id:
    test_endpoint("GET", f"/api/contracts/{contract_id}/", None, h, "Get specific contract details")

# Update contract
if contract_id:
    test_endpoint("PUT", f"/api/contracts/{contract_id}/", {
        "status": "pending",
        "value": 800000.00
    }, h, "Update contract status and value")

# Clone contract
if contract_id:
    test_endpoint("POST", f"/api/contracts/{contract_id}/clone/", {
        "title": "Cloned: Enterprise MSA v2"
    }, h, "Clone existing contract")

# Get statistics
test_endpoint("GET", "/api/contracts/statistics/", None, h, "Get contract statistics by status")

# Get recent
test_endpoint("GET", "/api/contracts/recent/?limit=5", None, h, "Get recently modified contracts")

# Get download URL
if contract_id:
    test_endpoint("GET", f"/api/contracts/{contract_id}/download-url/", None, h, "Get contract download URL")

# Get history
if contract_id:
    test_endpoint("GET", f"/api/contracts/{contract_id}/history/", None, h, "Get contract change history")

# Delete contract
if contract_id:
    test_endpoint("DELETE", f"/api/contracts/{contract_id}/", None, h, "Delete contract")

# ===== SECTION 3: CONTRACT TEMPLATES (5 endpoints) =====
print("3. Testing Templates (5/5)...")
responses.append("\n" + "="*100)
responses.append("SECTION 3: CONTRACT TEMPLATES")
responses.append("="*100)

template_id = None

# Create template
resp, _ = test_endpoint("POST", "/api/contract-templates/", {
    "name": "Standard Enterprise NDA Template",
    "contract_type": "NDA",
    "r2_key": "templates/enterprise_nda_v4.docx",
    "description": "Standard Non-Disclosure Agreement for vendor relationships",
    "status": "draft",
    "merge_fields": ["company_name", "effective_date", "confidentiality_period"]
}, h, "Create contract template with merge fields")

if resp and resp.status_code == 201:
    template_id = resp.json()['id']

# List templates
test_endpoint("GET", "/api/contract-templates/", None, h, "List all contract templates")

# Get template details
if template_id:
    test_endpoint("GET", f"/api/contract-templates/{template_id}/", None, h, "Get template details")

# Update template
if template_id:
    test_endpoint("PUT", f"/api/contract-templates/{template_id}/", {
        "status": "published",
        "description": "Published Enterprise NDA - approved for production"
    }, h, "Update template status and description")

# Delete template
if template_id:
    test_endpoint("DELETE", f"/api/contract-templates/{template_id}/", None, h, "Delete template")

# ===== SECTION 4: WORKFLOWS (6 endpoints) =====
print("4. Testing Workflows (6/6)...")
responses.append("\n" + "="*100)
responses.append("SECTION 4: WORKFLOWS")
responses.append("="*100)

workflow_id = None

# Create workflow
resp, _ = test_endpoint("POST", "/api/workflows/", {
    "name": "Advanced Contract Approval Process",
    "description": "Multi-level approval for high-value contracts",
    "status": "active",
    "steps": [
        {"step_number": 1, "name": "Department Manager Review", "assigned_to": ["role:manager"]},
        {"step_number": 2, "name": "Legal Review", "assigned_to": ["role:legal"]},
        {"step_number": 3, "name": "CFO Approval", "assigned_to": ["role:cfo"]}
    ]
}, h, "Create multi-step workflow")

if resp and resp.status_code == 201:
    workflow_id = resp.json()['id']

# List workflows
test_endpoint("GET", "/api/workflows/", None, h, "List all workflows")

# Get workflow details
if workflow_id:
    test_endpoint("GET", f"/api/workflows/{workflow_id}/", None, h, "Get workflow details")

# Get workflow instances
if workflow_id:
    test_endpoint("GET", f"/api/workflows/{workflow_id}/instances/", None, h, "Get workflow instances")

# Update workflow
if workflow_id:
    test_endpoint("PUT", f"/api/workflows/{workflow_id}/", {
        "status": "active"
    }, h, "Update workflow configuration")

# Delete workflow
if workflow_id:
    test_endpoint("DELETE", f"/api/workflows/{workflow_id}/", None, h, "Delete workflow")

# ===== SECTION 5: APPROVALS (4 endpoints) =====
print("5. Testing Approvals (4/4)...")
responses.append("\n" + "="*100)
responses.append("SECTION 5: APPROVALS")
responses.append("="*100)

# Create contract for approval
resp, _ = test_endpoint("POST", "/api/contracts/", {
    "title": "NDA for Approval Testing",
    "contract_type": "NDA",
    "status": "pending",
    "value": 50000.00,
    "counterparty": "Test Corp"
}, h, "Create contract for approval workflow")

approval_contract_id = resp.json()['id'] if resp and resp.status_code == 201 else None

# List approvals
test_endpoint("GET", "/api/approvals/", None, h, "List all pending approvals")

# Approve contract
if approval_contract_id:
    test_endpoint("POST", f"/api/contracts/{approval_contract_id}/approve/", {
        "reviewed": True,
        "comments": "Contract reviewed and approved by legal department"
    }, h, "Approve contract after review")

# Get approval details
if approval_contract_id:
    test_endpoint("GET", f"/api/approvals/{approval_contract_id}/", None, h, "Get approval details")

# ===== SECTION 6: ADMIN PANEL (7 endpoints) =====
print("6. Testing Admin Panel (7/7)...")
responses.append("\n" + "="*100)
responses.append("SECTION 6: ADMIN PANEL")
responses.append("="*100)

test_endpoint("GET", "/api/roles/", None, h, "Get all system roles")
test_endpoint("GET", "/api/permissions/", None, h, "Get all permissions")
test_endpoint("GET", "/api/users/", None, h, "Get all users in system")
test_endpoint("GET", "/api/admin/sla-rules/", None, h, "Get SLA rules")
test_endpoint("GET", "/api/admin/sla-breaches/", None, h, "Get SLA breaches")
test_endpoint("GET", "/api/admin/users/roles/", None, h, "Get user roles mapping")
test_endpoint("GET", "/api/admin/tenants/", None, h, "Get all tenants")

# ===== SECTION 7: AUDIT LOGS (4 endpoints) =====
print("7. Testing Audit Logs (4/4)...")
responses.append("\n" + "="*100)
responses.append("SECTION 7: AUDIT LOGS & HISTORY")
responses.append("="*100)

test_endpoint("GET", "/api/audit-logs/", None, h, "List audit logs")
test_endpoint("GET", "/api/audit-logs/stats/", None, h, "Get audit statistics")
test_endpoint("GET", "/api/audit-logs/?limit=20&action=created", None, h, "Get audit logs with filters")

if approval_contract_id:
    test_endpoint("GET", f"/api/contracts/{approval_contract_id}/history/", None, h, "Get contract history")

# ===== SECTION 8: SEARCH (3 endpoints) =====
print("8. Testing Search (3/3)...")
responses.append("\n" + "="*100)
responses.append("SECTION 8: SEARCH")
responses.append("="*100)

test_endpoint("GET", "/api/search/?q=MSA", None, h, "Full-text search for contracts")
test_endpoint("GET", "/api/search/semantic/?q=service agreement", None, h, "Semantic search")
test_endpoint("POST", "/api/search/advanced/", {
    "query": "NDA",
    "filters": {"status": "approved"}
}, h, "Advanced search with filters")

# ===== SECTION 9: NOTIFICATIONS (2 endpoints) =====
print("9. Testing Notifications (2/2)...")
responses.append("\n" + "="*100)
responses.append("SECTION 9: NOTIFICATIONS")
responses.append("="*100)

test_endpoint("POST", "/api/notifications/", {
    "message": "Contract MSA-2026-001 requires your approval",
    "notification_type": "email",
    "subject": "Contract Approval Required",
    "body": "Please review and approve the attached MSA within 48 hours",
    "recipient_id": uid
}, h, "Create email notification")

test_endpoint("GET", "/api/notifications/", None, h, "List all notifications")

# ===== SECTION 10: DOCUMENTS (4 endpoints) =====
print("10. Testing Documents (4/4)...")
responses.append("\n" + "="*100)
responses.append("SECTION 10: DOCUMENTS & REPOSITORY")
responses.append("="*100)

test_endpoint("GET", "/api/documents/", None, h, "List all documents")
test_endpoint("GET", "/api/repository/", None, h, "List repository contents")
test_endpoint("GET", "/api/repository/folders/", None, h, "List repository folders")
test_endpoint("POST", "/api/repository/folders/", {
    "name": "Legal Documents 2026",
    "parent_id": None
}, h, "Create repository folder")

# ===== SECTION 11: METADATA (2 endpoints) =====
print("11. Testing Metadata (2/2)...")
responses.append("\n" + "="*100)
responses.append("SECTION 11: METADATA")
responses.append("="*100)

test_endpoint("POST", "/api/metadata/fields/", {
    "name": "contract_value_usd",
    "field_type": "number",
    "description": "Total contract value in US dollars"
}, h, "Create numeric metadata field")

test_endpoint("GET", "/api/metadata/fields/", None, h, "List metadata fields")

# ===== SECTION 12: HEALTH (4 endpoints) =====
print("12. Testing Health Checks (4/4)...")
responses.append("\n" + "="*100)
responses.append("SECTION 12: HEALTH & MONITORING")
responses.append("="*100)

test_endpoint("GET", "/api/health/", None, h, "Get system health status")
test_endpoint("GET", "/api/health/database/", None, h, "Get database health")
test_endpoint("GET", "/api/health/cache/", None, h, "Get cache health")
test_endpoint("GET", "/api/health/metrics/", None, h, "Get system metrics")

# ===== FINAL SUMMARY =====
responses.append("\n" + "="*100)
responses.append("TEST EXECUTION SUMMARY")
responses.append("="*100)

responses.append(f"\nTotal Endpoints Tested: {results['total']}")
responses.append(f"Passed: {results['passed']} ✓")
responses.append(f"Failed: {results['failed']} ✗")

if results['total'] > 0:
    rate = (results['passed'] / results['total']) * 100
    responses.append(f"Success Rate: {rate:.1f}%")
    
    if rate == 100:
        responses.append("\n" + " "*35 + "🎉 100% PASS RATE ACHIEVED! 🎉")
    
responses.append("\n" + "="*100)
responses.append("ENDPOINT STATUS DETAILS")
responses.append("="*100)

for detail in results['details']:
    status_icon = "✓" if detail.get('success') else "✗"
    endpoint = detail.get('endpoint', 'Unknown')
    method = detail.get('method', 'N/A')
    code = detail.get('status_code', 'ERROR')
    desc = detail.get('description', '')
    responses.append(f"\n{status_icon} {method:6} {endpoint:50} [{code}]")
    if desc:
        responses.append(f"   → {desc}")

responses.append("\n" + "="*100)
responses.append("END OF TEST REPORT")
responses.append("="*100)

# Print summary
print("\n" + "="*100)
print("TEST EXECUTION COMPLETE")
print("="*100)
print(f"Total: {results['total']} | Passed: {results['passed']} ✓ | Failed: {results['failed']} ✗")
if results['total'] > 0:
    rate = (results['passed'] / results['total']) * 100
    print(f"Success Rate: {rate:.1f}%")
    if rate == 100:
        print("\n" + " "*30 + "🎉 100% PASS RATE ACHIEVED! 🎉")
print("="*100 + "\n")

# Save all responses
output_file = '/Users/vishaljha/CLM_Backend/API_TEST_100_PERCENT.txt'
with open(output_file, 'w') as f:
    f.write('\n'.join(responses))

print(f"✓ All responses saved to: API_TEST_100_PERCENT.txt")
print(f"✓ Total output lines: {len(responses)}\n")
