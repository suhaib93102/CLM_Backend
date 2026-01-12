# APPROVAL WORKFLOW ENGINE - IMPLEMENTATION GUIDE

## Quick Start

### 1. Basic Setup

```python
from workflows.engine import WorkflowEngine
from uuid import uuid4

# Initialize with standard workflow
tenant_id = uuid4()
engine = WorkflowEngine(tenant_id, 'standard')

# Get workflow steps
steps = engine.get_workflow_steps()
print(steps)
# Output: ['submission', 'initial_review', 'manager_approval', 
#          'final_approval', 'completed']
```

### 2. Create Approvals

```python
# Define who approves each step
approver_mapping = {
    'initial_review': manager_id,
    'manager_approval': director_id,
    'final_approval': vp_id
}

# Create approval records
approval_ids = engine.create_approvals(
    entity_id=contract_id,
    entity_type='contract',
    requester_id=requester_id,
    context={},
    approver_mapping=approver_mapping
)
```

### 3. Process Approvals

```python
# Approve a record
success, msg = engine.approve(approval_id, approver_id, "Looks good")

# Reject a record
success, msg = engine.reject(approval_id, approver_id, "Needs revision")

# Check status
status = engine.get_approval_status(contract_id, 'contract')
print(f"Completion: {status['completion_rate']:.0f}%")
```

---

## Configuration Patterns

### Pattern 1: Value-Based Routing

```python
engine = WorkflowEngine(tenant_id, 'value_based')

# Automatically adds steps based on value
context = {
    'contract_type': 'Service Agreement',
    'contract_value': 2500000  # $2.5M
}

steps = engine.get_workflow_steps(context)
# Includes: legal_review, finance_approval automatically
```

**Rules Applied:**
- \$100K - \$1M: Add finance approval
- \$1M - \$5M: Add legal review  
- \$5M+: Add executive approval

### Pattern 2: Type-Based Routing

```python
engine = WorkflowEngine(tenant_id, 'type_based')

# Automatically routes based on type
context = {
    'contract_type': 'NDA'  # NDAs require legal
}

steps = engine.get_workflow_steps(context)
# Includes: legal_review automatically
```

**Rules Applied:**
- NDA → Legal review
- Vendor Agreement → Finance approval
- Service Agreement → Standard path

### Pattern 3: Custom Rules

```python
from workflows.engine import ApprovalRule, RuleCondition

# Add custom rule for strategic vendors
rule = ApprovalRule(
    name="Strategic Vendor Approval",
    condition=RuleCondition.IN_LIST,
    field="vendor_tier",
    threshold=["Strategic", "Platinum"],
    action="add_executive_approval",
    priority=1
)

engine.add_rule(rule)

# Now applies automatically
context = {
    'vendor_tier': 'Strategic'
}
steps = engine.get_workflow_steps(context)
# Includes: executive_approval automatically
```

---

## Real-World Scenarios

### Scenario 1: Small Service Contract

```python
contract = {
    'id': uuid4(),
    'type': 'Service Agreement',
    'value': 75000
}

engine = WorkflowEngine(tenant_id, 'value_based')
steps = engine.get_workflow_steps({
    'contract_type': contract['type'],
    'contract_value': contract['value']
})

# Output: 5 steps
# submission → initial_review → manager_approval → 
# final_approval → completed

approver_mapping = {
    'initial_review': compliance_id,
    'manager_approval': manager_id,
    'final_approval': director_id
}

approvals = engine.create_approvals(
    entity_id=contract['id'],
    entity_type='contract',
    requester_id=requester_id,
    context={'contract_type': contract['type'], 
             'contract_value': contract['value']},
    approver_mapping=approver_mapping
)
# Time to approval: ~2-3 days (simple path)
```

### Scenario 2: Medium Enterprise Contract

```python
contract = {
    'id': uuid4(),
    'type': 'MSA',
    'value': 750000
}

engine = WorkflowEngine(tenant_id, 'value_based')
steps = engine.get_workflow_steps({
    'contract_type': contract['type'],
    'contract_value': contract['value']
})

# Output: 6 steps - finance_approval added
# submission → initial_review → manager_approval → 
# finance_approval → final_approval → completed

approver_mapping = {
    'initial_review': compliance_id,
    'manager_approval': manager_id,
    'finance_approval': finance_controller_id,
    'final_approval': vp_id
}

approvals = engine.create_approvals(
    entity_id=contract['id'],
    entity_type='contract',
    requester_id=requester_id,
    context={'contract_type': contract['type'],
             'contract_value': contract['value']},
    approver_mapping=approver_mapping
)
# Time to approval: ~5-7 days (added finance review)
```

### Scenario 3: High-Value Strategic Contract

```python
contract = {
    'id': uuid4(),
    'type': 'Partnership',
    'value': 8500000
}

engine = WorkflowEngine(tenant_id, 'value_based')
steps = engine.get_workflow_steps({
    'contract_type': contract['type'],
    'contract_value': contract['value']
})

# Output: 7 steps - legal_review + executive_approval added
# submission → initial_review → manager_approval →
# legal_review → finance_approval → executive_approval →
# final_approval → completed

approver_mapping = {
    'initial_review': compliance_id,
    'manager_approval': director_id,
    'legal_review': general_counsel_id,
    'finance_approval': cfo_id,
    'executive_approval': ceo_id,
    'final_approval': board_chair_id
}

approvals = engine.create_approvals(
    entity_id=contract['id'],
    entity_type='contract',
    requester_id=requester_id,
    context={'contract_type': contract['type'],
             'contract_value': contract['value']},
    approver_mapping=approver_mapping
)
# Time to approval: ~10-15 days (comprehensive process)
```

---

## API Integration

