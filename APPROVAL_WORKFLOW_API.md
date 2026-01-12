# 📚 Approval Workflow API Documentation

## Overview
Complete API endpoints for managing approval workflows, notifications, and tracking.

---

## 🔑 Authentication
All endpoints require JWT Bearer token authentication.

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📋 Approval Endpoints

### 1. Create Approval Request
**Endpoint:** `POST /api/approvals/`

Creates a new approval request for a document.

**Request Body:**
```json
{
  "entity_type": "contract",
  "entity_id": "uuid-of-contract",
  "approver_id": "uuid-of-approver",
  "approver_email": "approver@company.com",
  "approver_name": "Jane Smith",
  "document_title": "Service Agreement - Acme Corp",
  "priority": "high",
  "metadata": {
    "contract_value": 50000,
    "department": "Sales"
  }
}
```

**Response:**
```json
{
  "id": "approval-uuid",
  "status": "pending",
  "entity_type": "contract",
  "entity_id": "contract-uuid",
  "approver_id": "approver-uuid",
  "approver_name": "Jane Smith",
  "document_title": "Service Agreement - Acme Corp",
  "priority": "high",
  "created_at": "2026-01-12T10:30:00Z",
  "expiry_date": "2026-01-19T10:30:00Z",
  "email_sent": true,
  "message": "Approval request created and email sent to approver"
}
```

**Status Codes:**
- `201 Created`: Approval request created successfully
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized to create approval
- `404 Not Found`: Entity not found

---

### 2. Get Pending Approvals
**Endpoint:** `GET /api/approvals/pending/`

Get all pending approval requests for the current user.

**Query Parameters:**
- `entity_type` (optional): Filter by entity type (contract, etc)
- `priority` (optional): Filter by priority (low, normal, high, urgent)
- `limit` (optional): Max results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Example:**
```
GET /api/approvals/pending/?entity_type=contract&priority=high&limit=10
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "approval-uuid",
      "entity_type": "contract",
      "entity_id": "contract-uuid",
      "document_title": "Service Agreement - Acme Corp",
      "requester_name": "John Manager",
      "priority": "high",
      "status": "pending",
      "created_at": "2026-01-12T10:30:00Z",
      "expiry_date": "2026-01-19T10:30:00Z",
      "is_expired": false,
      "days_remaining": 7
    }
  ]
}
```

---

### 3. Get Approval Details
**Endpoint:** `GET /api/approvals/{id}/`

Get detailed information about a specific approval request.

**Response:**
```json
{
  "id": "approval-uuid",
  "status": "pending",
  "entity_type": "contract",
  "entity_id": "contract-uuid",
  "requester_id": "requester-uuid",
  "requester_name": "John Manager",
  "approver_id": "approver-uuid",
  "approver_name": "Jane Smith",
  "document_title": "Service Agreement - Acme Corp",
  "priority": "high",
  "created_at": "2026-01-12T10:30:00Z",
  "expiry_date": "2026-01-19T10:30:00Z",
  "approved_at": null,
  "approval_comment": null,
  "is_expired": false,
  "email_sent": true,
  "metadata": {
    "contract_value": 50000,
    "department": "Sales"
  }
}
```

---

### 4. Approve Approval Request
**Endpoint:** `POST /api/approvals/{id}/approve/`

Approve an approval request.

**Request Body:**
```json
{
  "comment": "Looks good. Approved for execution."
}
```

**Response:**
```json
{
  "id": "approval-uuid",
  "status": "approved",
  "approved_at": "2026-01-12T11:00:00Z",
  "approval_comment": "Looks good. Approved for execution.",
  "message": "Approval request approved successfully",
  "notification_sent": true,
  "notifications": {
    "email": {
      "sent": true,
      "recipient": "requester@company.com",
      "status": "sent"
    },
    "in_app": {
      "created": true,
      "notification_id": "notification-uuid"
    }
  }
}
```

