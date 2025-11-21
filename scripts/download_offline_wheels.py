#!/usr/bin/env python3
"""
Download Python wheels for offline Docker build.
Allows downloading Linux wheels even when running on Windows.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def download_wheels(
    requirements_file: str = "requirements.txt",
    output_dir: str = "offline_packages",
    platform: str = "manylinux2014_x86_64",
    python_version: str = "3.11"
):
    """
    Download wheels for a specific platform.
    
    Args:
        requirements_file: Path to requirements.txt
        output_dir: Directory to save wheels
        platform: Target platform (e.g. manylinux2014_x86_64)
        python_version: Target Python version (e.g. 3.11)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading wheels to {output_path.absolute()}")
    print(f"Target Platform: {platform}")
    print(f"Target Python: {python_version}")
    
    # Basic pip download command
    cmd = [
        sys.executable, "-m", "pip", "download",
        "-r", requirements_file,
        "-d", str(output_path),
        "--python-version", python_version,
        "--only-binary=:all:", # Prefer wheels
        "--platform", platform,
        # We need to be careful with dependencies that might not have wheels
        # some might need --no-deps if they are pure source
    ]
    
    # Special handling for PyTorch (CPU version to save space)
    print("Downloading PyTorch (CPU)...")
    torch_cmd = [
        sys.executable, "-m", "pip", "download",
        "-d", str(output_path),
        "--python-version", python_version,
        "--only-binary=:all:",
        "--platform", platform,
        "--index-url", "https://download.pytorch.org/whl/cpu",
        "torch", "torchvision", "torchaudio"
    ]
    
    try:
        subprocess.run(torch_cmd, check=True)
        subprocess.run(cmd, check=True)
        print("\n✓ Download complete!")
        print(f"Files: {len(list(output_path.glob('*')))}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error downloading packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_wheels()

