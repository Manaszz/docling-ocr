#!/usr/bin/env python3
"""Test archive upload functionality"""

import zipfile
import rarfile
import tempfile
from pathlib import Path
import requests
import sys

def create_test_archive(archive_type='zip'):
    """Create a test archive with a text file"""

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Created temp directory: {temp_dir}")

    # Create sample files
    sample_file = temp_dir / 'test.txt'
    sample_file.write_text('Hello from archive!', encoding='utf-8')

    # Create archive
    if archive_type == 'zip':
        archive_path = temp_dir / 'test.zip'
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sample_file, 'test.txt')
    elif archive_type == 'rar':
        # Note: rarfile doesn't support writing, so we'll skip RAR creation for now
        archive_path = temp_dir / 'test.rar'
        # For testing, we'll just create an empty file as placeholder
        archive_path.write_bytes(b'dummy rar content')
        print("Warning: RAR creation not supported by rarfile library")
    else:
        raise ValueError(f"Unsupported archive type: {archive_type}")

    print(f"Created {archive_type.upper()} archive: {archive_path}")

    return archive_path

def test_archive_upload(archive_path):
    """Test uploading archive to the API"""

    # Check if archive exists
    if not archive_path.exists():
        print(f"Archive file not found: {archive_path}")
        return False

    print(f"Uploading {archive_path.name}...")

    try:
        # Upload file
        url = "http://localhost:8002/ocr/docling/upload"
        with open(archive_path, 'rb') as f:
            files = {'file': (archive_path.name, f, 'application/octet-stream')}
            response = requests.post(url, files=files, timeout=30)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response contains {len(data)} items")
            for i, item in enumerate(data):
                print(f"  Item {i+1}: {item.get('file_name', 'unknown')}")
                if 'error' in item:
                    print(f"    Error: {item['error']}")
                elif 'file_text' in item:
                    print(f"    Text length: {len(item['file_text'])} chars")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Is the service running?")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing archive upload functionality...")

    # Test ZIP upload
    print("\n=== Testing ZIP Upload ===")
    zip_path = create_test_archive('zip')
    zip_success = test_archive_upload(zip_path)

    # Test RAR upload - skip for now since rarfile doesn't support writing
    print("\n=== Skipping RAR Upload (rarfile doesn't support writing) ===")
    rar_success = True  # Skip this test

    # Summary
    print("\n=== Test Results ===")
    print(f"ZIP upload: {'PASS' if zip_success else 'FAIL'}")
    print(f"RAR upload: SKIPPED (rarfile limitation)")

    if not zip_success:
        print("\nArchive upload functionality needs to be fixed!")
        sys.exit(1)
    else:
        print("\nZIP upload working correctly!")

if __name__ == "__main__":
    main()
