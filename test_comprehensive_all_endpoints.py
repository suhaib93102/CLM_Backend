#!/usr/bin/env python
"""
COMPREHENSIVE PRODUCTION TEST - ALL 50+ ENDPOINTS
Contracts CRUD (11) + Templates (5) + Versions (5) + Workflows (6) 
+ Approvals (4) + Admin (7) + Audit & History (3)
"""
import os, django, json, sys
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User

# Cleanup
User.objects.filter(email="comprehensive@test.com").delete()

client = Client()
results = []

def log(msg):
    """Log message and store in results"""
    print(msg)
    results.append(msg)

def test_endpoint(method, url, data=None, headers=None):
    """Test a single endpoint"""
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
        return success, resp.status_code, resp
    except Exception as e:
        return False, "ERROR", str(e)

# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================

log("\n" + "="*120)
log(" "*35 + "COMPREHENSIVE PRODUCTION TEST - ALL ENDPOINTS")
log(" "*25 + "Contracts (11) | Templates (5) | Versions (5) | Workflows (6) | Approvals (4) | Admin (7) | Audit (3)")
log("="*120 + "\n")

# ===== STEP 1: AUTHENTICATION =====
log("1. AUTHENTICATION ENDPOINTS")
log("-" * 120)

auth_tests = [
    ("POST", "/api/auth/register/", {"email": "comprehensive@test.com", "password": "Test123!@#", "full_name": "Test User"}),
    ("POST", "/api/auth/login/", {"email": "comprehensive@test.com", "password": "Test123!@#"}),
]

token = None
uid = None
for method, url, data in auth_tests:
    success, code, resp = test_endpoint(method, url, data, {})
    if success:
        log(f"  ✓ {method:4} {url:40} [{code}]")
        if "/login/" in url:
            token = resp.json()['access']
            uid = resp.json()['user']['user_id']
    else:
        log(f"  ✗ {method:4} {url:40} [{code}]")

h = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
log(f"\n✓ Authentication successful - Token: {token[:20]}...\n")

# ===== STEP 2: CONTRACTS CRUD (11 endpoints) =====
log("2. CONTRACTS CRUD ENDPOINTS (11 Total)")
log("-" * 120)

contract_id = None
contract_tests = [
    ("POST", "/api/contracts/", {"title": "Service Agreement", "contract_type": "MSA", "status": "draft", "value": 50000, "counterparty": "Acme Corp", "start_date": "2026-01-15", "end_date": "2027-01-14"}),
    ("GET", "/api/contracts/", None),
    ("GET", "/api/contracts/?limit=5&offset=0", None),
    ("GET", "/api/contracts/?status=draft", None),
    ("GET", "/api/contracts/statistics/", None),
    ("GET", "/api/contracts/recent/", None),
]

for method, url, data in contract_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
        if method == "POST" and "/contracts/" in url and code == 201:
            contract_id = resp.json()['id']
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

# GET specific contract
if contract_id:
    success, code, resp = test_endpoint("GET", f"/api/contracts/{contract_id}/", None, h)
    if success:
        log(f"  ✓ GET  /api/contracts/<id>/                         [{code}]")
    else:
        log(f"  ✗ GET  /api/contracts/<id>/                         [{code}]")
    
    # UPDATE contract
    success, code, resp = test_endpoint("PUT", f"/api/contracts/{contract_id}/", {"status": "pending"}, h)
    if success:
        log(f"  ✓ PUT  /api/contracts/<id>/                         [{code}]")
    else:
        log(f"  ✗ PUT  /api/contracts/<id>/                         [{code}]")
    
    # CLONE contract
    success, code, resp = test_endpoint("POST", f"/api/contracts/{contract_id}/clone/", {"title": "Cloned MSA"}, h)
    if success:
        log(f"  ✓ POST /api/contracts/<id>/clone/                   [{code}]")
    else:
        log(f"  ✗ POST /api/contracts/<id>/clone/                   [{code}]")
    
    # GET download URL
    success, code, resp = test_endpoint("GET", f"/api/contracts/{contract_id}/download-url/", None, h)
    if success:
        log(f"  ✓ GET  /api/contracts/<id>/download-url/            [{code}]")
    else:
        log(f"  ✗ GET  /api/contracts/<id>/download-url/            [{code}]")
    
    # DELETE contract
    success, code, resp = test_endpoint("DELETE", f"/api/contracts/{contract_id}/", None, h)
    if success:
        log(f"  ✓ DELETE /api/contracts/<id>/                       [{code}]")
    else:
        log(f"  ✗ DELETE /api/contracts/<id>/                       [{code}]")

log("")

# ===== STEP 3: TEMPLATES CRUD (5 endpoints) =====
log("3. CONTRACT TEMPLATES CRUD (5 Total)")
log("-" * 120)

template_id = None
template_tests = [
    ("POST", "/api/contract-templates/", {"name": "NDA Template", "contract_type": "NDA", "r2_key": "nda_template.docx", "description": "Standard NDA"}),
    ("GET", "/api/contract-templates/", None),
    ("GET", "/api/contract-templates/?limit=10", None),
]

