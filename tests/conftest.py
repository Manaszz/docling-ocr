"""Test configuration and fixtures"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_files_dir():
    """Test files directory"""
    return Path(__file__).parent / "test_files"


@pytest.fixture
def sample_txt_file(test_files_dir, tmp_path):
    """Create a sample text file"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello Docling OCR!\nThis is a test file.", encoding="utf-8")
    return test_file


@pytest.fixture
def sample_md_file(tmp_path):
    """Create a sample markdown file"""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test Document\n\nThis is a test.", encoding="utf-8")
    return test_file

