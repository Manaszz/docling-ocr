"""Test archive upload functionality"""

import pytest
import zipfile
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_zip_file(tmp_path):
    """Create a sample ZIP file with markdown files"""
    zip_path = tmp_path / "test.zip"

    # Create sample files
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Create markdown files
    md_file1 = content_dir / "readme.md"
    md_file1.write_text("# Test Document\n\nThis is a test document.\nHello World!", encoding="utf-8")

    md_file2 = content_dir / "document.md"
    md_file2.write_text("# Another Document\n\nThis is another test document.", encoding="utf-8")

    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(md_file1, "readme.md")
        zipf.write(md_file2, "document.md")

    return zip_path


def test_upload_zip_archive(client, sample_zip_file):
    """Test uploading a ZIP archive"""
    with open(sample_zip_file, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload",
            files={"file": ("test.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    data = response.json()

    # Should return a list of conversion results
    assert isinstance(data, list)
    assert len(data) == 2  # Should process both files

    # Check that both files were processed
    file_names = {item["file_name"] for item in data}
    assert "readme.md" in file_names
    assert "document.md" in file_names

    # Check that conversion was successful
    for item in data:
        assert "file_text" in item
        assert "file_extension" in item
        assert "metadata" in item
        assert "pipeline_used" in item
        assert item["pipeline_used"] == "std"  # Default pipeline

        # Should not have errors
        assert "error" not in item or not item["error"]


def test_upload_zip_archive_md(client, sample_zip_file):
    """Test uploading a ZIP archive and getting MD files"""
    with open(sample_zip_file, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload/md",
            files={"file": ("test.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # Should return a ZIP file
    content = response.content
    assert len(content) > 0

    # Save and examine the returned ZIP
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        with zipfile.ZipFile(tmp_path, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) == 2
            # Files are converted to .md regardless of input format
            assert any("readme" in f and f.endswith(".md") for f in files)
            assert any("document" in f and f.endswith(".md") for f in files)
    finally:
        Path(tmp_path).unlink()


def test_upload_empty_zip(client, tmp_path):
    """Test uploading an empty ZIP archive"""
    empty_zip = tmp_path / "empty.zip"
    with zipfile.ZipFile(empty_zip, 'w') as zipf:
        pass  # Create empty ZIP

    with open(empty_zip, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload",
            files={"file": ("empty.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["error"] == "No supported files found in archive"


def test_upload_zip_with_unsupported_files(client, tmp_path):
    """Test uploading ZIP with only unsupported files"""
    zip_path = tmp_path / "unsupported.zip"

    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Create unsupported file
    exe_file = content_dir / "program.exe"
    exe_file.write_bytes(b"dummy exe content")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(exe_file, "program.exe")

    with open(zip_path, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload",
            files={"file": ("unsupported.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["error"] == "No supported files found in archive"


def test_upload_zip_vlm_pipeline(client, sample_zip_file):
    """Test uploading ZIP with VLM pipeline"""
    # Skip if VLM is not available
    from app.core.config import settings
    if not settings.docling_vlm_enabled:
        pytest.skip("VLM pipeline not enabled")

    with open(sample_zip_file, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload?pipeline=vlm",
            files={"file": ("test.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    for item in data:
        assert item["pipeline_used"] == "vlm"


def test_upload_zip_with_subdirectory(client, tmp_path):
    """Test uploading ZIP with files in subdirectories"""
    zip_path = tmp_path / "subdir.zip"

    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Create files in subdirectories
    sub_dir = content_dir / "docs"
    sub_dir.mkdir()

    file1 = content_dir / "root.txt"
    file1.write_text("Root file", encoding="utf-8")

    file2 = sub_dir / "sub.txt"
    file2.write_text("Subdirectory file", encoding="utf-8")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file1, "root.txt")
        zipf.write(file2, "docs/sub.txt")

    with open(zip_path, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload",
            files={"file": ("subdir.zip", f, "application/zip")}
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    file_names = {item["file_name"] for item in data}
    assert "root.txt" in file_names
    assert "docs/sub.txt" in file_names
