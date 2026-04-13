from app.tools.base import BaseTool
from app.config import settings
from typing import Any, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class EmailTool(BaseTool):
    name = "send_email"
    description = "Send an email to a recipient. Can draft emails, send emails with attachments, and handle email composition."
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "to_email": {
                "type": "string",
                "description": "Recipient email address"
            },
            "subject": {
                "type": "string",
                "description": "Email subject line"
            },
            "body": {
                "type": "string",
                "description": "Email body content"
            },
            "html": {
                "type": "string",
                "description": "HTML version of email body (optional)"
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["to_email", "subject", "body"]
    
    async def execute(self, to_email: str, subject: str, body: str, html: str = None, **kwargs) -> Dict[str, Any]:
        """
        Send email via SMTP
        """
        try:
            if not settings.EMAIL_ADDRESS or not settings.EMAIL_PASSWORD:
                return {
                    "success": False,
                    "message": "Email credentials not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env",
                    "draft": {
                        "to": to_email,
                        "subject": subject,
                        "body": body
                    }
                }
            
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # HTML version (if provided)
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            # Send email
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }
