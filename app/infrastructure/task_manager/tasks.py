import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.infrastructure.config import settings
from app.infrastructure.celery_settings import app

def send_email(receiver_email, subject, body):

    message = MIMEMultipart()
    message['From'] = settings.email_username
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(settings.email_host, settings.email_port) as server:
        server.login(settings.email_username, settings.email_password)
        server.sendmail(settings.email_username, receiver_email, message.as_string())


@app.task
def send_registration_email(user_email):
    subject = "Регистрация успешна"
    body = "Добро пожаловать! Спасибо за регистрацию на нашем сайте."
    send_email(user_email, subject, body)
