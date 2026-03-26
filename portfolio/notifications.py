import os
import json
import logging
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

class PortfolioNotifier:
    """Complete notification system for portfolio"""
    
    @staticmethod
    def send_admin_email(contact_message):
        """Send email notification to admin"""
        subject = f"🔔 New Contact Form Submission: {contact_message.subject}"
        
        # Create HTML email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #333; }}
                .message {{ background: white; padding: 15px; border-left: 4px solid #007bff; margin-top: 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .badge {{ background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📬 New Contact Message</h2>
                    <p>You have received a new message from your portfolio website</p>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">👤 From:</div>
                        <div>{contact_message.name}</div>
                    </div>
                    <div class="field">
                        <div class="label">📧 Email:</div>
                        <div><a href="mailto:{contact_message.email}">{contact_message.email}</a></div>
                    </div>
                    <div class="field">
                        <div class="label">📝 Subject:</div>
                        <div><span class="badge">{contact_message.subject}</span></div>
                    </div>
                    <div class="field">
                        <div class="label">📅 Date:</div>
                        <div>{contact_message.created_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div class="field">
                        <div class="label">💬 Message:</div>
                        <div class="message">{contact_message.message.replace(chr(10), '<br>')}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>View this message in admin panel: <a href="{settings.BASE_DIR}/admin/portfolio/contactmessage/">Click here</a></p>
                    <p>This is an automated notification from your portfolio website.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        NEW CONTACT MESSAGE
        
        From: {contact_message.name}
        Email: {contact_message.email}
        Subject: {contact_message.subject}
        Date: {contact_message.created_date.strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {contact_message.message}
        
        View in admin: {settings.BASE_DIR}/admin/portfolio/contactmessage/
        """
        
        try:
            contact_email = getattr(settings, 'CONTACT_EMAIL', None)
            if contact_email:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact_email],
                    fail_silently=False,
                    html_message=html_message
                )
                logger.info(f"Email notification sent to {contact_email}")
                return True
            else:
                logger.warning("CONTACT_EMAIL not configured in settings")
                return False
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def log_to_file(contact_message):
        """Log notifications to a JSON file"""
        log_file = os.path.join(settings.BASE_DIR, 'notifications.log')
        
        log_entry = {
            'id': contact_message.id,
            'timestamp': datetime.now().isoformat(),
            'type': 'contact_form',
            'name': contact_message.name,
            'email': contact_message.email,
            'subject': contact_message.subject,
            'message_preview': contact_message.message[:100],
            'full_message': contact_message.message,
            'status': 'new'
        }
        
        try:
            # Read existing logs
            existing_logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            existing_logs.append(json.loads(line.strip()))
                        except:
                            continue
            
            # Append new log
            existing_logs.append(log_entry)
            
            # Write all logs back
            with open(log_file, 'w') as f:
                for log in existing_logs:
                    f.write(json.dumps(log) + '\n')
            
            logger.info(f"Notification logged to file: {log_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
            return False
    
    @staticmethod
    def send_slack_notification(contact_message):
        """Send notification to Slack (optional)"""
        import requests
        
        slack_webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
        if not slack_webhook_url:
            return False
        
        slack_message = {
            "text": f"📬 New Contact Message from {contact_message.name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Contact Message*\n*From:* {contact_message.name}\n*Email:* {contact_message.email}\n*Subject:* {contact_message.subject}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:*\n{contact_message.message[:200]}"
                    }
                }
            ]
        }
        
        try:
            response = requests.post(slack_webhook_url, json=slack_message)
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    @staticmethod
    def create_admin_notification(contact_message):
        """Create a notification record in the database (for admin panel)"""
        # This could be extended to create a custom Notification model
        # For now, just mark as unread
        contact_message.is_read = False
        contact_message.save()
        return True

class NotificationManager:
    """Manager class to handle all notifications"""
    
    def __init__(self, contact_message):
        self.contact_message = contact_message
        self.notifications_sent = []
    
    def send_all(self):
        """Send all configured notifications"""
        results = {
            'email': False,
            'file': False,
            'slack': False,
            'admin': False
        }
        
        # Send email notification
        if getattr(settings, 'SEND_EMAIL_NOTIFICATIONS', True):
            results['email'] = PortfolioNotifier.send_admin_email(self.contact_message)
            if results['email']:
                self.notifications_sent.append('email')
        
        # Log to file
        if getattr(settings, 'LOG_NOTIFICATIONS', True):
            results['file'] = PortfolioNotifier.log_to_file(self.contact_message)
            if results['file']:
                self.notifications_sent.append('file')
        
        # Send Slack notification
        if getattr(settings, 'SEND_SLACK_NOTIFICATIONS', False):
            results['slack'] = PortfolioNotifier.send_slack_notification(self.contact_message)
            if results['slack']:
                self.notifications_sent.append('slack')
        
        # Create admin notification
        results['admin'] = PortfolioNotifier.create_admin_notification(self.contact_message)
        if results['admin']:
            self.notifications_sent.append('admin')
        
        return results
    
    def get_summary(self):
        """Get summary of notifications sent"""
        return {
            'total': len(self.notifications_sent),
            'methods': self.notifications_sent,
            'message_id': self.contact_message.id
        }