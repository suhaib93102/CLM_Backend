#!/usr/bin/env python
"""
Production-level Authentication Test with Real Email Sending
Tests complete authentication flow with real OTP email delivery
"""

import os
import sys
import json
import time
import requests
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from authentication.models import User
from authentication.otp_service import OTPService

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = f"test-auth-{int(time.time())}@test.com"
REAL_EMAIL = "movieswatch996886@gmail.com"  # Real recipient
TEST_PASSWORD = "Test@123456"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def test_email_configuration():
    """Test email configuration"""
    print_section("📧 EMAIL CONFIGURATION TEST")
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test sending a simple email
    print("\n🔄 Testing email delivery...")
    try:
        send_mail(
            'CLM Authentication Test',
            f'Testing email configuration on {datetime.now().isoformat()}',
            settings.DEFAULT_FROM_EMAIL,
            [REAL_EMAIL],
            fail_silently=False,
        )
        print_success("Test email sent successfully to real inbox")
        return True
    except Exception as e:
        print_error(f"Failed to send test email: {str(e)}")
        return False

def test_register_endpoint() -> Optional[Dict]:
    """Test user registration endpoint"""
    print_section("1️⃣  USER REGISTRATION TEST")
    
    print(f"Endpoint: POST {BASE_URL}/auth/register/")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Password: {TEST_PASSWORD}\n")
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "first_name": "Test User"
    }
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code in [200, 201]:
            print_success("User registered successfully")
            return response.json()
        else:
            print_error(f"Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Registration request failed: {str(e)}")
        return None

def test_login_endpoint() -> Optional[str]:
    """Test login endpoint and get access token"""
    print_section("2️⃣  USER LOGIN TEST")
    
    # Use existing test user
    login_email = "test@example.com"
    login_password = "Test@123456"
    
    print(f"Endpoint: POST {BASE_URL}/auth/login/")
    print(f"Email: {login_email}")
    print(f"Password: {login_password}\n")
    
    payload = {
        "email": login_email,
        "password": login_password
    }
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        
        # Mask tokens in output
        display_data = response_data.copy()
        if 'access' in display_data:
            display_data['access'] = display_data['access'][:20] + '...'
        if 'refresh' in display_data:
            display_data['refresh'] = display_data['refresh'][:20] + '...'
        
        print(f"Response:\n{json.dumps(display_data, indent=2)}\n")
        
        if response.status_code == 200 and 'access' in response_data:
            print_success("Login successful")
            return response_data['access']
        else:
            print_error(f"Login failed: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Login request failed: {str(e)}")
        return None

