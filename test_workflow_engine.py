#!/usr/bin/env python
"""
Comprehensive Approval Workflow Engine Test Suite

Demonstrates:
1. Rule-based workflow configuration
2. Dynamic step generation
3. Approval creation and management
4. Status tracking
5. Escalation handling
6. Multi-scenario testing
"""

import os
import django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from uuid import uuid4
from workflows.engine import (
    WorkflowEngine,
    ApprovalRule,
    RuleCondition,
    WorkflowConfigurations,
    create_workflow_instance
)
from approvals.models import ApprovalModel
from tenants.models import TenantModel
from authentication.models import User


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        for line in details.split('\n'):
            print(f"       {line}")


def setup_test_data():
    """Create test data"""
    # Get or create test tenant
    tenant = TenantModel.objects.filter(name="Workflow Test Tenant").first()
    if not tenant:
        tenant = TenantModel.objects.create(
            id=uuid4(),
            name="Workflow Test Tenant",
            domain="workflow-test.com"
        )
    
    # Get or create test users
    approvers = {}
    user_roles = {
        'manager': 'Manager',
        'legal': 'Legal',
        'finance': 'Finance',
        'executive': 'Executive'
    }
    
    for role_key, role_name in user_roles.items():
        email = f"approver_{role_key}@workflow-test.com"
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password='TestPass123!@#'
            )
        user.tenant_id = tenant.id
        user.save()
        approvers[role_key] = user.user_id
    
    # Create requester
    requester_email = "requester@workflow-test.com"
    requester = User.objects.filter(email=requester_email).first()
    if not requester:
        requester = User.objects.create_user(
            email=requester_email,
            password='TestPass123!@#'
        )
    requester.tenant_id = tenant.id
    requester.save()
    
    return tenant, approvers, requester


def test_1_rule_evaluation():
    """Test 1: Rule Evaluation"""
    print_section("TEST 1: RULE EVALUATION")
    
    tenant, _, _ = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'value_based')
    
    # Test Case 1: Standard value contract
    context_standard = {
        'contract_type': 'Service Agreement',
        'contract_value': 50000
    }
    
    actions = engine.evaluate_rules(context_standard)
    test_1a = len(actions) == 0  # No special rules triggered
    print_test(
        "Standard Value Contract (No rules triggered)",
        test_1a,
        f"Actions: {actions}"
    )
    
    # Test Case 2: High value contract
    context_high = {
        'contract_type': 'Service Agreement',
        'contract_value': 2000000
    }
    
    actions = engine.evaluate_rules(context_high)
    test_1b = 'add_legal_review' in actions
    print_test(
        "High Value Contract (Legal review triggered)",
        test_1b,
        f"Actions: {actions}"
    )
    
    # Test Case 3: Very high value contract
    context_very_high = {
        'contract_type': 'Service Agreement',
        'contract_value': 6000000
    }
    
    actions = engine.evaluate_rules(context_very_high)
    test_1c = ('add_legal_review' in actions and 'add_executive_approval' in actions)
    print_test(
        "Very High Value Contract (Multiple rules triggered)",
        test_1c,
        f"Actions: {actions}"
    )
    
    return test_1a and test_1b and test_1c


def test_2_dynamic_workflow_steps():
    """Test 2: Dynamic Workflow Step Generation"""
    print_section("TEST 2: DYNAMIC WORKFLOW STEP GENERATION")
    
    tenant, _, _ = setup_test_data()
    
    # Test Case 1: Simple workflow
    engine = WorkflowEngine(tenant.id, 'simple')
    steps_simple = engine.get_workflow_steps()
    test_2a = steps_simple == ['submission', 'manager_approval', 'completed']
    print_test(
        "Simple Workflow Steps",
        test_2a,
        f"Steps: {' → '.join(steps_simple)}"
    )
    
    # Test Case 2: Standard workflow
    engine = WorkflowEngine(tenant.id, 'standard')
    steps_standard = engine.get_workflow_steps()
    test_2b = len(steps_standard) >= 3
    print_test(
        "Standard Workflow Steps",
        test_2b,
        f"Steps: {' → '.join(steps_standard)}"
    )
    
    # Test Case 3: Value-based workflow - high value
    engine = WorkflowEngine(tenant.id, 'value_based')
    context_high = {
        'contract_type': 'Service Agreement',
        'contract_value': 2000000
    }
    steps_high = engine.get_workflow_steps(context_high)
    test_2c = 'legal_review' in steps_high
    print_test(
        "Value-Based Workflow with High Value (Legal added)",
        test_2c,
        f"Steps: {' → '.join(steps_high)}"
    )
    
    # Test Case 4: Value-based workflow - very high value
    context_very_high = {
        'contract_type': 'Service Agreement',
        'contract_value': 6000000
    }
    steps_very_high = engine.get_workflow_steps(context_very_high)
    test_2d = 'legal_review' in steps_very_high and 'executive_approval' in steps_very_high
    print_test(
        "Value-Based Workflow with Very High Value (Legal + Executive added)",
        test_2d,
        f"Steps: {' → '.join(steps_very_high)}"
    )
    
    return test_2a and test_2b and test_2c and test_2d


