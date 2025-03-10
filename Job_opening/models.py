from django.db import models
import uuid
from client_auth.models import Company


class JobOpening(models.Model):
    """Model representing a job opening created by a company."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    applicants = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=(("Active", "Active"), ("Pending", "Pending"), ("Archived", "Archived")),
        default="Pending"
    )
    postedDate = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    jobType = models.CharField(max_length=20, blank=True, null=True)
    experienceLevel = models.CharField(max_length=20, blank=True, null=True)
    questions = models.JSONField(default=list, blank=True)
    application_link = models.URLField(max_length=255, blank=True, null=True)
    benchmark = models.IntegerField(default=0)

    def __str__(self):
        """Return a string representation of the job opening."""
        return f"{self.title} - {self.company.name}"


class ApplicantResponse(models.Model):
    """Model representing an applicant's response to a job opening."""
    jobId = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="responses")
    applicantId = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=(("New", "New"), ("In Progress", "In Progress"), ("Rejected", "Rejected")),
        default="New"
    )
    score = models.IntegerField(default=0, null=True, blank=True)
    appliedFor = models.CharField(max_length=255)
    appliedDate = models.DateField()
    cvKeywords = models.JSONField(null=True, blank=True)
    resumeParseData = models.JSONField(null=True, blank=True)
    email = models.EmailField(max_length=255)

    def __str__(self):
        """Return a string representation of the applicant response."""
        return f"Response for {self.jobId.title} - {self.applicantId}"

    def save(self, *args, **kwargs):
        """Override save to update the applicants count on the related job opening."""
        super().save(*args, **kwargs)
        self.jobId.applicants = self.jobId.responses.count()
        self.jobId.save(update_fields=['applicants'])