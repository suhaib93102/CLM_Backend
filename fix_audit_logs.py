import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Drop existing table
    cursor.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
    
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL,
            user_id UUID NOT NULL,
            entity_type VARCHAR(100),
            entity_id UUID,
            action VARCHAR(20),
            changes JSONB DEFAULT '{}'::jsonb,
            ip_address INET,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    print("✓ audit_logs table recreated successfully")
