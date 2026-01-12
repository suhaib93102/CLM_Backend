#!/usr/bin/env python
"""Test email sending functionality"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from authentication.models import User
import time

print("=" * 70)
print("📧 TESTING EMAIL CONFIGURATION & SENDING")
print("=" * 70)
print()

print("1️⃣  Email Configuration:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

print("2️⃣  Sending test email...")
try:
    send_mail(
        'CLM Authentication Test - ' + str(int(time.time())),
        'This is a test email from CLM Authentication System.\n\nIf you receive this, email sending is working correctly!',
        settings.DEFAULT_FROM_EMAIL,
        ['movieswatch996886@gmail.com'],
        fail_silently=False,
    )
    print("   ✅ Test email sent successfully!")
    print("   📬 Check your inbox at movieswatch996886@gmail.com")
except Exception as e:
    print(f"   ❌ Error sending email: {e}")
    sys.exit(1)

print()
print("3️⃣  Testing OTP generation and email...")

# Create or get test user
test_email = f"otp-test-{int(time.time())}@test.com"
print(f"   Creating test user: {test_email}")

try:
    user = User.objects.create_user(
        email=test_email,
        password="Test@123456",
        first_name="OTP Test"
    )
    print(f"   ✅ User created: {user.email}")
    
    # Generate OTP
    otp = ''.join(str(i) for i in range(6))[:6]
    user.login_otp = otp
    user.login_otp_created_at = django.utils.timezone.now()
    user.save()
    
    print(f"   ✅ OTP Generated: {otp}")
    
    # Send OTP email
    from authentication.otp_service import OTPService
    result = OTPService.send_login_otp(user, otp)
    
    if result:
        print(f"   ✅ OTP email sent to {test_email}")
    else:
        print(f"   ⚠️  OTP email could not be sent (user email not real)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("✅ EMAIL TESTING COMPLETE")
print("=" * 70)
print()
print("Next Steps:")
print("1. Check your inbox for the test email")
print("2. If received, email configuration is working")
print("3. Run the full authentication test")
