#!/usr/bin/env python
"""
Reset and rebuild database with proper schema
"""
import os
import sys
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from django.db import connection
from django.core.management.sql import emit_post_migrate_signal

# Drop all tables
print("🔴 Dropping all tables...")
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")

print("✅ Schema recreated")

# Run migrations to create tables
print("\n🔵 Running migrations...")
call_command('migrate', '--run-syncdb', verbosity=1)

# Emit post-migrate signal
emit_post_migrate_signal(2, False, 'default')

print("\n✅ Database reset complete!")
