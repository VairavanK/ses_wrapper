# src/ses_emailer/ses_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_ses_email(
    from_email,
    to_emails,
    subject,
    body_text,
    body_html=None,
    cc_emails=None,
    bcc_emails=None,
    attachments=None,
    smtp_username=None,
    smtp_password=None,
    smtp_host=None,
    smtp_port=587,
    region="ap-southeast-1"
):
    """
    Send email via Amazon SES SMTP (STARTTLS by default) with CC/BCC and attachments.
    Credentials default to env vars: SES_SMTP_USERNAME / SES_SMTP_PASSWORD.
    """
    smtp_username = smtp_username or os.environ.get('SES_SMTP_USERNAME')
    smtp_password = smtp_password or os.environ.get('SES_SMTP_PASSWORD')
    smtp_host = smtp_host or f"email-smtp.{region}.amazonaws.com"

    if not smtp_username or not smtp_password:
        return {
            'success': False,
            'message': 'SMTP credentials not provided',
            'error': 'smtp_username and smtp_password are required (or env variables)'
        }

    if isinstance(to_emails, str):
        to_emails = [to_emails]
    if cc_emails and isinstance(cc_emails, str):
        cc_emails = [cc_emails]
    if bcc_emails and isinstance(bcc_emails, str):
        bcc_emails = [bcc_emails]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)

    msg.attach(MIMEText(body_text, 'plain'))
    if body_html:
        msg.attach(MIMEText(body_html, 'html'))

    if attachments:
        for file_path in attachments:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': f'Attachment not found: {file_path}',
                    'error': f'File does not exist: {file_path}',
                }
            try:
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    f'attachment; filename={os.path.basename(file_path)}')
                    msg.attach(part)
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Error attaching file {file_path}',
                    'error': str(e),
                }

    all_recipients = list(to_emails)
    if cc_emails:
        all_recipients.extend(cc_emails)
    if bcc_emails:
        all_recipients.extend(bcc_emails)

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, all_recipients, msg.as_string())
        server.quit()
        return {
            'success': True,
            'message': f'Email sent successfully to {len(all_recipients)} recipient(s)',
            'recipients': all_recipients
        }
    except smtplib.SMTPAuthenticationError as e:
        return {
            'success': False,
            'message': 'SMTP authentication failed',
            'error': f'Invalid credentials or permissions: {str(e)}'
        }
    except smtplib.SMTPException as e:
        return {
            'success': False,
            'message': 'SMTP error occurred',
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'message': 'Unexpected error sending email',
            'error': str(e)
        }
