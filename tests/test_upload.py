"""Test upload endpoints"""

import pytest


def test_upload_text_file(client, sample_txt_file):
    """Test uploading a text file"""
    with open(sample_txt_file, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "file_name" in data[0]
    assert "file_text" in data[0]
    assert "Hello Docling OCR" in data[0]["file_text"]


def test_upload_md_file(client, sample_md_file):
    """Test uploading and getting MD file"""
    with open(sample_md_file, 'rb') as f:
        response = client.post(
            "/ocr/docling/upload/md",
            files={"file": ("test.md", f, "text/markdown")}
        )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/markdown; charset=utf-8"


def test_upload_no_file(client):
    """Test upload without file"""
    response = client.post("/ocr/docling/upload")
    
    assert response.status_code == 422  # Validation error

