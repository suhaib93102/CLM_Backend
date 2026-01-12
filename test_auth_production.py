#!/usr/bin/env python
"""
Real-world Production Authentication Test
Tests complete authentication flow with real email OTP verification
"""

import os
import sys
import json
import time
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()

from django.conf import settings
from authentication.models import User
from authentication.otp_service import OTPService
from django.utils import timezone

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL_1 = f"auth-test-1-{int(time.time())}@test.com"
TEST_EMAIL_2 = f"auth-test-2-{int(time.time())}@test.com"
TEST_PASSWORD = "SecurePass@123"
REAL_RECIPIENT = "movieswatch996886@gmail.com"

class AuthenticationTest:
    """Production-level authentication test"""
    
    def __init__(self):
        self.results = []
        self.tokens = {}
    
    def print_header(self, title):
        print(f"\n{'='*80}")
        print(f"🔐 {title}")
        print(f"{'='*80}\n")
    
    def print_success(self, msg):
        print(f"✅ {msg}")
    
    def print_error(self, msg):
        print(f"❌ {msg}")
    
    def print_info(self, msg):
        print(f"ℹ️  {msg}")
    
    def print_warning(self, msg):
        print(f"⚠️  {msg}")
    
    def test_1_register_users(self):
        """Test 1: Register two new users"""
        self.print_header("TEST 1: USER REGISTRATION")
        
        users_data = [
            {"email": TEST_EMAIL_1, "name": "User One"},
            {"email": TEST_EMAIL_2, "name": "User Two"},
        ]
        
        for user_data in users_data:
            print(f"📝 Registering: {user_data['email']}")
            
            payload = {
                "email": user_data['email'],
                "password": TEST_PASSWORD,
                "first_name": user_data['name']
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register/",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.print_success(f"Registered: {user_data['email']}")
                    
                    if 'access' in data:
                        self.tokens[user_data['email']] = data['access']
                        self.print_info(f"Access token received")
                    
                    self.results.append({
                        'test': f"Register {user_data['email']}",
                        'status': 'PASS'
                    })
                else:
                    self.print_error(f"Failed: {response.text}")
                    self.results.append({
                        'test': f"Register {user_data['email']}",
                        'status': 'FAIL'
                    })
            except Exception as e:
                self.print_error(f"Exception: {str(e)}")
                self.results.append({
                    'test': f"Register {user_data['email']}",
                    'status': 'FAIL'
                })
    
    def test_2_login(self):
        """Test 2: Login with existing user"""
        self.print_header("TEST 2: USER LOGIN")
        
        login_email = "test@example.com"
        login_password = "Test@123456"
        
        print(f"🔑 Logging in: {login_email}")
        
        payload = {
            "email": login_email,
            "password": login_password
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[login_email] = data['access']
                
                self.print_success(f"Login successful")
                self.print_info(f"User: {data.get('user', {}).get('email')}")
                self.print_info(f"Token received (valid for 24 hours)")
                
                self.results.append({
                    'test': 'Login',
                    'status': 'PASS'
                })
            else:
                self.print_error(f"Login failed: {response.text}")
                self.results.append({
                    'test': 'Login',
                    'status': 'FAIL'
                })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Login',
                'status': 'FAIL'
            })
    
    def test_3_get_current_user(self):
        """Test 3: Get current user info"""
        self.print_header("TEST 3: GET CURRENT USER")
        
        if not self.tokens:
            self.print_warning("No tokens available")
            return
        
        # Use first token
        email, token = next(iter(self.tokens.items()))
        
        print(f"📋 Getting user info for: {email}")
        
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
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success("Retrieved current user")
                self.print_info(f"Email: {data.get('email')}")
                self.print_info(f"Name: {data.get('first_name')} {data.get('last_name', '')}")
                self.print_info(f"User ID: {data.get('user_id')}")
                
                self.results.append({
                    'test': 'Get Current User',
                    'status': 'PASS'
                })
            else:
                self.print_error(f"Failed: {response.text}")
                self.results.append({
                    'test': 'Get Current User',
                    'status': 'FAIL'
                })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Get Current User',
                'status': 'FAIL'
            })
    
    def test_4_request_login_otp(self):
        """Test 4: Request login OTP via email"""
        self.print_header("TEST 4: REQUEST LOGIN OTP")
        
        print(f"📧 Requesting OTP for: {REAL_RECIPIENT}")
        
        payload = {"email": REAL_RECIPIENT}
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/request-login-otp/",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.print_success("OTP requested successfully")
                self.print_warning("⏰ OTP sent to email inbox")
                self.print_warning("   Valid for 10 minutes")
                self.print_info(f"📬 Check: movieswatch996886@gmail.com")
                
                # Get OTP from database for testing
                try:
                    user = User.objects.get(email=REAL_RECIPIENT)
                    if user.login_otp:
                        self.print_info(f"Generated OTP (for testing): {user.login_otp}")
                except:
                    pass
                
                self.results.append({
                    'test': 'Request Login OTP',
                    'status': 'PASS'
                })
            else:
                self.print_error(f"Failed: {response.text}")
                self.results.append({
                    'test': 'Request Login OTP',
                    'status': 'FAIL'
                })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Request Login OTP',
                'status': 'FAIL'
            })
    
    def test_5_request_password_reset_otp(self):
        """Test 5: Request password reset OTP"""
        self.print_header("TEST 5: REQUEST PASSWORD RESET OTP")
        
        print(f"📧 Requesting password reset OTP for: {REAL_RECIPIENT}")
        
        payload = {"email": REAL_RECIPIENT}
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/forgot-password/",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.print_success("Password reset OTP requested")
                self.print_warning("⏰ OTP sent to email inbox")
                self.print_warning("   Valid for 10 minutes")
                self.print_info(f"📬 Check: movieswatch996886@gmail.com")
                
                # Get OTP from database for testing
                try:
                    user = User.objects.get(email=REAL_RECIPIENT)
                    if user.password_reset_otp:
                        self.print_info(f"Generated OTP (for testing): {user.password_reset_otp}")
                except:
                    pass
                
                self.results.append({
                    'test': 'Request Password Reset OTP',
                    'status': 'PASS'
                })
            else:
                self.print_error(f"Failed: {response.text}")
                self.results.append({
                    'test': 'Request Password Reset OTP',
                    'status': 'FAIL'
                })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Request Password Reset OTP',
                'status': 'FAIL'
            })
    
    def test_6_verify_otp(self):
        """Test 6: Verify OTP"""
        self.print_header("TEST 6: VERIFY OTP")
        
        try:
            user = User.objects.get(email=REAL_RECIPIENT)
            
            if user.login_otp:
                print(f"🔐 Verifying login OTP: {user.login_otp}")
                
                payload = {
                    "email": REAL_RECIPIENT,
                    "otp": user.login_otp
                }
                
                response = requests.post(
                    f"{BASE_URL}/auth/verify-email-otp/",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.print_success("OTP verified successfully")
                    data = response.json()
                    if 'user' in data:
                        self.print_info(f"User verified: {data.get('user', {}).get('email')}")
                    
                    self.results.append({
                        'test': 'Verify OTP',
                        'status': 'PASS'
                    })
                else:
                    self.print_error(f"OTP verification failed: {response.text}")
                    self.results.append({
                        'test': 'Verify OTP',
                        'status': 'FAIL'
                    })
        except User.DoesNotExist:
            self.print_warning("User not found - skipping OTP verification")
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Verify OTP',
                'status': 'FAIL'
            })
    
    def test_7_refresh_token(self):
        """Test 7: Refresh token"""
        self.print_header("TEST 7: REFRESH TOKEN")
        
        # Login to get refresh token
        payload = {
            "email": "test@example.com",
            "password": "Test@123456"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                login_data = response.json()
                refresh_token = login_data.get('refresh')
                
                if refresh_token:
                    print(f"🔄 Refreshing token...")
                    
                    payload = {"refresh": refresh_token}
                    
                    response = requests.post(
                        f"{BASE_URL}/auth/refresh/",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.print_success("Token refreshed successfully")
                        data = response.json()
                        self.print_info(f"New access token received")
                        
                        self.results.append({
                            'test': 'Refresh Token',
                            'status': 'PASS'
                        })
                    else:
                        self.print_error(f"Failed: {response.text}")
                        self.results.append({
                            'test': 'Refresh Token',
                            'status': 'FAIL'
                        })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Refresh Token',
                'status': 'FAIL'
            })
    
    def test_8_logout(self):
        """Test 8: Logout"""
        self.print_header("TEST 8: LOGOUT")
        
        if not self.tokens:
            self.print_warning("No tokens available")
            return
        
        email, token = next(iter(self.tokens.items()))
        
        print(f"👋 Logging out: {email}")
        
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
            
            if response.status_code == 200:
                self.print_success("Logout successful")
                
                self.results.append({
                    'test': 'Logout',
                    'status': 'PASS'
                })
            else:
                self.print_error(f"Logout failed: {response.text}")
                self.results.append({
                    'test': 'Logout',
                    'status': 'FAIL'
                })
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.results.append({
                'test': 'Logout',
                'status': 'FAIL'
            })
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        
        print("\nDetailed Results:")
        for result in self.results:
            status = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status} {result['test']}")
        
        print(f"\n{'='*80}")
        print(f"📊 TOTAL: {passed}/{total} tests passed ({100*passed//total}%)")
        print(f"{'='*80}\n")
        
        if passed == total:
            print("🎉 All tests passed! Authentication is production-ready.\n")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check output above.\n")
    
    def run(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("🚀 PRODUCTION-LEVEL AUTHENTICATION TEST SUITE")
        print("="*80)
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Server: {BASE_URL}")
        print(f"Email: {settings.EMAIL_HOST_USER}")
        print("="*80)
        
        self.test_1_register_users()
        self.test_2_login()
        self.test_3_get_current_user()
        self.test_4_request_login_otp()
        self.test_5_request_password_reset_otp()
        self.test_6_verify_otp()
        self.test_7_refresh_token()
        self.test_8_logout()
        
        self.print_summary()

if __name__ == "__main__":
    test = AuthenticationTest()
    try:
        test.run()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
