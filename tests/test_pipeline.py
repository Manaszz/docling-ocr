"""Test pipeline endpoints"""

import pytest


def test_get_pipeline_config(client):
    """Test getting pipeline configuration"""
    response = client.get("/ocr/docling/pipeline")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "mode" in data
    assert data["mode"] in ["standard", "vlm"]


def test_get_formats(client):
    """Test getting supported formats"""
    response = client.get("/ocr/docling/formats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "input_formats" in data
    assert "output_formats" in data
    assert "archive_formats" in data
    
    # Check some expected formats
    assert ".pdf" in data["input_formats"]
    assert "markdown" in data["output_formats"]

