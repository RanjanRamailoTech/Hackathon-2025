from .utils import Util
import logging
from call.models import Interview
from django.conf import settings


logger = logging.getLogger(__name__)


def send_application_email(applicant_name, applicant_email, job_title, job_id, score, benchmark, applicant_id, request_host):
    """Send an acceptance or rejection email based on applicant's score."""
    if not applicant_email or not isinstance(applicant_email, str):
        logger.error(f"Invalid email address for {applicant_name}: {applicant_email}")
        return
    interview_id = None
    if score >= benchmark:
        subject = f"Acceptance: Application for {job_title}"
        interview = Interview.objects.create(
            applicant_job_pipeline_id_id=applicant_id,
            status="Pending"
        )
        interview_id = interview.id
        interview_url = f"{settings.FRONTEND_HOST}?job_id={job_id}&interview_id={interview_id}"
        message = (
            f"Dear {applicant_name},\n\n"
            f"Congratulations! We are pleased to inform you that your application for the {job_title} position "
            f"has been accepted. \n\n"
            f"Please proceed with your interview by clicking the following link:\n"
            f"{interview_url}\n\n"
            f"Best regards,\nThe Hiring Team"
        )
    else:
        subject = f"Rejection: Application for {job_title}"
        message = (
            f"Dear {applicant_name},\n\n"
            f"Thank you for applying for the {job_title} position. Unfortunately, your profile "
            f"was not well aligned for this job, and we will not be moving forward with your application.\n\n"
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
        return {"interview_id": interview_id} if interview_id else None
    except Exception as e:
        logger.error(f"Failed to send email to {applicant_email}: {str(e)}")