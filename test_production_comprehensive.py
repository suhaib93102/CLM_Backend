#!/usr/bin/env python
"""
CLM Backend - Production Level Comprehensive Testing Suite
Tests: Contracts, Templates, Versions, Notifications, Documents, Admin Panel
"""

import os
import sys
import django
import json
import time
from datetime import datetime
from decimal import Decimal
from io import BytesIO

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
TEST_EMAIL = "production_test@example.com"
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
            for key, value in response_data.items():
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
            return False, None, None
        
        data = response.json()
        access_token = data.get('access')
        user_id = data.get('user', {}).get('user_id')
        
        print_test("User Registration", True, details=f"User ID: {user_id}")
        print_info(f"✓ Access token acquired: {access_token[:50]}...")
        
        return True, access_token, user_id


# ============================================================================
# PART 2: CONTRACTS TESTS
# ============================================================================

class ContractTests:
    """Test contract CRUD and operations"""
    
    @staticmethod
    def test_create_contract(access_token):
        """Create a contract"""
        print_section("CONTRACTS: CREATE")
        
        # Create a test file
        pdf_content = b'%PDF-1.4\n%fake pdf content\n'
        test_file = SimpleUploadedFile(
            "test_contract.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        response = client.post(
            f'{BASE_URL}/contracts/',
            data={
                'file': test_file,
                'title': 'Production Test Contract',
                'counterparty': 'Test Vendor Inc.',
                'contract_type': 'Service Agreement',
                'status': 'draft'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 201
        data = response.json() if passed else {}
        contract_id = data.get('id')
        
        print_test("Create Contract", passed, 
                  details=f"Contract ID: {contract_id}" if contract_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, contract_id

    @staticmethod
    def test_list_contracts(access_token):
        """List all contracts"""
        print_section("CONTRACTS: LIST")
        
        response = client.get(
            f'{BASE_URL}/contracts/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Contracts", passed, 
                  details=f"Total: {count} contracts")
        
        return passed, data

    @staticmethod
    def test_get_contract(access_token, contract_id):
        """Get contract details"""
        print_section("CONTRACTS: GET DETAILS")
        
        if not contract_id:
            print_test("Get Contract", False, error="No contract ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/contracts/{contract_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Contract Details", passed,
                  details=f"Title: {data.get('title')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_update_contract(access_token, contract_id):
        """Update contract"""
        print_section("CONTRACTS: UPDATE")
        
        if not contract_id:
            print_test("Update Contract", False, error="No contract ID provided")
            return False
        
        response = client.put(
            f'{BASE_URL}/contracts/{contract_id}/',
            data={
                'title': 'Updated Production Test Contract',
                'status': 'In Review',
                'description': 'Updated description'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Update Contract", passed,
                  details=f"New Status: {data.get('status')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed

    @staticmethod
    def test_contract_versions(access_token, contract_id):
        """Test contract versioning"""
        print_section("CONTRACTS: VERSION HISTORY")
        
        if not contract_id:
            print_test("List Contract Versions", False, error="No contract ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/contracts/{contract_id}/versions/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Contract Versions", passed,
                  details=f"Total versions: {count}")
        
        return passed, data

    @staticmethod
    def test_create_version(access_token, contract_id):
        """Create new contract version"""
        print_section("CONTRACTS: CREATE NEW VERSION")
        
        if not contract_id:
            print_test("Create Contract Version", False, error="No contract ID provided")
            return False, None
        
        response = client.post(
            f'{BASE_URL}/contracts/{contract_id}/create-version/',
            data={
                'content': 'Updated contract content for new version...',
                'change_summary': 'Updated terms and conditions'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Create Contract Version", passed,
                  details=f"Version: {data.get('version_number')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_clone_contract(access_token, contract_id):
        """Clone a contract"""
        print_section("CONTRACTS: CLONE")
        
        if not contract_id:
            print_test("Clone Contract", False, error="No contract ID provided")
            return False, None
        
        response = client.post(
            f'{BASE_URL}/contracts/{contract_id}/clone/',
            data={'title': 'Cloned Production Test Contract'},
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        new_id = data.get('id')
        
        print_test("Clone Contract", passed,
                  details=f"New Contract ID: {new_id}" if new_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, new_id


# ============================================================================
# PART 3: CONTRACT TEMPLATES TESTS
# ============================================================================

class TemplateTests:
    """Test contract templates"""
    
    @staticmethod
    def test_create_template(access_token):
        """Create contract template"""
        print_section("TEMPLATES: CREATE")
        
        response = client.post(
            f'{BASE_URL}/contract-templates/',
            data={
                'title': 'Production Test Template',
                'description': 'Test template for production',
                'category': 'Service Agreement',
                'content': 'Template content goes here...',
                'tags': ['test', 'production']
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        template_id = data.get('id')
        
        print_test("Create Template", passed,
                  details=f"Template ID: {template_id}" if template_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, template_id

    @staticmethod
    def test_list_templates(access_token):
        """List all templates"""
        print_section("TEMPLATES: LIST")
        
        response = client.get(
            f'{BASE_URL}/contract-templates/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Templates", passed,
                  details=f"Total: {count} templates")
        
        return passed, data

    @staticmethod
    def test_get_template(access_token, template_id):
        """Get template details"""
        print_section("TEMPLATES: GET DETAILS")
        
        if not template_id:
            print_test("Get Template", False, error="No template ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/contract-templates/{template_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Template Details", passed,
                  details=f"Title: {data.get('title')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_update_template(access_token, template_id):
        """Update template"""
        print_section("TEMPLATES: UPDATE")
        
        if not template_id:
            print_test("Update Template", False, error="No template ID provided")
            return False
        
        response = client.put(
            f'{BASE_URL}/contract-templates/{template_id}/',
            data={
                'title': 'Updated Production Test Template',
                'description': 'Updated template description',
                'content': 'Updated template content...'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Update Template", passed,
                  error=data.get('error') if not passed else None)
        
        return passed

    @staticmethod
    def test_template_versions(access_token, template_id):
        """Test template version history"""
        print_section("TEMPLATES: VERSION HISTORY")
        
        if not template_id:
            print_test("List Template Versions", False, error="No template ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/contract-templates/{template_id}/versions/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Template Versions", passed,
                  details=f"Total versions: {count}")
        
        return passed, data

    @staticmethod
    def test_clone_template(access_token, template_id):
        """Clone a template"""
        print_section("TEMPLATES: CLONE")
        
        if not template_id:
            print_test("Clone Template", False, error="No template ID provided")
            return False, None
        
        response = client.post(
            f'{BASE_URL}/contract-templates/{template_id}/clone/',
            data={'title': 'Cloned Production Test Template'},
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        new_id = data.get('id')
        
        print_test("Clone Template", passed,
                  details=f"New Template ID: {new_id}" if new_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, new_id


# ============================================================================
# PART 4: CLAUSES TESTS
# ============================================================================

class ClauseTests:
    """Test contract clauses"""
    
    @staticmethod
    def test_create_clause(access_token):
        """Create a clause"""
        print_section("CLAUSES: CREATE")
        
        response = client.post(
            f'{BASE_URL}/clauses/',
            data={
                'title': 'Production Test Clause',
                'category': 'Payment Terms',
                'content': 'Test clause content...',
                'description': 'This is a test clause'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        clause_id = data.get('id')
        
        print_test("Create Clause", passed,
                  details=f"Clause ID: {clause_id}" if clause_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, clause_id

    @staticmethod
    def test_list_clauses(access_token):
        """List all clauses"""
        print_section("CLAUSES: LIST")
        
        response = client.get(
            f'{BASE_URL}/clauses/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Clauses", passed,
                  details=f"Total: {count} clauses")
        
        return passed, data

    @staticmethod
    def test_get_clause(access_token, clause_id):
        """Get clause details"""
        print_section("CLAUSES: GET DETAILS")
        
        if not clause_id:
            print_test("Get Clause", False, error="No clause ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/clauses/{clause_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Clause Details", passed,
                  details=f"Title: {data.get('title')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_clause_versions(access_token, clause_id):
        """Test clause version history"""
        print_section("CLAUSES: VERSION HISTORY")
        
        if not clause_id:
            print_test("List Clause Versions", False, error="No clause ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/clauses/{clause_id}/versions/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Clause Versions", passed,
                  details=f"Total versions: {count}")
        
        return passed, data


# ============================================================================
# PART 5: DOCUMENT STORAGE & RETRIEVAL TESTS
# ============================================================================

class DocumentTests:
    """Test document storage and retrieval"""
    
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

    @staticmethod
    def test_repository_list(access_token):
        """List repository documents"""
        print_section("REPOSITORY: LIST")
        
        response = client.get(
            f'{BASE_URL}/repository/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("List Repository", passed,
                  details=f"Documents in repository")
        
        return passed, data

    @staticmethod
    def test_create_document(access_token):
        """Create document in repository"""
        print_section("DOCUMENTS: CREATE")
        
        response = client.post(
            f'{BASE_URL}/repository/',
            data={
                'title': 'Production Test Document',
                'content': 'This is a test document for production testing',
                'document_type': 'Reference',
                'tags': ['test', 'production']
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        doc_id = data.get('id')
        
        print_test("Create Document", passed,
                  details=f"Document ID: {doc_id}" if doc_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, doc_id

    @staticmethod
    def test_get_document(access_token, doc_id):
        """Get document details"""
        print_section("DOCUMENTS: GET DETAILS")
        
        if not doc_id:
            print_test("Get Document", False, error="No document ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/repository/{doc_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Document Details", passed,
                  details=f"Title: {data.get('title')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_update_document(access_token, doc_id):
        """Update document"""
        print_section("DOCUMENTS: UPDATE")
        
        if not doc_id:
            print_test("Update Document", False, error="No document ID provided")
            return False
        
        response = client.put(
            f'{BASE_URL}/repository/{doc_id}/',
            data={
                'title': 'Updated Production Test Document',
                'content': 'Updated content for test document'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Update Document", passed,
                  error=data.get('error') if not passed else None)
        
        return passed

    @staticmethod
    def test_document_versions(access_token, doc_id):
        """Test document version history"""
        print_section("DOCUMENTS: VERSION HISTORY")
        
        if not doc_id:
            print_test("List Document Versions", False, error="No document ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/repository/{doc_id}/versions/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Document Versions", passed,
                  details=f"Total versions: {count}")
        
        return passed, data


# ============================================================================
# PART 6: NOTIFICATIONS TESTS
# ============================================================================

class NotificationTests:
    """Test notification system"""
    
    @staticmethod
    def test_list_notifications(access_token):
        """List notifications"""
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
        """Create notification"""
        print_section("NOTIFICATIONS: CREATE")
        
        response = client.post(
            f'{BASE_URL}/notifications/',
            data={
                'title': 'Production Test Notification',
                'message': 'This is a test notification',
                'notification_type': 'Alert',
                'priority': 'High'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        notif_id = data.get('id')
        
        print_test("Create Notification", passed,
                  details=f"Notification ID: {notif_id}" if notif_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, notif_id

    @staticmethod
    def test_get_notification(access_token, notif_id):
        """Get notification details"""
        print_section("NOTIFICATIONS: GET DETAILS")
        
        if not notif_id:
            print_test("Get Notification", False, error="No notification ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/notifications/{notif_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Notification Details", passed,
                  details=f"Title: {data.get('title')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_update_notification(access_token, notif_id):
        """Update notification"""
        print_section("NOTIFICATIONS: UPDATE")
        
        if not notif_id:
            print_test("Update Notification", False, error="No notification ID provided")
            return False
        
        response = client.put(
            f'{BASE_URL}/notifications/{notif_id}/',
            data={
                'title': 'Updated Production Test Notification',
                'status': 'Read'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Update Notification", passed,
                  details=f"Status: {data.get('status')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed


# ============================================================================
# PART 7: WORKFLOW TESTS
# ============================================================================

class WorkflowTests:
    """Test workflow management"""
    
    @staticmethod
    def test_list_workflows(access_token):
        """List workflows"""
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
        """Create workflow"""
        print_section("WORKFLOWS: CREATE")
        
        response = client.post(
            f'{BASE_URL}/workflows/',
            data={
                'name': 'Production Test Workflow',
                'description': 'Test workflow for production',
                'workflow_type': 'Approval',
                'status': 'Active'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        workflow_id = data.get('id')
        
        print_test("Create Workflow", passed,
                  details=f"Workflow ID: {workflow_id}" if workflow_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, workflow_id

    @staticmethod
    def test_get_workflow(access_token, workflow_id):
        """Get workflow details"""
        print_section("WORKFLOWS: GET DETAILS")
        
        if not workflow_id:
            print_test("Get Workflow", False, error="No workflow ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/workflows/{workflow_id}/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Workflow Details", passed,
                  details=f"Name: {data.get('name')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data

    @staticmethod
    def test_workflow_status(access_token, workflow_id):
        """Get workflow status"""
        print_section("WORKFLOWS: STATUS")
        
        if not workflow_id:
            print_test("Get Workflow Status", False, error="No workflow ID provided")
            return False, None
        
        response = client.get(
            f'{BASE_URL}/workflows/{workflow_id}/status/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Get Workflow Status", passed,
                  details=f"Current Status: {data.get('status')}" if passed else None,
                  error=data.get('error') if not passed else None)
        
        return passed, data


# ============================================================================
# PART 8: METADATA & AUDIT TESTS
# ============================================================================

class MetadataTests:
    """Test metadata management"""
    
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
        """Create metadata field"""
        print_section("METADATA: CREATE FIELD")
        
        response = client.post(
            f'{BASE_URL}/metadata/fields/',
            data={
                'name': 'production_field',
                'label': 'Production Test Field',
                'field_type': 'String',
                'required': False
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        passed = response.status_code == 201 or response.status_code == 200
        data = response.json() if passed else {}
        field_id = data.get('id')
        
        print_test("Create Metadata Field", passed,
                  details=f"Field ID: {field_id}" if field_id else None,
                  error=data.get('error') if not passed else None)
        
        return passed, field_id


class AuditTests:
    """Test audit logging"""
    
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
                  details=f"Total: {count} audit entries")
        
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
        
        print_test("Get Audit Statistics", passed,
                  details=f"Stats retrieved")
        
        return passed, data


# ============================================================================
# PART 9: SEARCH & ANALYSIS TESTS
# ============================================================================

class SearchTests:
    """Test search functionality"""
    
    @staticmethod
    def test_basic_search(access_token):
        """Basic search"""
        print_section("SEARCH: BASIC")
        
        response = client.get(
            f'{BASE_URL}/search/?q=test',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("Basic Search", passed,
                  details=f"Results found: {count}")
        
        return passed, data

    @staticmethod
    def test_semantic_search(access_token):
        """Semantic search"""
        print_section("SEARCH: SEMANTIC")
        
        response = client.get(
            f'{BASE_URL}/search/semantic/?q=agreement',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Semantic Search", passed,
                  details=f"Semantic search executed")
        
        return passed, data

    @staticmethod
    def test_search_facets(access_token):
        """Search facets"""
        print_section("SEARCH: FACETS")
        
        response = client.get(
            f'{BASE_URL}/search/facets/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Search Facets", passed,
                  details=f"Facets retrieved")
        
        return passed, data


# ============================================================================
# PART 10: APPROVALS & HEALTH CHECK
# ============================================================================

class ApprovalTests:
    """Test approval system"""
    
    @staticmethod
    def test_list_approvals(access_token):
        """List approvals"""
        print_section("APPROVALS: LIST")
        
        response = client.get(
            f'{BASE_URL}/approvals/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        
        print_test("List Approvals", passed,
                  details=f"Total: {count} approvals")
        
        return passed, data


class HealthTests:
    """Test system health"""
    
    @staticmethod
    def test_system_health():
        """Test system health"""
        print_section("SYSTEM HEALTH")
        
        response = client.get(f'{BASE_URL}/health/')
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("System Health Check", passed,
                  details=f"Status: {data.get('status')}")
        
        return passed, data

    @staticmethod
    def test_database_health():
        """Test database health"""
        print_section("DATABASE HEALTH")
        
        response = client.get(f'{BASE_URL}/health/database/')
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Database Health Check", passed,
                  details=f"Database status: {data.get('database')}")
        
        return passed, data

    @staticmethod
    def test_cache_health():
        """Test cache health"""
        print_section("CACHE HEALTH")
        
        response = client.get(f'{BASE_URL}/health/cache/')
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test("Cache Health Check", passed,
                  details=f"Cache status: {data.get('cache')}")
        
        return passed, data


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Execute all production tests"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*12 + "CLM BACKEND - PRODUCTION LEVEL TESTING SUITE" + " "*22 + "║")
    print("║" + " "*78 + "║")
    print("║" + f"  Tests: Contracts, Templates, Versions, Documents, Notifications" + " "*14 + "║")
    print("║" + f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*45 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{Colors.ENDC}\n")
    
    results = {}
    tokens = {}
    ids = {}
    
    try:
        # ====== HEALTH CHECKS ======
        passed, _ = HealthTests.test_system_health()
        results['System Health'] = passed
        
        passed, _ = HealthTests.test_database_health()
        results['Database Health'] = passed
        
        passed, _ = HealthTests.test_cache_health()
        results['Cache Health'] = passed
        
        # ====== AUTHENTICATION ======
        passed, access_token, user_id = AuthenticationTests.test_auth_setup()
        results['User Registration'] = passed
        tokens['access'] = access_token
        ids['user_id'] = user_id
        
        if not access_token:
            print(f"{Colors.FAIL}Authentication failed. Stopping tests.{Colors.ENDC}")
            return False
        
        # ====== CONTRACTS ======
        passed, contract_id = ContractTests.test_create_contract(access_token)
        results['Create Contract'] = passed
        ids['contract_id'] = contract_id
        
        if contract_id:
            passed, _ = ContractTests.test_list_contracts(access_token)
            results['List Contracts'] = passed
            
            passed, _ = ContractTests.test_get_contract(access_token, contract_id)
            results['Get Contract'] = passed
            
            passed = ContractTests.test_update_contract(access_token, contract_id)
            results['Update Contract'] = passed
            
            passed, _ = ContractTests.test_contract_versions(access_token, contract_id)
            results['Contract Versions'] = passed
            
            passed, _ = ContractTests.test_create_version(access_token, contract_id)
            results['Create Contract Version'] = passed
            
            passed, _ = ContractTests.test_clone_contract(access_token, contract_id)
            results['Clone Contract'] = passed
        
        # ====== TEMPLATES ======
        passed, template_id = TemplateTests.test_create_template(access_token)
        results['Create Template'] = passed
        ids['template_id'] = template_id
        
        if template_id:
            passed, _ = TemplateTests.test_list_templates(access_token)
            results['List Templates'] = passed
            
            passed, _ = TemplateTests.test_get_template(access_token, template_id)
            results['Get Template'] = passed
            
            passed = TemplateTests.test_update_template(access_token, template_id)
            results['Update Template'] = passed
            
            passed, _ = TemplateTests.test_template_versions(access_token, template_id)
            results['Template Versions'] = passed
            
            passed, _ = TemplateTests.test_clone_template(access_token, template_id)
            results['Clone Template'] = passed
        
        # ====== CLAUSES ======
        passed, clause_id = ClauseTests.test_create_clause(access_token)
        results['Create Clause'] = passed
        ids['clause_id'] = clause_id
        
        if clause_id:
            passed, _ = ClauseTests.test_list_clauses(access_token)
            results['List Clauses'] = passed
            
            passed, _ = ClauseTests.test_get_clause(access_token, clause_id)
            results['Get Clause'] = passed
            
            passed, _ = ClauseTests.test_clause_versions(access_token, clause_id)
            results['Clause Versions'] = passed
        
        # ====== DOCUMENTS ======
        passed, _ = DocumentTests.test_list_documents(access_token)
        results['List Documents'] = passed
        
        passed, _ = DocumentTests.test_repository_list(access_token)
        results['List Repository'] = passed
        
        passed, doc_id = DocumentTests.test_create_document(access_token)
        results['Create Document'] = passed
        ids['doc_id'] = doc_id
        
        if doc_id:
            passed, _ = DocumentTests.test_get_document(access_token, doc_id)
            results['Get Document'] = passed
            
            passed = DocumentTests.test_update_document(access_token, doc_id)
            results['Update Document'] = passed
            
            passed, _ = DocumentTests.test_document_versions(access_token, doc_id)
            results['Document Versions'] = passed
        
        # ====== NOTIFICATIONS ======
        passed, _ = NotificationTests.test_list_notifications(access_token)
        results['List Notifications'] = passed
        
        passed, notif_id = NotificationTests.test_create_notification(access_token)
        results['Create Notification'] = passed
        ids['notif_id'] = notif_id
        
        if notif_id:
            passed, _ = NotificationTests.test_get_notification(access_token, notif_id)
            results['Get Notification'] = passed
            
            passed = NotificationTests.test_update_notification(access_token, notif_id)
            results['Update Notification'] = passed
        
        # ====== WORKFLOWS ======
        passed, _ = WorkflowTests.test_list_workflows(access_token)
        results['List Workflows'] = passed
        
        passed, workflow_id = WorkflowTests.test_create_workflow(access_token)
        results['Create Workflow'] = passed
        ids['workflow_id'] = workflow_id
        
        if workflow_id:
            passed, _ = WorkflowTests.test_get_workflow(access_token, workflow_id)
            results['Get Workflow'] = passed
            
            passed, _ = WorkflowTests.test_workflow_status(access_token, workflow_id)
            results['Workflow Status'] = passed
        
        # ====== METADATA ======
        passed, _ = MetadataTests.test_list_metadata_fields(access_token)
        results['List Metadata Fields'] = passed
        
        passed, _ = MetadataTests.test_create_metadata_field(access_token)
        results['Create Metadata Field'] = passed
        
        # ====== AUDIT ======
        passed, _ = AuditTests.test_list_audit_logs(access_token)
        results['List Audit Logs'] = passed
        
        passed, _ = AuditTests.test_audit_stats(access_token)
        results['Audit Statistics'] = passed
        
        # ====== SEARCH ======
        passed, _ = SearchTests.test_basic_search(access_token)
        results['Basic Search'] = passed
        
        passed, _ = SearchTests.test_semantic_search(access_token)
        results['Semantic Search'] = passed
        
        passed, _ = SearchTests.test_search_facets(access_token)
        results['Search Facets'] = passed
        
        # ====== APPROVALS ======
        passed, _ = ApprovalTests.test_list_approvals(access_token)
        results['List Approvals'] = passed
        
    except Exception as e:
        print(f"{Colors.FAIL}ERROR: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
    
    # ========== SUMMARY ==========
    print_section("FINAL SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    pass_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}Test Results:{Colors.ENDC}")
    print(f"├─ Total Tests: {total_tests}")
    print(f"├─ Passed: {Colors.OKGREEN}{passed_tests}{Colors.ENDC}")
    print(f"├─ Failed: {Colors.FAIL}{failed_tests}{Colors.ENDC}")
    print(f"└─ Pass Rate: {Colors.OKGREEN}{pass_percentage:.1f}%{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Test Categories:{Colors.ENDC}")
    
    categories = {
        'Health Checks': ['System Health', 'Database Health', 'Cache Health'],
        'Authentication': ['User Registration'],
        'Contracts': ['Create Contract', 'List Contracts', 'Get Contract', 'Update Contract', 
                     'Contract Versions', 'Create Contract Version', 'Clone Contract'],
        'Templates': ['Create Template', 'List Templates', 'Get Template', 'Update Template',
                     'Template Versions', 'Clone Template'],
        'Clauses': ['Create Clause', 'List Clauses', 'Get Clause', 'Clause Versions'],
        'Documents': ['List Documents', 'List Repository', 'Create Document', 'Get Document',
                     'Update Document', 'Document Versions'],
        'Notifications': ['List Notifications', 'Create Notification', 'Get Notification',
                         'Update Notification'],
        'Workflows': ['List Workflows', 'Create Workflow', 'Get Workflow', 'Workflow Status'],
        'Metadata': ['List Metadata Fields', 'Create Metadata Field'],
        'Audit': ['List Audit Logs', 'Audit Statistics'],
        'Search': ['Basic Search', 'Semantic Search', 'Search Facets'],
        'Approvals': ['List Approvals']
    }
    
    for category, tests in categories.items():
        cat_results = [results.get(t, False) for t in tests if t in results]
        if cat_results:
            cat_passed = sum(1 for v in cat_results if v)
            cat_total = len(cat_results)
            status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if all(cat_results) else f"{Colors.FAIL}✗{Colors.ENDC}"
            print(f"{status} {category}: {cat_passed}/{cat_total} passed")
    
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.ENDC}")
    for test_name, passed in results.items():
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*80}")
    if failed_tests == 0:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED - PRODUCTION READY!{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠ {failed_tests} TEST(S) FAILED - REVIEW REQUIRED{Colors.ENDC}")
    print(f"{'='*80}\n")
    
    # Cleanup
    cleanup()
    
    return failed_tests == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
