import sys

from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def extract_audio(video_file, output_file):
    # Load the video file
    video_clip = VideoFileClip(video_file)
    
    # Extract audio from the video
    audio_clip = video_clip.audio
    
    # Write the audio to an output file
    audio_clip.write_audiofile(output_file, codec='mp3', bitrate='320k')
    
    # Close the clips to free resources
    audio_clip.close()
    video_clip.close()
    
    print(f"Successfully extracted audio to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_audio.py <video_file> <output_audio_file>")
        sys.exit(1)

    input_video = sys.argv[1]
    output_audio = sys.argv[2]

    # Ensure the input video file exists and is an MP4 file
    if os.path.exists(input_video) and input_video.endswith(('.mp4', '.avi', '.mov')):
        extract_audio(input_video, output_audio)
    else:
        print(f"The file {input_video} does not exist or is not a valid video format.")
