#!/usr/bin/env python
"""
CLM Backend - Production Level Comprehensive Testing Suite
Tests: Health, Auth, Documents, Notifications, Workflows, Search, Admin
"""

import os
import sys
import django
import json
import time
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch, MagicMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
client = Client()

BASE_URL = "http://localhost:8000/api"

# Test User Credentials
TEST_EMAIL = "production_test_final@example.com"
TEST_PASSWORD = "ProductionTest123!"

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_test(test_name, passed, response_data=None, error=None, details=None):
    """Print test result"""
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {details}")
    if response_data:
        if isinstance(response_data, dict):
            for key, value in list(response_data.items())[:3]:  # Show first 3 keys
                if key not in ['response'] and not isinstance(value, (dict, list)):
                    print(f"  ├─ {key}: {value}")
    if error:
        print(f"  {Colors.FAIL}Error: {error}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def cleanup():
    """Clean up test data"""
    try:
        User.objects.filter(email=TEST_EMAIL).delete()
        print_info("Cleaned up test user")
    except:
        pass

# ============================================================================
# PART 1: AUTHENTICATION & SETUP
# ============================================================================

class AuthenticationTests:
    """Setup authentication for subsequent tests"""
    
    @staticmethod
    def test_auth_setup():
        """Setup user and get JWT token"""
        print_section("AUTHENTICATION SETUP")
        
        # Clean up
        cleanup()
        
        # Register
        response = client.post(
            f'{BASE_URL}/auth/register/',
            data={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD,
                'full_name': 'Production Test User'
            },
            content_type='application/json'
        )
        
        if response.status_code != 201:
            print_test("User Registration", False, error=response.json())
            return False, None
        
        user_data = response.json()
        user_id = user_data.get('user_id')
        print_test("User Registration", True, details=f"User ID: {user_id}")
        
        # Login
        response = client.post(
            f'{BASE_URL}/auth/login/',
            data={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD
            },
            content_type='application/json'
        )
        
        if response.status_code != 200:
            print_test("User Login", False, error=response.json())
            return False, None
        
        login_data = response.json()
        access_token = login_data.get('access')
        print_test("User Login", True, details="Token acquired")
        print_info(f"✓ Access token acquired: {access_token[:50]}...")
        
        return True, access_token

# ============================================================================
# PART 2: HEALTH CHECKS
# ============================================================================

class HealthTests:
    """Health check tests"""
    
    @staticmethod
    def test_system_health():
        """Test system health endpoint"""
        print_section("HEALTH: SYSTEM")
        
        response = client.get(f'{BASE_URL}/health/')
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("System Health Check", passed, 
                  details=f"Status: {data.get('status')}" if passed else None)
        return passed
    
    @staticmethod
    def test_database_health():
        """Test database health endpoint"""
        print_section("HEALTH: DATABASE")
        
        response = client.get(f'{BASE_URL}/health/database/')
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Database Health Check", passed,
                  details=f"Status: {data.get('status')}" if passed else None)
        return passed
    
    @staticmethod
    def test_cache_health():
        """Test cache health endpoint"""
        print_section("HEALTH: CACHE")
        
        response = client.get(f'{BASE_URL}/health/cache/')
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Cache Health Check", passed,
                  details=f"Status: {data.get('status')}" if passed else None)
        return passed

# ============================================================================
# PART 3: DOCUMENTS & REPOSITORY
# ============================================================================

class DocumentTests:
    """Document storage and retrieval tests"""
    
    @staticmethod
    def test_list_documents(access_token):
        """List all documents"""
        print_section("DOCUMENTS: LIST")
        
        response = client.get(
            f'{BASE_URL}/documents/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Documents", passed, 
                  details=f"Total: {count} documents")
        return passed, data

# ============================================================================
# PART 4: NOTIFICATIONS
# ============================================================================

