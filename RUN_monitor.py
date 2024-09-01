import subprocess
import time
import os
import argparse

def is_program_running(program_name):
    """Check if the specified program is running, excluding this script's process."""
    try:
        # Get all processes matching the program name
        output = subprocess.check_output(["pgrep", "-f", program_name]).decode().splitlines()
        # Exclude the current process's PID
        current_pid = str(os.getpid())
        running_pids = [pid for pid in output if pid != current_pid]
        return len(running_pids) > 0
    except subprocess.CalledProcessError:
        return False

def run_program(program_path):
    """Run the specified program script."""
    subprocess.Popen(["python3", program_path])

def monitor_program(program_name, program_path):
    """Monitor the specified program and restart if not running."""
    while True:
        if not is_program_running(program_name):
            print(f"{program_name} is not running. Starting it...")
            run_program(program_path)
        else:
            print(f"{program_name} is running.")
        time.sleep(30)  # Wait for 30 seconds before checking again

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a Python script and restart it if it crashes.")
    parser.add_argument("program_path", type=str, help="The path to the Python script to monitor.")
    args = parser.parse_args()

    program_name = os.path.basename(args.program_path)
    monitor_program(program_name, args.program_path)
