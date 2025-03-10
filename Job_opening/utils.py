import smtplib
import ssl
from django.conf import settings


class GetEnv:
    """Utility class to load email configuration from settings."""
    @staticmethod
    def load_email_config():
        """Load email configuration from Django settings.

        Returns:
            tuple: A tuple containing the email username and app password.
        """
        return settings.EMAIL_USERNAME, settings.EMAIL_APP_PASSWORD


class Util:
    """Utility class for sending emails."""
    @staticmethod
    def send_email(data):
        """Send an email using SMTP with SSL encryption.

        Args:
            data (dict): A dictionary containing email details with keys:
                - email_subject (str): The subject of the email.
                - email_body (str): The body of the email.
                - to_email (str): The recipient's email address.

        Raises:
            Exception: If the email fails to send, the exception is raised and handled by the caller.
        """
        smtp_port = 587
        smtp_server = "smtp.gmail.com"
        email_from, app_password = GetEnv.load_email_config()
        simple_email_context = ssl.create_default_context()

        subject = data['email_subject']
        body = data['email_body']
        email_to = data['to_email']
        message = f"Subject: {subject}\n\n{body}"

        try:
            TIE_server = smtplib.SMTP(smtp_server, smtp_port)
            TIE_server.starttls(context=simple_email_context)
            TIE_server.login(email_from, app_password)
            TIE_server.sendmail(email_from, email_to, message.encode('utf-8'))
        finally:
            TIE_server.quit()