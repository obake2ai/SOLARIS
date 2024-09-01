import subprocess
import time
import os
import argparse

def is_program_running(program_path):
    """Check if the specified program is running using its full path."""
    try:
        # Get the list of all running processes
        output = subprocess.check_output(["ps", "aux"]).decode().splitlines()
        # Check if the full path of the program is in the process list
        for line in output:
            if program_path in line and "python3" in line:
                return True
        return False
    except subprocess.CalledProcessError:
        return False

def run_program(program_path):
    """Run the specified program script."""
    subprocess.Popen(["python3", program_path])

def monitor_program(program_path):
    """Monitor the specified program and restart if not running."""
    program_name = os.path.basename(program_path)
    while True:
        if not is_program_running(program_path):
            print(f"{program_name} is not running. Starting it...")
            run_program(program_path)
        else:
            print(f"{program_name} is running.")
        time.sleep(30)  # Wait for 30 seconds before checking again

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a Python script and restart it if it crashes.")
    parser.add_argument("program_path", type=str, help="The path to the Python script to monitor.")
    args = parser.parse_args()

    monitor_program(os.path.abspath(args.program_path))