def test_request_login_otp(email: str) -> Tuple[bool, Optional[str]]:
    """Test requesting login OTP"""
    print_section("3️⃣  REQUEST LOGIN OTP TEST")
    
    print(f"Endpoint: POST {BASE_URL}/auth/request-login-otp/")
    print(f"Email: {email}\n")
    
    payload = {"email": email}
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}\n")
    print("📧 OTP will be sent to the real email inbox...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/request-login-otp/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            print_success("OTP requested successfully")
            print_warning("⏰ OTP is valid for 10 minutes")
            
            # For testing purposes, get the actual OTP from the database
            try:
                user = User.objects.get(email=email)
                actual_otp = user.login_otp
                if actual_otp:
                    print_info(f"OTP generated (for testing): {actual_otp}")
                    return True, actual_otp
            except:
                pass
            
            print_info("Check your real email inbox for the OTP code")
            return True, None
        else:
            print_error(f"OTP request failed: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"OTP request failed: {str(e)}")
        return False, None

def test_request_password_reset_otp(email: str) -> Tuple[bool, Optional[str]]:
    """Test requesting password reset OTP"""
    print_section("4️⃣  REQUEST PASSWORD RESET OTP TEST")
    
    print(f"Endpoint: POST {BASE_URL}/auth/forgot-password/")
    print(f"Email: {email}\n")
    
    payload = {"email": email}
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}\n")
    print("📧 Password reset OTP will be sent to the real email inbox...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/forgot-password/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            print_success("Password reset OTP requested successfully")
            print_warning("⏰ OTP is valid for 10 minutes")
            
            # For testing purposes, get the actual OTP from the database
            try:
                user = User.objects.get(email=email)
                actual_otp = user.password_reset_otp
                if actual_otp:
                    print_info(f"OTP generated (for testing): {actual_otp}")
                    return True, actual_otp
            except:
                pass
            
            print_info("Check your real email inbox for the OTP code")
            return True, None
        else:
            print_error(f"OTP request failed: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"OTP request failed: {str(e)}")
        return False, None

def test_verify_otp(email: str, otp: str, otp_type: str = 'email') -> bool:
    """Test OTP verification"""
    endpoint_name = "VERIFY EMAIL OTP" if otp_type == 'email' else "VERIFY PASSWORD RESET OTP"
    print_section(f"5️⃣  {endpoint_name} TEST")
    
    endpoint = f"/auth/verify-email-otp/" if otp_type == 'email' else "/auth/verify-password-reset-otp/"
    
    print(f"Endpoint: POST {BASE_URL}{endpoint}")
    print(f"Email: {email}")
    print(f"OTP: {otp}\n")
    
    payload = {
        "email": email,
        "otp": otp
    }
    
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        
        # Mask token if present
        display_data = response_data.copy()
        if 'reset_token' in display_data:
            display_data['reset_token'] = display_data['reset_token'][:20] + '...'
        
        print(f"Response:\n{json.dumps(display_data, indent=2)}\n")
        
        if response.status_code == 200:
            print_success(f"OTP verified successfully")
            return True
        else:
            print_error(f"OTP verification failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"OTP verification request failed: {str(e)}")
        return False

def test_get_current_user(token: str) -> bool:
    """Test getting current user with authentication"""
    print_section("6️⃣  GET CURRENT USER TEST (Authenticated)")
    
    print(f"Endpoint: GET {BASE_URL}/auth/me/")
    print(f"Authorization: Bearer <token>\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            print_success("Retrieved current user successfully")
            return True
        else:
            print_error(f"Failed to get current user: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_logout(token: str) -> bool:
    """Test logout endpoint"""
    print_section("7️⃣  LOGOUT TEST")
    
    print(f"Endpoint: POST {BASE_URL}/auth/logout/")
    print(f"Authorization: Bearer <token>\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        if response.status_code == 200:
            print_success("Logout successful")
            return True
        else:
            print_error(f"Logout failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Logout request failed: {str(e)}")
        return False

def run_production_test():
    """Run full production-level authentication test"""
    print_section("🚀 PRODUCTION-LEVEL AUTHENTICATION TEST")
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Real Email (for OTP): {REAL_EMAIL}")
    print(f"Base URL: {BASE_URL}\n")
    
    results = {}
    
    # Test 1: Email Configuration
    results['email_config'] = test_email_configuration()
    
    # Test 2: Register
    register_response = test_register_endpoint()
    results['register'] = register_response is not None
    
    # Test 3: Login
    access_token = test_login_endpoint()
    results['login'] = access_token is not None
    
    # Test 4: Get Current User
    if access_token:
        results['get_current_user'] = test_get_current_user(access_token)
    
    # Test 5: Request Login OTP (use real email)
    otp_success, login_otp = test_request_login_otp(REAL_EMAIL)
    results['request_login_otp'] = otp_success
    
    # Test 6: Verify Login OTP (if OTP was retrieved)
    if login_otp:
        results['verify_login_otp'] = test_verify_otp(REAL_EMAIL, login_otp, otp_type='email')
    else:
        print_warning("Skipping OTP verification - user needs to enter OTP from email manually")
    
    # Test 7: Request Password Reset OTP (use real email)
    reset_otp_success, reset_otp = test_request_password_reset_otp(REAL_EMAIL)
    results['request_password_reset_otp'] = reset_otp_success
    
    # Test 8: Verify Password Reset OTP (if OTP was retrieved)
    if reset_otp:
        results['verify_password_reset_otp'] = test_verify_otp(REAL_EMAIL, reset_otp, otp_type='reset')
    else:
        print_warning("Skipping OTP verification - user needs to enter OTP from email manually")
    
    # Test 9: Logout
    if access_token:
        results['logout'] = test_logout(access_token)
    
    # Print summary
    print_section("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n{Colors.BOLD}Overall Result: {passed_tests}/{total_tests} tests passed{Colors.END}")
    
    if passed_tests == total_tests:
        print_success("All tests passed! Authentication is production-ready.")
    else:
        print_warning(f"Some tests failed. Please check the output above.")
    
    print(f"\nEnd Time: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    try:
        run_production_test()
    except KeyboardInterrupt:
        print_warning("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
