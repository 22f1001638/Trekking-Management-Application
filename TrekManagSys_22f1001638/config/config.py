import os


class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///trek.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret')

    # SMTP configuration for email delivery
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@trekmanager.local')

    # Twilio configuration for SMS delivery
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')

    # Webhook delivery
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')

    # Admin email delivery
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')