for method, url, data in template_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
        if method == "POST" and code == 201:
            template_id = resp.json()['id']
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

# GET specific template
if template_id:
    success, code, resp = test_endpoint("GET", f"/api/contract-templates/{template_id}/", None, h)
    if success:
        log(f"  ✓ GET  /api/contract-templates/<id>/                [{code}]")
    else:
        log(f"  ✗ GET  /api/contract-templates/<id>/                [{code}]")
    
    # UPDATE template
    success, code, resp = test_endpoint("PUT", f"/api/contract-templates/{template_id}/", {"status": "published"}, h)
    if success:
        log(f"  ✓ PUT  /api/contract-templates/<id>/                [{code}]")
    else:
        log(f"  ✗ PUT  /api/contract-templates/<id>/                [{code}]")
    
    # DELETE template
    success, code, resp = test_endpoint("DELETE", f"/api/contract-templates/{template_id}/", None, h)
    if success:
        log(f"  ✓ DELETE /api/contract-templates/<id>/              [{code}]")
    else:
        log(f"  ✗ DELETE /api/contract-templates/<id>/              [{code}]")

log("")

# ===== STEP 4: CONTRACT VERSIONS (5 endpoints) =====
log("4. CONTRACT VERSIONS (5 Total)")
log("-" * 120)

# Create a fresh contract for version testing
success, code, resp = test_endpoint("POST", "/api/contracts/", {"title": "Version Test Contract", "contract_type": "MSA", "status": "draft"}, h)
if success:
    version_contract_id = resp.json()['id']
    log(f"  ✓ Created contract for version testing [{code}]")
    
    # Test versions endpoints
    version_tests = [
        ("GET", f"/api/contracts/{version_contract_id}/versions/", None),
        ("POST", f"/api/contracts/{version_contract_id}/create-version/", {"change_summary": "Updated clauses", "selected_clauses": []}),
        ("GET", f"/api/contracts/{version_contract_id}/versions/1/", None),
        ("GET", f"/api/contracts/{version_contract_id}/versions/1/clauses/", None),
        ("GET", f"/api/contracts/{version_contract_id}/versions/1/download/", None),
    ]
    
    for method, url, data in version_tests:
        success, code, resp = test_endpoint(method, url, data, h)
        status = "✓" if success else "✗"
        endpoint = url.replace(version_contract_id, "<contract_id>")
        log(f"  {status} {method:4} {endpoint:50} [{code}]")

log("")

# ===== STEP 5: WORKFLOWS (6 endpoints) =====
log("5. WORKFLOWS (6 Total)")
log("-" * 120)

workflow_id = None
workflow_tests = [
    ("POST", "/api/workflows/", {"name": "Approval Workflow", "description": "Multi-step approval", "status": "active", "steps": [{"step_number": 1, "name": "Initial Review"}]}),
    ("GET", "/api/workflows/", None),
    ("GET", "/api/workflows/?limit=10", None),
]

for method, url, data in workflow_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
        if method == "POST" and code == 201:
            workflow_id = resp.json()['id']
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

# GET, UPDATE, DELETE workflow
if workflow_id:
    success, code, resp = test_endpoint("GET", f"/api/workflows/{workflow_id}/", None, h)
    if success:
        log(f"  ✓ GET  /api/workflows/<id>/                         [{code}]")
    else:
        log(f"  ✗ GET  /api/workflows/<id>/                         [{code}]")
    
    success, code, resp = test_endpoint("PUT", f"/api/workflows/{workflow_id}/", {"status": "archived"}, h)
    if success:
        log(f"  ✓ PUT  /api/workflows/<id>/                         [{code}]")
    else:
        log(f"  ✗ PUT  /api/workflows/<id>/                         [{code}]")
    
    success, code, resp = test_endpoint("GET", f"/api/workflows/{workflow_id}/instances/", None, h)
    if success:
        log(f"  ✓ GET  /api/workflows/<id>/instances/               [{code}]")
    else:
        log(f"  ✗ GET  /api/workflows/<id>/instances/               [{code}]")
    
    success, code, resp = test_endpoint("DELETE", f"/api/workflows/{workflow_id}/", None, h)
    if success:
        log(f"  ✓ DELETE /api/workflows/<id>/                       [{code}]")
    else:
        log(f"  ✗ DELETE /api/workflows/<id>/                       [{code}]")

log("")

# ===== STEP 6: APPROVALS (4 endpoints) =====
log("6. APPROVALS (4 Total)")
log("-" * 120)

# Create contract for approval testing
success, code, resp = test_endpoint("POST", "/api/contracts/", {"title": "Approval Test", "contract_type": "MSA", "status": "draft"}, h)
if success:
    approval_contract_id = resp.json()['id']
    log(f"  ✓ Created contract for approval testing [{code}]")
    
    approval_tests = [
        ("GET", "/api/approvals/", None),
        ("GET", "/api/approvals/?limit=10", None),
        ("POST", f"/api/contracts/{approval_contract_id}/approve/", {"reviewed": True, "comments": "Approved"}),
    ]
    
    for method, url, data in approval_tests:
        success, code, resp = test_endpoint(method, url, data, h)
        if success:
            log(f"  ✓ {method:4} {url:50} [{code}]")
            if method == "POST" and "approve" in url:
                approval_id = approval_contract_id
        else:
            log(f"  ✗ {method:4} {url:50} [{code}]")
    
    # Try to get approval details
    success, code, resp = test_endpoint("GET", f"/api/approvals/{approval_contract_id}/", None, h)
    status = "✓" if success else "✗"
    log(f"  {status} GET  /api/approvals/<id>/                        [{code}]")

