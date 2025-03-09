import subprocess
import sys
import os
import venv
from pathlib import Path

def run_command(command, use_sudo=False):
    """Run a shell command and handle errors."""
    if use_sudo and "RENDER" not in os.environ:
        command = f"sudo {command}"
    
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
    
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
    else:
        print(f"Virtual environment already exists at {venv_path}")
    
    venv_bin = venv_path / ("Scripts" if sys.platform == "win32" else "bin")
    os.environ["VIRTUAL_ENV"] = str(venv_path.absolute())
    os.environ["PATH"] = f"{venv_bin}{os.pathsep}{os.environ['PATH']}"
    print(f"Virtual environment activated via environment variables")
    
    run_command(f"{venv_bin}/pip install --upgrade pip")
    return str(venv_bin)

def install_system_dependencies():
    """Install system dependencies required for PyAudio."""
    print("Installing system dependencies...")
    commands = [
        "apt-get update",
        "apt-get install -y portaudio19-dev python3-dev"
    ]
    
    for cmd in commands:
        run_command(cmd, use_sudo=True)

def main():
    venv_bin = create_and_activate_venv()
    pip_cmd = f"{venv_bin}/pip"
    python_cmd = f"{venv_bin}/python"
    
    install_system_dependencies()
    
    print("Attempting to install PyAudio...")
    success = run_command(f"{pip_cmd} install pyaudio")
    
    if not success:
        print("PyAudio installation failed. Retrying with additional build options...")
        run_command(f"{pip_cmd} install --no-cache-dir --global-option='build_ext' --global-option='-I/usr/include' pyaudio")
    
    print("Installing other dependencies...")
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    print("Running migrations...")
    run_command(f"{python_cmd} manage.py migrate")

if __name__ == "__main__":
    main()