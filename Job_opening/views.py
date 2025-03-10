from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import JobOpening, ApplicantResponse, Company
from .serializers import JobOpeningSerializer, ApplicantResponseSerializer, JobOpeningPublicSerializer
import logging
from .tasks import send_application_email

logger = logging.getLogger(__name__)

class JobOpeningListCreateView(APIView):
    """View for listing and creating job openings."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve a list of job openings for the authenticated user's company.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            Response: A response containing serialized job opening data or an error message.

        Raises:
            Company.DoesNotExist: If the user's company does not exist.
        """
        try:
            company = request.user.company
            job_openings = JobOpening.objects.filter(company=company).order_by('-postedDate')
            serializer = JobOpeningSerializer(job_openings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create a new job opening for the authenticated user's company.

        Args:
            request (HttpRequest): The incoming HTTP request with job opening data.

        Returns:
            Response: A response containing the created job opening data or validation errors.

        Raises:
            Company.DoesNotExist: If the user's company does not exist.
        """
        serializer = JobOpeningSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                company = request.user.company
                serializer.save(company=company)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Company.DoesNotExist:
                return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class JobOpeningDetailView(APIView):
    """View for retrieving, updating, and deleting a specific job opening."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """Retrieve details of a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            pk (int): The primary key of the job opening.

        Returns:
            Response: A response containing the serialized job opening data or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist.
        """
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=pk, company=company)
            serializer = JobOpeningSerializer(job_opening)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """Update details of a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request with updated data.
            pk (int): The primary key of the job opening.

        Returns:
            Response: A response containing the updated job opening data or validation errors.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist.
        """
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
        """Delete a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            pk (int): The primary key of the job opening.

        Returns:
            Response: A response indicating successful deletion or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist.
        """
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=pk, company=company)
            job_opening.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)

logger = logging.getLogger(__name__)

   
class JobOpeningPublicDetailView(APIView):
    """View for retrieving public details of a job opening."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        """Retrieve public details of a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            pk (int): The primary key of the job opening.

        Returns:
            Response: A response containing public job opening data or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist.
        """
        try:
            job_opening = JobOpening.objects.get(id=pk)
            serializer = JobOpeningPublicSerializer(job_opening)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)


class ApplicantResponseCreateView(APIView):
    """View for creating an applicant response."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, jobId):
        """Create a new applicant response and initiate candidate selection process.

        Args:
            request (HttpRequest): The incoming HTTP request with applicant data.
            jobId (int): The ID of the job opening being applied to.

        Returns:
            Response: A response containing the created applicant response data or validation errors.
        """
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
            data = self.candidate_selection(request,instance)
            logger.info(f"Successfully created applicant response for jobId {jobId}")
            response_data = serializer.data
            
            if data and 'interview_id' in data:
                response_data['interview_id'] = data['interview_id']
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def candidate_selection(self,request, instance):
        """Evaluate the applicant's score and send an acceptance or rejection email.

        Args:
            request (HttpRequest): The incoming HTTP request.
            instance (ApplicantResponse): The applicant response instance to evaluate.

        Returns:
            dict or None: A dictionary with 'interview_id' if accepted, otherwise None.
        """
        job = instance.jobId
        applicant_email = instance.email
        applicant_name = instance.name
        job_title = job.title
        benchmark = job.benchmark
        score = instance.score
        applicant_id = instance.id

        logger.debug(f"Preparing email for {applicant_name} at {applicant_email}")

        if not applicant_email or not isinstance(applicant_email, str):
            logger.error(f"Invalid email address for {applicant_name}: {applicant_email}")
            instance.status = "New"
            instance.save(update_fields=['status'])
            return

        if score >= benchmark:
            instance.status = "In Progress"
            logger.debug(f"Setting status to 'In Progress' for {applicant_name}")
        else:
            instance.status = "Rejected"
            logger.debug(f"Setting status to 'Rejected' for {applicant_name}")
        instance.save(update_fields=['status'])
        

        request_host = request.get_host() if request else "127.0.0.1:8000"  # Fallback
        
        return send_application_email(applicant_name, applicant_email, job_title, job.id, score, benchmark, applicant_id, request_host)


class ApplicantResponseListView(APIView):
    """View for listing applicant responses for a specific job."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jobId):
        """Retrieve a list of applicant responses for a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            jobId (int): The ID of the job opening.

        Returns:
            Response: A response containing serialized applicant response data or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist or is not owned by the company.
        """
        try:
            company = request.user.company
            job_opening = JobOpening.objects.get(id=jobId, company=company)
            responses = ApplicantResponse.objects.filter(jobId=job_opening)
            serializer = ApplicantResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found or not owned by this company"}, status=status.HTTP_404_NOT_FOUND)


class ApplicantResponseDetailView(APIView):
    """View for retrieving details of a specific applicant response."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jobId, responseId):
        """Retrieve details of a specific applicant response for a job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            jobId (int): The ID of the job opening.
            responseId (int): The ID of the applicant response.

        Returns:
            Response: A response containing the serialized applicant response data or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist or is not owned by the company.
            ApplicantResponse.DoesNotExist: If the response does not exist for the job opening.
        """
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
    """View for retrieving questions associated with a job opening."""
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access for candidates

    def get(self, request, jobId):
        """Retrieve the list of questions associated with a specific job opening.

        Args:
            request (HttpRequest): The incoming HTTP request.
            jobId (int): The ID of the job opening.

        Returns:
            Response: A response containing the list of questions or an error message.

        Raises:
            JobOpening.DoesNotExist: If the job opening does not exist.
            Exception: For unexpected errors, logged and returned as a 500 response.
        """
        try:
            job_opening = JobOpening.objects.get(id=jobId)
            questions = job_opening.questions
            if not questions or not isinstance(questions, list):
                return Response({"questions": []}, status=status.HTTP_200_OK)
            return Response({"questions": questions}, status=status.HTTP_200_OK)
        except JobOpening.DoesNotExist:
            return Response({"error": "Job opening not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching questions for jobId {jobId}: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CompanyDashboardStatsView(APIView):
    """View for retrieving company dashboard statistics."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve statistical data for the authenticated user's company dashboard.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            Response: A response containing job openings, candidate count, and interviews in progress or an error message.

        Raises:
            Company.DoesNotExist: If the user's company does not exist.
            Exception: For unexpected errors, logged and returned as a 500 response.
        """
        try:
            company = request.user.company
            job_count = JobOpening.objects.filter(company=company).count()
            
            candidate_count = ApplicantResponse.objects.filter(jobId__company=company).count()
            interviews_in_progress = ApplicantResponse.objects.filter(
                jobId__company=company,
                status="In Progress"
            ).count()

            return Response({
                "job_openings": job_count,
                "total_candidates": candidate_count,
                "interviews_in_progress": interviews_in_progress
            }, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching dashboard stats: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyApplicantResponsesListView(APIView):
    """View for listing all applicant responses for a company."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve all applicant responses associated with the authenticated user's company.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            Response: A response containing serialized applicant response data or an error message.

        Raises:
            Company.DoesNotExist: If the user's company does not exist.
            Exception: For unexpected errors, logged and returned as a 500 response.
        """
        try:
            company = request.user.company
            responses = ApplicantResponse.objects.filter(jobId__company=company)
            serializer = ApplicantResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Company not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching company responses: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)