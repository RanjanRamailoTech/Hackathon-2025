import subprocess

def run_command(command):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")

def main():
    # Install system dependencies (only works if you have sudo permissions)
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y portaudio19-dev")

    # Install Python dependencies
    run_command("pip install -r requirements.txt")

    # Run Django migrations
    run_command("python3 manage.py migrate")

if __name__ == "__main__":
    main()
