from django.db import models
import uuid
from client_auth.models import Company
import os
from django.conf import settings


def cv_upload_path(instance, filename):
    """Generate a structured path for CV uploads."""
    # Job opening ID as the base directory
    job_dir = f"Job_{instance.job_opening_id}"
    # Applicant ID as the filename (assuming ID is available at save time)
    filename = f"cv_{instance.id or 'temp'}.pdf"  # Use 'temp' if ID isn’t set yet
    return os.path.join('cvs', job_dir, filename)


class JobOpening(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    form_url = models.CharField(max_length=255, blank=True, null=True)  # Generated later
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    def __str__(self):
        return f"{self.title} - {self.company.name}"


class FormField(models.Model):
    FIELD_TYPES = (
        ("text", "Text"),
        ("email", "Email"),
        ("number", "Number"),
        ("choice", "Choice"),
    )
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="form_fields")
    question = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=True)
    options = models.JSONField(blank=True, null=True)  # For choice fields, e.g., ["Option1", "Option2"]

    def __str__(self):
        return f"{self.question} ({self.job_opening.title})"
    
    
class ApplicantResponse(models.Model):
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="responses")
    applicant_id = models.UUIDField(default=uuid.uuid4, editable=False)
    email_address = models.EmailField()  # New fixed field
    name = models.CharField(max_length=255)  # New fixed field
    gender = models.CharField(max_length=10, choices=(("male", "Male"), ("female", "Female")))
    country = models.CharField(max_length=100)  # New fixed field
    phone_number = models.CharField(max_length=20)  # New fixed field
    responses = models.JSONField()  # Custom form field responses
    cv = models.FileField(upload_to=cv_upload_path, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.job_opening.title} - {self.applicant_id}"
    
    def save(self, *args, **kwargs):
        # If this is a new instance, save first to get an ID, then rename the file
        if not self.id:
            super().save(*args, **kwargs)  # Save to generate ID
            if self.cv and 'temp' in self.cv.name:
                old_path = self.cv.path
                new_name = f"cv_{self.id}.pdf"
                new_path = os.path.join(settings.MEDIA_ROOT, 'cvs', f"Job_{self.job_opening_id}", new_name)
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                os.rename(old_path, new_path)
                self.cv.name = os.path.join('cvs', f"Job_{self.job_opening_id}", new_name)
                super().save(update_fields=['cv'])  # Update the cv field
        else:
            super().save(*args, **kwargs)
            
            
class ArchivedJobOpening(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    form_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    deadline = models.DateTimeField()
    archived_at = models.DateTimeField(auto_now_add=True)  # When it was archived

    def __str__(self):
        return f"{self.title} - {self.company.name} (Archived)"