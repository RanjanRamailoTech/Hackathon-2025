import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and handle errors."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return False

def main():
    # Try to install PyAudio using a pre-compiled wheel first
    print("Attempting to install PyAudio using pre-compiled wheel...")
    success = run_command("pip install --no-build-isolation --only-binary=:all: PyAudio")
    
    if not success:
        print("Pre-compiled wheel installation failed, trying alternative approach...")
        # If we're on Render, we can use their specific approach
        if "RENDER" in os.environ:
            print("Detected Render environment, using apt-get without sudo...")
            run_command("apt-get update")
            run_command("apt-get install -y portaudio19-dev python3-dev")
        else:
            # For local development, try with sudo
            print("Using sudo for local environment...")
            run_command("sudo apt-get update")
            run_command("sudo apt-get install -y portaudio19-dev python3-dev")
    
    # Install other Python dependencies
    print("Installing other dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Run Django migrations
    print("Running migrations...")
    run_command("python3 manage.py migrate")

if __name__ == "__main__":
    main()