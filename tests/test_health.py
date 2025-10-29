"""Test health endpoint"""

import pytest


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/ocr/docling/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "version" in data
    assert "pipeline_mode" in data
    assert data["pipeline_mode"] in ["standard", "vlm"]


def test_api_info(client):
    """Test API info endpoint"""
    response = client.get("/api")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data

