import subprocess
import sys
import os
import venv
from pathlib import Path

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

def create_and_activate_venv():
    """Create and activate a virtual environment."""
    venv_path = Path(".venv")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
    else:
        print(f"Virtual environment already exists at {venv_path}")
    
    # Determine the path to the activate script based on OS
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        activate_cmd = f"call {activate_script}"
    else:
        activate_script = venv_path / "bin" / "activate"
        activate_cmd = f"source {activate_script}"
    
    # Update PATH and VIRTUAL_ENV environment variables
    if sys.platform == "win32":
        venv_bin = venv_path / "Scripts"
    else:
        venv_bin = venv_path / "bin"
    
    os.environ["VIRTUAL_ENV"] = str(venv_path.absolute())
    os.environ["PATH"] = f"{venv_bin}{os.pathsep}{os.environ['PATH']}"
    
    # We can't actually source/activate in the same Python process,
    # but we've updated PATH so pip/python commands will use the virtual environment
    print(f"Virtual environment activated via environment variables")
    
    # Upgrade pip in the virtual environment
    run_command(f"{venv_bin}/pip install --upgrade pip")
    
    return str(venv_bin)

def main():
    # Create and activate virtual environment
    venv_bin = create_and_activate_venv()
    pip_cmd = f"{venv_bin}/pip"
    python_cmd = f"{venv_bin}/python"
    
    # Try to install PyAudio using a pre-compiled wheel first
    print("Attempting to install PyAudio using pre-compiled wheel...")
    success = run_command(f"{pip_cmd} install --no-build-isolation --only-binary=:all: PyAudio")
    
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
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Run Django migrations
    print("Running migrations...")
    run_command(f"{python_cmd} manage.py migrate")

if __name__ == "__main__":
    main()