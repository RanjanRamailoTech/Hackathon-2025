from rest_framework import serializers
from .models import Interview

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['candidate_id', 'job_description', 'video_file']
