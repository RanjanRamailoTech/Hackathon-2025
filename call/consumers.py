import json
import asyncio
import base64
import numpy as np
import cv2
import subprocess
import tempfile
import os
import speech_recognition as sr
import openai  # Import OpenAI client
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class InterviewConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_video_file = None  # Temporary file for storing video chunks

    async def connect(self):
        print("Attempting to connect")
        self.interview_id = self.scope['url_route']['kwargs']['interview_id']
        self.room_group_name = f'interview_{self.interview_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Connection accepted for interview ID: {self.interview_id}")

    async def disconnect(self, close_code):
        print("Disconnecting...")
        # Clean up temporary files when disconnecting
        if self.temp_video_file and os.path.exists(self.temp_video_file.name):
            print(f"Removing temporary video file: {self.temp_video_file.name}")
            os.remove(self.temp_video_file.name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("Disconnected successfully.")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                data = json.loads(text_data)
                message_type = data.get('type', None)

                if message_type == 'heartbeat':
                    print("Received heartbeat from client")
                    return

                if message_type == 'audio_chunk':
                    audio_data = data.get('audio_data', None)
                    if audio_data:
                        print("Received audio chunk.")
                        await self.process_audio_chunk(audio_data)

            elif bytes_data:
                print("Received video frame.")
                await self.process_video_frame(bytes_data)

        except Exception as e:
            print(f"Error in receive method: {e}")


    async def process_audio_chunk(self, audio_data):
        print("Processing audio chunk...")
        loop = asyncio.get_event_loop()
        text_response = await loop.run_in_executor(None, self.process_audio, audio_data)
        await self.send(text_data=json.dumps({'text_response': text_response}))
        print(f"Audio processing result")

    async def process_video_frame(self, video_frame):
        # Append incoming video frame to a temporary file
        if not self.temp_video_file:
            # Create a temporary file for storing video chunks
            self.temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            print(f"Created temporary video file: {self.temp_video_file.name}")

        with open(self.temp_video_file.name, 'ab') as f:
            f.write(video_frame)
            print(f"Appended video frame to {self.temp_video_file.name}")
        
        # Extract audio from the video file after receiving each chunk (or after a certain condition)
        audio_text = await self.extract_audio_and_process(self.temp_video_file.name)
        
        # Send the extracted audio text back to the client
        await self.send(text_data=json.dumps({'audio_text': await self.extract_qa_pairs_from_audio(audio_text)}))
        print(f"Extracted audio text sent to client")

    async def extract_audio_and_process(self, video_path):
        """
        Extracts audio from the video file and processes it for speech-to-text.
        """
        print(f"Extracting audio from video file: {video_path}")
        
        try:
            # Create a temporary file for the extracted audio
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")  # Use MP3 format
            temp_audio_path = temp_audio_file.name
            temp_audio_file.close()
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
            audio_text = await self.speech_to_text(temp_audio_file.name)

            print(f"Transcribed audio text: {audio_text}")

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return "Error extracting audio"
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "Processing failed"

        finally:
            # Clean up temporary files regardless of success/failure
            if temp_audio_file and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    print(f"Deleted temporary audio file: {temp_audio_path}")
                except Exception as e:
                    print(f"Error deleting temp file: {str(e)}")

        return audio_text

    async def speech_to_text(self, audio_path):
        """
        Converts audio to text using OpenAI's Whisper API.
        """
          # Set your OpenAI API key here
        client = openai.OpenAI(api_key = settings.OPEN_AI_KEY)  # Instantiate the OpenAI client

        print(f"Transcribing audio from: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="text"  # You can adjust this based on your needs
                )
            
            return transcription # Return the transcribed text directly
        
        except Exception as e:
            print(f"Error during transcription: {e}")
            return "Transcription failed"

    async def extract_qa_pairs_from_audio(self, audio_text):
        """
        Uses OpenAI's GPT model to extract question-answer pairs from audio_text.
        """
        client = openai.OpenAI(api_key = settings.OPEN_AI_KEY)  # Instantiate the OpenAI client
        
        prompt = (
            "Convert the following interview transcript into a structured JSON format where each exchange has 'interviewer' and 'candidate' fields. Identify when the interviewer is asking questions and when the candidate is responding. Format the output as an array of JSON objects with the structure {'interviewer': '[interviewer's question]', 'candidate': '[candidate's response]'}."
            f"{audio_text}"
        )
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            if isinstance(response.choices, list):
                qa_pairs_response = response.choices[0].message.content
            # If it's not a list but has a direct message attribute
            else:
                qa_pairs_response = response.choices.message.content
            
            print(f"Extracted QA Pairs Response: {qa_pairs_response}")  # Log response
            
            # Here you would need to parse qa_pairs_response into your qa_pairs list.
            # This is a placeholder; you will need to implement parsing logic based on how you want to structure it.
            
            # Assuming the response is in JSON format
            self.qa_pairs = json.loads(qa_pairs_response)  # Convert string response to list of dictionaries
            return self.qa_pairs
            
        except Exception as e:
            print(f"Error during QA extraction: {e}")

    async def calculate_candidate_score_from_interview(self, qa_pairs):
        client = openai.OpenAI(api_key = settings.OPEN_AI_KEY)