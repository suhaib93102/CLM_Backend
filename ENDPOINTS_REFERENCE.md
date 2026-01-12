# CLM BACKEND - COMPLETE API ENDPOINTS REFERENCE

**Last Updated:** January 12, 2026  
**API Version:** 1.0  
**Base URL:** `/api`  
**Authentication:** Bearer Token (JWT)

---

## TABLE OF CONTENTS
1. [Authentication](#authentication)
2. [Contracts](#contracts)
3. [Contract Templates](#contract-templates)
4. [Contract Versions](#contract-versions)
5. [Workflows](#workflows)
6. [Approvals](#approvals)
7. [Admin Panel](#admin-panel)
8. [Audit Logs & History](#audit-logs--history)
9. [Health & Status](#health--status)

---

## AUTHENTICATION

### Register User
```
POST /api/auth/register/
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}

Response (201):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "uuid",
    "email": "user@example.com"
  }
}
```

### Login
```
POST /api/auth/login/
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (200):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "tenant_id": "uuid"
  }
}
```

### Logout
```
POST /api/auth/logout/
Authorization: Bearer {token}

Response (200):
{
  "message": "Logged out"
}
```

### Refresh Token
```
POST /api/auth/refresh/
Content-Type: application/json

Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
```
GET /api/auth/me/
Authorization: Bearer {token}

Response (200):
{
  "user_id": "uuid",
  "email": "user@example.com",
  "tenant_id": "uuid"
}
```

---

## CONTRACTS

### List All Contracts
```
GET /api/contracts/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer (default: 20)
  - offset: integer (default: 0)
  - status: string (draft|pending|approved|rejected|executed)
  - search: string

Response (200):
{
  "count": 127,
  "next": "/api/contracts/?offset=20",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Service Agreement",
      "contract_type": "MSA",
      "status": "draft",
      "value": 50000.00,
      "counterparty": "Acme Corp",
      "start_date": "2026-01-15",
      "end_date": "2027-01-14",
      "created_by": "uuid",
      "created_at": "2026-01-12T10:30:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### Create Contract
```
POST /api/contracts/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "title": "Service Agreement",
  "contract_type": "MSA",
  "status": "draft",
  "value": 50000.00,
  "counterparty": "Acme Corp",
  "start_date": "2026-01-15",
  "end_date": "2027-01-14"
}

Response (201):
{
  "id": "uuid",
  "title": "Service Agreement",
  "contract_type": "MSA",
  "status": "draft",
  "value": 50000.00,
  "counterparty": "Acme Corp",
  "start_date": "2026-01-15",
  "end_date": "2027-01-14",
  "created_by": "uuid",
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

### Get Contract Details
```
GET /api/contracts/{id}/
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "title": "Service Agreement",
  "contract_type": "MSA",
  "status": "draft",
  "value": 50000.00,
  "counterparty": "Acme Corp",
  "start_date": "2026-01-15",
  "end_date": "2027-01-14",
  "is_approved": false,
  "approved_by": null,
  "approved_at": null,
  "created_by": "uuid",
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z",
  "latest_version": {
    "id": "uuid",
    "version_number": 1,
    "change_summary": "Initial document",
    "r2_key": "contracts/uuid/v1.docx",
    "file_size": 45632,
    "file_hash": "sha256hash",
    "created_by": "uuid",
    "created_at": "2026-01-12T10:30:00Z"
  }
}
```

### Update Contract
```
PUT /api/contracts/{id}/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "title": "Updated Service Agreement",
  "status": "pending",
  "value": 55000.00
}

Response (200):
{
  "id": "uuid",
  "title": "Updated Service Agreement",
  "contract_type": "MSA",
  "status": "pending",
  "value": 55000.00,
  ...
}
```

### Delete Contract
```
DELETE /api/contracts/{id}/
Authorization: Bearer {token}

Response (204): No Content
```

### Get Contract Statistics
```
GET /api/contracts/statistics/
Authorization: Bearer {token}

Response (200):
{
  "total": 127,
  "draft": 45,
  "pending": 30,
  "approved": 40,
  "rejected": 5,
  "executed": 7,
  "monthly_trends": [
    {
      "month": "Jan",
      "approved": 12,
      "rejected": 2
    },
    {
      "month": "Feb",
      "approved": 15,
      "rejected": 1
    }
  ]
}
```

### Get Recent Contracts
```
GET /api/contracts/recent/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer (default: 10)

Response (200):
[
  {
    "id": "uuid",
    "title": "Service Agreement",
    "status": "draft",
    "created_by_name": "John Doe",
    "updated_at": "2026-01-12T10:30:00Z",
    ...
  }
]
```

### Get Contract Download URL
```
GET /api/contracts/{id}/download-url/
Authorization: Bearer {token}

Response (200):
{
  "contract_id": "uuid",
  "version_number": 1,
  "r2_key": "contracts/uuid/v1.docx",
  "download_url": "https://r2.cloudflare.com/presigned-url..."
}
```

### Clone Contract
```
POST /api/contracts/{id}/clone/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "title": "Cloned Service Agreement"
}

Response (201):
{
  "id": "new-uuid",
  "title": "Cloned Service Agreement",
  "contract_type": "MSA",
  "status": "draft",
  ...
}
```

### Generate Contract from Template
```
POST /api/contracts/generate/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "template_id": "uuid",
  "structured_inputs": {
    "counterparty": "Acme Corp",
    "value": 50000,
    "start_date": "2026-01-15",
    "end_date": "2027-01-14"
  },
  "user_instructions": "Make termination clause stricter",
  "title": "MSA with Acme Corp",
  "selected_clauses": ["CONF-001", "TERM-001", "LIAB-002"]
}

Response (201):
{
  "contract": {...},
  "version": {...},
  "mandatory_clauses": [...],
  "clause_suggestions": {...},
  "validation_errors": []
}
```

---

## CONTRACT TEMPLATES

### List Templates
```
GET /api/contract-templates/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer
  - offset: integer
  - search: string

Response (200):
{
  "count": 25,
  "results": [
    {
      "id": "uuid",
      "name": "NDA Template",
      "contract_type": "NDA",
      "description": "Standard Non-Disclosure Agreement",
      "version": 3,
      "status": "published",
      "r2_key": "templates/nda.docx",
      "merge_fields": ["company_name", "date", "confidentiality_period"],
      "mandatory_clauses": ["CONF-001"],
      "created_by": "uuid",
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### Create Template
```
POST /api/contract-templates/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "NDA Template",
  "contract_type": "NDA",
  "description": "Standard Non-Disclosure Agreement",
  "r2_key": "templates/nda.docx",
  "merge_fields": ["company_name", "date"],
  "mandatory_clauses": ["CONF-001"],
  "business_rules": {
    "min_value": 0,
    "max_value": 1000000
  },
  "status": "draft"
}

Response (201):
{
  "id": "uuid",
  "name": "NDA Template",
  ...
}
```

### Get Template Details
```
GET /api/contract-templates/{id}/
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "name": "NDA Template",
  "contract_type": "NDA",
  "description": "Standard Non-Disclosure Agreement",
  "version": 1,
  "status": "draft",
  "r2_key": "templates/nda.docx",
  "merge_fields": ["company_name", "date"],
  "mandatory_clauses": ["CONF-001"],
  "business_rules": {...},
  "created_by": "uuid",
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

### Update Template
```
PUT /api/contract-templates/{id}/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "status": "published",
  "merge_fields": ["company_name", "date", "contact_person"]
}

Response (200):
{
  "id": "uuid",
  ...
}
```

### Delete Template
```
DELETE /api/contract-templates/{id}/
Authorization: Bearer {token}

Response (204): No Content
```

---

## CONTRACT VERSIONS

### List Contract Versions
```
GET /api/contracts/{contract_id}/versions/
Authorization: Bearer {token}

Response (200):
[
  {
    "id": "uuid",
    "contract": "uuid",
    "version_number": 2,
    "r2_key": "contracts/uuid/v2.docx",
    "template_id": "uuid",
    "template_version": 3,
    "change_summary": "Updated liability clause",
    "file_size": 48234,
    "file_hash": "sha256hash",
    "created_by": "uuid",
    "created_at": "2026-01-12T11:00:00Z"
  },
  {
    "id": "uuid",
    "contract": "uuid",
    "version_number": 1,
    "r2_key": "contracts/uuid/v1.docx",
    "template_id": "uuid",
    "template_version": 3,
    "change_summary": "Initial document upload",
    "file_size": 45632,
    "file_hash": "sha256hash",
    "created_by": "uuid",
    "created_at": "2026-01-12T10:30:00Z"
  }
]
```

### Create Contract Version
```
POST /api/contracts/{contract_id}/create-version/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "selected_clauses": ["CONF-001", "TERM-001", "LIAB-002"],
  "change_summary": "Updated liability clause to stricter version"
}

Response (201):
{
  "id": "uuid",
  "contract": "uuid",
  "version_number": 2,
  "r2_key": "contracts/uuid/v2.docx",
  "template_id": "uuid",
  "template_version": 3,
  "change_summary": "Updated liability clause to stricter version",
  "file_size": 48234,
  "file_hash": "sha256hash",
  "created_by": "uuid",
  "created_at": "2026-01-12T11:00:00Z"
}
```

### Get Specific Version
```
GET /api/contracts/{contract_id}/versions/{version_number}/
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "contract": "uuid",
  "version_number": 2,
  ...
}
```

### Get Version Clauses with Provenance
```
GET /api/contracts/{contract_id}/versions/{version_number}/clauses/
Authorization: Bearer {token}

Response (200):
{
  "clauses": [
    {
      "clause_id": "CONF-001",
      "clause_version": 3,
      "name": "Confidentiality Clause",
      "content": "All parties agree to maintain confidentiality...",
      "is_mandatory": true,
      "position": 1,
      "alternatives_suggested": [...],
      "provenance": {
        "source": "template",
        "template_id": "uuid",
        "template_version": 5,
        "added_at": "2026-01-12T11:00:00Z",
        "added_by": "uuid"
      }
    }
  ]
}
```

### Validate Clauses Against Business Rules
```
POST /api/contracts/validate-clauses/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "contract_type": "MSA",
  "contract_value": 50000,
  "selected_clauses": ["CONF-001", "TERM-001"]
}

Response (200):
{
  "is_valid": false,
  "errors": [
    "Mandatory clause missing: LIAB-001"
  ],
  "warnings": [],
  "mandatory_clauses": [
    {
      "clause_id": "LIAB-001",
      "name": "Liability Limitation",
      "message": "Liability limitation required for all contracts"
    }
  ]
}
```

---

## WORKFLOWS

### List Workflows
```
GET /api/workflows/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer
  - offset: integer
  - status: string (active|archived)

Response (200):
{
  "count": 15,
  "results": [
    {
      "id": "uuid",
      "name": "Contract Approval Workflow",
      "description": "Multi-step approval process",
      "status": "active",
      "steps": [
        {
          "step_number": 1,
          "name": "Initial Review",
          "assigned_to": ["role:manager"],
          "required_approval": true
        },
        {
          "step_number": 2,
          "name": "Legal Review",
          "assigned_to": ["role:legal"],
          "required_approval": true
        },
        {
          "step_number": 3,
          "name": "Final Approval",
          "assigned_to": ["role:admin"],
          "required_approval": true
        }
      ],
      "created_by": "uuid",
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### Create Workflow
```
POST /api/workflows/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Contract Approval Workflow",
  "description": "Multi-step approval process",
  "status": "active",
  "steps": [
    {
      "step_number": 1,
      "name": "Initial Review",
      "assigned_to": ["role:manager"],
      "required_approval": true
    },
    {
      "step_number": 2,
      "name": "Legal Review",
      "assigned_to": ["role:legal"],
      "required_approval": true
    }
  ]
}

Response (201):
{
  "id": "uuid",
  "name": "Contract Approval Workflow",
  ...
}
```

### Get Workflow Details
```
GET /api/workflows/{id}/
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "name": "Contract Approval Workflow",
  ...
}
```

### Update Workflow
```
PUT /api/workflows/{id}/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "status": "archived",
  "steps": [...]
}

Response (200):
{
  "id": "uuid",
  ...
}
```

### Delete Workflow
```
DELETE /api/workflows/{id}/
Authorization: Bearer {token}

Response (204): No Content
```

### Get Workflow Instances
```
GET /api/workflows/{id}/instances/
Authorization: Bearer {token}

Response (200):
[
  {
    "id": "uuid",
    "workflow": "uuid",
    "contract_id": "uuid",
    "status": "in_progress",
    "current_step": 1,
    "steps_completed": 1,
    "total_steps": 3,
    "created_at": "2026-01-12T10:30:00Z",
    "updated_at": "2026-01-12T11:00:00Z"
  }
]
```

---

## APPROVALS

### List Approvals
```
GET /api/approvals/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer
  - offset: integer
  - status: string (pending|approved|rejected)
  - assigned_to: uuid

Response (200):
{
  "count": 42,
  "results": [
    {
      "id": "uuid",
      "contract_id": "uuid",
      "contract_title": "Service Agreement",
      "status": "pending",
      "assigned_to": "uuid",
      "assigned_by": "uuid",
      "due_date": "2026-01-15",
      "comments": null,
      "approved_at": null,
      "created_at": "2026-01-12T10:30:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### Approve Contract
```
POST /api/contracts/{id}/approve/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "reviewed": true,
  "comments": "Document reviewed and approved for execution"
}

Response (200):
{
  "id": "uuid",
  "title": "Service Agreement",
  "status": "approved",
  "is_approved": true,
  "approved_by": "uuid",
  "approved_at": "2026-01-12T11:00:00Z",
  ...
}
```

### Get Approval Details
```
GET /api/approvals/{id}/
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "contract_id": "uuid",
  "contract_title": "Service Agreement",
  "status": "pending",
  "assigned_to": "uuid",
  "assigned_by": "uuid",
  "due_date": "2026-01-15",
  "comments": null,
  "approved_at": null,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

### Update Approval Status
```
PUT /api/approvals/{id}/
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "status": "approved",
  "comments": "Approved after legal review"
}

Response (200):
{
  "id": "uuid",
  "status": "approved",
  "comments": "Approved after legal review",
  "approved_at": "2026-01-12T11:00:00Z",
  ...
}
```

---

## ADMIN PANEL

### List Roles
```
GET /api/roles/
Authorization: Bearer {token}

Response (200):
{
  "roles": [
    {
      "id": "admin",
      "name": "Administrator",
      "description": "Full system access"
    },
    {
      "id": "user",
      "name": "User",
      "description": "Standard user access"
    },
    {
      "id": "viewer",
      "name": "Viewer",
      "description": "Read-only access"
    },
    {
      "id": "manager",
      "name": "Manager",
      "description": "Team management access"
    }
  ]
}
```

### List Permissions
```
GET /api/permissions/
Authorization: Bearer {token}

Response (200):
{
  "permissions": [
    {
      "id": "view_contracts",
      "name": "View Contracts",
      "category": "Contracts"
    },
    {
      "id": "create_contracts",
      "name": "Create Contracts",
      "category": "Contracts"
    },
    {
      "id": "edit_contracts",
      "name": "Edit Contracts",
      "category": "Contracts"
    },
    {
      "id": "delete_contracts",
      "name": "Delete Contracts",
      "category": "Contracts"
    },
    {
      "id": "view_templates",
      "name": "View Templates",
      "category": "Templates"
    },
    {
      "id": "create_templates",
      "name": "Create Templates",
      "category": "Templates"
    },
    {
      "id": "view_users",
      "name": "View Users",
      "category": "Administration"
    },
    {
      "id": "manage_users",
      "name": "Manage Users",
      "category": "Administration"
    },
    {
      "id": "view_audit_logs",
      "name": "View Audit Logs",
      "category": "Administration"
    }
  ]
}
```

### List Users
```
GET /api/users/
Authorization: Bearer {token}

Response (200):
{
  "users": [
    {
      "id": "uuid",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2026-01-01T10:00:00Z",
      "last_login": "2026-01-12T10:30:00Z"
    }
  ],
  "total": 42
}
```

### List SLA Rules
```
GET /api/admin/sla-rules/
Authorization: Bearer {token}

Response (200):
{
  "sla_rules": [
    {
      "id": "sla-1",
      "name": "Standard SLA",
      "description": "Standard service level agreement",
      "tenant_id": "uuid",
      "response_time": 24,
      "resolution_time": 72,
      "priority_levels": ["Low", "Medium", "High", "Critical"],
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    },
    {
      "id": "sla-2",
      "name": "Premium SLA",
      "description": "Premium service level agreement",
      "tenant_id": "uuid",
      "response_time": 4,
      "resolution_time": 24,
      "priority_levels": ["Low", "Medium", "High", "Critical"],
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### List SLA Breaches
```
GET /api/admin/sla-breaches/
Authorization: Bearer {token}

Response (200):
{
  "sla_breaches": [
    {
      "id": "uuid",
      "contract_id": "uuid",
      "sla_rule_id": "sla-1",
      "breach_type": "response_time",
      "breach_time": "2026-01-12T14:00:00Z",
      "resolution_time": null,
      "status": "open",
      "created_at": "2026-01-12T14:00:00Z"
    }
  ],
  "total": 3
}
```

### List User Roles
```
GET /api/admin/users/roles/
Authorization: Bearer {token}

Response (200):
{
  "user_roles": [
    {
      "user_id": "uuid",
      "email": "john@example.com",
      "name": "John Doe",
      "roles": ["admin"],
      "is_active": true,
      "last_login": "2026-01-12T10:30:00Z",
      "date_joined": "2026-01-01T10:00:00Z"
    },
    {
      "user_id": "uuid",
      "email": "jane@example.com",
      "name": "Jane Smith",
      "roles": ["user", "manager"],
      "is_active": true,
      "last_login": "2026-01-12T09:30:00Z",
      "date_joined": "2026-01-05T10:00:00Z"
    }
  ]
}
```

### List Tenants (Admin Only)
```
GET /api/admin/tenants/
Authorization: Bearer {token}

Response (200):
{
  "tenants": [
    {
      "id": "uuid",
      "name": "Acme Corporation",
      "created_at": "2026-01-01T10:00:00Z"
    },
    {
      "id": "uuid",
      "name": "Global Industries",
      "created_at": "2026-01-05T10:00:00Z"
    }
  ]
}
```

---

## AUDIT LOGS & HISTORY

### List Audit Logs
```
GET /api/audit-logs/
Authorization: Bearer {token}
Query Parameters:
  - limit: integer (default: 20)
  - offset: integer (default: 0)
  - action: string (created|updated|deleted|approved|rejected)
  - entity_type: string (contract|template|workflow|approval)
  - start_date: ISO date string
  - end_date: ISO date string

Response (200):
{
  "count": 543,
  "results": [
    {
      "id": "uuid",
      "entity_type": "contract",
      "entity_id": "uuid",
      "action": "created",
      "performed_by": "uuid",
      "performer_email": "john@example.com",
      "changes": {
        "title": {"old": null, "new": "Service Agreement"},
        "status": {"old": null, "new": "draft"}
      },
      "metadata": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
      },
      "created_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

### Get Audit Statistics
```
GET /api/audit-logs/stats/
Authorization: Bearer {token}
Query Parameters:
  - days: integer (default: 30)

Response (200):
{
  "total_actions": 543,
  "actions_by_type": {
    "created": 150,
    "updated": 280,
    "deleted": 45,
    "approved": 60,
    "rejected": 8
  },
  "actions_by_entity": {
    "contract": 350,
    "template": 120,
    "workflow": 50,
    "approval": 23
  },
  "actions_by_user": [
    {
      "user_id": "uuid",
      "email": "john@example.com",
      "action_count": 245
    },
    {
      "user_id": "uuid",
      "email": "jane@example.com",
      "action_count": 198
    }
  ],
  "daily_trends": [
    {
      "date": "2026-01-12",
      "action_count": 45
    },
    {
      "date": "2026-01-11",
      "action_count": 38
    }
  ]
}
```

### Get Contract History
```
GET /api/contracts/{id}/history/
Authorization: Bearer {token}

Response (200):
{
  "history": [
    {
      "id": "uuid",
      "entity_type": "contract",
      "entity_id": "uuid",
      "action": "updated",
      "performed_by": "uuid",
      "performer_email": "john@example.com",
      "changes": {
        "status": {"old": "draft", "new": "pending"},
        "value": {"old": 50000, "new": 55000}
      },
      "created_at": "2026-01-12T11:00:00Z"
    },
    {
      "id": "uuid",
      "entity_type": "contract",
      "entity_id": "uuid",
      "action": "created",
      "performed_by": "uuid",
      "performer_email": "john@example.com",
      "changes": {},
      "created_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

---

## HEALTH & STATUS

### System Health Check
```
GET /api/health/
Authorization: Bearer {token}

Response (200):
{
  "status": "healthy",
  "timestamp": "2026-01-12T12:00:00Z",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "storage": "healthy"
  }
}
```

### Database Health Check
```
GET /api/health/database/
Authorization: Bearer {token}

Response (200):
{
  "status": "healthy",
  "timestamp": "2026-01-12T12:00:00Z",
  "connection": "active",
  "latency_ms": 2.5
}
```

### Cache Health Check
```
GET /api/health/cache/
Authorization: Bearer {token}

Response (200):
{
  "status": "healthy",
  "timestamp": "2026-01-12T12:00:00Z",
  "connection": "active",
  "latency_ms": 1.2
}
```

### System Metrics
```
GET /api/health/metrics/
Authorization: Bearer {token}

Response (200):
{
  "timestamp": "2026-01-12T12:00:00Z",
  "uptime_seconds": 86400,
  "requests_total": 15234,
  "requests_per_minute": 12.3,
  "errors_total": 23,
  "error_rate": 0.15,
  "database_connections": 5,
  "cache_memory_usage_mb": 128
}
```

---

## ERROR RESPONSES

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": {
    "field_name": ["Field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "detail": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied",
  "detail": "You do not have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "detail": "The requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

---

## COMMON QUERY PARAMETERS

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Number of results to return (default: 20, max: 100) |
| `offset` | integer | Number of results to skip (default: 0) |
| `search` | string | Search term for text search |
| `status` | string | Filter by status |
| `sort` | string | Sort field (prefix with `-` for descending) |

---

## AUTHENTICATION HEADER

All endpoints (except /auth/register and /auth/login) require:

```
Authorization: Bearer {access_token}
```

Where `{access_token}` is obtained from the login or register endpoint.

---

## RATE LIMITING

- **Standard:** 100 requests per minute
- **Premium:** 1000 requests per minute
- **Admin:** Unlimited

Response headers include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642068000
```

---

## WEBHOOK EVENTS

Webhooks are sent for the following events:

- `contract.created`
- `contract.updated`
- `contract.deleted`
- `contract.approved`
- `workflow.instance.step_completed`
- `approval.created`
- `approval.status_changed`
- `template.published`

---

## PAGINATION

All list endpoints return paginated results:

```json
{
  "count": 127,
  "next": "/api/contracts/?offset=20",
  "previous": null,
  "results": [...]
}
```

Navigate using `next` and `previous` URLs or manually with `limit` and `offset` parameters.

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
