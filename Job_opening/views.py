from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import JobOpening, ApplicantResponse, Company, ArchivedJobOpening
from .serializers import JobOpeningSerializer, ApplicantResponseSerializer, ArchivedJobOpeningSerializer

from django.utils import timezone

# Existing Views (unchanged for brevity)
class JobOpeningListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.company
            now = timezone.now()
            job_openings = JobOpening.objects.filter(company=company, deadline__gt=now)
            serializer = JobOpeningSerializer(job_openings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = JobOpeningSerializer(data=request.data)
        if serializer.is_valid():
            try:
                company = request.user.company
                serializer.save(company=company)
                job_opening = JobOpening.objects.get(id=serializer.data["id"])
                job_opening.form_url = f"/apply/{job_opening.id}/"
                job_opening.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Company.DoesNotExist:
                return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobOpeningDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=pk, company=company)
            serializer = JobOpeningSerializer(job_opening)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=pk, company=company)
            serializer = JobOpeningSerializer(job_opening, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=pk, company=company)
            job_opening.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)

class ApplicantResponseCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        try:
            job_opening = JobOpening.objects.get(id=job_id)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)
        
        now = timezone.now()
        if job_opening.deadline <= now:
            return Response({"error": "Cannot submit response: This job opening has expired."}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "job_opening": job_id,
            "email_address": request.data.get("email_address"),
            "name": request.data.get("name"),
            "gender": request.data.get("gender"),
            "country": request.data.get("country"),
            "phone_number": request.data.get("phone_number"),
            "responses": request.data.get("responses", {}),
            "cv": request.FILES.get("cv")
        }
        
        serializer = ApplicantResponseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobOpeningResponsesListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=job_id, company=company)
            responses = ApplicantResponse.objects.filter(job_opening=job_opening)
            serializer = ApplicantResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found or not owned by this company"}, status=status.HTTP_404_NOT_FOUND)
        
class JobOpeningResponseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id, response_id):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=job_id, company=company)
            response = ApplicantResponse.objects.get(id=response_id, job_opening=job_opening)
            serializer = ApplicantResponseSerializer(response)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found or not owned by this company"}, status=status.HTTP_404_NOT_FOUND)
        except ApplicantResponse.DoesNotExist:
            return Response({"error": "Response not found for this job opening"}, status=status.HTTP_404_NOT_FOUND)

class ArchivedJobOpeningsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.company
            archived_jobs = ArchivedJobOpening.objects.filter(company=company)
            serializer = ArchivedJobOpeningSerializer(archived_jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        

def archive_expired_jobs():
    """Move expired job openings to ArchivedJobOpening table."""
    now = timezone.now()
    expired_jobs = JobOpening.objects.filter(deadline__lte=now)
    for job in expired_jobs:
        ArchivedJobOpening.objects.create(
            company=job.company,
            title=job.title,
            description=job.description,
            form_url=job.form_url,
            created_at=job.created_at,
            deadline=job.deadline
        )
        job.responses.all().delete()  # Delete responses (optional)
        job.form_fields.all().delete()  # Delete form fields
        job.delete()
        
