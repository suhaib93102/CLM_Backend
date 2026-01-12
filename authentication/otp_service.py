import os
import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class OTPService:
    """Service for managing OTP generation and email sending"""
    
    OTP_LENGTH = 6
    OTP_VALIDITY_MINUTES = 10
    MAX_ATTEMPTS = 5
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(OTPService.OTP_LENGTH))
    
    @staticmethod
    def send_login_otp(user, otp):
        """Send OTP for login via email"""
        try:
            subject = "Your CLM Login OTP"
            message = f"""
            Hello {user.first_name or user.email},
            
            Your one-time password (OTP) for CLM login is:
            
            {otp}
            
            This OTP is valid for {OTPService.OTP_VALIDITY_MINUTES} minutes.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            CLM Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending login OTP: {e}")
            return False
    
    @staticmethod
    def send_password_reset_otp(user, otp):
        """Send OTP for password reset via email"""
        try:
            subject = "Your CLM Password Reset OTP"
            message = f"""
            Hello {user.first_name or user.email},
            
            Your one-time password (OTP) for password reset is:
            
            {otp}
            
            This OTP is valid for {OTPService.OTP_VALIDITY_MINUTES} minutes.
            
            If you didn't request this, please ignore this email and your password will remain unchanged.
            
            Best regards,
            CLM Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending password reset OTP: {e}")
            return False
    
    @staticmethod
    def verify_otp(user, otp, otp_type='login'):
        """Verify OTP with expiry and attempt checks"""
        if otp_type == 'login':
            stored_otp = user.login_otp
        else:
            stored_otp = user.password_reset_otp
        
        # Check if OTP is set
        if not stored_otp:
            return False, "OTP not requested"
        
        # Check OTP attempts
        if user.otp_attempts >= OTPService.MAX_ATTEMPTS:
            return False, "Too many attempts. Please request a new OTP"
        
        # Check OTP expiry
        if user.otp_created_at:
            expiry_time = user.otp_created_at + timedelta(minutes=OTPService.OTP_VALIDITY_MINUTES)
            if timezone.now() > expiry_time:
                return False, "OTP has expired"
        
        # Verify OTP
        if str(stored_otp) != str(otp).strip():
            user.otp_attempts += 1
            user.save(update_fields=['otp_attempts'])
            return False, f"Invalid OTP ({OTPService.MAX_ATTEMPTS - user.otp_attempts} attempts remaining)"
        
        return True, "OTP verified successfully"
    
    @staticmethod
    def clear_otp(user, otp_type='login'):
        """Clear OTP after successful verification"""
        if otp_type == 'login':
            user.login_otp = None
        else:
            user.password_reset_otp = None
        user.otp_attempts = 0
        user.save(update_fields=[f'{otp_type}_otp', 'otp_attempts'])
