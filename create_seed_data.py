import os
import sys
import django
import uuid
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from authentication.models import User
from contracts.models import Contract, ContractTemplate, Clause
from workflows.models import Workflow, WorkflowInstance
from notifications.models import NotificationModel
from audit_logs.models import AuditLogModel
from repository.models import RepositoryModel, RepositoryFolderModel
from metadata.models import MetadataFieldModel
from ocr.models import OCRJobModel
from redaction.models import RedactionJobModel
from ai.models import AIInferenceModel
from rules.models import RuleModel
from approvals.models import ApprovalModel
from tenants.models import TenantModel
from search.models import SearchIndexModel

print("🔵 Creating seed data...")

# Create test user
tenant_id = uuid.uuid4()
user = User.objects.create_user(
    email='test@example.com',
    password='Test@123456',
    first_name='Test',
    last_name='User',
    tenant_id=tenant_id,
    is_active=True
)
print(f"✅ Created user: {user.email}")

# Create tenant
tenant = TenantModel.objects.create(
    name='Test Tenant',
    domain='test.example.com',
    status='active'
)
print(f"✅ Created tenant: {tenant.name}")

# Create contract template
template = ContractTemplate.objects.create(
    title='Standard Service Agreement',
    description='Standard template for service agreements',
    content='Service Agreement Content Here',
    version='1.0',
    is_active=True,
    created_by=user.user_id,
    tenant_id=tenant_id
)
print(f"✅ Created contract template: {template.title}")

# Create contracts
contracts = []
for i in range(5):
    contract = Contract.objects.create(
        title=f'Contract {i+1} - {datetime.now().strftime("%Y-%m-%d")}',
        description=f'Test contract {i+1}',
        content=f'Contract content {i+1}',
        status='draft',
        version='1.0',
        created_by=user.user_id,
        tenant_id=tenant_id,
        template=template
    )
    contracts.append(contract)
    print(f"✅ Created contract: {contract.title}")

# Create clauses
clauses = []
for i in range(10):
    clause = Clause.objects.create(
        title=f'Clause {i+1}',
        content=f'Clause content {i+1}',
        category='terms',
        created_by=user.user_id,
        tenant_id=tenant_id
    )
    clauses.append(clause)
    print(f"✅ Created clause: {clause.title}")

# Create workflows
workflow = Workflow.objects.create(
    name='Contract Approval Workflow',
    description='Standard approval workflow',
    status='active',
    config={'steps': ['draft', 'review', 'approved']},
    created_by=user.user_id,
    tenant_id=tenant_id
)
print(f"✅ Created workflow: {workflow.name}")

# Create workflow instance
workflow_instance = WorkflowInstance.objects.create(
    workflow=workflow,
    contract=contracts[0],
    current_step='draft',
    status='active',
    created_by=user.user_id,
    tenant_id=tenant_id
)
print(f"✅ Created workflow instance for {contracts[0].title}")

# Create notifications
notification = NotificationModel.objects.create(
    recipient_id=user.user_id,
    type='email',
    subject='Test Notification',
    content='This is a test notification',
    status='sent',
    tenant_id=tenant_id
)
print(f"✅ Created notification: {notification.subject}")

# Create audit logs
audit_log = AuditLogModel.objects.create(
    tenant_id=tenant_id,
    user_id=user.user_id,
    entity_type='contract',
    entity_id=contracts[0].id,
    action='created',
    changes={'field': 'title', 'old': '', 'new': contracts[0].title}
)
print(f"✅ Created audit log")

# Create repository documents
repo_doc = RepositoryModel.objects.create(
    name='Test Document',
    description='A test document',
    document_type='pdf',
    file_path='/documents/test.pdf',
    file_size=1024,
    mime_type='application/pdf',
    created_by=user.user_id,
    tenant_id=tenant_id
)
print(f"✅ Created repository document: {repo_doc.name}")

# Create repository folder
repo_folder = RepositoryFolderModel.objects.create(
    name='Contracts',
    parent_id=None,
    tenant_id=tenant_id
)
print(f"✅ Created repository folder: {repo_folder.name}")

# Create metadata field
metadata = MetadataFieldModel.objects.create(
    name='contract_type',
    field_type='text',
    is_required=False,
    tenant_id=tenant_id
)
print(f"✅ Created metadata field: {metadata.name}")

# Create OCR job
ocr_job = OCRJobModel.objects.create(
    document_id=repo_doc.id,
    status='completed',
    extracted_text='Extracted OCR text',
    confidence=0.95,
    tenant_id=tenant_id
)
print(f"✅ Created OCR job")

# Create redaction job
redaction_job = RedactionJobModel.objects.create(
    document_id=repo_doc.id,
    status='completed',
    patterns=['SSN', 'EMAIL'],
    redacted_content={'redacted': True},
    tenant_id=tenant_id
)
print(f"✅ Created redaction job")

# Create AI inference
ai_inference = AIInferenceModel.objects.create(
    model_name='gpt-4',
    input_text='Test input',
    output_text='Test output',
    status='completed',
    usage={'tokens': 100},
    tenant_id=tenant_id
)
print(f"✅ Created AI inference")

# Create rule
rule = RuleModel.objects.create(
    name='Auto Approval Rule',
    description='Auto approve contracts under $10k',
    rule_type='auto_approval',
    config={'threshold': 10000},
    is_active=True,
    tenant_id=tenant_id
)
print(f"✅ Created rule: {rule.name}")

# Create approval
approval = ApprovalModel.objects.create(
    contract=contracts[0],
    approver_id=user.user_id,
    status='pending',
    tenant_id=tenant_id
)
print(f"✅ Created approval")

# Create search index
search_index = SearchIndexModel.objects.create(
    entity_type='contract',
    entity_id=contracts[0].id,
    content=contracts[0].content,
    metadata={'title': contracts[0].title},
    tenant_id=tenant_id
)
print(f"✅ Created search index")

print("\n✅ Seed data creation complete!")
print(f"\nTest Credentials:")
print(f"  Email: test@example.com")
print(f"  Password: Test@123456")