def test_3_approval_creation():
    """Test 3: Approval Record Creation"""
    print_section("TEST 3: APPROVAL RECORD CREATION")
    
    tenant, approvers, requester = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'value_based')
    
    entity_id = uuid4()
    context = {
        'contract_type': 'Service Agreement',
        'contract_value': 500000
    }
    
    approver_mapping = {
        'manager_approval': approvers['manager'],
        'finance_approval': approvers['finance'],
        'final_approval': approvers['executive']
    }
    
    # Create approvals
    approval_ids = engine.create_approvals(
        entity_id=entity_id,
        entity_type='contract',
        requester_id=requester.user_id,
        context=context,
        approver_mapping=approver_mapping
    )
    
    test_3a = len(approval_ids) > 0
    print_test(
        "Approval Records Created",
        test_3a,
        f"Created {len(approval_ids)} approval records"
    )
    
    # Verify approval records exist
    approvals = ApprovalModel.objects.filter(
        entity_id=entity_id,
        entity_type='contract'
    )
    
    test_3b = approvals.count() == len(approval_ids)
    print_test(
        "Approval Records Persisted",
        test_3b,
        f"Database count: {approvals.count()}, Expected: {len(approval_ids)}"
    )
    
    # Get approval status
    status = engine.get_approval_status(entity_id, 'contract')
    test_3c = status['total'] == len(approval_ids)
    test_3d = status['pending'] == len(approval_ids)
    print_test(
        "Approval Status Tracking",
        test_3c and test_3d,
        f"Total: {status['total']}, Pending: {status['pending']}, "
        f"Completion: {status['completion_rate']:.0f}%"
    )
    
    return test_3a and test_3b and test_3c and test_3d, approval_ids


def test_4_approval_workflow():
    """Test 4: Approval and Rejection Workflow"""
    print_section("TEST 4: APPROVAL AND REJECTION WORKFLOW")
    
    tenant, approvers, requester = setup_test_data()
    
    # Create workflow and approvals
    test_passed, approval_ids = test_3_approval_creation()
    
    if not approval_ids:
        print_test("Approval Workflow", False, "No approval records to test")
        return False
    
    engine = WorkflowEngine(tenant.id, 'value_based')
    
    # Approve first approval
    approval_id = approval_ids[0]
    approval = ApprovalModel.objects.get(id=approval_id)
    approver_id = approval.approver_id
    
    success, message = engine.approve(
        approval_id=approval_id,
        approver_id=approver_id,
        comment="Approved after review"
    )
    
    test_4a = success
    print_test(
        "Approve Record",
        test_4a,
        f"Message: {message}"
    )
    
    # Verify approval status
    approval_updated = ApprovalModel.objects.get(id=approval_id)
    test_4b = approval_updated.status == 'approved'
    print_test(
        "Approval Status Updated",
        test_4b,
        f"Status: {approval_updated.status}"
    )
    
    # Reject second approval
    if len(approval_ids) > 1:
        approval_id_2 = approval_ids[1]
        approval_2 = ApprovalModel.objects.get(id=approval_id_2)
        approver_id_2 = approval_2.approver_id
        
        success, message = engine.reject(
            approval_id=approval_id_2,
            approver_id=approver_id_2,
            comment="Does not meet requirements"
        )
        
        test_4c = success
        print_test(
            "Reject Record",
            test_4c,
            f"Message: {message}"
        )
        
        # Verify rejection status
        approval_2_updated = ApprovalModel.objects.get(id=approval_id_2)
        test_4d = approval_2_updated.status == 'rejected'
        print_test(
            "Rejection Status Updated",
            test_4d,
            f"Status: {approval_2_updated.status}"
        )
        
        return test_4a and test_4b and test_4c and test_4d
    
    return test_4a and test_4b


