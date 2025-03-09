# Job_opening/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicantResponse
from .tasks import send_application_email  # Import the task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ApplicantResponse)
def send_application_response_email(sender, instance, created, **kwargs):
    if created:
        job = instance.jobId
        applicant_email = instance.email
        applicant_name = instance.name
        job_title = job.title
        benchmark = job.benchmark
        score = instance.score
        applicant_id = instance.id

        logger.debug(f"Preparing email for {applicant_name} at {applicant_email}")

        if not applicant_email or not isinstance(applicant_email, str):
            logger.error(f"Invalid email address for {applicant_name}: {applicant_email}")
            instance.status = "New"
            instance.save(update_fields=['status'])
            return

        if score >= benchmark:
            instance.status = "In Progress"
        else:
            instance.status = "Rejected"
        instance.save(update_fields=['status'])

        # Get request host (assuming signal has access to request context; otherwise, pass via view)
        request = kwargs.get('request', None)  # This won't work directly in signals; we'll fix via view
        request_host = request.get_host() if request else "127.0.0.1:8000"  # Fallback
        
        # Trigger Celery task
        send_application_email.delay(applicant_name, applicant_email, job_title, score, benchmark, applicant_id, request_host)
        logger.debug(f"Queued email task for {applicant_email}")