import os
import smtplib
from email.message import EmailMessage
from flask import current_app
import requests

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None


def _send_email(to_address, subject, body, html=None):
    config = current_app.config
    smtp_server = config.get('SMTP_SERVER')
    smtp_port = config.get('SMTP_PORT', 587)
    smtp_username = config.get('SMTP_USERNAME')
    smtp_password = config.get('SMTP_PASSWORD')
    mail_from = config.get('MAIL_FROM', 'noreply@trekmanager.local')

    if not smtp_server:
        current_app.logger.warning('SMTP_SERVER is not configured; skipping email to %s', to_address)
        return False

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = mail_from
    message['To'] = to_address
    message.set_content(body)
    if html:
        message.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            if smtp_username and smtp_password:
                smtp.starttls()
                smtp.login(smtp_username, smtp_password)
            smtp.send_message(message)
        current_app.logger.info('Sent email to %s', to_address)
        return True
    except Exception as exc:
        current_app.logger.error('Failed to send email to %s: %s', to_address, exc)
        return False


def _send_sms(to_number, text):
    config = current_app.config
    account_sid = config.get('TWILIO_ACCOUNT_SID')
    auth_token = config.get('TWILIO_AUTH_TOKEN')
    from_number = config.get('TWILIO_FROM_NUMBER')

    if not TwilioClient or not account_sid or not auth_token or not from_number:
        current_app.logger.warning('Twilio is not configured; skipping SMS to %s', to_number)
        return False

    try:
        client = TwilioClient(account_sid, auth_token)
        client.messages.create(body=text, from_=from_number, to=to_number)
        current_app.logger.info('Sent SMS to %s', to_number)
        return True
    except Exception as exc:
        current_app.logger.error('Failed to send SMS to %s: %s', to_number, exc)
        return False


def _send_webhook(text, url=None):
    config = current_app.config
    webhook_url = url or config.get('GOOGLE_CHAT_WEBHOOK_URL')
    if not webhook_url:
        current_app.logger.warning('No webhook URL configured; skipping webhook notification')
        return False

    payload = {
        'text': text
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        response.raise_for_status()
        current_app.logger.info('Sent webhook notification to %s', webhook_url)
        return True
    except Exception as exc:
        current_app.logger.error('Failed to send webhook notification to %s: %s', webhook_url, exc)
        return False


def notify_user(user, subject, body, html=None):
    sent = False
    if user.email_id:
        sent = _send_email(user.email_id, subject, body, html) or sent

    if user.phone_num:
        sms_body = f'{subject}\n\n{body}'
        sent = _send_sms(user.phone_num, sms_body) or sent

    if current_app.config.get('GOOGLE_CHAT_WEBHOOK_URL'):
        webhook_body = f'{subject}\n\n{body}'
        sent = _send_webhook(webhook_body) or sent

    if not sent:
        current_app.logger.warning('No notification channel succeeded for user %s', user.user_id)
    return sent


def notify_admin(subject, body, html=None):
    config = current_app.config
    admin_email = config.get('ADMIN_EMAIL')
    sent = False

    if admin_email:
        sent = _send_email(admin_email, subject, body, html) or sent

    if config.get('GOOGLE_CHAT_WEBHOOK_URL'):
        webhook_body = f'{subject}\n\n{body}'
        sent = _send_webhook(webhook_body) or sent

    if not sent:
        current_app.logger.warning('No notification channel succeeded for admin alerts')
    return sent
