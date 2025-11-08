#!/usr/bin/env python3
"""Unit test for archive handler functionality"""

import tempfile
import zipfile
from pathlib import Path
import sys
import os

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.archive_handler import ArchiveHandler

def test_archive_detection():
    """Test archive file detection"""
    print("Testing archive detection...")

    handler = ArchiveHandler()

    # Test ZIP detection
    assert handler.is_archive("test.zip") == True
    assert handler.is_archive("test.ZIP") == True

    # Test RAR detection
    assert handler.is_archive("test.rar") == True
    assert handler.is_archive("test.RAR") == True

    # Test 7Z detection
    assert handler.is_archive("test.7z") == True

    # Test non-archive files
    assert handler.is_archive("test.txt") == False
    assert handler.is_archive("test.pdf") == False

    print("PASS: Archive detection tests passed")

def test_zip_extraction():
    """Test ZIP file extraction"""
    print("Testing ZIP extraction...")

    handler = ArchiveHandler()

    # Create a test ZIP file
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / 'test.zip'

    # Create sample content
    content_dir = temp_dir / 'content'
    content_dir.mkdir()

    # Create sample files
    sample1 = content_dir / 'file1.txt'
    sample1.write_text('Hello from file 1', encoding='utf-8')

    sample2 = content_dir / 'file2.txt'
    sample2.write_text('Hello from file 2', encoding='utf-8')

    # Create subdirectory with file
    sub_dir = content_dir / 'subdir'
    sub_dir.mkdir()
    sample3 = sub_dir / 'file3.txt'
    sample3.write_text('Hello from subdirectory', encoding='utf-8')

    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in content_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(content_dir)
                zipf.write(file_path, arcname)

    print(f"Created ZIP file: {zip_path}")
    print(f"ZIP size: {zip_path.stat().st_size} bytes")

    # Test extraction
    extract_dir = Path(tempfile.mkdtemp())
    extracted_dir = handler.extract_archive(zip_path, extract_dir)

    print(f"Extracted to: {extracted_dir}")

    # Verify extraction
    extracted_files = list(extracted_dir.rglob('*'))
    extracted_file_paths = [f for f in extracted_files if f.is_file()]

    print(f"Extracted {len(extracted_file_paths)} files:")
    for f in extracted_file_paths:
        print(f"  {f.relative_to(extracted_dir)}")

    # Check that all original files are present
    assert len(extracted_file_paths) == 3

    # Check file contents
    ext_file1 = extracted_dir / 'file1.txt'
    ext_file2 = extracted_dir / 'file2.txt'
    ext_file3 = extracted_dir / 'subdir' / 'file3.txt'

    assert ext_file1.exists()
    assert ext_file2.exists()
    assert ext_file3.exists()

    assert ext_file1.read_text(encoding='utf-8') == 'Hello from file 1'
    assert ext_file2.read_text(encoding='utf-8') == 'Hello from file 2'
    assert ext_file3.read_text(encoding='utf-8') == 'Hello from subdirectory'

    print("PASS: ZIP extraction test passed")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    shutil.rmtree(extract_dir)

def test_file_finding():
    """Test finding supported files in directory"""
    print("Testing file finding...")

    handler = ArchiveHandler()

    # Create test directory structure
    temp_dir = Path(tempfile.mkdtemp())

    # Create supported files
    pdf_file = temp_dir / 'document.pdf'
    pdf_file.write_bytes(b'dummy pdf content')

    txt_file = temp_dir / 'readme.txt'
    txt_file.write_text('readme content', encoding='utf-8')

    # Create unsupported files
    exe_file = temp_dir / 'program.exe'
    exe_file.write_bytes(b'dummy exe content')

    # Create subdirectory with more files
    sub_dir = temp_dir / 'docs'
    sub_dir.mkdir()

    docx_file = sub_dir / 'report.docx'
    docx_file.write_bytes(b'dummy docx content')

    # Define supported extensions
    supported_extensions = {'.pdf', '.txt', '.docx'}

    # Test file finding
    found_files = handler.find_files_in_directory(temp_dir, supported_extensions)

    print(f"Found {len(found_files)} supported files:")
    for f in found_files:
        print(f"  {f.relative_to(temp_dir)}")

    # Should find 3 files: document.pdf, readme.txt, docs/report.docx
    assert len(found_files) == 3

    # Check that all expected files are found
    file_names = {f.name for f in found_files}
    assert 'document.pdf' in file_names
    assert 'readme.txt' in file_names
    assert 'report.docx' in file_names

    print("PASS: File finding test passed")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

def main():
    """Run all tests"""
    print("Testing Archive Handler functionality...\n")

    try:
        test_archive_detection()
        print()

        test_zip_extraction()
        print()

        test_file_finding()
        print()

        print("SUCCESS: All Archive Handler tests passed!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
