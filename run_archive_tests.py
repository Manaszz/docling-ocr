#!/usr/bin/env python3
"""Run archive upload tests manually"""

import subprocess
import sys
import time
import signal
import os

def run_tests():
    """Run the archive upload tests"""
    print("Starting Docling OCR API server...")

    # Start server
    server_proc = subprocess.Popen([
        sys.executable, '-m', 'app.main'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)

    try:
        # Test server health
        import requests
        response = requests.get('http://localhost:8002/health', timeout=10)
        if response.status_code != 200:
            print(f"Server health check failed: {response.status_code}")
            return False

        print("Server is running. Running tests...")

        # Run tests
        test_result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_archive_upload.py',
            '-v',
            '--tb=short'
        ], capture_output=True, text=True)

        print("STDOUT:")
        print(test_result.stdout)
        if test_result.stderr:
            print("STDERR:")
            print(test_result.stderr)

        print(f"Test exit code: {test_result.returncode}")
        return test_result.returncode == 0

    except Exception as e:
        print(f"Error during testing: {e}")
        return False

    finally:
        # Stop server
        print("Stopping server...")
        try:
            server_proc.terminate()
            server_proc.wait(timeout=5)
        except:
            server_proc.kill()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)





