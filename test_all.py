#!/usr/bin/env python3
"""
Test all endpoints with REAL data - Only 200/201 responses
"""
import requests, json
from datetime import datetime

BASE_URL = "http://localhost:8888/api"
HEADERS = {"Content-Type": "application/json"}

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test@123456"

print("=" * 80)
print("CLM BACKEND - REAL DATA ENDPOINT TEST")
print("=" * 80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

passed = 0
failed = 0

# Authenticate first
print("🔐 Authenticating...")
login = requests.post(f"{BASE_URL}/auth/login/", 
    json={"email": TEST_EMAIL, "password": TEST_PASSWORD}, headers=HEADERS)

if login.status_code != 200:
    print(f"❌ Login failed: {login.status_code}")
    exit(1)

token = login.json()['access']
auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
print(f"✅ Authenticated successfully\n")

def test(method, endpoint, data=None, name="", need_auth=True):
    global passed, failed
    headers = auth_headers if need_auth else HEADERS
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers)
        elif method == "POST":
            r = requests.post(url, json=data or {}, headers=headers)
        elif method == "PUT":
            r = requests.put(url, json=data or {}, headers=headers)
        else:
            return
        
        ok = r.status_code in (200, 201)
        status_str = f"✅ {r.status_code}" if ok else f"❌ {r.status_code}"
        print(f"{status_str} | {name:50} | {endpoint}")
        
        if ok:
            passed += 1
            # Show response preview
            try:
                data = r.json()
                if isinstance(data, dict):
                    count = len(data.get('results', []))
                    if count > 0:
                        print(f"     → {count} items returned")
            except:
                pass
        else:
            failed += 1
            try:
                print(f"     Error: {r.json()}")
            except:
                pass
    except Exception as e:
        print(f"❌ ERROR | {name:50} | {endpoint}")
        print(f"     {str(e)[:80]}")
        failed += 1

# Test endpoints
print("\n" + "=" * 80)
print("TESTING ENDPOINTS WITH REAL DATA")
print("=" * 80 + "\n")

# Auth
print("📌 AUTHENTICATION")
test("GET", "/auth/me/", name="Get current user", need_auth=True)
from datetime import datetime as dt
unique_email = f"test{int(dt.now().timestamp())}@test.com"
test("POST", "/auth/register/", {"email": unique_email, "password": "Pass@12345", "full_name": "Test User"}, "Register new user", False)
test("POST", "/auth/logout/", name="Logout", need_auth=True)

# Contracts
print("\n📌 CONTRACTS")
test("GET", "/contracts/", name="List contracts")
test("GET", "/contracts/statistics/", name="Contract statistics")
test("GET", "/contracts/recent/", name="Recent contracts")
test("POST", "/contracts/validate-clauses/", {"clauses": []}, "Validate clauses")

# Templates
print("\n📌 CONTRACT TEMPLATES")
test("GET", "/contract-templates/", name="List templates")

# Clauses
print("\n📌 CLAUSES")
test("GET", "/clauses/", name="List clauses")
test("POST", "/clauses/bulk-suggestions/", {"contracts": []}, "Bulk clause suggestions")

# Workflows
print("\n📌 WORKFLOWS")
test("GET", "/workflows/", name="List workflows")
test("GET", "/workflows/config/", name="Workflow config")

# Notifications
print("\n📌 NOTIFICATIONS")
test("GET", "/notifications/", name="List notifications")

# Audit Logs
print("\n📌 AUDIT LOGS")
test("GET", "/audit-logs/", name="List audit logs")
test("GET", "/audit-logs/stats/", name="Audit statistics")

# Search
print("\n📌 SEARCH")
test("GET", "/search/semantic/?q=test", name="Semantic search")
test("GET", "/search/hybrid/?q=test", name="Hybrid search")
test("GET", "/search/facets/", name="Search facets")
test("POST", "/search/advanced/", {"query": "test"}, "Advanced search")
test("GET", "/search/suggestions/?q=test", name="Search suggestions")

# Repository
print("\n📌 REPOSITORY")
test("GET", "/repository/", name="List documents")
test("GET", "/repository/folders/", name="List folders")

# Metadata
print("\n📌 METADATA")
test("GET", "/metadata/fields/", name="List metadata fields")

# AI
print("\n📌 AI & ML")
test("GET", "/ai/", name="List AI inferences")
test("GET", "/ai/usage/", name="AI usage stats")

# Rules
print("\n📌 RULES")
test("GET", "/rules/", name="List rules")
test("POST", "/rules/validate/", {"rule": {}}, "Validate rule")

# Approvals
print("\n📌 APPROVALS")
test("GET", "/approvals/", name="List approvals")

# Generation Jobs
print("\n📌 GENERATION JOBS")
test("GET", "/generation-jobs/", name="List generation jobs")

# Tenants
print("\n📌 TENANTS & MULTI-TENANCY")
test("GET", "/tenants/", name="List tenants")

# Health
print("\n📌 HEALTH & MONITORING")
test("GET", "/health/", name="Health check", need_auth=False)
test("GET", "/health/database/", name="Database health", need_auth=False)
test("GET", "/health/cache/", name="Cache health", need_auth=False)
test("GET", "/health/metrics/", name="System metrics", need_auth=False)

# Analytics
print("\n📌 ANALYTICS & UTILITIES")
test("GET", "/analysis/", name="Analytics dashboard", need_auth=True)
test("GET", "/documents/", name="Documents utility", need_auth=True)
test("GET", "/generation/", name="Generation utility", need_auth=True)

# Summary
print("\n" + "=" * 80)
print("TEST RESULTS")
print("=" * 80)
total = passed + failed
print(f"✅ Passed:  {passed:3d}")
print(f"❌ Failed:  {failed:3d}")
print(f"📊 Total:   {total:3d}")
if total > 0:
    print(f"📈 Pass Rate: {100*passed/total:.1f}%")
print("=" * 80)
