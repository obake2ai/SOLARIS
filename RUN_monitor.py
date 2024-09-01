import subprocess
import time
import os
import argparse

def is_program_running(program_path):
    """Check if the specified program is running using its full path, excluding this script's process."""
    try:
        # `ps aux` で全てのプロセスをリストし、フルパスで検索
        output = subprocess.check_output(["ps", "aux"]).decode().splitlines()
        # 現在のスクリプトのプロセスIDを取得
        current_pid = str(os.getpid())
        for line in output:
            # `python3` コマンドで `program_path` が実行されているか確認し、自分のPIDを除外
            if f"python3 {program_path}" in line:
                if current_pid in line:
                    continue  # 自分のプロセスは無視
                print(f"Found running process: {line}")  # デバッグ用出力
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
            print(f"[Monitor] {program_name} is not running. Starting it...")
            run_program(program_path)
        else:
            print(f"[Monitor] {program_name} is running.")
        time.sleep(30)  # Wait for 30 seconds before checking again

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a Python script and restart it if it crashes.")
    parser.add_argument("program_path", type=str, help="The path to the Python script to monitor.")
    args = parser.parse_args()

    # `os.path.abspath` を使って絶対パスに変換
    monitor_program(os.path.abspath(args.program_path))
