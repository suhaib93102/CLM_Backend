#!/usr/bin/env python
"""
Create real test data in database
"""
import os, sys, django, uuid
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.utils import timezone
from authentication.models import User
from contracts.models import Contract, ContractTemplate
from workflows.models import Workflow
from tenants.models import TenantModel

print("🔵 Clearing old data...")
User.objects.filter(email='test@example.com').delete()
TenantModel.objects.filter(name='Test Tenant').delete()
Contract.objects.all().delete()
ContractTemplate.objects.all().delete()

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
    tenant_id=tenant_id,
    name='Standard Service Agreement',
    contract_type='MSA',
    description='Standard template',
    version=1,
    status='published',
    r2_key='templates/standard-msa.docx',
    created_by=user.user_id
)
print(f"✅ Created template: {template.name}")

# Create contracts
for i in range(3):
    contract = Contract.objects.create(
        tenant_id=tenant_id,
        template=template,
        title=f'Contract #{i+1}',
        description=f'Test contract {i+1}',
        current_version=1,
        status='approved',
        is_approved=True,
        created_by=user.user_id,
        contract_type='MSA',
        approved_by=user.user_id
    )
    print(f"✅ Created contract: {contract.title}")

# Create workflow
workflow = Workflow.objects.create(
    name='Approval Workflow',
    description='Standard approval',
    status='active',
    config={'steps': ['draft', 'review', 'approved']},
    created_by=user.user_id,
    tenant_id=tenant_id
)
print(f"✅ Created workflow: {workflow.name}")

print("\n✅ Seed data complete!")
print(f"Test Credentials:")
print(f"  Email: test@example.com")
print(f"  Password: Test@123456")
