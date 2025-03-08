# Job_opening/tasks.py
from celery import shared_task
from .utils import Util  # Adjust import based on your structure
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_application_email(applicant_name, applicant_email, job_title, score, benchmark):
    if not applicant_email or not isinstance(applicant_email, str):
        logger.error(f"Invalid email address for {applicant_name}: {applicant_email}")
        return

    if score >= benchmark:
        subject = f"Acceptance: Application for {job_title}"
        message = (
            f"Dear {applicant_name},\n\n"
            f"Congratulations! We are pleased to inform you that your application for the {job_title} position "
            f"has been accepted. Your score of {score} meets or exceeds our benchmark of {benchmark}.\n\n"
            f"We will contact you soon with next steps.\n\n"
            f"Best regards,\nThe Hiring Team"
        )
    else:
        subject = f"Rejection: Application for {job_title}"
        message = (
            f"Dear {applicant_name},\n\n"
            f"Thank you for applying for the {job_title} position. Unfortunately, your score of {score} "
            f"did not meet our benchmark of {benchmark}, and we will not be moving forward with your application.\n\n"
            f"We appreciate your interest and wish you the best in your job search.\n\n"
            f"Best regards,\nThe Hiring Team"
        )

    email_data = {
        'email_subject': subject,
        'email_body': message,
        'to_email': applicant_email
    }
    try:
        Util.send_email(email_data)
        logger.info(f"Email sent to {applicant_email} for {job_title}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {applicant_email}: {str(e)}")