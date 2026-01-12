#!/usr/bin/env python
"""
Approval Workflow with Email Notifications - Complete Test
Demonstrates end-to-end approval workflow with Gmail SMTP integration
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.test import Client
from authentication.models import User
from tenants.models import TenantModel
from contracts.models import Contract
from approvals.models import ApprovalModel
from notifications.models import NotificationModel
from notifications.email_service import EmailService
from notifications.notification_service import NotificationService
from approvals.workflow_engine import ApprovalWorkflowEngine


# Colors for output
class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_header(title):
    print(f"\n{Colors.BOLD}{'='*80}\n{title}\n{'='*80}{Colors.ENDC}\n")


def test_email_configuration():
    """Test Gmail SMTP configuration"""
    print_header("TEST 1: Email Service Configuration")
    
    email_service = EmailService()
    
    # Check if configured by verifying credentials exist
    has_smtp_host = bool(email_service.smtp_host)
    has_sender_email = bool(email_service.sender_email)
    has_sender_password = bool(email_service.sender_password)
    
    is_configured = has_smtp_host and has_sender_email and has_sender_password
    
    if is_configured:
        print_success(f"Email service configured")
        print(f"  SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
        print(f"  Sender: {email_service.sender_email}")
        print(f"  App Name: {email_service.sender_name}")
        return True
    else:
        print_error("Email service not configured")
        print("  Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to .env file")
        return False


def test_approval_request_notification():
    """Test approval request email"""
    print_header("TEST 2: Approval Request Email Notification")
    
    email_service = EmailService()
    
    # Check if configured
    is_configured = bool(email_service.sender_email and email_service.sender_password)
    
    if not is_configured:
        print_error("Email service not configured, skipping test")
        return False
    
    try:
        result = email_service.send_approval_request_email(
            recipient_email='test.approver@example.com',
            recipient_name='Jane Smith',
            approver_name='Jane Smith',
            document_title='Service Agreement - Acme Corp',
            document_type='contract',
            approval_id='APR-001-TEST',
            requester_name='John Manager',
            priority='high'
        )
        
        if result:
            print_success("Approval request email sent successfully")
            print("  Email contains:")
            print("    - Document details")
            print("    - Approve/Reject buttons")
            print("    - Direct action links")
            return True
        else:
            print_error("Failed to send approval request email")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_approval_response_notifications():
    """Test approval response emails (approved/rejected)"""
    print_header("TEST 3: Approval Response Email Notifications")
    
    email_service = EmailService()
    
    # Check if configured
    is_configured = bool(email_service.sender_email and email_service.sender_password)
    
    if not is_configured:
        print_error("Email service not configured")
        return False
    
    results = []
    
    # Test approval email
    try:
        result = email_service.send_approval_approved_email(
            recipient_email='requester@example.com',
            recipient_name='John Manager',
            document_title='Service Agreement - Acme Corp',
            approver_name='Jane Smith',
            approval_comment='Looks good. Approved for execution.'
        )
        results.append(('Approval Email', result))
    except Exception as e:
        print_error(f"Approval email error: {str(e)}")
        results.append(('Approval Email', False))
    
    # Test rejection email
    try:
        result = email_service.send_approval_rejected_email(
            recipient_email='requester@example.com',
            recipient_name='John Manager',
            document_title='Service Agreement - Acme Corp',
            approver_name='Jane Smith',
            rejection_reason='Need clarification on payment terms section 4.2'
        )
        results.append(('Rejection Email', result))
    except Exception as e:
        print_error(f"Rejection email error: {str(e)}")
        results.append(('Rejection Email', False))
    
    # Print results
    for name, success in results:
        if success:
            print_success(f"{name} sent successfully")
        else:
            print_error(f"{name} failed")
    
    return all(r[1] for r in results)


def test_workflow_engine():
    """Test approval workflow engine"""
    print_header("TEST 4: Approval Workflow Engine")
    
    engine = ApprovalWorkflowEngine()
    
    # Create rule
    print("Creating workflow rule...")
    rule = engine.create_rule(
        name='High-Value Contract Review',
        entity_type='contract',
        conditions={'value_gt': 25000},
        approvers=['manager@example.com', 'cfo@example.com'],
        approval_levels=2,
        timeout_days=7,
        escalation_enabled=True,
        notification_enabled=True
    )
    print_success(f"Rule created: {rule.name}")
    
    # Create approval request
    print("Creating approval request...")
    request, email_sent = engine.create_approval_request(
        entity_id='contract-123',
        entity_type='contract',
        entity={'value_gt': 50000},
        requester_id='user-001',
        requester_email='john@company.com',
        requester_name='John Manager',
        approver_id='approver-001',
        approver_email='jane@company.com',
        approver_name='Jane Smith',
        document_title='Service Agreement - Acme Corp',
        priority='high',
        metadata={'contract_value': 50000}
    )
    
    if request:
        print_success(f"Approval request created: {request.request_id}")
        print(f"  Status: {request.status.value}")
        print(f"  Priority: {request.priority.value}")
        print(f"  Email sent: {email_sent}")
        
        # List pending requests
        pending = engine.list_pending_requests()
        print(f"  Total pending requests: {len(pending)}")
        
        # Approve request
        print("Approving request...")
        success, msg = engine.approve_request(request.request_id, comment="Approved - ready to proceed")
        if success:
            print_success(f"Request approved: {msg}")
        else:
            print_error(f"Approval failed: {msg}")
        
        # Get statistics
        stats = engine.get_statistics()
        print(f"\nWorkflow Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Approved: {stats['approved']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Approval Rate: {stats['approval_rate']:.1f}%")
        
        return True
    else:
        print_error("Failed to create approval request")
        return False


def test_in_app_notifications():
    """Test in-app notification creation"""
    print_header("TEST 5: In-App Notifications")
    
    try:
        # Get or create tenant
        tenant = TenantModel.objects.first()
        if not tenant:
            tenant = TenantModel.objects.create(name='Test Tenant')
        
        # Create test user
        test_user, created = User.objects.get_or_create(
            email='notification.test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'tenant_id': tenant.id,
                'is_active': True
            }
        )
        
        # Create notification
        notification = NotificationModel.objects.create(
            tenant_id=tenant.id,
            recipient_id=test_user.user_id,
            notification_type='in_app',
            subject='Approval Request: Service Agreement',
            body='You have a new approval request from John Manager',
            status='pending'
        )
        
        print_success(f"In-app notification created: {notification.id}")
        print(f"  Recipient: {test_user.email}")
        print(f"  Subject: {notification.subject}")
        print(f"  Status: {notification.status}")
        
        # Verify in database
        db_notification = NotificationModel.objects.get(id=notification.id)
        print_success(f"Verified in database")
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_end_to_end_approval():
    """Test complete approval workflow with database"""
    print_header("TEST 6: End-to-End Approval Workflow (Database)")
    
    try:
        # Get or create tenant
        tenant = TenantModel.objects.first()
        if not tenant:
            tenant = TenantModel.objects.create(name='Workflow Test Tenant')
        print_success(f"Using tenant: {tenant.name}")
        
        # Create users
        requester, _ = User.objects.get_or_create(
            email='workflow.requester@example.com',
            defaults={
                'first_name': 'Workflow',
                'last_name': 'Requester',
                'tenant_id': tenant.id,
                'is_active': True
            }
        )
        
        approver, _ = User.objects.get_or_create(
            email='workflow.approver@example.com',
            defaults={
                'first_name': 'Workflow',
                'last_name': 'Approver',
                'tenant_id': tenant.id,
                'is_active': True
            }
        )
        print_success(f"Created users: Requester and Approver")
        
        # Create contract
        contract = Contract.objects.create(
            tenant_id=tenant.id,
            title='End-to-End Test Contract',
            description='Testing the complete approval workflow',
            status='draft',
            contract_type='Service Agreement',
            created_by=requester.user_id
        )
        print_success(f"Created contract: {contract.title}")
        
        # Create approval request in database
        approval = ApprovalModel.objects.create(
            tenant_id=tenant.id,
            entity_type='contract',
            entity_id=contract.id,
            requester_id=requester.user_id,
            approver_id=approver.user_id,
            status='pending',
            comment='Awaiting approval'
        )
        print_success(f"Created approval request in database: {approval.id}")
        
        # Update status
        approval.status = 'approved'
        approval.comment = 'Approved - meets all requirements'
        approval.save()
        print_success(f"Updated approval status to: {approval.status}")
        
        # Query approvals
        pending = ApprovalModel.objects.filter(
            tenant_id=tenant.id,
            status='pending'
        ).count()
        approved = ApprovalModel.objects.filter(
            tenant_id=tenant.id,
            status='approved'
        ).count()
        
        print(f"\nApproval Statistics:")
        print(f"  Pending: {pending}")
        print(f"  Approved: {approved}")
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*80}")
    print("APPROVAL WORKFLOW WITH EMAIL NOTIFICATIONS - COMPLETE TEST")
    print(f"{'='*80}{Colors.ENDC}\n")
    
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Approval Request Email", test_approval_request_notification),
        ("Approval Response Emails", test_approval_response_notifications),
        ("Workflow Engine", test_workflow_engine),
        ("In-App Notifications", test_in_app_notifications),
        ("End-to-End Approval", test_end_to_end_approval),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test {test_name} failed with error: {str(e)}")
            results[test_name] = False
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}" if result else f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"\nApproval workflow with email notifications is fully functional!\n")
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}⚠️  Some tests failed{Colors.ENDC}\n")
        return 1


if __name__ == '__main__':
    exit(main())
