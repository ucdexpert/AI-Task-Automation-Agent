"""
Email service - Send email notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str, html: bool = False) -> bool:
    """Send an email notification"""
    if not settings.EMAIL_ADDRESS or not settings.EMAIL_PASSWORD:
        logger.warning("Email credentials not configured, skipping email send")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        content = MIMEText(body, 'html' if html else 'plain')
        msg.attach(content)

        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        
        # Send email
        server.sendmail(settings.EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()

        logger.info(f"✅ Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False


def send_task_completion_email(to_email: str, user_name: str, task_description: str, status: str, task_id: int):
    """Send task completion notification email"""
    subject = f"Task {'Completed' if status == 'completed' else 'Failed'}: {task_description[:50]}..."
    
    status_emoji = "✅" if status == "completed" else "❌"
    status_color = "#22C55E" if status == "completed" else "#EF4444"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1A1D27; border-radius: 12px; padding: 24px; border: 1px solid rgba(255,255,255,0.08);">
            <h1 style="color: #F1F5F9; margin-top: 0;">
                {status_emoji} Task {status.title()}
            </h1>
            <p style="color: #64748B;">Hi {user_name},</p>
            <p style="color: #F1F5F9;">Your task has been processed:</p>
            
            <div style="background: #0F1117; padding: 16px; border-radius: 8px; margin: 16px 0;">
                <p style="color: #F1F5F9; font-weight: bold; margin: 0 0 8px 0;">Task Description:</p>
                <p style="color: #94A3B8; margin: 0;">{task_description}</p>
            </div>
            
            <div style="margin: 16px 0;">
                <span style="background: {status_color}; color: white; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;">
                    {status.upper()}
                </span>
            </div>
            
            <p style="color: #64748B; font-size: 14px;">
                View full details in your dashboard.
            </p>
            
            <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 24px 0;">
            <p style="color: #64748B; font-size: 12px; margin: 0;">
                AI Task Automation Agent
            </p>
        </div>
    </body>
    </html>
    """
    
    send_email(to_email, subject, html_body, html=True)
