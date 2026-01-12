"""
Approval Workflow Engine - Configurable Rules-Based Processing

Supports:
- Multi-step approval workflows
- Conditional routing based on contract values/types
- Parallel and sequential approvals
- Auto-escalation rules
- SLA tracking
- Audit logging
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import uuid

from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail

from approvals.models import ApprovalModel
from authentication.models import User
from tenants.models import TenantModel

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval Status Enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class RuleCondition(Enum):
    """Rule Condition Types"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    CONTAINS = "contains"


class WorkflowStep(Enum):
    """Standard Workflow Steps"""
    SUBMISSION = "submission"
    INITIAL_REVIEW = "initial_review"
    MANAGER_APPROVAL = "manager_approval"
    LEGAL_REVIEW = "legal_review"
    FINANCE_APPROVAL = "finance_approval"
    EXECUTIVE_APPROVAL = "executive_approval"
    FINAL_APPROVAL = "final_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ApprovalRule:
    """
    Defines a rule for automatic approval or escalation
    
    Example:
        rule = ApprovalRule(
            name="High Value Auto-Escalate",
            condition=RuleCondition.GREATER_THAN,
            field="contract_value",
            threshold=500000,
            action="escalate_to_executive"
        )
    """
    
    def __init__(
        self,
        name: str,
        condition: RuleCondition,
        field: str,
        threshold: Any,
        action: str,
        description: str = "",
        priority: int = 1
    ):
        self.name = name
        self.condition = condition
        self.field = field
        self.threshold = threshold
        self.action = action
        self.description = description
        self.priority = priority
    
    def evaluate(self, context: Dict) -> bool:
        """
        Evaluate if rule applies to given context
        
        Args:
            context: Dictionary with contract/entity data
            
        Returns:
            True if rule condition is met
        """
        value = context.get(self.field)
        
        if value is None:
            return False
        
        if self.condition == RuleCondition.GREATER_THAN:
            return value > self.threshold
        elif self.condition == RuleCondition.LESS_THAN:
            return value < self.threshold
        elif self.condition == RuleCondition.EQUALS:
            return value == self.threshold
        elif self.condition == RuleCondition.IN_LIST:
            return value in self.threshold
        elif self.condition == RuleCondition.NOT_IN_LIST:
            return value not in self.threshold
        elif self.condition == RuleCondition.CONTAINS:
            return self.threshold in str(value)
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary for storage"""
        return {
            'name': self.name,
            'condition': self.condition.value,
            'field': self.field,
            'threshold': self.threshold,
            'action': self.action,
            'description': self.description,
            'priority': self.priority
        }


class WorkflowEngine:
    """
    Main Workflow Engine - Manages approval workflows with configurable rules
    """
    
    # Standard workflow definitions
    WORKFLOW_TEMPLATES = {
        'simple': {
            'steps': [
                'submission',
                'manager_approval',
                'completed'
            ],
            'parallel': False,
            'rules': []
        },
        'standard': {
            'steps': [
                'submission',
                'initial_review',
                'manager_approval',
                'final_approval',
                'completed'
            ],
            'parallel': False,
            'rules': []
        },
        'comprehensive': {
            'steps': [
                'submission',
                'initial_review',
                'manager_approval',
                'legal_review',
                'finance_approval',
                'executive_approval',
                'final_approval',
                'completed'
            ],
            'parallel': False,
            'rules': []
        },
        'value_based': {
            'steps': [
                'submission',
                'initial_review',
                'manager_approval',
                'final_approval',
                'completed'
            ],
            'parallel': False,
            'rules': [
                {
                    'name': 'High Value Contract',
                    'condition': 'greater_than',
                    'field': 'contract_value',
                    'threshold': 1000000,
                    'action': 'add_legal_review'
                },
                {
                    'name': 'Very High Value Contract',
                    'condition': 'greater_than',
                    'field': 'contract_value',
                    'threshold': 5000000,
                    'action': 'add_executive_approval'
                }
            ]
        },
        'type_based': {
            'steps': [
                'submission',
                'initial_review',
                'manager_approval',
                'final_approval',
                'completed'
            ],
            'parallel': False,
            'rules': [
                {
                    'name': 'NDA Requires Legal',
                    'condition': 'equals',
                    'field': 'contract_type',
                    'threshold': 'NDA',
                    'action': 'add_legal_review'
                },
                {
                    'name': 'Vendor Agreement Requires Finance',
                    'condition': 'equals',
                    'field': 'contract_type',
                    'threshold': 'Vendor Agreement',
                    'action': 'add_finance_approval'
                }
            ]
        }
    }
    
    def __init__(self, tenant_id: UUID, workflow_name: str = 'standard'):
        """
        Initialize workflow engine
        
        Args:
            tenant_id: UUID of tenant
            workflow_name: Name of workflow template to use
        """
        self.tenant_id = tenant_id
        self.workflow_name = workflow_name
        self.workflow_config = self.WORKFLOW_TEMPLATES.get(
            workflow_name,
            self.WORKFLOW_TEMPLATES['standard']
        )
        self.rules: List[ApprovalRule] = self._load_rules()
        self.current_step = 0
        self.context = {}
    
    def _load_rules(self) -> List[ApprovalRule]:
        """Load rules from workflow configuration"""
        rules = []
        for rule_config in self.workflow_config.get('rules', []):
            rule = ApprovalRule(
                name=rule_config.get('name', ''),
                condition=RuleCondition(rule_config.get('condition', 'equals')),
                field=rule_config.get('field', ''),
                threshold=rule_config.get('threshold', ''),
                action=rule_config.get('action', ''),
                priority=rule_config.get('priority', 1)
            )
            rules.append(rule)
        
        # Sort by priority
        rules.sort(key=lambda r: r.priority)
        return rules
    
    def add_rule(self, rule: ApprovalRule) -> None:
        """
        Add a custom rule to workflow
        
        Args:
            rule: ApprovalRule instance
        """
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
        logger.info(f"Added rule: {rule.name}")
    
    def evaluate_rules(self, context: Dict) -> List[str]:
        """
        Evaluate all rules against context
        
        Args:
            context: Dictionary with entity data (contract_value, contract_type, etc.)
            
        Returns:
            List of actions to perform
        """
        self.context = context
        actions = []
        
        logger.info(f"Evaluating {len(self.rules)} rules for context: {context.get('contract_type')}")
        
        for rule in self.rules:
            if rule.evaluate(context):
                actions.append(rule.action)
                logger.info(f"  ✓ Rule matched: {rule.name} → {rule.action}")
            else:
                logger.debug(f"  ✗ Rule not matched: {rule.name}")
        
        return actions
    
    def get_workflow_steps(self, context: Dict = None) -> List[str]:
        """
        Get dynamic workflow steps based on rules
        
        Args:
            context: Entity context for rule evaluation
            
        Returns:
            List of workflow step names
        """
        if context:
            actions = self.evaluate_rules(context)
        else:
            actions = []
        
        steps = self.workflow_config['steps'].copy()
        
        # Apply actions to modify workflow
        for action in actions:
            if action == 'add_legal_review' and 'legal_review' not in steps:
                # Insert after initial_review
                try:
                    idx = steps.index('manager_approval')
                    steps.insert(idx, 'legal_review')
                except ValueError:
                    steps.append('legal_review')
                logger.info("  Added legal_review step")
            
            elif action == 'add_finance_approval' and 'finance_approval' not in steps:
                # Insert after legal_review or before final
                try:
                    idx = steps.index('final_approval')
                    steps.insert(idx, 'finance_approval')
                except ValueError:
                    steps.insert(len(steps) - 1, 'finance_approval')
                logger.info("  Added finance_approval step")
            
            elif action == 'add_executive_approval' and 'executive_approval' not in steps:
                # Insert as second to last
                steps.insert(len(steps) - 1, 'executive_approval')
                logger.info("  Added executive_approval step")
            
            elif action == 'escalate_to_executive':
                # Skip to executive approval
                if 'executive_approval' not in steps:
                    steps.insert(len(steps) - 1, 'executive_approval')
                logger.info("  Escalated to executive_approval")
        
        return steps
    
    def create_approvals(
        self,
        entity_id: UUID,
        entity_type: str,
        requester_id: UUID,
        context: Dict,
        approver_mapping: Dict[str, UUID] = None
    ) -> List[UUID]:
        """
        Create approval records based on workflow
        
        Args:
            entity_id: ID of entity needing approval
            entity_type: Type of entity (contract, etc.)
            requester_id: UUID of user requesting approval
            context: Entity context for rule evaluation
            approver_mapping: Dict mapping step names to approver IDs
                Example: {'manager_approval': uuid1, 'legal_review': uuid2}
            
        Returns:
            List of created approval IDs
        """
        if approver_mapping is None:
            approver_mapping = {}
        
        approval_ids = []
        steps = self.get_workflow_steps(context)
        
        logger.info(f"Creating approvals for {entity_type}:{entity_id}")
        logger.info(f"Workflow steps: {steps}")
        
        for step in steps:
            if step in ['submission', 'completed', 'rejected']:
                continue
            
            approver_id = approver_mapping.get(step)
            if not approver_id:
                logger.warning(f"No approver mapped for step: {step}")
                continue
            
            try:
                # Ensure approver_id is a valid UUID
                if isinstance(approver_id, str):
                    approver_id = UUID(approver_id)
                
                approval = ApprovalModel.objects.create(
                    tenant_id=self.tenant_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    requester_id=requester_id,
                    approver_id=approver_id,
                    status=ApprovalStatus.PENDING.value,
                    comment=f"Awaiting {step}",
                )
                approval_ids.append(approval.id)
                logger.info(f"  Created approval {approval.id} for step: {step}")
            
            except Exception as e:
                logger.error(f"Failed to create approval for {step}: {str(e)}")
        
        return approval_ids
    
    def approve(
        self,
        approval_id: UUID,
        approver_id: UUID,
        comment: str = ""
    ) -> Tuple[bool, str]:
        """
        Approve a pending approval
        
        Args:
            approval_id: ID of approval record
            approver_id: UUID of approver
            comment: Optional approval comment
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            approval = ApprovalModel.objects.get(id=approval_id)
            
            if approval.status != ApprovalStatus.PENDING.value:
                return False, f"Approval already {approval.status}"
            
            if approval.approver_id and approval.approver_id != approver_id:
                return False, "Not authorized to approve"
            
            approval.status = ApprovalStatus.APPROVED.value
            approval.approver_id = approver_id
            approval.comment = comment
            approval.approved_at = timezone.now()
            approval.save()
            
            logger.info(f"Approved: {approval_id} by {approver_id}")
            return True, "Approval successful"
        
        except ApprovalModel.DoesNotExist:
            return False, "Approval not found"
        except Exception as e:
            logger.error(f"Approval error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def reject(
        self,
        approval_id: UUID,
        approver_id: UUID,
        comment: str = ""
    ) -> Tuple[bool, str]:
        """
        Reject a pending approval
        
        Args:
            approval_id: ID of approval record
            approver_id: UUID of approver
            comment: Rejection reason
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            approval = ApprovalModel.objects.get(id=approval_id)
            
            if approval.status != ApprovalStatus.PENDING.value:
                return False, f"Approval already {approval.status}"
            
            approval.status = ApprovalStatus.REJECTED.value
            approval.approver_id = approver_id
            approval.comment = comment or "No reason provided"
            approval.approved_at = timezone.now()
            approval.save()
            
            # Mark all subsequent approvals as expired
            ApprovalModel.objects.filter(
                entity_id=approval.entity_id,
                entity_type=approval.entity_type,
                status=ApprovalStatus.PENDING.value,
                created_at__gt=approval.created_at
            ).update(status=ApprovalStatus.EXPIRED.value)
            
            logger.info(f"Rejected: {approval_id} by {approver_id}")
            return True, "Approval rejected"
        
        except ApprovalModel.DoesNotExist:
            return False, "Approval not found"
        except Exception as e:
            logger.error(f"Rejection error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_approval_status(self, entity_id: UUID, entity_type: str) -> Dict:
        """
        Get overall approval status for entity
        
        Args:
            entity_id: ID of entity
            entity_type: Type of entity
            
        Returns:
            Dictionary with approval status breakdown
        """
        approvals = ApprovalModel.objects.filter(
            entity_id=entity_id,
            entity_type=entity_type
        ).order_by('created_at')
        
        total = approvals.count()
        approved = approvals.filter(status=ApprovalStatus.APPROVED.value).count()
        pending = approvals.filter(status=ApprovalStatus.PENDING.value).count()
        rejected = approvals.filter(status=ApprovalStatus.REJECTED.value).count()
        
        approval_list = []
        for approval in approvals:
            approval_list.append({
                'id': str(approval.id),
                'step': approval.comment,
                'status': approval.status,
                'approver_id': str(approval.approver_id) if approval.approver_id else None,
                'comment': approval.comment,
                'created_at': approval.created_at.isoformat() if approval.created_at else None,
                'approved_at': approval.approved_at.isoformat() if approval.approved_at else None
            })
        
        all_approved = (approved == total and total > 0)
        
        return {
            'entity_id': str(entity_id),
            'entity_type': entity_type,
            'total': total,
            'approved': approved,
            'pending': pending,
            'rejected': rejected,
            'all_approved': all_approved,
            'completion_rate': (approved / total * 100) if total > 0 else 0,
            'approvals': approval_list
        }
    
    def get_pending_approvals(self, approver_id: UUID) -> List[Dict]:
        """
        Get all pending approvals for an approver
        
        Args:
            approver_id: UUID of approver
            
        Returns:
            List of pending approval records
        """
        approvals = ApprovalModel.objects.filter(
            approver_id=approver_id,
            status=ApprovalStatus.PENDING.value,
            tenant_id=self.tenant_id
        ).order_by('created_at')
        
        result = []
        for approval in approvals:
            result.append({
                'id': str(approval.id),
                'entity_id': str(approval.entity_id),
                'entity_type': approval.entity_type,
                'requester_id': str(approval.requester_id),
                'status': approval.status,
                'comment': approval.comment,
                'created_at': approval.created_at.isoformat() if approval.created_at else None,
                'days_pending': (timezone.now() - approval.created_at).days if approval.created_at else 0
            })
        
        return result
    
    def escalate_overdue(self, days_threshold: int = 3) -> List[UUID]:
        """
        Escalate approvals pending for more than threshold days
        
        Args:
            days_threshold: Number of days before escalation
            
        Returns:
            List of escalated approval IDs
        """
        cutoff_date = timezone.now() - timedelta(days=days_threshold)
        
        old_approvals = ApprovalModel.objects.filter(
            status=ApprovalStatus.PENDING.value,
            created_at__lt=cutoff_date
        )
        
        escalated = []
        for approval in old_approvals:
            approval.status = ApprovalStatus.ESCALATED.value
            approval.save()
            escalated.append(approval.id)
            logger.info(f"Escalated approval {approval.id}")
        
        return escalated


# ============================================================================
# Configuration Templates for Different Scenarios
# ============================================================================

class WorkflowConfigurations:
    """Predefined workflow configurations"""
    
    @staticmethod
    def get_contract_approval_rules() -> List[ApprovalRule]:
        """Rules for contract approvals"""
        return [
            ApprovalRule(
                name="Standard Contract",
                condition=RuleCondition.LESS_THAN,
                field="contract_value",
                threshold=100000,
                action="standard_approval",
                priority=1
            ),
            ApprovalRule(
                name="Medium Value Contract",
                condition=RuleCondition.GREATER_THAN,
                field="contract_value",
                threshold=100000,
                action="add_finance_approval",
                priority=2
            ),
            ApprovalRule(
                name="High Value Contract",
                condition=RuleCondition.GREATER_THAN,
                field="contract_value",
                threshold=1000000,
                action="add_legal_review",
                priority=3
            ),
            ApprovalRule(
                name="Very High Value Contract",
                condition=RuleCondition.GREATER_THAN,
                field="contract_value",
                threshold=5000000,
                action="add_executive_approval",
                priority=4
            ),
            ApprovalRule(
                name="NDA Auto-Escalate",
                condition=RuleCondition.EQUALS,
                field="contract_type",
                threshold="NDA",
                action="add_legal_review",
                priority=5
            ),
        ]
    
    @staticmethod
    def get_vendor_onboarding_rules() -> List[ApprovalRule]:
        """Rules for vendor onboarding"""
        return [
            ApprovalRule(
                name="Vendor Risk Assessment",
                condition=RuleCondition.IN_LIST,
                field="vendor_type",
                threshold=["High Risk", "New Vendor"],
                action="add_executive_approval",
                priority=1
            ),
            ApprovalRule(
                name="International Vendor",
                condition=RuleCondition.EQUALS,
                field="vendor_country",
                threshold="International",
                action="add_compliance_review",
                priority=2
            ),
        ]
    
    @staticmethod
    def get_change_order_rules() -> List[ApprovalRule]:
        """Rules for change orders"""
        return [
            ApprovalRule(
                name="Minor Change",
                condition=RuleCondition.LESS_THAN,
                field="change_amount",
                threshold=50000,
                action="manager_approval",
                priority=1
            ),
            ApprovalRule(
                name="Major Change",
                condition=RuleCondition.GREATER_THAN,
                field="change_amount",
                threshold=500000,
                action="add_executive_approval",
                priority=2
            ),
        ]


# ============================================================================
# Utility Functions
# ============================================================================

def create_workflow_instance(
    tenant_id: UUID,
    workflow_type: str,
    entity_id: UUID,
    entity_type: str,
    requester_id: UUID,
    entity_data: Dict
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Create a new workflow instance with automatic rule evaluation
    
    Args:
        tenant_id: UUID of tenant
        workflow_type: Type of workflow ('standard', 'value_based', etc.)
        entity_id: ID of entity needing approval
        entity_type: Type of entity
        requester_id: UUID of requester
        entity_data: Entity data for rule evaluation
        
    Returns:
        Tuple of (success, message, workflow_info)
    """
    try:
        engine = WorkflowEngine(tenant_id, workflow_type)
        steps = engine.get_workflow_steps(entity_data)
        
        logger.info(f"Created workflow instance with {len(steps)} steps")
        
        return True, "Workflow instance created", {
            'workflow_type': workflow_type,
            'steps': steps,
            'entity_id': str(entity_id),
            'entity_type': entity_type
        }
    
    except Exception as e:
        logger.error(f"Workflow creation error: {str(e)}")
        return False, f"Error: {str(e)}", None
