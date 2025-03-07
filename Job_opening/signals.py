# Job_opening/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicantResponse
from .tasks import parse_cv_keywords
import os

@receiver(post_save, sender=ApplicantResponse)
def parse_cv_on_save(sender, instance, created, **kwargs):
    """Trigger CV parsing in the background after ApplicantResponse is saved."""
    if created and instance.cv:  # Only run on creation, not updates
        cv_path = instance.cv.path
        if os.path.exists(cv_path):
            # Queue the task with Celery using the instance ID
            parse_cv_keywords.delay(instance.id)
        else:
            print(f"Warning: CV file not found at {cv_path} during signal")