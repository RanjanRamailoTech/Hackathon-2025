from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import JobOpening, ApplicantResponse, Company
from .serializers import JobOpeningSerializer, ApplicantResponseSerializer
import logging
from django.utils import timezone
from django.db.models.signals import post_save


class JobOpeningListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.company
            job_openings = JobOpening.objects.filter(company=company)
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

logger = logging.getLogger(__name__)

class ApplicantResponseCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, jobId):
        data = {
            "jobId": jobId,
            "name": request.data.get("name"),
            "role": request.data.get("role"),
            "status": request.data.get("status"),
            "score": request.data.get("score"),
            "appliedFor": request.data.get("appliedFor"),
            "appliedDate": request.data.get("appliedDate"),
            "cv": request.FILES.get("cv"),
            "resumeParseData": request.data.get("resumeParseData"),
            "email": request.data.get("email")
        }
        logger.debug(f"Received data: {data}")

        serializer = ApplicantResponseSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            
            # Manually trigger signal with request context
            post_save.send(
                sender=ApplicantResponse,
                instance=instance,
                created=True,
                request=request  # Pass request to signal
            )
            logger.info(f"Successfully created applicant response for jobId {jobId}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicantResponseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jobId):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=jobId, company=company)
            responses = ApplicantResponse.objects.filter(jobId=job_opening)
            serializer = ApplicantResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found or not owned by this company"}, status=status.HTTP_404_NOT_FOUND)


class ApplicantResponseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jobId, responseId):
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=jobId, company=company)
            response = ApplicantResponse.objects.get(id=responseId, jobId=job_opening)
            serializer = ApplicantResponseSerializer(response)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found or not owned by this company"}, status=status.HTTP_404_NOT_FOUND)
        except ApplicantResponse.DoesNotExist:
            return Response({"error": "Response not found for this job opening"}, status=status.HTTP_404_NOT_FOUND)
    
class JobOpeningQuestionsView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access for candidates

    def get(self, request, jobId):
        try:
            job_opening = JobOpening.objects.get(id=jobId)
            questions = job_opening.questions  # JSONField containing the list of questions
            if not questions or not isinstance(questions, list):
                return Response({"questions": []}, status=status.HTTP_200_OK)  # Return empty list if no questions
            return Response({"questions": questions}, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching questions for jobId {jobId}: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class ArchivedJobOpeningsListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         try:
#             company = request.user.company
#             archived_jobs = ArchivedJobOpening.objects.filter(company=company)
#             serializer = ArchivedJobOpeningSerializer(archived_jobs, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Company.DoesNotExist:
#             return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        

# def archive_expired_jobs():
#     """Move expired job openings to ArchivedJobOpening table."""
#     now = timezone.now()
#     expired_jobs = JobOpening.objects.filter(deadline__lte=now)
#     for job in expired_jobs:
#         ArchivedJobOpening.objects.create(
#             company=job.company,
#             title=job.title,
#             description=job.description,
#             form_url=job.form_url,
#             created_at=job.created_at,
#             deadline=job.deadline
#         )
#         job.responses.all().delete()  # Delete responses (optional)
#         job.form_fields.all().delete()  # Delete form fields
#         job.delete()
        