class NotificationTests:
    """Notification system tests"""
    
    @staticmethod
    def test_list_notifications(access_token):
        """List all notifications"""
        print_section("NOTIFICATIONS: LIST")
        
        response = client.get(
            f'{BASE_URL}/notifications/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Notifications", passed, 
                  details=f"Total: {count} notifications")
        return passed, data
    
    @staticmethod
    def test_create_notification(access_token):
        """Create a notification"""
        print_section("NOTIFICATIONS: CREATE")
        
        response = client.post(
            f'{BASE_URL}/notifications/',
            data={
                'tenant_id': '00000000-0000-0000-0000-000000000000',
                'recipient_id': '00000000-0000-0000-0000-000000000000',
                'subject': 'Test Notification',
                'body': 'This is a test notification',
                'notification_type': 'email'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code in [200, 201]
        data = response.json() if passed else {}
        notification_id = data.get('id')
        
        print_test("Create Notification", passed,
                  details=f"ID: {notification_id}" if notification_id else None,
                  error=data.get('error') if not passed else None)
        return passed, notification_id

# ============================================================================
# PART 5: WORKFLOWS
# ============================================================================

class WorkflowTests:
    """Workflow tests"""
    
    @staticmethod
    def test_list_workflows(access_token):
        """List all workflows"""
        print_section("WORKFLOWS: LIST")
        
        response = client.get(
            f'{BASE_URL}/workflows/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Workflows", passed, 
                  details=f"Total: {count} workflows")
        return passed, data
    
    @staticmethod
    def test_create_workflow(access_token):
        """Create a workflow"""
        print_section("WORKFLOWS: CREATE")
        
        response = client.post(
            f'{BASE_URL}/workflows/',
            data={
                'tenant_id': '00000000-0000-0000-0000-000000000000',
                'name': 'Test Workflow',
                'description': 'Test workflow for production testing',
                'created_by': '00000000-0000-0000-0000-000000000000',
                'steps': [
                    {'order': 1, 'action': 'create_contract', 'description': 'Create a contract'},
                    {'order': 2, 'action': 'send_for_review', 'description': 'Send for review'},
                    {'order': 3, 'action': 'approve', 'description': 'Approve contract'}
                ]
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code in [200, 201]
        data = response.json() if passed else {}
        workflow_id = data.get('id')
        
        print_test("Create Workflow", passed,
                  details=f"ID: {workflow_id}" if workflow_id else None,
                  error=data.get('error') if not passed else None)
        return passed, workflow_id

# ============================================================================
# PART 6: METADATA
# ============================================================================

class MetadataTests:
    """Metadata/Custom Fields tests"""
    
    @staticmethod
    def test_list_metadata_fields(access_token):
        """List metadata fields"""
        print_section("METADATA: LIST FIELDS")
        
        response = client.get(
            f'{BASE_URL}/metadata/fields/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Metadata Fields", passed, 
                  details=f"Total: {count} fields")
        return passed, data
    
    @staticmethod
    def test_create_metadata_field(access_token):
        """Create a metadata field"""
        print_section("METADATA: CREATE FIELD")
        
        response = client.post(
            f'{BASE_URL}/metadata/fields/',
            data={
                'tenant_id': '00000000-0000-0000-0000-000000000000',
                'name': 'Custom Department',
                'field_type': 'text',
                'required': False,
                'description': 'Custom department field for testing'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code in [200, 201]
        data = response.json() if passed else {}
        field_id = data.get('id')
        
        print_test("Create Metadata Field", passed,
                  details=f"ID: {field_id}" if field_id else None,
                  error=data.get('error') if not passed else None)
        return passed, field_id

# ============================================================================
# PART 7: AUDIT LOGS
# ============================================================================

class AuditTests:
    """Audit logging tests"""
    
    @staticmethod
    def test_list_audit_logs(access_token):
        """List audit logs"""
        print_section("AUDIT LOGS: LIST")
        
        response = client.get(
            f'{BASE_URL}/audit-logs/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Audit Logs", passed, 
                  details=f"Total: {count} audit logs")
        return passed, data
    
    @staticmethod
    def test_audit_stats(access_token):
        """Get audit statistics"""
        print_section("AUDIT LOGS: STATISTICS")
        
        response = client.get(
            f'{BASE_URL}/audit-logs/stats/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Audit Statistics", passed, 
                  details=f"Stats retrieved: {len(data)} metrics" if passed else None)
        return passed, data

# ============================================================================
# PART 8: SEARCH
# ============================================================================

class SearchTests:
    """Search functionality tests"""
    
    @staticmethod
    def test_basic_search(access_token):
        """Test basic search"""
        print_section("SEARCH: BASIC")
        
        response = client.get(
            f'{BASE_URL}/search/?q=test',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("Basic Search", passed, 
                  details=f"Results: {count}")
        return passed, data
    
    @staticmethod
    def test_semantic_search(access_token):
        """Test semantic search"""
        print_section("SEARCH: SEMANTIC")
        
        response = client.get(
            f'{BASE_URL}/search/semantic/?q=contract',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("Semantic Search", passed, 
                  details=f"Results: {count}")
        return passed, data

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_all_tests():
    """Run all production tests"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   CLM BACKEND - PRODUCTION COMPREHENSIVE TEST SUITE            ║")
    print("║   Testing: Health, Auth, Documents, Notifications,            ║")
    print("║            Workflows, Metadata, Audit, Search                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Track results
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # Part 1: Health Checks
    print_section("PHASE 1: HEALTH CHECKS")
    health_system = HealthTests.test_system_health()
    results['total'] += 1
    if health_system: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('System Health', health_system))
    
    health_db = HealthTests.test_database_health()
    results['total'] += 1
    if health_db: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Database Health', health_db))
    
    health_cache = HealthTests.test_cache_health()
    results['total'] += 1
    if health_cache: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Cache Health', health_cache))
    
    # Part 2: Authentication
    print_section("PHASE 2: AUTHENTICATION")
    auth_passed, access_token = AuthenticationTests.test_auth_setup()
    results['total'] += 1
    if auth_passed: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Authentication', auth_passed))
    
    if not access_token:
        print(f"\n{Colors.FAIL}Authentication failed. Stopping tests.{Colors.ENDC}")
        return results
    
    # Part 3: Documents
    print_section("PHASE 3: DOCUMENTS & STORAGE")
    doc_passed, doc_data = DocumentTests.test_list_documents(access_token)
    results['total'] += 1
    if doc_passed: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Documents', doc_passed))
    
    # Part 4: Notifications
    print_section("PHASE 4: NOTIFICATIONS")
    notif_list, _ = NotificationTests.test_list_notifications(access_token)
    results['total'] += 1
    if notif_list: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('List Notifications', notif_list))
    
    notif_create, notif_id = NotificationTests.test_create_notification(access_token)
    results['total'] += 1
    if notif_create: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Create Notification', notif_create))
    
    # Part 5: Workflows
    print_section("PHASE 5: WORKFLOWS")
    workflow_list, _ = WorkflowTests.test_list_workflows(access_token)
    results['total'] += 1
    if workflow_list: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('List Workflows', workflow_list))
    
    workflow_create, workflow_id = WorkflowTests.test_create_workflow(access_token)
    results['total'] += 1
    if workflow_create: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Create Workflow', workflow_create))
    
    # Part 6: Metadata
    print_section("PHASE 6: METADATA")
    metadata_list, _ = MetadataTests.test_list_metadata_fields(access_token)
    results['total'] += 1
    if metadata_list: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('List Metadata', metadata_list))
    
    metadata_create, field_id = MetadataTests.test_create_metadata_field(access_token)
    results['total'] += 1
    if metadata_create: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Create Metadata Field', metadata_create))
    
    # Part 7: Audit Logs
    print_section("PHASE 7: AUDIT LOGS")
    audit_list, _ = AuditTests.test_list_audit_logs(access_token)
    results['total'] += 1
    if audit_list: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('List Audit Logs', audit_list))
    
    audit_stats, _ = AuditTests.test_audit_stats(access_token)
    results['total'] += 1
    if audit_stats: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Audit Statistics', audit_stats))
    
    # Part 8: Search
    print_section("PHASE 8: SEARCH")
    search_basic, _ = SearchTests.test_basic_search(access_token)
    results['total'] += 1
    if search_basic: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Basic Search', search_basic))
    
    search_semantic, _ = SearchTests.test_semantic_search(access_token)
    results['total'] += 1
    if search_semantic: results['passed'] += 1
    else: results['failed'] += 1
    results['tests'].append(('Semantic Search', search_semantic))
    
    # Print Summary
    print_section("TEST SUMMARY")
    pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.OKGREEN}Passed: {results['passed']}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed: {results['failed']}{Colors.ENDC}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print()
    
    for test_name, passed in results['tests']:
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"  {status} {test_name}")
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    return results

if __name__ == '__main__':
    try:
        results = run_all_tests()
        cleanup()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        cleanup()
    except Exception as e:
        print(f"\n{Colors.FAIL}Error running tests: {e}{Colors.ENDC}")
        cleanup()
