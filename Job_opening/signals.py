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

        # Trigger Celery task
        send_application_email.delay(applicant_name, applicant_email, job_title, score, benchmark)
        logger.debug(f"Queued email task for {applicant_email}")