from django.db import models
import uuid
from client_auth.models import Company
import os
from django.conf import settings


# def cv_upload_path(instance, filename):
#     """Generate a structured path for CV uploads."""
#     job_dir = f"Job_{instance.job_opening_id}"
#     # Use a unique filename based on UUID or a timestamp if ID isn’t available yet
#     applicant_id = instance.applicant_id or uuid.uuid4()  # Fallback to UUID if applicant_id isn’t set
#     filename = f"cv_{applicant_id}.pdf"
#     return os.path.join('cvs', job_dir, filename)


class JobOpening(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100, blank=True, null=True)  # New field
    location = models.CharField(max_length=100, blank=True, null=True)  # New field
    applicants = models.IntegerField(default=0)  # New field for applicant count
    status = models.CharField(
        max_length=20,
        choices=(("Active", "Active"), ("Pending", "Pending"), ("Archived", "Archived")),
        default="Pending"
    )
    postedDate = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    jobType = models.CharField(blank=True,null=True)
    experienceLevel = models.CharField(max_length=20,blank=True,null=True)
    questions = models.JSONField(default=list, blank=True)
    application_link = models.URLField(max_length=255, blank=True, null=True)  # for application link
    benchmark = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


#hashlib for resume parsing

class ApplicantResponse(models.Model):
    jobId = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="responses")
    applicantId = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)  # e.g., "Backend Engineer"
    status = models.CharField(
        max_length=20,
        choices=(("New", "New"), ("In Progress", "In Progress"), ("Rejected", "Rejected")),
        default="New"
    )
    score = models.IntegerField(default=0,null=True,blank=True)
    appliedFor = models.CharField(max_length=255)  # e.g., "Backend Engineer"
    appliedDate = models.DateField()
    cvKeywords = models.JSONField(null=True, blank=True)  # Parsed from resumeParseData
    resumeParseData = models.JSONField(null=True, blank=True)  # Raw data from frontend
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f"Response for {self.jobId.title} - {self.applicantId}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Increment applicants count on the job opening
        self.jobId.applicants = self.jobId.responses.count()
        self.jobId.save(update_fields=['applicants'])
         
            
# class ArchivedJobOpening(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     form_url = models.CharField(max_length=255, blank=True, null=True)
#     created_at = models.DateTimeField()
#     deadline = models.DateTimeField()
#     archived_at = models.DateTimeField(auto_now_add=True)  # When it was archived

#     def __str__(self):
#         return f"{self.title} - {self.company.name} (Archived)"