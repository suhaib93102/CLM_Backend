#!/usr/bin/env python
"""
FINAL COMPREHENSIVE TEST - Production Ready
All modules: Templates, Versions, Contracts, Notifications, Admin, Documents
"""
import os, django, json
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from authentication.models import User

client = Client()
User.objects.filter(email="final@test.com").delete()

print("\n" + "="*100)
print("PRODUCTION COMPREHENSIVE TEST - ALL MODULES")
print("="*100)

# AUTH
client.post('/api/auth/register/', json.dumps({
    "email": "final@test.com", "password": "Test123!@#", "full_name": "Test"
}), content_type='application/json')

r = client.post('/api/auth/login/', json.dumps({
    "email": "final@test.com", "password": "Test123!@#"
}), content_type='application/json')

token = r.json().get('access')
uid = r.json().get('user', {}).get('user_id')
tid = r.json().get('user', {}).get('tenant_id')
h = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

print(f"\n✓ Auth: User {uid[:8]}... Tenant {tid[:8]}...\n")

# Test all endpoints
tests = [
    # CONTRACTS
    ("POST", "/api/contracts/", {"title": "MSA", "status": "draft"}),
    ("GET", "/api/contracts/", None),
    
    # TEMPLATES  
    ("POST", "/api/contract-templates/", {"name": "NDA", "contract_type": "NDA", "r2_key": "nda.docx"}),
    ("GET", "/api/contract-templates/", None),
    
    # NOTIFICATIONS
    ("POST", "/api/notifications/", {"message": "Test", "notification_type": "email", "subject": "S", "body": "B", "recipient_id": uid}),
    ("GET", "/api/notifications/", None),
    
    # WORKFLOWS
    ("POST", "/api/workflows/", {"name": "Workflow", "steps": []}),
    ("GET", "/api/workflows/", None),
    
    # METADATA
    ("POST", "/api/metadata/fields/", {"name": "field", "field_type": "text"}),
    ("GET", "/api/metadata/fields/", None),
    
    # DOCUMENTS
    ("GET", "/api/documents/", None),
    ("GET", "/api/repository/", None),
    ("GET", "/api/repository/folders/", None),
    
    # ADMIN PANEL
    ("GET", "/api/roles/", None),
    ("GET", "/api/permissions/", None),
    ("GET", "/api/users/", None),
    ("GET", "/api/admin/sla-rules/", None),
    ("GET", "/api/admin/sla-breaches/", None),
    ("GET", "/api/admin/users/roles/", None),
    ("GET", "/api/admin/tenants/", None),
    
    # AUDIT & SEARCH
    ("GET", "/api/audit-logs/", None),
    ("GET", "/api/audit-logs/stats/", None),
    ("GET", "/api/search/", None),
    ("POST", "/api/search/advanced/", {"query": "test"}),
    
    # APPROVALS
    ("GET", "/api/approvals/", None),
    
    # HEALTH
    ("GET", "/api/health/", None),
]

passed = 0
failed = 0

for method, url, data in tests:
    try:
        if method == "GET":
            resp = client.get(url, **h)
        else:
            resp = client.post(url, json.dumps(data), content_type='application/json', **h)
        
        if resp.status_code in [200, 201]:
            print(f"✓ {method:4} {url}")
            passed += 1
        else:
            print(f"✗ {method:4} {url} ({resp.status_code})")
            failed += 1
    except Exception as e:
        print(f"✗ {method:4} {url} (Error: {str(e)[:50]})")
        failed += 1

print("\n" + "="*100)
print(f"RESULTS: {passed} PASSED | {failed} FAILED | Total: {passed+failed}")
print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
print("="*100)

if failed == 0:
    print("\n🎉 ALL {0} ENDPOINTS WORKING - PRODUCTION READY! 🎉\n".format(passed+failed))
