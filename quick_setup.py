#!/usr/bin/env python
"""Quick setup of test data"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

import uuid
from tenants.models import TenantModel
from authentication.models import User
from contracts.models import Contract
from search.models import SearchIndexModel
from search.services_corrected import SearchIndexingService

print("\n" + "="*70)
print("🔧 QUICK TEST DATA SETUP")
print("="*70)

# Create or get tenant
print("\n1️⃣  Creating Tenant...")
tenant = TenantModel.objects.filter(name='Test Tenant 1').first()
if not tenant:
    tenant_id = uuid.uuid4()
    tenant = TenantModel.objects.create(
        id=tenant_id,
        name='Test Tenant 1',
        domain='test-tenant-1.local',
        status='active'
    )
    print(f"  ✅ Created: {tenant.name} ({tenant.id})")
else:
    print(f"  ⚠️  Exists: {tenant.name} ({tenant.id})")

# Create or get user
print("\n2️⃣  Creating User...")
user = User.objects.filter(email='test@example.com').first()
if not user:
    user = User.objects.create_user(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='testpass123',
        tenant_id=tenant.id
    )
    print(f"  ✅ Created: {user.email}")
else:
    print(f"  ⚠️  Exists: {user.email}")

# Create contracts
print("\n3️⃣  Creating Test Contracts...")
contracts_data = [
    ('Service Agreement', 'Service agreement with cloud computing services, payment terms of $5000/month, auto-renewal clause for 1 year periods'),
    ('NDA', 'Non-disclosure agreement with confidentiality obligations for 5 years, protection of trade secrets'),
    ('License Agreement', 'Software license agreement with restrictions on reverse engineering, 3 year term renewable annually'),
]

for title, content in contracts_data:
    contract, created = Contract.objects.get_or_create(
        title=title,
        tenant_id=tenant.id,
        defaults={
            'description': content,
            'status': 'executed',
            'is_approved': True,
            'created_by': user.user_id,
        }
    )
    print(f"  {'✅ Created' if created else '⚠️  Exists'}: {title}")

# Index contracts  
print("\n4️⃣  Indexing Contracts...")
indexed = 0
for contract in Contract.objects.filter(tenant_id=tenant.id):
    try:
        exists = SearchIndexModel.objects.filter(
            entity_id=str(contract.id),
            entity_type='contract',
            tenant_id=tenant.id
        ).exists()
        
        if not exists:
            SearchIndexingService.create_index(
                entity_type='contract',
                entity_id=str(contract.id),
                title=contract.title,
                content=contract.description or contract.title,
                tenant_id=tenant.id,
                keywords=['contract', 'agreement']
            )
            print(f"  ✅ Indexed: {contract.title}")
            indexed += 1
        else:
            print(f"  ⚠️  Already indexed: {contract.title}")
    except Exception as e:
        print(f"  ❌ Error indexing {contract.title}: {str(e)}")

print("\n" + "="*70)
print(f"📊 SETUP COMPLETE")
print(f"  • Tenant: {tenant.name}")
print(f"  • User: {user.email}")
print(f"  • Contracts: {Contract.objects.filter(tenant_id=tenant.id).count()}")
print("="*70 + "\n")
