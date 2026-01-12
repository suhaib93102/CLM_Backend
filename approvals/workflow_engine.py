import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    ESCALATED = 'escalated'


class ApprovalPriority(Enum):
    """Approval priority levels"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'


class ApprovalRule:
    """Configuration rule for approval workflows"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        entity_type: str,
        conditions: Dict,
        approvers: List[str],
        approval_levels: int = 1,
        timeout_days: int = 7,
        escalation_enabled: bool = True,
        notification_enabled: bool = True
    ):
        """
        Initialize approval rule
        
        Args:
            rule_id: Unique rule identifier
            name: Rule name
            entity_type: Type of entity (contract, etc)
            conditions: Dict of conditions that trigger this rule
            approvers: List of approver emails/IDs
            approval_levels: Number of approval levels
            timeout_days: Days before approval expires
            escalation_enabled: Auto-escalate if timeout
            notification_enabled: Send notifications
        """
        self.rule_id = rule_id
        self.name = name
        self.entity_type = entity_type
        self.conditions = conditions
        self.approvers = approvers
        self.approval_levels = approval_levels
        self.timeout_days = timeout_days
        self.escalation_enabled = escalation_enabled
        self.notification_enabled = notification_enabled
        self.created_at = datetime.now()
    
    def matches(self, entity: Dict) -> bool:
        """Check if entity matches this rule"""
        for key, value in self.conditions.items():
            if key not in entity:
                return False
            if isinstance(value, (list, tuple)):
                if entity[key] not in value:
                    return False
            else:
                if entity[key] != value:
                    return False
        return True
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary"""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'entity_type': self.entity_type,
            'conditions': self.conditions,
            'approvers': self.approvers,
            'approval_levels': self.approval_levels,
            'timeout_days': self.timeout_days,
            'escalation_enabled': self.escalation_enabled,
            'notification_enabled': self.notification_enabled,
            'created_at': self.created_at.isoformat()
        }


class ApprovalRequest:
    """Represents a single approval request"""
    
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        requester_id: str,
        requester_email: str,
        requester_name: str,
        approver_id: str,
        approver_email: str,
        approver_name: str,
        document_title: str,
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        rule_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize approval request
        
        Args:
            entity_id: ID of entity needing approval
            entity_type: Type of entity
            requester_id: ID of person requesting approval
            requester_email: Email of requester
            requester_name: Name of requester
            approver_id: ID of approver
            approver_email: Email of approver
            approver_name: Name of approver
            document_title: Title of document
            priority: Priority level
            rule_id: ID of rule that triggered this request
            metadata: Additional metadata
        """
        self.request_id = str(uuid.uuid4())
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.requester_id = requester_id
        self.requester_email = requester_email
        self.requester_name = requester_name
        self.approver_id = approver_id
        self.approver_email = approver_email
        self.approver_name = approver_name
        self.document_title = document_title
        self.priority = priority
        self.rule_id = rule_id
        self.metadata = metadata or {}
        
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.approved_at = None
        self.rejected_at = None
        self.rejection_reason = None
        self.approval_comment = None
        self.expiry_date = datetime.now() + timedelta(days=7)
        
        self.email_sent = False
        self.reminder_sent_count = 0
        self.escalated = False
    
    def approve(self, comment: str = "") -> bool:
        """Mark as approved"""
        if self.status != ApprovalStatus.PENDING:
            logger.warning(f"Cannot approve request {self.request_id} - status is {self.status}")
            return False
        
        self.status = ApprovalStatus.APPROVED
        self.approved_at = datetime.now()
        self.approval_comment = comment
        self.updated_at = datetime.now()
        logger.info(f"Approval request {self.request_id} approved")
        return True
    
    def reject(self, reason: str) -> bool:
        """Mark as rejected"""
        if self.status != ApprovalStatus.PENDING:
            logger.warning(f"Cannot reject request {self.request_id} - status is {self.status}")
            return False
        
        self.status = ApprovalStatus.REJECTED
        self.rejected_at = datetime.now()
        self.rejection_reason = reason
        self.updated_at = datetime.now()
        logger.info(f"Approval request {self.request_id} rejected")
        return True
    
    def is_expired(self) -> bool:
        """Check if approval request has expired"""
        return datetime.now() > self.expiry_date and self.status == ApprovalStatus.PENDING
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'requester_id': self.requester_id,
            'requester_name': self.requester_name,
            'approver_id': self.approver_id,
            'approver_name': self.approver_name,
            'document_title': self.document_title,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'approval_comment': self.approval_comment,
            'expiry_date': self.expiry_date.isoformat(),
            'is_expired': self.is_expired()
        }


