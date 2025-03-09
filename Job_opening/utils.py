"""
Simple Text Email Python Script
"""
from dotenv import load_dotenv
import smtplib
import ssl
import os
from django.conf import settings

class GetEnv:
    def load_email_config():
        return settings.EMAIL_USERNAME, settings.EMAIL_APP_PASSWORD


class Util:
    @staticmethod
    def send_email(data):
        
        # Setup port number and servr name
        smtp_port = 587                 # Standard secure SMTP port
        smtp_server = "smtp.gmail.com"  # Google SMTP Server

        email_from, app_password = GetEnv.load_email_config()
        print(email_from)
        print(app_password)
        simple_email_context = ssl.create_default_context()
        
        subject = data['email_subject']
        body = data['email_body']
        email_to = data['to_email']
        message = f"Subject: {subject}\n\n{body}"
        

        try:
            # Connect to the server
            print("Connecting to server...")
            TIE_server = smtplib.SMTP(smtp_server, smtp_port)
            TIE_server.starttls(context=simple_email_context)
            TIE_server.login(email_from, app_password)
            print("Connected to server :-)")
            
            # Send the actual email
            print(f"Sending email to - {email_to}")
            TIE_server.sendmail(email_from, email_to,message.encode('utf-8'))
            print(f"Email successfully sent to - {email_to}")

        # If there's an error, print it out
        except Exception as e:
            print(e)

        # Close the port
        finally:
            TIE_server.quit()


