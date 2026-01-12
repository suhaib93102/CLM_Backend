#!/usr/bin/env python
"""
FINAL PRODUCTION TEST - ALL ENDPOINTS VERIFIED
Templates, Versions, Contracts, Notifications, Admin, Document Storage
"""
import os, django, json
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User
User.objects.filter(email="finaltest@prod.com").delete()

client = Client()
print("\n" + "="*110)
print(" "*30 + "FINAL PRODUCTION COMPREHENSIVE TEST")
print(" "*20 + "All Modules: Templates, Versions, Contracts, Notifications, Admin, Documents")
print("="*110 + "\n")

# AUTH
r = client.post('/api/auth/register/', json.dumps({
    "email": "finaltest@prod.com", "password": "FinalTest123!@#", "full_name": "Final Test"
}), content_type='application/json')

r = client.post('/api/auth/login/', json.dumps({
    "email": "finaltest@prod.com", "password": "FinalTest123!@#"
}), content_type='application/json')

token = r.json()['access']
uid = r.json()['user']['user_id']
h = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

print(f"✓ Authentication: User {uid[:8]}...\n")

# All endpoints to test
endpoints = [
    # ===== CONTRACTS MODULE =====
    ("POST", "/api/contracts/", {"title": "MSA", "status": "draft"}),
    ("GET", "/api/contracts/", None),
    ("POST", "/api/contracts/", {"title": "NDA", "status": "draft"}),
    ("GET", "/api/contracts/?limit=5", None),
    ("GET", "/api/contracts/statistics/", None),
    ("GET", "/api/contracts/recent/", None),
    
    # ===== TEMPLATES MODULE =====
    ("POST", "/api/contract-templates/", {"name": "NDA Template", "contract_type": "NDA", "r2_key": "nda.docx"}),
    ("GET", "/api/contract-templates/", None),
    ("POST", "/api/contract-templates/", {"name": "MSA Template", "contract_type": "MSA", "r2_key": "msa.docx"}),
    
    # ===== NOTIFICATIONS MODULE =====
    ("POST", "/api/notifications/", {"message": "Test", "notification_type": "email", "subject": "Subj", "body": "Body", "recipient_id": uid}),
    ("GET", "/api/notifications/", None),
    
    # ===== WORKFLOWS MODULE =====
    ("POST", "/api/workflows/", {"name": "Approval Flow", "steps": []}),
    ("GET", "/api/workflows/", None),
    
    # ===== METADATA MODULE =====
    ("POST", "/api/metadata/fields/", {"name": "contract_value", "field_type": "number"}),
    ("GET", "/api/metadata/fields/", None),
    ("POST", "/api/metadata/fields/", {"name": "department", "field_type": "text"}),
    
    # ===== DOCUMENT STORAGE & REPOSITORY =====
    ("GET", "/api/documents/", None),
    ("GET", "/api/repository/", None),
    ("GET", "/api/repository/folders/", None),
    ("POST", "/api/repository/folders/", {"name": "Legal", "parent_id": None}),
    
    # ===== ADMIN PANEL =====
    ("GET", "/api/roles/", None),
    ("GET", "/api/permissions/", None),
    ("GET", "/api/users/", None),
    ("GET", "/api/admin/sla-rules/", None),
    ("GET", "/api/admin/sla-breaches/", None),
    ("GET", "/api/admin/users/roles/", None),
    ("GET", "/api/admin/tenants/", None),
    
    # ===== AUDIT & SEARCH =====
    ("GET", "/api/audit-logs/", None),
    ("GET", "/api/audit-logs/stats/", None),
    ("GET", "/api/search/", None),
    ("POST", "/api/search/advanced/", {"query": "contract"}),
    
    # ===== APPROVALS =====
    ("GET", "/api/approvals/", None),
    
    # ===== HEALTH CHECKS =====
    ("GET", "/api/health/", None),
    ("GET", "/api/health/database/", None),
    ("GET", "/api/health/cache/", None),
]

passed = 0
failed = 0
failed_tests = []

for method, url, data in endpoints:
    try:
        if method == "GET":
            resp = client.get(url, **h)
        else:
            resp = client.post(url, json.dumps(data), content_type='application/json', **h)
        
        if resp.status_code in [200, 201]:
            print(f"  ✓ {method:4} {url}")
            passed += 1
        else:
            print(f"  ✗ {method:4} {url} ({resp.status_code})")
            failed += 1
            failed_tests.append((method, url, resp.status_code))
    except Exception as e:
        print(f"  ✗ {method:4} {url} (Error)")
        failed += 1
        failed_tests.append((method, url, str(e)[:50]))

print("\n" + "="*110)
print(f"RESULTS: {passed:2d} PASSED | {failed:2d} FAILED | TOTAL: {passed+failed}")
print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
print("="*110)

if failed > 0:
    print("\nFailed Tests:")
    for method, url, error in failed_tests:
        print(f"  {method:4} {url} - {error}")

if failed == 0:
    print("\n" + " "*30 + "🎉 ALL {0} ENDPOINTS WORKING! PRODUCTION READY! 🎉".format(passed+failed))
print("\n" + "="*110 + "\n")
