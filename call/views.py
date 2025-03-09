from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Interview, EvaluationResult
from .serializers import InterviewSerializer, EvaluationResultSerializer
from rest_framework import status
import tempfile
import os
from django.conf import settings
from rest_framework import permissions
from .serializers import InterviewSerializer
import time
from Job_opening.models import JobOpening, ApplicantResponse
from Job_opening.serializers import JobDescriptionSerializer
from django.core.exceptions import ObjectDoesNotExist
from .services import(
    extract_audio_and_process,
    speech_to_text,
    calculate_candidate_score,
)
from .final_report_gen import(
    generate_final_report,
)

class StartInterview(APIView):
    
    def post(self, request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            interview = serializer.save()
            return Response({
                'interview_id': interview.id,
                'ws_url': f"ws://{request.get_host()}/ws/interviews/{interview.id}/"
            }, status=201)
        return Response(serializer.errors, status=400)


class InterviewProcessingAPI(APIView):
    
    """
    API view for processing interview videos and audio.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        """
        Process uploaded interview recording.
        
        Accepts:
          - video_file: A video file upload containing interview footage
          - audio_data: Base64 encoded audio data
          
        Returns:
          - Processed QA pairs extracted from the interview
        """
        
        interview_id = request.query_params.get('interview_id')
        
        if not interview_id:
            return Response({"error": "interview_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            interview = Interview.objects.get(id=interview_id)
        except Interview.DoesNotExist:
            return Response({"error": "Interview not found"}, status=status.HTTP_404_NOT_FOUND)

        if 'video_file' not in request.FILES:
            return Response({"error": "video_file is required"}, status=status.HTTP_400_BAD_REQUEST)
        question = request.data.get('question',None)
        if not question:
            return Response({"error":"Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        applicant_response = interview.applicant_job_pipeline_id  # This gets the ApplicantResponse object
        job_opening = applicant_response.jobId
        if question not in job_opening.questions:
            return Response({"error":"Question doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        job_description = JobDescriptionSerializer(job_opening).data
        video_file = request.FILES['video_file']
        
        # Define storage directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'interview', str(interview_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename for the video chunk
        timestamp = int(time.time() * 1000)  # Milliseconds for uniqueness
        video_filename = f"video_chunk_{timestamp}_{video_file.name}"
        video_path = os.path.join(upload_dir, video_filename)
        
        # Save the video file
        with open(video_path, 'wb+') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        video_file = interview.video_file
        video_file.append(video_path)
        videos = {
            'video_file': video_file
        }
        # Update Interview model’s video_file JSON field
        interview_serializer = InterviewSerializer(interview,data=videos, partial=True)
        if interview_serializer.is_valid():
            interview_serializer.save()
        else:
            print(interview_serializer.errors)
            return Response({"error": "Failed to update the video list"}, status=status.HTTP_400_BAD_REQUEST)
        try:    
                if 'video_file' in request.FILES:
                    # Handle video processing
                    video_file = request.FILES['video_file']
                    
                    # Save the uploaded video to a temporary file
                    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    for chunk in video_file.chunks():
                        temp_video_file.write(chunk)
                    temp_video_file.close()
                    
                    try:
                        # Process the video file
                        audio_text = extract_audio_and_process(temp_video_file.name)
                        score = calculate_candidate_score(job_description, question, audio_text)
                        try:
                            evaluation_result = EvaluationResult.objects.get(interview=interview)
                        except ObjectDoesNotExist:
                            # If it does not exist, create a new instance
                            evaluation_result = EvaluationResult.objects.create(interview=interview, verbal_scores={}, non_verbal_scores={}, final_report="")
                        finally:
                            existing_scores = evaluation_result.verbal_scores
                            existing_scores[question] = score.get("evaluation",0)
                            evaluation_result.verbal_scores = existing_scores
                            evaluation_result.save()
                        print("Final flag: ",request.data.get('final_flag'))
                        if request.data.get('final_flag', False):
                            try:
                                evaluation_result = EvaluationResult.objects.get(interview=interview)
                                final_report = generate_final_report(evaluation_result,job_description)
                                evaluation_result.final_report = final_report
                                evaluation_result.save()
                            except ObjectDoesNotExist:
                                return Response({"error":"Cannot generate report on empty records"}, status=status.HTTP_400_BAD_REQUEST)
                            except Exception as e:
                                print(f"An error occurred while generating the final report: {e}")
                        # Return the extracted QA pairs
                        return Response({"message":"Video processed successfully"
                            }, status=status.HTTP_200_OK)
                    finally:
                        # Clean up the temporary file
                        if os.path.exists(temp_video_file.name):
                            os.remove(temp_video_file.name)
                            print(f"Removed temporary video file: {temp_video_file.name}")
                
                else:
                    return Response({
                        'error': 'No audio_data or video_file provided',
                        'required_params': ['audio_data OR video_file']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response({
                'error': str(e),
                'traceback': traceback_str
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def process_audio(self, audio_data):
    #     """
    #     Process base64 encoded audio data.
        
    #     Args:
    #         audio_data: Base64 encoded audio string
            
    #     Returns:
    #         Transcribed text from the audio
    #     """
    #     import base64
        
    #     # Create a temporary file for the audio data
    #     temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    #     temp_audio_path = temp_audio_file.name
    #     temp_audio_file.close()
        
    #     try:
    #         # Decode base64 audio data and write to file
    #         audio_bytes = base64.b64decode(audio_data)
    #         with open(temp_audio_path, 'wb') as f:
    #             f.write(audio_bytes)
            
    #         # Process the audio file for speech-to-text
    #         transcribed_text = speech_to_text(temp_audio_path)
    #         return transcribed_text
            
    #     except Exception as e:
    #         print(f"Error processing audio: {e}")
    #         return f"Error processing audio: {str(e)}"
            
    #     finally:
    #         # Clean up temporary files
    #         if os.path.exists(temp_audio_path):
    #             os.remove(temp_audio_path)
    #             print(f"Deleted temporary audio file: {temp_audio_path}")

class InterviewReport(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, applicant_response_id):
        if not applicant_response_id:
            return Response({"error":"Job ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        candidate = ApplicantResponse.objects.filter(id=applicant_response_id).first()
        if not candidate:
            return Response({"error":"Candidate application doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        interview = Interview.objects.filter(applicant_job_pipeline_id=applicant_response_id).first()
        report = EvaluationResult.objects.filter(interview=interview).first()
        return Response({"data":EvaluationResultSerializer(report).data},status=status.HTTP_200_OK)
        