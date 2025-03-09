from rest_framework import serializers
from .models import Interview

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['applicant_job_pipeline_id','status', 'video_file', 'created_at']