def test_5_approval_status_tracking():
    """Test 5: Approval Status Tracking"""
    print_section("TEST 5: APPROVAL STATUS TRACKING")
    
    tenant, approvers, requester = setup_test_data()
    
    # Create workflow and approvals
    test_passed, approval_ids = test_3_approval_creation()
    
    if not approval_ids:
        print_test("Approval Status", False, "No approval records")
        return False
    
    entity_id = ApprovalModel.objects.get(id=approval_ids[0]).entity_id
    engine = WorkflowEngine(tenant.id, 'value_based')
    
    # Get initial status
    status = engine.get_approval_status(entity_id, 'contract')
    test_5a = status['pending'] == len(approval_ids)
    print_test(
        "Initial Status (All Pending)",
        test_5a,
        f"Pending: {status['pending']}/{status['total']}"
    )
    
    # Approve all
    for approval_id in approval_ids:
        approval = ApprovalModel.objects.get(id=approval_id)
        engine.approve(approval_id, approval.approver_id, "Approved")
    
    # Get final status
    status = engine.get_approval_status(entity_id, 'contract')
    test_5b = status['approved'] == len(approval_ids)
    test_5c = status['all_approved'] == True
    test_5d = status['completion_rate'] == 100.0
    
    print_test(
        "Final Status (All Approved)",
        test_5b and test_5c and test_5d,
        f"Approved: {status['approved']}/{status['total']}, "
        f"Completion: {status['completion_rate']:.0f}%"
    )
    
    return test_5a and test_5b and test_5c and test_5d


def test_6_pending_approvals_query():
    """Test 6: Pending Approvals Query"""
    print_section("TEST 6: PENDING APPROVALS QUERY")
    
    tenant, approvers, requester = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'standard')
    
    # Create a workflow with pending approvals for specific approver
    entity_id = uuid4()
    context = {
        'contract_type': 'NDA',
        'contract_value': 100000
    }
    
    approver_mapping = {
        'initial_review': approvers['manager'],
        'manager_approval': approvers['manager'],
        'final_approval': approvers['executive']
    }
    
    approval_ids = engine.create_approvals(
        entity_id=entity_id,
        entity_type='contract',
        requester_id=requester.user_id,
        context=context,
        approver_mapping=approver_mapping
    )
    
    # Get pending approvals for manager
    pending = engine.get_pending_approvals(approvers['manager'])
    test_6a = len(pending) > 0
    print_test(
        "Pending Approvals Retrieved",
        test_6a,
        f"Found {len(pending)} pending approvals for manager"
    )
    
    # Verify approval details
    if pending:
        approval = pending[0]
        test_6b = approval['status'] == 'pending'
        test_6c = approval['entity_type'] == 'contract'
        print_test(
            "Approval Details Valid",
            test_6b and test_6c,
            f"Status: {approval['status']}, Entity: {approval['entity_type']}"
        )
        
        return test_6a and test_6b and test_6c
    
    return test_6a


def test_7_custom_rules():
    """Test 7: Custom Rule Configuration"""
    print_section("TEST 7: CUSTOM RULE CONFIGURATION")
    
    tenant, _, _ = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'simple')
    
    # Add custom rule
    custom_rule = ApprovalRule(
        name="Strategic Partner Approval",
        condition=RuleCondition.IN_LIST,
        field="partner_type",
        threshold=["Strategic", "Key Account"],
        action="add_executive_approval",
        priority=1
    )
    
    engine.add_rule(custom_rule)
    test_7a = custom_rule in engine.rules
    print_test(
        "Custom Rule Added",
        test_7a,
        f"Rule: {custom_rule.name}"
    )
    
    # Evaluate custom rule
    context = {
        'partner_type': 'Strategic',
        'contract_value': 100000
    }
    
    actions = engine.evaluate_rules(context)
    test_7b = 'add_executive_approval' in actions
    print_test(
        "Custom Rule Evaluated",
        test_7b,
        f"Actions: {actions}"
    )
    
    return test_7a and test_7b


