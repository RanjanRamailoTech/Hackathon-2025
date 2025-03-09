from django.db import models
from Job_opening.models import ApplicantResponse
import os
from django.utils import timezone


def interview_video_upload_path(instance, filename):
    # Save to Media/Interview/<interview_id>/vid_<timestamp>.mp4
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return f"Interview/{instance.id}/vid_{timestamp}.mp4"

class Interview(models.Model):
    applicant_job_pipeline_id = models.ForeignKey(ApplicantResponse, on_delete=models.CASCADE)
    video_file = models.JSONField(default=list)
    status = models.CharField(max_length=20, default="In Progress")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Interview {self.id} for {self.applicant_job_pipeline_id}"
    

class EvaluationResult(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE)
    verbal_scores = models.JSONField()
    non_verbal_scores = models.JSONField()
    final_report = models.TextField()