class ApprovalWorkflowEngine:
    """
    Main approval workflow engine
    Manages rules, requests, and notifications
    """
    
    def __init__(self):
        """Initialize workflow engine"""
        self.rules: Dict[str, ApprovalRule] = {}
        self.requests: Dict[str, ApprovalRequest] = {}
        self.email_service = None  # Will be injected
        self.notification_service = None  # Will be injected
        logger.info("ApprovalWorkflowEngine initialized")
    
    def set_email_service(self, email_service):
        """Set email service dependency"""
        self.email_service = email_service
    
    def set_notification_service(self, notification_service):
        """Set notification service dependency"""
        self.notification_service = notification_service
    
    # ====== RULE MANAGEMENT ======
    
    def create_rule(
        self,
        name: str,
        entity_type: str,
        conditions: Dict,
        approvers: List[str],
        approval_levels: int = 1,
        timeout_days: int = 7,
        escalation_enabled: bool = True,
        notification_enabled: bool = True
    ) -> ApprovalRule:
        """
        Create a new approval rule
        
        Args:
            name: Rule name
            entity_type: Type of entity
            conditions: Dict of conditions
            approvers: List of approvers
            approval_levels: Number of levels
            timeout_days: Timeout in days
            escalation_enabled: Enable auto-escalation
            notification_enabled: Enable notifications
        
        Returns:
            Created ApprovalRule
        """
        rule_id = str(uuid.uuid4())
        rule = ApprovalRule(
            rule_id=rule_id,
            name=name,
            entity_type=entity_type,
            conditions=conditions,
            approvers=approvers,
            approval_levels=approval_levels,
            timeout_days=timeout_days,
            escalation_enabled=escalation_enabled,
            notification_enabled=notification_enabled
        )
        self.rules[rule_id] = rule
        logger.info(f"Created approval rule: {rule.name}")
        return rule
    
    def get_rule(self, rule_id: str) -> Optional[ApprovalRule]:
        """Get rule by ID"""
        return self.rules.get(rule_id)
    
    def list_rules(self, entity_type: Optional[str] = None) -> List[ApprovalRule]:
        """List all rules, optionally filtered by entity type"""
        rules = list(self.rules.values())
        if entity_type:
            rules = [r for r in rules if r.entity_type == entity_type]
        return rules
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Deleted approval rule: {rule_id}")
            return True
        return False
    
    # ====== REQUEST MANAGEMENT ======
    
    def create_approval_request(
        self,
        entity_id: str,
        entity_type: str,
        entity: Dict,
        requester_id: str,
        requester_email: str,
        requester_name: str,
        approver_id: str,
        approver_email: str,
        approver_name: str,
        document_title: str,
        priority: str = 'normal',
        metadata: Optional[Dict] = None
    ) -> Tuple[ApprovalRequest, bool]:
        """
        Create approval request and match to rules
        
        Returns:
            Tuple of (ApprovalRequest, notification_sent)
        """
        # Convert priority string to enum
        try:
            priority_enum = ApprovalPriority[priority.upper()]
        except KeyError:
            priority_enum = ApprovalPriority.NORMAL
        
        # Find matching rule
        matching_rule = None
        for rule in self.rules.values():
            if rule.entity_type == entity_type and rule.matches(entity):
                matching_rule = rule
                break
        
        # Create request
        request = ApprovalRequest(
            entity_id=entity_id,
            entity_type=entity_type,
            requester_id=requester_id,
            requester_email=requester_email,
            requester_name=requester_name,
            approver_id=approver_id,
            approver_email=approver_email,
            approver_name=approver_name,
            document_title=document_title,
            priority=priority_enum,
            rule_id=matching_rule.rule_id if matching_rule else None,
            metadata=metadata
        )
        
        self.requests[request.request_id] = request
        logger.info(f"Created approval request: {request.request_id}")
        
        # Send notification if enabled
        notification_sent = False
        if matching_rule and matching_rule.notification_enabled:
            notification_sent = self._send_approval_notification(request)
        
        return request, notification_sent
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get request by ID"""
        return self.requests.get(request_id)
    
    def approve_request(
        self,
        request_id: str,
        comment: str = ""
    ) -> Tuple[bool, str]:
        """
        Approve a request
        
        Returns:
            Tuple of (success, message)
        """
        request = self.get_request(request_id)
        if not request:
            return False, f"Request {request_id} not found"
        
        if request.status != ApprovalStatus.PENDING:
            return False, f"Request already {request.status.value}"
        
        success = request.approve(comment)
        if success:
            # Send approval notification
            self._send_approval_notification(request, status='approved')
            return True, "Request approved successfully"
        
        return False, "Failed to approve request"
    
    def reject_request(
        self,
        request_id: str,
        reason: str
    ) -> Tuple[bool, str]:
        """
        Reject a request
        
        Returns:
            Tuple of (success, message)
        """
        request = self.get_request(request_id)
        if not request:
            return False, f"Request {request_id} not found"
        
        if request.status != ApprovalStatus.PENDING:
            return False, f"Request already {request.status.value}"
        
        success = request.reject(reason)
        if success:
            # Send rejection notification
            self._send_approval_notification(request, status='rejected')
            return True, "Request rejected successfully"
        
        return False, "Failed to reject request"
    
    def list_pending_requests(
        self,
        approver_id: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """List pending approval requests"""
        requests = [r for r in self.requests.values() if r.status == ApprovalStatus.PENDING]
        
        if approver_id:
            requests = [r for r in requests if r.approver_id == approver_id]
        
        if entity_type:
            requests = [r for r in requests if r.entity_type == entity_type]
        
        return requests
    
    # ====== NOTIFICATIONS ======
    
    def _send_approval_notification(
        self,
        request: ApprovalRequest,
        status: str = 'pending'
    ) -> bool:
        """
        Send approval notification via email and in-app
        
        Args:
            request: ApprovalRequest object
            status: 'pending', 'approved', or 'rejected'
        
        Returns:
            True if notification sent
        """
        try:
            if status == 'pending':
                # Send approval request email
                if self.email_service:
                    email_sent = self.email_service.send_approval_request_email(
                        recipient_email=request.approver_email,
                        recipient_name=request.approver_name,
                        approver_name=request.approver_name,
                        document_title=request.document_title,
                        document_type=request.entity_type,
                        approval_id=request.request_id,
                        requester_name=request.requester_name,
                        priority=request.priority.value
                    )
                    request.email_sent = email_sent
                    logger.info(f"Approval request email sent to {request.approver_email}")
                
                # Create in-app notification
                if self.notification_service:
                    self.notification_service.create_notification(
                        recipient_id=request.approver_id,
                        notification_type='approval_request',
                        subject=f"Approval Request: {request.document_title}",
                        body=f"You have a new approval request from {request.requester_name} for '{request.document_title}'",
                        related_id=request.request_id,
                        action_url=f"/approvals/{request.request_id}"
                    )
            
            elif status == 'approved':
                # Send approval approved email to requester
                if self.email_service:
                    self.email_service.send_approval_approved_email(
                        recipient_email=request.requester_email,
                        recipient_name=request.requester_name,
                        document_title=request.document_title,
                        approver_name=request.approver_name,
                        approval_comment=request.approval_comment
                    )
                
                # Create in-app notification
                if self.notification_service:
                    self.notification_service.create_notification(
                        recipient_id=request.requester_id,
                        notification_type='approval_approved',
                        subject=f"Approved: {request.document_title}",
                        body=f"Your document '{request.document_title}' has been approved by {request.approver_name}",
                        related_id=request.request_id
                    )
            
            elif status == 'rejected':
                # Send rejection email to requester
                if self.email_service:
                    self.email_service.send_approval_rejected_email(
                        recipient_email=request.requester_email,
                        recipient_name=request.requester_name,
                        document_title=request.document_title,
                        approver_name=request.approver_name,
                        rejection_reason=request.rejection_reason
                    )
                
                # Create in-app notification
                if self.notification_service:
                    self.notification_service.create_notification(
                        recipient_id=request.requester_id,
                        notification_type='approval_rejected',
                        subject=f"Rejected: {request.document_title}",
                        body=f"Your document '{request.document_title}' has been rejected. Reason: {request.rejection_reason}",
                        related_id=request.request_id
                    )
            
            return True
        except Exception as e:
            logger.error(f"Failed to send approval notification: {str(e)}")
            return False
    
    # ====== ANALYTICS ======
    
    def get_statistics(self) -> Dict:
        """Get approval workflow statistics"""
        total = len(self.requests)
        pending = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.PENDING)
        approved = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.REJECTED)
        expired = sum(1 for r in self.requests.values() if r.is_expired())
        
        # Average approval time
        approved_requests = [r for r in self.requests.values() if r.approved_at]
        avg_time_hours = 0
        if approved_requests:
            total_hours = sum(
                (r.approved_at - r.created_at).total_seconds() / 3600
                for r in approved_requests
            )
            avg_time_hours = total_hours / len(approved_requests)
        
        return {
            'total_requests': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'expired': expired,
            'approval_rate': (approved / total * 100) if total > 0 else 0,
            'rejection_rate': (rejected / total * 100) if total > 0 else 0,
            'avg_approval_time_hours': round(avg_time_hours, 2),
            'total_rules': len(self.rules)
        }
    
    def export_data(self) -> Dict:
        """Export all workflow data"""
        return {
            'rules': [rule.to_dict() for rule in self.rules.values()],
            'requests': [request.to_dict() for request in self.requests.values()],
            'statistics': self.get_statistics()
        }
