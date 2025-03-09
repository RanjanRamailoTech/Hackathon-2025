# Job_opening/serializers.py
from rest_framework import serializers
from .models import JobOpening, ApplicantResponse
import json
import re
import logging
from django.urls import reverse


logger = logging.getLogger(__name__)


class JobOpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOpening
        fields = [
            "id", "title", "department", "location", "applicants", "status", "postedDate",
            "description", "requirements", "jobType", "experienceLevel", "questions", "application_link", "benchmark"
        ]

    def create(self, validated_data):
        # Create the JobOpening instance with all fields
        job_opening = JobOpening.objects.create(**validated_data)
        return job_opening

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.department = validated_data.get("department", instance.department)
        instance.location = validated_data.get("location", instance.location)
        instance.applicants = validated_data.get("applicants", instance.applicants)
        instance.status = validated_data.get("status", instance.status)
        instance.postedDate = validated_data.get("postedDate", instance.postedDate)
        instance.description = validated_data.get("description", instance.description)
        instance.requirements = validated_data.get("requirements", instance.requirements)
        instance.jobType = validated_data.get("jobType", instance.jobType)
        instance.experienceLevel = validated_data.get("experienceLevel", instance.experienceLevel)
        instance.questions = validated_data.get("questions", instance.questions)
        instance.save()
        return instance

    def validate_questions(self, value):
        """Ensure questions is a list of strings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Questions must be a list.")
        for question in value:
            if not isinstance(question, str):
                raise serializers.ValidationError("Each question must be a string.")
        return value
    
    def create(self, validated_data):
        instance = JobOpening.objects.create(**validated_data)
        request = self.context.get('request')
        if request:
            apply_url = reverse('applicant-response-create', kwargs={'jobId': instance.id})
            instance.application_link = request.build_absolute_uri(apply_url)
            instance.save(update_fields=['application_link'])
        logger.debug(f"Created JobOpening with application_link: {instance.application_link}")
        return instance

class ApplicantResponseSerializer(serializers.ModelSerializer):
    jobId = serializers.PrimaryKeyRelatedField(queryset=JobOpening.objects.all())
    class Meta:
        model = ApplicantResponse
        fields = [
            "id", "jobId", "name", "role", "score", "appliedFor",
            "appliedDate", "resumeParseData", "cvKeywords", "email"
        ]
        read_only_fields = ["id", "cvKeywords"]  # cvKeywords is computed, not sent by frontend

    def validate_jobId(self, value):
        if not JobOpening.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid jobId: Job opening does not exist.")
        return value
    
    def extract_keywords(self, parse_data):
        if not parse_data or not isinstance(parse_data, dict):
            return {}
        text = " ".join([str(value) for value in parse_data.values()]).lower()
        keywords = set()
        technical_keywords = {
            "programmingLanguages": ["python", "java", "javascript", "c++"],
            "frameworksTools": ["django", "flask", "react", "node.js"],
            "databases": ["postgresql", "mysql", "mongodb"],
            "concepts": ["machine learning", "big data", "cloud computing"]
        }
        all_keywords = set(sum(technical_keywords.values(), []))
        for keyword in all_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                keywords.add(keyword)
        categorized_keywords = {cat: [kw for kw in kws if kw in keywords] for cat, kws in technical_keywords.items()}
        return {k: v for k, v in categorized_keywords.items() if v}


    def create(self, validated_data):
        logger.debug(f"Validated data before processing: {validated_data}")
        resumeParseData = validated_data.pop("resumeParseData", None)
        
        instance = ApplicantResponse.objects.create(**validated_data)
        
        if resumeParseData:
            instance.resumeParseData = resumeParseData
            instance.cvKeywords = self.extract_keywords(resumeParseData)
            instance.save(update_fields=["resumeParseData", "cvKeywords"])
        logger.debug(f"Created instance: {instance}")
        return instance
    
    def to_representation(self, instance):
        # Exclude cvKeywords and resumeParseData in responses
        ret = super().to_representation(instance)
        ret.pop("cvKeywords", None)
        ret.pop("resumeParseData", None)
        return ret



# class ArchivedJobOpeningSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArchivedJobOpening
#         fields = [
#             "id", "title", "department", "location", "applicants", "status", "posted_date",
#             "description", "requirements", "job_type", "experience_level", "questions", "archived_at"
#         ]