from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Interview, EvaluationResult
from .serializers import InterviewSerializer
from rest_framework import status
import tempfile
import os
import json
import subprocess
import openai
from django.conf import settings
from rest_framework import permissions
from .serializers import InterviewSerializer
import time
from Job_opening.models import JobOpening
from Job_opening.serializers import JobDescriptionSerializer
from django.core.exceptions import ObjectDoesNotExist

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
        # current_videos = interview.video_file or []
        # current_videos.append(video_path)
        # interview.video_file = current_videos
        # interview.save(update_fields=['video_file'])
        
        try:
                # # Check what type of data we're receiving
                # if 'audio_data' in request.data:
                #     # Handle audio processing
                #     audio_data = request.data.get('audio_data')
                #     text_response = self.process_audio(audio_data)
                #     qa_pairs = self.extract_qa_pairs_from_audio(text_response)
                #     return Response({'qa_pairs': qa_pairs}, status=status.HTTP_200_OK)
                
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
                        audio_text = self.extract_audio_and_process(temp_video_file.name)
                        # qa_pairs = self.extract_qa_pairs_from_audio(question + audio_text)
                        
                        # Optional: Calculate score if requested
                        if request.data.get('calculate_score', True):
                            score = self.calculate_candidate_score(job_description, question, audio_text)
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
    #         transcribed_text = self.speech_to_text(temp_audio_path)
    #         return transcribed_text
            
    #     except Exception as e:
    #         print(f"Error processing audio: {e}")
    #         return f"Error processing audio: {str(e)}"
            
    #     finally:
    #         # Clean up temporary files
    #         if os.path.exists(temp_audio_path):
    #             os.remove(temp_audio_path)
    #             print(f"Deleted temporary audio file: {temp_audio_path}")
    
    def extract_audio_and_process(self, video_path):
        """
        Extracts audio from the video file and processes it for speech-to-text.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Transcribed text from the extracted audio
        """
        print(f"Extracting audio from video file: {video_path}")
        
        # Create a temporary file for the extracted audio
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_audio_path = temp_audio_file.name
        temp_audio_file.close()
        
        try:
            # Use FFmpeg to extract audio from the video file
            command = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # No video
                "-ac", "1",  # Mono channel
                "-ar", "12000",  # Sampling rate (12kHz for Whisper)
                "-b:a", "16k",  # Bitrate (16 kbps)
                "-y", temp_audio_path  # Overwrite output file if exists
            ]
            
            print("Running FFmpeg command:", ' '.join(command))
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            if result.returncode != 0:
                print("FFmpeg error:", result.stderr.decode())
                return "Error extracting audio"

            # Process the extracted audio for speech-to-text (STT)
            audio_text = self.speech_to_text(temp_audio_path)
            print(f"Transcribed audio text: {audio_text}")
            return audio_text

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return f"Error extracting audio: {e.stderr.decode()}"
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Processing failed: {str(e)}"

        finally:
            # Clean up temporary files
            if os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    print(f"Deleted temporary audio file: {temp_audio_path}")
                except Exception as e:
                    print(f"Error deleting temp file: {str(e)}")
    
    def speech_to_text(self, audio_path):
        """
        Converts audio to text using OpenAI's Whisper API.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text from the audio
        """
        client = openai.OpenAI(api_key=settings.OPEN_AI_KEY)

        print(f"Transcribing audio from: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="text"
                )
            
            return transcription
        
        except Exception as e:
            print(f"Error during transcription: {e}")
            return f"Transcription failed: {str(e)}"
    
    # def extract_qa_pairs_from_audio(self, audio_text):
    #     """
    #     Uses OpenAI's GPT model to extract question-answer pairs from audio_text.
        
    #     Args:
    #         audio_text: Transcribed text from the interview
            
    #     Returns:
    #         Structured QA pairs extracted from the transcription
    #     """
    #     client = openai.OpenAI(api_key=settings.OPEN_AI_KEY)
        
    #     prompt = (
    #         "Convert the following interview transcript into a structured JSON format with an array of objects. "
    #         "Each object should have 'interviewer' and 'candidate' fields. "
    #         "Identify when the interviewer is asking questions and when the candidate is responding. "
    #         "The output must be valid JSON that can be parsed. Do not include any explanations or text outside the JSON array. "
    #         "Format example: [{\"interviewer\": \"question here\", \"candidate\": \"answer here\"}]"
    #         f"\n\n{audio_text}"
    #     )
        
    #     try:
    #         response = client.chat.completions.create(
    #             model="gpt-3.5-turbo",
    #             messages=[
    #                 {
    #                     "role": "system", 
    #                     "content": "You are a helpful assistant that specializes in structuring interview transcripts into QA pairs. Always return valid, parseable JSON."
    #                 },
    #                 {
    #                     "role": "user", 
    #                     "content": prompt
    #                 }
    #             ]
    #         )
            
    #         if isinstance(response.choices, list):
    #             qa_pairs_response = response.choices[0].message.content
    #         else:
    #             qa_pairs_response = response.choices.message.content
            
    #         print(f"Extracted QA Pairs Response: {qa_pairs_response}")
            
    #         # Clean up the response to handle potential formatting issues
    #         qa_pairs_response = qa_pairs_response.strip()
            
    #         # If response starts with ```json and ends with ```, remove these markers
    #         if qa_pairs_response.startswith("```json") and qa_pairs_response.endswith("```"):
    #             qa_pairs_response = qa_pairs_response[7:-3].strip()
    #         elif qa_pairs_response.startswith("```") and qa_pairs_response.endswith("```"):
    #             qa_pairs_response = qa_pairs_response[3:-3].strip()
            
    #         # Try to parse the JSON
    #         try:
    #             qa_pairs = json.loads(qa_pairs_response)
    #             return qa_pairs
    #         except json.JSONDecodeError as e:
    #             print(f"Error parsing JSON response: {e}")
    #             print(f"Raw response: {qa_pairs_response}")
                
    #             # Fallback: Try to extract JSON if it's embedded in text
    #             import re
    #             json_pattern = r'\[\s*\{.*\}\s*\]'
    #             json_match = re.search(json_pattern, qa_pairs_response, re.DOTALL)
                
    #             if json_match:
    #                 try:
    #                     extracted_json = json_match.group(0)
    #                     qa_pairs = json.loads(extracted_json)
    #                     return qa_pairs
    #                 except json.JSONDecodeError:
    #                     pass
                
    #             # If all parsing attempts fail, return a structured error with default empty array
    #             return [{"error": "Failed to parse QA pairs", "raw_response": qa_pairs_response}]
            
    #     except Exception as e:
    #         print(f"Error during QA extraction: {e}")
    #         return [{"error": f"QA extraction failed: {str(e)}"}]
    
    def calculate_candidate_score(self, job_description, question, answer):
        """
        Calculate a candidate score based on the interview QA pairs.
        
        Args:
            qa_pairs: Structured QA pairs from the interview
            
        Returns:
            Candidate assessment and scores
        """
        client = openai.OpenAI(api_key=settings.OPEN_AI_KEY)
        
        prompt = (
            "Act as expert QA hiring analyst. Analyze ONLY the candidate's answer in relation to: "
            f"1. Job requirements: {job_description}\n"
            f"2. Interview question: '{question}'\n"
            f"3. Candidate response: '{answer}'\n\n"
            
            "Evaluation Criteria:\n"
            "- Relevance to job requirements (30% weight)\n"
            "- Technical accuracy for QA roles (25% weight)\n" 
            "- Problem-solving approach (20% weight)\n"
            "- Communication clarity (15% weight)\n"
            "- Alignment with QA best practices (10% weight)\n\n"
            
            "Output format: Only return numerical score between 0-10 (1 decimal allowed) "
            "based on weighted criteria. No explanations. Example: 7.5"
        )

        
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # Using a more advanced model for evaluation
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert hiring manager with exceptional skills in candidate evaluation."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            if isinstance(response.choices, list):
                evaluation = response.choices[0].message.content
            else:
                evaluation = response.choices.message.content
            
            return {
                "evaluation": evaluation
            }
            
        except Exception as e:
            print(f"Error during candidate evaluation: {e}")
            return {"error": f"Candidate evaluation failed: {str(e)}"}