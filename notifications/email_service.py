"""
Email Notification Service

Handles sending emails for various approval workflows and notifications.
Supports HTML templates and clickable approval actions.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications
    Supports multiple templates for different notification types
    """
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', 587))
        self.sender_email = os.getenv('EMAIL_HOST_USER', 'noreply@example.com')
        self.sender_password = os.getenv('EMAIL_HOST_PASSWORD', '')
        self.app_url = os.getenv('APP_URL', 'http://localhost:8000')
    
    def send_approval_request_email(
        self,
        recipient_email: str,
        recipient_name: str,
        approver_name: str,
        document_title: str,
        document_type: str,
        approval_id: str,
        requester_name: str,
        priority: str = 'normal'
    ) -> bool:
        """
        Send approval request notification email
        
        Args:
            recipient_email: Approver's email
            recipient_name: Approver's name
            approver_name: Name of the approver
            document_title: Title of the document
            document_type: Type of document (contract, etc)
            approval_id: ID of the approval request
            requester_name: Name of person requesting approval
            priority: Priority level (normal, high, urgent)
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = f"🔔 Approval Request: {document_title}"
            
            # Create HTML email body with clickable action buttons
            html_body = self._get_approval_request_template(
                recipient_name=recipient_name,
                approver_name=approver_name,
                document_title=document_title,
                document_type=document_type,
                requester_name=requester_name,
                approval_id=approval_id,
                priority=priority
            )
            
            return self._send_email(
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                notification_type='approval_request'
            )
        except Exception as e:
            logger.error(f"Failed to send approval request email: {str(e)}")
            return False
    
    def send_approval_approved_email(
        self,
        recipient_email: str,
        recipient_name: str,
        document_title: str,
        approver_name: str,
        approval_comment: str = ""
    ) -> bool:
        """
        Send approval approved notification
        
        Args:
            recipient_email: Recipient's email
            recipient_name: Recipient's name
            document_title: Title of approved document
            approver_name: Name of approver
            approval_comment: Optional comment from approver
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = f"✅ Approval Approved: {document_title}"
            
            html_body = self._get_approval_approved_template(
                recipient_name=recipient_name,
                document_title=document_title,
                approver_name=approver_name,
                approval_comment=approval_comment
            )
            
            return self._send_email(
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                notification_type='approval_approved'
            )
        except Exception as e:
            logger.error(f"Failed to send approval approved email: {str(e)}")
            return False
    
    def send_approval_rejected_email(
        self,
        recipient_email: str,
        recipient_name: str,
        document_title: str,
        approver_name: str,
        rejection_reason: str = ""
    ) -> bool:
        """
        Send approval rejected notification
        
        Args:
            recipient_email: Recipient's email
            recipient_name: Recipient's name
            document_title: Title of rejected document
            approver_name: Name of approver
            rejection_reason: Reason for rejection
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = f"❌ Approval Rejected: {document_title}"
            
            html_body = self._get_approval_rejected_template(
                recipient_name=recipient_name,
                document_title=document_title,
                approver_name=approver_name,
                rejection_reason=rejection_reason
            )
            
            return self._send_email(
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                notification_type='approval_rejected'
            )
        except Exception as e:
            logger.error(f"Failed to send approval rejected email: {str(e)}")
            return False
    
    def _send_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        notification_type: str = 'general'
    ) -> bool:
        """
        Internal method to send email via SMTP
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            html_body: HTML email body
            notification_type: Type of notification
        
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['X-Notification-Type'] = notification_type
            msg['X-Timestamp'] = datetime.now().isoformat()
            
            # Attach HTML body
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.sender_password:
                    server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _get_approval_request_template(
        self,
        recipient_name: str,
        approver_name: str,
        document_title: str,
        document_type: str,
        requester_name: str,
        approval_id: str,
        priority: str
    ) -> str:
        """Generate HTML template for approval request email"""
        
        priority_color = {
            'urgent': '#dc3545',
            'high': '#fd7e14',
            'normal': '#0056b3'
        }.get(priority, '#0056b3')
        
        approve_url = f"{self.app_url}/approvals/{approval_id}/approve"
        reject_url = f"{self.app_url}/approvals/{approval_id}/reject"
        view_url = f"{self.app_url}/approvals/{approval_id}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                    margin-bottom: 20px;
                }}
                .priority-badge {{
                    display: inline-block;
                    background-color: {priority_color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    text-transform: uppercase;
                    font-size: 12px;
                }}
                .info-box {{
                    background-color: #f0f0f0;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box strong {{
                    color: #667eea;
                }}
                .action-buttons {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 0 10px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 14px;
                    transition: all 0.3s ease;
                }}
                .btn-approve {{
                    background-color: #28a745;
                    color: white;
                }}
                .btn-approve:hover {{
                    background-color: #218838;
                    text-decoration: none;
                }}
                .btn-reject {{
                    background-color: #dc3545;
                    color: white;
                }}
                .btn-reject:hover {{
                    background-color: #c82333;
                    text-decoration: none;
                }}
                .btn-view {{
                    background-color: #0056b3;
                    color: white;
                }}
                .btn-view:hover {{
                    background-color: #004085;
                    text-decoration: none;
                }}
                .footer {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-radius: 4px;
                }}
                .document-details {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                .document-details tr {{
                    border-bottom: 1px solid #ddd;
                }}
                .document-details td {{
                    padding: 12px;
                }}
                .document-details td:first-child {{
                    font-weight: bold;
                    color: #667eea;
                    width: 30%;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Approval Request</h1>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{recipient_name}</strong>,</p>
                    
                    <p>You have received a new approval request from <strong>{requester_name}</strong>.</p>
                    
                    <div class="priority-badge">Priority: {priority.upper()}</div>
                    
                    <div class="info-box">
                        <strong>Document Details:</strong>
                        <table class="document-details">
                            <tr>
                                <td>Document Type:</td>
                                <td>{document_type}</td>
                            </tr>
                            <tr>
                                <td>Document Title:</td>
                                <td><strong>{document_title}</strong></td>
                            </tr>
                            <tr>
                                <td>Requested By:</td>
                                <td>{requester_name}</td>
                            </tr>
                            <tr>
                                <td>Request Date:</td>
                                <td>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>Please review the document and take action:</p>
                    
                    <div class="action-buttons">
                        <a href="{approve_url}" class="btn btn-approve">✓ APPROVE</a>
                        <a href="{reject_url}" class="btn btn-reject">✗ REJECT</a>
                        <a href="{view_url}" class="btn btn-view">📄 VIEW DETAILS</a>
                    </div>
                    
                    <p style="color: #666; font-size: 13px; margin-top: 30px;">
                        <strong>Note:</strong> You can also approve or reject this request directly by clicking the buttons above. 
                        No login required for quick actions.
                    </p>
                </div>
                
                <div class="footer">
                    <p>© 2026 Contract Lifecycle Management System</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                    <p>Request ID: {approval_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _get_approval_approved_template(
        self,
        recipient_name: str,
        document_title: str,
        approver_name: str,
        approval_comment: str
    ) -> str:
        """Generate HTML template for approval approved email"""
        
        view_url = f"{self.app_url}/documents/view"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .header {{
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                    margin-bottom: 20px;
                }}
                .success-message {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #155724;
                }}
                .info-box {{
                    background-color: #f0f0f0;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box strong {{
                    color: #28a745;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 20px 0;
                    background-color: #28a745;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .action-button:hover {{
                    background-color: #218838;
                    text-decoration: none;
                }}
                .footer {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Approval Approved</h1>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{recipient_name}</strong>,</p>
                    
                    <div class="success-message">
                        <strong>Good News!</strong> Your document "<strong>{document_title}</strong>" 
                        has been approved by <strong>{approver_name}</strong>.
                    </div>
                    
                    <div class="info-box">
                        <p><strong>Document:</strong> {document_title}</p>
                        <p><strong>Approved By:</strong> {approver_name}</p>
                        <p><strong>Approval Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        {f'<p><strong>Comment:</strong> {approval_comment}</p>' if approval_comment else ''}
                    </div>
                    
                    <p>Your document has successfully passed the approval stage and is now ready for the next steps.</p>
                    
                    <center>
                        <a href="{view_url}" class="action-button">📄 View Document</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>© 2026 Contract Lifecycle Management System</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _get_approval_rejected_template(
        self,
        recipient_name: str,
        document_title: str,
        approver_name: str,
        rejection_reason: str
    ) -> str:
        """Generate HTML template for approval rejected email"""
        
        resubmit_url = f"{self.app_url}/documents/revise"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .header {{
                    background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                    margin-bottom: 20px;
                }}
                .rejection-message {{
                    background-color: #f8d7da;
                    border-left: 4px solid #dc3545;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #721c24;
                }}
                .reason-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #fd7e14;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .reason-box strong {{
                    color: #856404;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 20px 0;
                    background-color: #fd7e14;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .action-button:hover {{
                    background-color: #e0670b;
                    text-decoration: none;
                }}
                .footer {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Approval Rejected</h1>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{recipient_name}</strong>,</p>
                    
                    <div class="rejection-message">
                        <strong>Action Required</strong> - Your document "<strong>{document_title}</strong>" 
                        has been rejected by <strong>{approver_name}</strong>.
                    </div>
                    
                    {f'''
                    <div class="reason-box">
                        <strong>Reason for Rejection:</strong>
                        <p>{rejection_reason}</p>
                    </div>
                    ''' if rejection_reason else ''}
                    
                    <p>Please review the feedback above and make the necessary revisions to your document. 
                    Once you've made the changes, you can resubmit it for approval.</p>
                    
                    <center>
                        <a href="{resubmit_url}" class="action-button">📝 Revise & Resubmit</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>© 2026 Contract Lifecycle Management System</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
