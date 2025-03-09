from rest_framework import serializers
from .models import Interview, EvaluationResult

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['applicant_job_pipeline_id','status', 'video_file', 'created_at']

class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = ['interview','verbal_scores', 'final_report']