**Status Codes:**
- `200 OK`: Successfully approved
- `400 Bad Request`: Invalid approval state
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized to approve
- `404 Not Found`: Approval not found
- `409 Conflict`: Approval already processed

---

### 5. Reject Approval Request
**Endpoint:** `POST /api/approvals/{id}/reject/`

Reject an approval request.

**Request Body:**
```json
{
  "reason": "Need clarification on payment terms in section 4.2"
}
```

**Response:**
```json
{
  "id": "approval-uuid",
  "status": "rejected",
  "rejected_at": "2026-01-12T11:00:00Z",
  "rejection_reason": "Need clarification on payment terms in section 4.2",
  "message": "Approval request rejected successfully",
  "notification_sent": true,
  "notifications": {
    "email": {
      "sent": true,
      "recipient": "requester@company.com",
      "status": "sent"
    },
    "in_app": {
      "created": true,
      "notification_id": "notification-uuid"
    }
  }
}
```

---

### 6. Get Approval History
**Endpoint:** `GET /api/approvals/history/{entity_id}/`

Get all approval requests for a specific entity.

**Response:**
```json
{
  "entity_id": "contract-uuid",
  "entity_type": "contract",
  "total_approvals": 3,
  "approved": 1,
  "rejected": 1,
  "pending": 1,
  "approvals": [
    {
      "id": "approval-uuid-1",
      "approver_name": "Jane Smith",
      "status": "approved",
      "created_at": "2026-01-10T09:00:00Z",
      "approved_at": "2026-01-10T10:30:00Z",
      "comment": "Approved"
    },
    {
      "id": "approval-uuid-2",
      "approver_name": "Bob Manager",
      "status": "rejected",
      "created_at": "2026-01-11T09:00:00Z",
      "rejected_at": "2026-01-11T10:30:00Z",
      "reason": "Need revisions"
    },
    {
      "id": "approval-uuid-3",
      "approver_name": "Alice CFO",
      "status": "pending",
      "created_at": "2026-01-12T09:00:00Z",
      "approved_at": null,
      "comment": null
    }
  ]
}
```

---

## 🔔 Notification Endpoints

### 1. Get User Notifications
**Endpoint:** `GET /api/notifications/`

Get all notifications for the current user.

