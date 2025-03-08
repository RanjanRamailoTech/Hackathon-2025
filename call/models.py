from django.db import models

class Interview(models.Model):
    candidate_id = models.IntegerField()
    job_description = models.TextField()
    video_file = models.FileField(upload_to='interviews/')
    status = models.CharField(max_length=20, default='started')
    analysis_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class EvaluationResult(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE)
    verbal_scores = models.JSONField()
    non_verbal_scores = models.JSONField()
    final_report = models.TextField()