### Creating Approvals via REST API

```python
# In your views.py
from rest_framework.response import Response
from workflows.engine import WorkflowEngine
from django.utils import timezone

class ContractApprovalView(APIView):
    def post(self, request, contract_id):
        """Start approval workflow for contract"""
        
        # Get contract data
        contract = Contract.objects.get(id=contract_id)
        
        # Initialize engine
        engine = WorkflowEngine(
            request.user.tenant_id,
            'value_based'
        )
        
        # Get dynamic workflow steps
        context = {
            'contract_type': contract.contract_type,
            'contract_value': contract.value
        }
        steps = engine.get_workflow_steps(context)
        
        # Map approvers from request
        approver_mapping = request.data.get('approver_mapping', {})
        
        # Create approvals
        approval_ids = engine.create_approvals(
            entity_id=contract.id,
            entity_type='contract',
            requester_id=request.user.user_id,
            context=context,
            approver_mapping=approver_mapping
        )
        
        return Response({
            'status': 'success',
            'workflow_steps': steps,
            'approvals_created': len(approval_ids),
            'approval_ids': [str(id) for id in approval_ids]
        })
```

### Approving via REST API

```python
class ApprovalView(APIView):
    def post(self, request, approval_id):
        """Approve a specific approval"""
        
        engine = WorkflowEngine(request.user.tenant_id)
        
        success, message = engine.approve(
            approval_id=approval_id,
            approver_id=request.user.user_id,
            comment=request.data.get('comment', '')
        )
        
        if success:
            # Check if all approvals done
            approval = ApprovalModel.objects.get(id=approval_id)
            status = engine.get_approval_status(
                approval.entity_id,
                approval.entity_type
            )
            
            return Response({
                'status': 'approved',
                'completion': status['completion_rate'],
                'all_approved': status['all_approved']
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

## Monitoring & Analytics

### Check Pending Approvals

```python
engine = WorkflowEngine(tenant_id)

# Get all pending for a user
pending = engine.get_pending_approvals(user_id)

for approval in pending:
    days = approval['days_pending']
    if days > 3:
        print(f"⚠️  Approval pending {days} days: {approval['entity_id']}")
    else:
        print(f"✓ Approval pending {days} days: {approval['entity_id']}")
```

### Track Approval Progress

```python
# Get full status for a contract
status = engine.get_approval_status(contract_id, 'contract')

print(f"Total: {status['total']}")
print(f"Approved: {status['approved']}")
print(f"Pending: {status['pending']}")
print(f"Rejected: {status['rejected']}")
print(f"Progress: {status['completion_rate']:.0f}%")

# List all approvals
for approval in status['approvals']:
    print(f"  • {approval['step']}: {approval['status']}")
```

### Escalation Handling

```python
# Find and escalate overdue approvals
escalated = engine.escalate_overdue(days_threshold=5)

print(f"Escalated {len(escalated)} approvals")

for approval_id in escalated:
    approval = ApprovalModel.objects.get(id=approval_id)
    # Send escalation notification to manager
    send_escalation_email(approval.approver_id)
```

---

## Best Practices

### 1. Always Provide Complete Approver Mapping

```python
# ✓ GOOD - Maps all steps
approver_mapping = {
    'initial_review': compliance_id,
    'manager_approval': manager_id,
    'final_approval': director_id
}

# ✗ BAD - Missing mappings
approver_mapping = {
    'manager_approval': manager_id
}
```

### 2. Use Context Data for Rule Evaluation

```python
# ✓ GOOD - Provides all data for rules
context = {
    'contract_type': 'MSA',
    'contract_value': 1500000,
    'vendor_tier': 'Strategic'
}

# ✗ BAD - Missing data
context = {}
```

### 3. Test Rules Before Deploying

```python
# Test rule evaluation
engine = WorkflowEngine(tenant_id, 'value_based')

test_contracts = [
    {'value': 50000},
    {'value': 500000},
    {'value': 2000000},
    {'value': 6000000}
]

for contract in test_contracts:
    steps = engine.get_workflow_steps(contract)
    print(f"${contract['value']:,} → {len(steps)} steps")
```

### 4. Monitor Escalations Regularly

```python
# Daily check for overdue approvals
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        engine = WorkflowEngine(tenant_id)
        escalated = engine.escalate_overdue(days_threshold=3)
        
        if escalated:
            notify_managers(escalated)
            self.stdout.write(f"Escalated {len(escalated)} approvals")
```

### 5. Always Include Comments

```python
# ✓ GOOD - Include context
engine.approve(
    approval_id,
    approver_id,
    comment="Reviewed against company policy, all looks good"
)

engine.reject(
    approval_id,
    approver_id,
    comment="Pricing needs to be adjusted. Current 15% above market rate"
)

# ✗ BAD - No comment
engine.approve(approval_id, approver_id, "")
```

---

## Deployment Checklist

- [ ] Create approver mappings for each approval step
- [ ] Configure workflow templates for your organization
- [ ] Create custom rules for business requirements
- [ ] Set up escalation monitoring (daily job)
- [ ] Test with sample contracts
- [ ] Configure email notifications
- [ ] Set SLA targets per step
- [ ] Train users on process
- [ ] Set up audit logging
- [ ] Create reporting dashboard

---

## Key Takeaways

✅ **Rule-Based:** Contracts automatically route based on configurable rules  
✅ **Dynamic:** Workflow steps generated on-the-fly  
✅ **Configurable:** Easy to add custom rules and templates  
✅ **Trackable:** Complete status and progress tracking  
✅ **Scalable:** Handles simple to complex workflows  
✅ **Production-Ready:** Error handling and logging built-in  

The workflow engine is **fully functional, configurable, and ready for production use** across all approval processes.
