"""
In-App Notification Service

Manages in-app notifications with:
- Rich notification types
- Clickable actions
- Read/unread tracking
- Notification center dashboard
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing in-app notifications"""
    
    def __init__(self):
        """Initialize notification service"""
        self.notifications = {}  # In-memory storage for demo
        logger.info("NotificationService initialized")
    
    def create_notification(
        self,
        recipient_id: str,
        notification_type: str,
        subject: str,
        body: str,
        related_id: Optional[str] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        priority: str = 'normal',
        data: Optional[Dict] = None
    ) -> str:
        """
        Create a new notification
        
        Args:
            recipient_id: ID of recipient user
            notification_type: Type of notification (approval_request, etc)
            subject: Notification subject
            body: Notification body
            related_id: ID of related entity
            action_url: URL for notification action
            action_text: Text for action button
            priority: 'low', 'normal', 'high', 'urgent'
            data: Additional data
        
        Returns:
            Notification ID
        """
        notification_id = str(uuid.uuid4())
        
        notification = {
            'id': notification_id,
            'recipient_id': recipient_id,
            'type': notification_type,
            'subject': subject,
            'body': body,
            'related_id': related_id,
            'action_url': action_url,
            'action_text': action_text or 'View',
            'priority': priority,
            'data': data or {},
            'read': False,
            'created_at': datetime.now().isoformat(),
            'read_at': None,
            'archived': False,
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        self.notifications[notification_id] = notification
        logger.info(f"Created notification {notification_id} for user {recipient_id}")
        return notification_id
    
    def get_notification(self, notification_id: str) -> Optional[Dict]:
        """Get notification by ID"""
        return self.notifications.get(notification_id)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        if notification_id not in self.notifications:
            return False
        
        self.notifications[notification_id]['read'] = True
        self.notifications[notification_id]['read_at'] = datetime.now().isoformat()
        logger.info(f"Marked notification {notification_id} as read")
        return True
    
    def mark_as_unread(self, notification_id: str) -> bool:
        """Mark notification as unread"""
        if notification_id not in self.notifications:
            return False
        
        self.notifications[notification_id]['read'] = False
        self.notifications[notification_id]['read_at'] = None
        logger.info(f"Marked notification {notification_id} as unread")
        return True
    
    def archive_notification(self, notification_id: str) -> bool:
        """Archive notification"""
        if notification_id not in self.notifications:
            return False
        
        self.notifications[notification_id]['archived'] = True
        logger.info(f"Archived notification {notification_id}")
        return True
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        if notification_id in self.notifications:
            del self.notifications[notification_id]
            logger.info(f"Deleted notification {notification_id}")
            return True
        return False
    
    def get_user_notifications(
        self,
        recipient_id: str,
        unread_only: bool = False,
        archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Get notifications for a user
        
        Returns:
            Dict with notifications and metadata
        """
        notifications = [
            n for n in self.notifications.values()
            if n['recipient_id'] == recipient_id and n['archived'] == archived
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        # Sort by created_at descending
        notifications = sorted(
            notifications,
            key=lambda n: n['created_at'],
            reverse=True
        )
        
        total = len(notifications)
        paginated = notifications[offset:offset + limit]
        
        return {
            'notifications': paginated,
            'total': total,
            'unread_count': sum(1 for n in notifications if not n['read']),
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        }
    
    def get_unread_count(self, recipient_id: str) -> int:
        """Get count of unread notifications"""
        return sum(
            1 for n in self.notifications.values()
            if n['recipient_id'] == recipient_id and not n['read']
        )
    
    def mark_all_as_read(self, recipient_id: str) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        for notification in self.notifications.values():
            if notification['recipient_id'] == recipient_id and not notification['read']:
                notification['read'] = True
                notification['read_at'] = datetime.now().isoformat()
                count += 1
        
        logger.info(f"Marked {count} notifications as read for user {recipient_id}")
        return count
    
    def get_notification_types(self) -> List[str]:
        """Get list of available notification types"""
        return [
            'approval_request',
            'approval_approved',
            'approval_rejected',
            'approval_escalated',
            'contract_created',
            'contract_updated',
            'contract_signed',
            'reminder',
            'system'
        ]
    
    def get_statistics(self, recipient_id: str) -> Dict:
        """Get notification statistics for user"""
        user_notifications = [
            n for n in self.notifications.values()
            if n['recipient_id'] == recipient_id
        ]
        
        total = len(user_notifications)
        unread = sum(1 for n in user_notifications if not n['read'])
        archived = sum(1 for n in user_notifications if n['archived'])
        
        by_type = {}
        for notification in user_notifications:
            ntype = notification['type']
            by_type[ntype] = by_type.get(ntype, 0) + 1
        
        return {
            'total_notifications': total,
            'unread_count': unread,
            'archived_count': archived,
            'active_count': total - archived,
            'by_type': by_type
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired notifications"""
        count = 0
        expired_ids = []
        
        now = datetime.now()
        for nid, notification in self.notifications.items():
            expires_at = datetime.fromisoformat(notification['expires_at'])
            if now > expires_at:
                expired_ids.append(nid)
                count += 1
        
        for nid in expired_ids:
            del self.notifications[nid]
        
        logger.info(f"Cleaned up {count} expired notifications")
        return count