**Query Parameters:**
- `type` (optional): Filter by type (email, in_app, sms)
- `status` (optional): Filter by status (pending, sent, failed)
- `read` (optional): Filter by read status (true/false)
- `limit` (optional): Max results
- `offset` (optional): Pagination

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": "notification-uuid",
      "type": "in_app",
      "subject": "Approval Request: Service Agreement",
      "body": "You have a new approval request from John Manager",
      "status": "pending",
      "is_read": false,
      "created_at": "2026-01-12T10:30:00Z",
      "related_id": "approval-uuid",
      "action_url": "/approvals/approval-uuid"
    }
  ]
}
```

---

### 2. Mark Notification as Read
**Endpoint:** `POST /api/notifications/{id}/read/`

Mark a notification as read.

**Response:**
```json
{
  "id": "notification-uuid",
  "is_read": true,
  "message": "Notification marked as read"
}
```

---

### 3. Delete Notification
**Endpoint:** `DELETE /api/notifications/{id}/`

Delete a notification.

**Response:**
```json
{
  "message": "Notification deleted successfully"
}
```

---

## 📊 Workflow Analytics Endpoints

### 1. Get Approval Statistics
**Endpoint:** `GET /api/approvals/analytics/stats/`

Get approval workflow statistics.

**Response:**
```json
{
  "total_requests": 45,
  "pending": 8,
  "approved": 35,
  "rejected": 2,
  "expired": 0,
  "approval_rate": 94.59,
  "rejection_rate": 5.41,
  "avg_approval_time_hours": 4.2,
  "total_rules": 5,
  "by_priority": {
    "low": 10,
    "normal": 25,
    "high": 8,
    "urgent": 2
  },
  "by_entity_type": {
    "contract": 35,
    "purchase_order": 10
  },
  "approval_time_distribution": {
    "under_1_hour": 15,
    "1_to_4_hours": 12,
    "4_to_24_hours": 6,
    "over_24_hours": 2
  }
}
```

---

### 2. Get Approval Performance
**Endpoint:** `GET /api/approvals/analytics/performance/`

Get performance metrics by approver.

**Response:**
```json
{
  "approvers": [
    {
      "approver_id": "approver-uuid",
      "approver_name": "Jane Smith",
      "total_assigned": 20,
      "approved": 18,
      "rejected": 2,
      "pending": 0,
      "approval_rate": 90.0,
      "avg_response_time_hours": 3.5,
      "performance_rating": "Excellent"
    }
  ]
}
```

---

## ⚙️ Workflow Management Endpoints

### 1. Create Approval Rule
**Endpoint:** `POST /api/workflows/rules/`

Create a new approval rule.

**Request Body:**
```json
{
  "name": "High-Value Contract Review",
  "entity_type": "contract",
  "conditions": {
    "value_gt": 25000,
    "contract_type": "Service Agreement"
  },
  "approvers": [
    {
      "approver_id": "uuid",
      "approver_email": "manager@company.com",
      "approver_name": "Jane Smith"
    }
  ],
  "approval_levels": 1,
  "timeout_days": 7,
  "escalation_enabled": true,
  "notification_enabled": true
}
```

**Response:**
```json
{
  "rule_id": "rule-uuid",
  "name": "High-Value Contract Review",
  "entity_type": "contract",
  "status": "active",
  "created_at": "2026-01-12T10:30:00Z",
  "message": "Approval rule created successfully"
}
```

---

### 2. List Approval Rules
**Endpoint:** `GET /api/workflows/rules/`

List all approval rules.

**Query Parameters:**
- `entity_type` (optional): Filter by entity type
- `status` (optional): Filter by status (draft, active, archived)

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "rule_id": "rule-uuid",
      "name": "High-Value Contract Review",
      "entity_type": "contract",
      "approval_levels": 2,
      "timeout_days": 7,
      "approvers_count": 2,
      "created_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

---

### 3. Update Approval Rule
**Endpoint:** `PUT /api/workflows/rules/{rule_id}/`

Update an existing approval rule.

---

### 4. Delete Approval Rule
**Endpoint:** `DELETE /api/workflows/rules/{rule_id}/`

Delete an approval rule.

---

## ❌ Error Responses

### Invalid Request
```json
{
  "error": "invalid_request",
  "message": "Missing required field: approver_email",
  "status": 400
}
```

### Authentication Error
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token",
  "status": 401
}
```

### Permission Error
```json
{
  "error": "forbidden",
  "message": "Not authorized to perform this action",
  "status": 403
}
```

### Not Found
```json
{
  "error": "not_found",
  "message": "Approval request not found",
  "status": 404
}
```

### Conflict
```json
{
  "error": "conflict",
  "message": "Approval already processed",
  "status": 409
}
```

---

## 📝 Example Workflows

### Complete Approval Flow

**1. Submit for Approval**
```bash
POST /api/approvals/
{
  "entity_type": "contract",
  "entity_id": "contract-uuid",
  "approver_email": "approver@company.com",
  "document_title": "Service Agreement",
  "priority": "high"
}
```

**2. Approver Checks Pending**
```bash
GET /api/approvals/pending/
```

**3. Approver Approves**
```bash
POST /api/approvals/{approval-id}/approve/
{
  "comment": "Approved - ready to proceed"
}
```

**4. Check Approval History**
```bash
GET /api/approvals/history/{contract-id}/
```

---

## 🔐 Rate Limiting

API endpoints have rate limiting:
- **Standard users:** 100 requests per hour
- **Bulk operations:** 10 requests per hour
- **Admin users:** 1000 requests per hour

---

## 📞 Support

For API issues or questions, contact the development team.
