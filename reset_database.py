#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("=" * 80)
print("RESETTING DATABASE STRUCTURE")
print("=" * 80)

# Drop and recreate clm_users table with proper schema
print("\n[1/5] Fixing clm_users table...")
with connection.cursor() as cursor:
    try:
        # Check current columns
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'clm_users' 
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"  Current columns: {columns}")
        
        # Add missing columns
        needed_columns = [
            ('login_otp', "VARCHAR(6)"),
            ('password_reset_otp', "VARCHAR(6)"),
            ('otp_created_at', "TIMESTAMP"),
        ]
        
        for col_name, col_type in needed_columns:
            if col_name not in columns:
                print(f"  Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE clm_users ADD COLUMN {col_name} {col_type} NULL")
            else:
                print(f"  Column already exists: {col_name}")
        
        connection.commit()
        print("  ✓ clm_users table fixed")
    except Exception as e:
        print(f"  Error: {e}")

# Fix audit_logs table
print("\n[2/5] Fixing audit_logs table...")
with connection.cursor() as cursor:
    try:
        # Drop if exists
        cursor.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
        print("  Dropped old audit_logs table")
        
        # Create new one with correct schema
        cursor.execute("""
            CREATE TABLE audit_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tenant_id UUID NOT NULL,
                user_id UUID NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                entity_id UUID NOT NULL,
                action VARCHAR(50) NOT NULL,
                changes JSONB,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES clm_users(user_id) ON DELETE SET NULL
            )
        """)
        cursor.execute("CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id)")
        cursor.execute("CREATE INDEX idx_audit_logs_user ON audit_logs(user_id)")
        cursor.execute("CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id)")
        cursor.execute("CREATE INDEX idx_audit_logs_created ON audit_logs(created_at)")
        connection.commit()
        print("  ✓ audit_logs table recreated with proper schema")
    except Exception as e:
        print(f"  Error: {e}")

# Remove problematic migration files
print("\n[3/5] Cleaning migration files...")
import glob
migration_files = glob.glob('/Users/vishaljha/Desktop/CLM_Backend/*/migrations/0*.py')
# Keep only __init__.py
for f in migration_files:
    if '__init__' not in f:
        try:
            os.remove(f)
            print(f"  Removed: {f.split('/')[-1]}")
        except:
            pass

print("  ✓ Migration files cleaned")

# Run fresh migrations
print("\n[4/5] Running fresh migrations...")
try:
    call_command('makemigrations', verbosity=0)
    print("  ✓ Migrations created")
    call_command('migrate', verbosity=0)
    print("  ✓ Migrations applied")
except Exception as e:
    print(f"  Warning: {e}")

print("\n[5/5] Creating default tenant...")
from authentication.models import User
from tenants.models import TenantModel

try:
    # Create default tenant
    default_tenant = TenantModel.objects.create(
        name="Default Tenant",
        domain="default.clm.local",
        is_active=True
    )
    print(f"  ✓ Default tenant created: {default_tenant.id}")
except Exception as e:
    print(f"  Note: Tenant creation skipped - {e}")

print("\n" + "=" * 80)
print("DATABASE RESET COMPLETE")
print("=" * 80)
