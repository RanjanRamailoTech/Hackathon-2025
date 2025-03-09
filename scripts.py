import subprocess

def run_command(command):
    """Run a shell command and print its output."""
    try:
        result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing command: {command}")
        print(e.stderr)

def main():
    # List of commands to run
    commands = [
        "sudo apt-get install -y portaudio19-dev python3-pyaudio",
        "pip install -r requirements.txt",
        "python3 manage.py migrate",
        "python3 manage.py runserver"
    ]

    for command in commands:
        run_command(command)

if __name__ == "__main__":
    main()