def test_8_escalation():
    """Test 8: Approval Escalation"""
    print_section("TEST 8: APPROVAL ESCALATION")
    
    tenant, approvers, requester = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'standard')
    
    # Create approval that's older than threshold
    entity_id = uuid4()
    
    approval = ApprovalModel.objects.create(
        tenant_id=tenant.id,
        entity_type='contract',
        entity_id=entity_id,
        requester_id=requester.user_id,
        approver_id=approvers['manager'],
        status='pending',
        comment='Old pending approval'
    )
    
    # Manually set created_at to 5 days ago
    from django.utils import timezone
    old_date = timezone.now() - timedelta(days=5)
    ApprovalModel.objects.filter(id=approval.id).update(created_at=old_date)
    
    # Escalate overdue approvals
    escalated = engine.escalate_overdue(days_threshold=3)
    test_8a = approval.id in escalated
    print_test(
        "Overdue Approvals Escalated",
        test_8a,
        f"Escalated {len(escalated)} approval(s)"
    )
    
    # Verify escalation status
    approval_updated = ApprovalModel.objects.get(id=approval.id)
    test_8b = approval_updated.status == 'escalated'
    print_test(
        "Escalation Status Updated",
        test_8b,
        f"Status: {approval_updated.status}"
    )
    
    return test_8a and test_8b


def test_9_type_based_workflow():
    """Test 9: Type-Based Workflow Configuration"""
    print_section("TEST 9: TYPE-BASED WORKFLOW CONFIGURATION")
    
    tenant, _, _ = setup_test_data()
    engine = WorkflowEngine(tenant.id, 'type_based')
    
    # Test NDA
    context_nda = {
        'contract_type': 'NDA',
        'contract_value': 50000
    }
    
    steps_nda = engine.get_workflow_steps(context_nda)
    test_9a = 'legal_review' in steps_nda
    print_test(
        "NDA Requires Legal Review",
        test_9a,
        f"Steps: {' → '.join(steps_nda)}"
    )
    
    # Test Vendor Agreement
    context_vendor = {
        'contract_type': 'Vendor Agreement',
        'contract_value': 150000
    }
    
    steps_vendor = engine.get_workflow_steps(context_vendor)
    test_9b = 'finance_approval' in steps_vendor
    print_test(
        "Vendor Agreement Requires Finance Review",
        test_9b,
        f"Steps: {' → '.join(steps_vendor)}"
    )
    
    return test_9a and test_9b


def test_10_workflow_instance_creation():
    """Test 10: Workflow Instance Creation"""
    print_section("TEST 10: WORKFLOW INSTANCE CREATION")
    
    tenant, _, requester = setup_test_data()
    
    entity_data = {
        'contract_type': 'MSA',
        'contract_value': 2000000
    }
    
    success, message, workflow_info = create_workflow_instance(
        tenant_id=tenant.id,
        workflow_type='value_based',
        entity_id=uuid4(),
        entity_type='contract',
        requester_id=requester.user_id,
        entity_data=entity_data
    )
    
    test_10a = success
    test_10b = workflow_info is not None
    test_10c = 'steps' in workflow_info if workflow_info else False
    
    print_test(
        "Workflow Instance Created",
        test_10a,
        f"Message: {message}"
    )
    
    if workflow_info:
        print_test(
            "Workflow Info Valid",
            test_10b and test_10c,
            f"Steps: {workflow_info.get('steps')}"
        )
    
    return test_10a and test_10b and test_10c


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  APPROVAL WORKFLOW ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting workflow rules, dynamic steps, and approval management...\n")
    
    results = {
        'Test 1: Rule Evaluation': test_1_rule_evaluation(),
        'Test 2: Dynamic Workflow Steps': test_2_dynamic_workflow_steps(),
        'Test 3: Approval Creation': test_3_approval_creation()[0],
        'Test 4: Approval Workflow': test_4_approval_workflow(),
        'Test 5: Status Tracking': test_5_approval_status_tracking(),
        'Test 6: Pending Approvals': test_6_pending_approvals_query(),
        'Test 7: Custom Rules': test_7_custom_rules(),
        'Test 8: Escalation': test_8_escalation(),
        'Test 9: Type-Based Workflow': test_9_type_based_workflow(),
        'Test 10: Instance Creation': test_10_workflow_instance_creation(),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Total: {passed}/{total} Tests Passed ({passed/total*100:.0f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ALL WORKFLOW ENGINE TESTS PASSED!")
        print("\n✅ Workflow Engine Features Validated:")
        print("   • Rule-based workflow configuration ✓")
        print("   • Dynamic step generation ✓")
        print("   • Approval creation and management ✓")
        print("   • Status tracking ✓")
        print("   • Escalation handling ✓")
        print("   • Custom rule support ✓")
        print("   • Multi-scenario testing ✓")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review output above.")
    
    print("\n" + "="*80 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