log("")

# ===== STEP 7: ADMIN PANEL (7 endpoints) =====
log("7. ADMIN PANEL (7 Total)")
log("-" * 120)

admin_tests = [
    ("GET", "/api/roles/", None),
    ("GET", "/api/permissions/", None),
    ("GET", "/api/users/", None),
    ("GET", "/api/admin/sla-rules/", None),
    ("GET", "/api/admin/sla-breaches/", None),
    ("GET", "/api/admin/users/roles/", None),
    ("GET", "/api/admin/tenants/", None),
]

for method, url, data in admin_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

log("")

# ===== STEP 8: AUDIT & HISTORY (3 endpoints) =====
log("8. AUDIT LOGS & HISTORY (3 Total)")
log("-" * 120)

audit_tests = [
    ("GET", "/api/audit-logs/", None),
    ("GET", "/api/audit-logs/stats/", None),
    ("GET", "/api/audit-logs/?limit=10", None),
]

for method, url, data in audit_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

# Contract history
if version_contract_id:
    success, code, resp = test_endpoint("GET", f"/api/contracts/{version_contract_id}/history/", None, h)
    status = "✓" if success else "✗"
    log(f"  {status} GET  /api/contracts/<id>/history/              [{code}]")

log("")

# ===== STEP 9: SEARCH (3 endpoints) =====
log("9. SEARCH ENDPOINTS (3 Total)")
log("-" * 120)

search_tests = [
    ("GET", "/api/search/?q=contract", None),
    ("GET", "/api/search/semantic/?q=agreement", None),
    ("POST", "/api/search/advanced/", {"query": "contract", "filters": {"status": "draft"}}),
]

for method, url, data in search_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

log("")

# ===== STEP 10: NOTIFICATIONS (2 endpoints) =====
log("10. NOTIFICATIONS (2 Total)")
log("-" * 120)

notification_tests = [
    ("POST", "/api/notifications/", {"message": "Test notification", "notification_type": "email", "subject": "Test", "body": "Test message", "recipient_id": uid}),
    ("GET", "/api/notifications/", None),
]

for method, url, data in notification_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

log("")

# ===== STEP 11: DOCUMENTS & REPOSITORY (4 endpoints) =====
log("11. DOCUMENTS & REPOSITORY (4 Total)")
log("-" * 120)

doc_tests = [
    ("GET", "/api/documents/", None),
    ("GET", "/api/repository/", None),
    ("GET", "/api/repository/folders/", None),
    ("POST", "/api/repository/folders/", {"name": "Legal Docs", "parent_id": None}),
]

for method, url, data in doc_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

log("")

# ===== STEP 12: METADATA (2 endpoints) =====
log("12. METADATA (2 Total)")
log("-" * 120)

metadata_tests = [
    ("POST", "/api/metadata/fields/", {"name": "contract_value", "field_type": "number", "description": "Contract value in USD"}),
    ("GET", "/api/metadata/fields/", None),
    ("POST", "/api/metadata/fields/", {"name": "department", "field_type": "text", "description": "Department name"}),
]

for method, url, data in metadata_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

log("")

# ===== STEP 13: HEALTH CHECKS (4 endpoints) =====
log("13. HEALTH & MONITORING (4 Total)")
log("-" * 120)

health_tests = [
    ("GET", "/api/health/", None),
    ("GET", "/api/health/database/", None),
    ("GET", "/api/health/cache/", None),
    ("GET", "/api/health/metrics/", None),
]

for method, url, data in health_tests:
    success, code, resp = test_endpoint(method, url, data, h)
    if success:
        log(f"  ✓ {method:4} {url:50} [{code}]")
    else:
        log(f"  ✗ {method:4} {url:50} [{code}]")

# ===== FINAL SUMMARY =====
log("\n" + "="*120)
passed = sum(1 for line in results if "✓" in line and "[" in line)
failed = sum(1 for line in results if "✗" in line and "[" in line)
total = passed + failed

log(f"FINAL RESULTS: {passed:3d} PASSED | {failed:3d} FAILED | TOTAL: {total}")
if total > 0:
    log(f"SUCCESS RATE: {(passed/total)*100:.1f}%")
log("="*120 + "\n")

if failed == 0:
    log(" "*35 + "🎉 ALL ENDPOINTS WORKING! PRODUCTION READY! 🎉\n")

# Save results to file
with open('/Users/vishaljha/CLM_Backend/TEST_RESULTS_COMPREHENSIVE.txt', 'w') as f:
    f.write('\n'.join(results))

log("✓ Results saved to TEST_RESULTS_COMPREHENSIVE.txt\n")
