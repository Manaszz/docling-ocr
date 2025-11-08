#!/usr/bin/env python3
"""Integration test for archive upload functionality"""

import zipfile
import tempfile
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_archive_processing():
    """Test the archive processing logic directly"""
    from app.services.archive_handler import ArchiveHandler
    from app.services.converter_manager import get_converter_manager

    print("Testing archive processing integration...")

    # Initialize services
    archive_handler = ArchiveHandler()
    converter_manager = get_converter_manager()

    # Get converter
    converter = converter_manager.get_converter("std")

    # Create test archive
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temp directory: {temp_dir}")

    zip_path = temp_dir / 'test.zip'

    # Create sample files
    content_dir = temp_dir / 'content'
    content_dir.mkdir()

    # Create markdown files (supported by Docling)
    sample1 = content_dir / 'file1.md'
    sample1.write_text('# File 1\n\nHello from file 1', encoding='utf-8')

    sample2 = content_dir / 'file2.md'
    sample2.write_text('# File 2\n\nHello from file 2', encoding='utf-8')

    # Create ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sample1, 'file1.md')
        zipf.write(sample2, 'file2.md')

    print(f"Created ZIP archive: {zip_path}")

    try:
        # Test extraction
        extract_dir = Path(tempfile.mkdtemp())
        extracted_dir = archive_handler.extract_archive(zip_path, extract_dir)
        print(f"Extracted to: {extracted_dir}")

        # Find files
        supported_extensions = converter.get_supported_extensions()
        files = archive_handler.find_files_in_directory(extracted_dir, supported_extensions)
        print(f"Found {len(files)} supported files: {[str(f.relative_to(extracted_dir)) for f in files]}")

        # Convert files
        results = []
        for file_path in files:
            try:
                result_data = converter.convert_with_auto_ocr(
                    file_path,
                    output_format="markdown",
                    ocr_mode="auto"
                )
                results.append({
                    'file': str(file_path.relative_to(extracted_dir)),
                    'success': True,
                    'text_length': len(result_data['text'])
                })
                print(f"Converted {file_path.relative_to(extracted_dir)}: {len(result_data['text'])} chars")
            except Exception as e:
                results.append({
                    'file': str(file_path.relative_to(extracted_dir)),
                    'success': False,
                    'error': str(e)
                })
                print(f"Failed to convert {file_path.relative_to(extracted_dir)}: {e}")

        # Check results
        successful = sum(1 for r in results if r['success'])
        print(f"Conversion results: {successful}/{len(results)} successful")

        if successful == len(results):
            print("SUCCESS: Archive processing works correctly!")
            return True
        else:
            print("FAIL: Some files failed to convert")
            return False

    except Exception as e:
        print(f"FAIL: Archive processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
            shutil.rmtree(extract_dir)
        except:
            pass

if __name__ == "__main__":
    success = test_archive_processing()
    sys.exit(0 if success else 1)
