#!/usr/bin/env python
"""
Setup test data for search functionality

This script creates:
1. Test tenants
2. Test users
3. Test contracts with content
4. Indexes for those contracts

Run with:
    python manage.py shell < setup_test_data.py
    OR
    python setup_test_data.py
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from tenants.models import TenantModel
from contracts.models import Contract
from search.models import SearchIndexModel, SearchAnalyticsModel
from search.services_corrected import SearchIndexingService

def create_test_data():
    """Create comprehensive test data"""
    
    print("\n" + "="*70)
    print("🔧 SETTING UP TEST DATA")
    print("="*70)
    
    # 1. Create Tenants
    print("\n1️⃣  Creating Tenants...")
    import uuid
    tenant_id_1 = uuid.uuid4()
    tenant_id_2 = uuid.uuid4()
    
    tenant1, created = TenantModel.objects.get_or_create(
        name="Test Tenant 1",
        defaults={
            'id': tenant_id_1,
            'domain': 'test-tenant-1.local',
            'status': 'active',
            'subscription_plan': 'enterprise'
        }
    )
    print(f"  {'✅ Created' if created else '⚠️  Already exists'}: {tenant1.name}")
    
    tenant2, created = TenantModel.objects.get_or_create(
        name="Test Tenant 2",
        defaults={
            'id': tenant_id_2,
            'domain': 'test-tenant-2.local',
            'status': 'active',
            'subscription_plan': 'professional'
        }
    )
    print(f"  {'✅ Created' if created else '⚠️  Already exists'}: {tenant2.name}")
    
    # 2. Create Users
    print("\n2️⃣  Creating Users...")
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'testuser1@example.com',
            'first_name': 'Test',
            'last_name': 'User 1',
            'is_active': True
        }
    )
    print(f"  {'✅ Created' if created else '⚠️  Already exists'}: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'testuser2@example.com',
            'first_name': 'Test',
            'last_name': 'User 2',
            'is_active': True
        }
    )
    print(f"  {'✅ Created' if created else '⚠️  Already exists'}: {user2.username}")
    
    # 3. Create Test Contracts with Rich Content
    print("\n3️⃣  Creating Test Contracts...")
    
    contracts_data = [
        {
            'title': 'Service Agreement - Cloud Services',
            'content': '''
            SERVICE AGREEMENT
            
            This Service Agreement ("Agreement") is entered into as of January 1, 2024.
            
            1. SERVICES
            The Provider agrees to provide cloud computing services including:
            - Storage services (100 GB minimum)
            - Computing resources (4 vCPU, 8 GB RAM)
            - Support services (24/7 availability)
            
            2. PAYMENT TERMS
            Monthly fee: $5,000 USD
            Payment due within 30 days of invoice
            Late payment penalties: 1.5% per month
            
            3. AUTO-RENEWAL
            This agreement shall automatically renew for successive one-year periods
            unless either party provides written notice of non-renewal at least
            60 days prior to the expiration date.
            
            4. TERMINATION
            Either party may terminate this agreement with 90 days written notice.
            Immediate termination is allowed for material breach.
            
            5. CONFIDENTIALITY
            All confidential information must be protected for 3 years after termination.
            
            6. LIABILITY
            Total liability limited to 12 months of fees paid.
            
            Signed: _______________
            Date: January 1, 2024
            ''',
            'entity_type': 'contract',
            'keywords': ['cloud', 'service', 'auto-renewal', 'payment', 'termination'],
            'tenant': tenant1
        },
        {
            'title': 'Non-Disclosure Agreement',
            'content': '''
            NON-DISCLOSURE AGREEMENT
            
            WHEREAS, the Disclosing Party desires to disclose certain confidential
            information to the Receiving Party;
            
            NOW, THEREFORE, the parties agree as follows:
            
            1. CONFIDENTIAL INFORMATION
            Confidential Information includes but is not limited to:
            - Trade secrets
            - Business plans
            - Financial information
            - Technical specifications
            - Customer lists
            
            2. OBLIGATIONS
            The Receiving Party shall:
            - Maintain confidentiality using reasonable care
            - Limit disclosure to employees with need to know
            - Return or destroy information upon request
            
            3. DURATION
            Obligations continue for 5 years after disclosure.
            
            4. REMEDIES
            Breach entitles Disclosing Party to injunctive relief and damages.
            
            5. GOVERNING LAW
            This agreement is governed by California law.
            
            Executed: January 15, 2024
            ''',
            'entity_type': 'contract',
            'keywords': ['confidential', 'nda', 'information', 'protection', 'breach'],
            'tenant': tenant1
        },
        {
            'title': 'Software License Agreement',
            'content': '''
            SOFTWARE LICENSE AGREEMENT
            
            GRANT OF LICENSE
            Licensor grants Licensee a non-exclusive, non-transferable license to use
            the Software subject to the terms of this Agreement.
            
            LICENSE RESTRICTIONS
            Licensee shall not:
            - Reverse engineer or decompile the Software
            - Rent, lease, or lend the Software
            - Create derivative works
            - Remove copyright notices
            
            SUPPORT AND UPDATES
            - Basic support included for first 12 months
            - Security updates provided for 3 years
            - Major version updates available for additional fee
            
            PAYMENT
            One-time license fee: $50,000
            Annual support fee: $10,000
            
            TERM AND TERMINATION
            Initial term: 3 years
            Renewable annually thereafter
            Termination for convenience allowed with 30 days notice
            
            INDEMNIFICATION
            Licensor indemnifies Licensee against third-party IP claims.
            
            WARRANTY DISCLAIMER
            SOFTWARE PROVIDED "AS IS" WITHOUT WARRANTY
            
            Effective Date: January 20, 2024
            ''',
            'entity_type': 'contract',
            'keywords': ['software', 'license', 'agreement', 'support', 'warranty'],
            'tenant': tenant2
        },
        {
            'title': 'Employee Agreement',
            'content': '''
            EMPLOYEE AGREEMENT
            
            This Employee Agreement ("Agreement") is made between Company and Employee.
            
            1. POSITION AND COMPENSATION
            Position: Senior Software Engineer
            Base Salary: $120,000 annually
            Bonus: Up to 20% based on performance
            Benefits: Health insurance, 401(k), stock options
            
            2. EMPLOYMENT STATUS
            Employment is at-will and can be terminated by either party.
            At-will employment means:
            - Either party can end employment at any time
            - Any or no reason required
            - No notice period required (unless specified below)
            
            3. NOTICE PERIOD
            Employee should provide 2 weeks written notice
            Company may require 2 weeks notice before termination
            
            4. CONFIDENTIALITY
            Employee agrees to maintain confidentiality of:
            - Trade secrets
            - Client information
            - Business strategies
            - Code and documentation
            
            5. NON-COMPETITION
            During employment and for 1 year after:
            - Cannot work for competing companies
            - Cannot solicit clients
            - Cannot solicit employees
            
            6. INTELLECTUAL PROPERTY
            All work product is company property.
            
            7. BENEFITS
            - Health insurance (company pays 80%)
            - 401(k) matching up to 4%
            - Stock options vesting over 4 years
            - Unlimited PTO
            
            Signed: _______________
            Date: January 25, 2024
            ''',
            'entity_type': 'contract',
            'keywords': ['employment', 'salary', 'benefits', 'confidentiality', 'non-compete'],
            'tenant': tenant2
        },
        {
            'title': 'Maintenance and Support Agreement',
            'content': '''
            MAINTENANCE AND SUPPORT AGREEMENT
            
            This agreement defines the terms for ongoing maintenance and support.
            
            SERVICE LEVELS
            - Critical Issues: 1-hour response, 4-hour resolution target
            - High Priority: 4-hour response, 1-day resolution target
            - Medium Priority: 1-day response, 3-day resolution target
            - Low Priority: 3-day response, 2-week resolution target
            
            SUPPORT HOURS
            - Tier 1: Business hours support (8 AM - 6 PM EST)
            - Tier 2: 24/7 emergency support
            
            MAINTENANCE WINDOWS
            Scheduled maintenance can occur:
            - Monthly on second Sunday from 2 AM - 6 AM EST
            - Additional emergency maintenance with 24-hour notice
            
            PRICING
            Annual maintenance: 20% of software license cost
            Invoiced quarterly in advance
            
            RENEWAL
            This agreement automatically renews annually unless terminated
            with 60 days written notice prior to expiration.
            
            PERFORMANCE METRICS
            - Uptime target: 99.9%
            - Average response time: < 2 hours
            - Customer satisfaction score: > 4.5/5
            
            Term: January 1, 2024 - December 31, 2024
            ''',
            'entity_type': 'contract',
            'keywords': ['maintenance', 'support', 'sla', 'uptime', 'response-time'],
            'tenant': tenant1
        }
    ]
    
    created_contracts = []
    for contract_data in contracts_data:
        # Create contract
        contract, created = Contract.objects.get_or_create(
            title=contract_data['title'],
            tenant_id=contract_data['tenant'].id,
            defaults={
                'description': contract_data['content'][:500],
                'status': 'executed',
                'is_approved': True,
                'created_by': user1.id,
                'contract_type': 'service-agreement',
                'counterparty': 'Sample Counterparty LLC'
            }
        )
        status = '✅ Created' if created else '⚠️  Already exists'
        print(f"  {status}: {contract.title}")
        created_contracts.append((contract, contract_data))
    
    # 4. Create Search Indexes
    print("\n4️⃣  Creating Search Indexes...")
    
    indexed_count = 0
    for contract, data in created_contracts:
        try:
            # Check if already indexed
            existing = SearchIndexModel.objects.filter(
                entity_id=str(contract.id),
                entity_type='contract',
                tenant_id=data['tenant'].id
            ).exists()
            
            if not existing:
                # Create index
                SearchIndexingService.create_index(
                    entity_type='contract',
                    entity_id=str(contract.id),
                    title=contract.title,
                    content=contract.description or contract.title,
                    tenant_id=data['tenant'].id,
                    keywords=data['keywords']
                )
                print(f"  ✅ Indexed: {contract.title}")
                indexed_count += 1
            else:
                print(f"  ⚠️  Already indexed: {contract.title}")
        except Exception as e:
            print(f"  ❌ Error indexing {contract.title}: {str(e)}")
    
    # 5. Print Summary
    print("\n" + "="*70)
    print("📊 SETUP SUMMARY")
    print("="*70)
    print(f"✅ Tenants created/updated: 2")
    print(f"✅ Users created/updated: 2")
    print(f"✅ Contracts created/updated: {len(created_contracts)}")
    print(f"✅ Indexes created: {indexed_count}")
    
    print("\n📝 Test Data Ready!")
    print("="*70)
    
    return {
        'tenants': [tenant1, tenant2],
        'users': [user1, user2],
        'contracts': created_contracts,
        'indexed_count': indexed_count
    }

if __name__ == '__main__':
    create_test_data()
