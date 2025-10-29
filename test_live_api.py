#!/usr/bin/env python3
"""Test live API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8002/ocr/docling"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    print("[OK] PASSED")

def test_api_info():
    """Test API info"""
    print("\n=== Testing /api ===")
    response = requests.get("http://localhost:8002/api")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Name: {data['name']}")
    print(f"Version: {data['version']}")
    print(f"Pipeline Mode: {data['pipeline_mode']}")
    assert response.status_code == 200
    print("[OK] PASSED")

def test_pipeline():
    """Test pipeline endpoint"""
    print("\n=== Testing /pipeline ===")
    response = requests.get(f"{BASE_URL}/pipeline")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    print("[OK] PASSED")

def test_formats():
    """Test formats endpoint"""
    print("\n=== Testing /formats ===")
    response = requests.get(f"{BASE_URL}/formats")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Input formats: {', '.join(data['input_formats'][:5])}...")
    print(f"Output formats: {', '.join(data['output_formats'])}")
    print(f"Archive formats: {', '.join(data['archive_formats'])}")
    assert response.status_code == 200
    print("[OK] PASSED")

def test_upload_md():
    """Test upload MD file"""
    print("\n=== Testing /upload with MD file ===")
    
    # Create test file
    with open("test_doc.md", "rb") as f:
        files = {"file": ("test_doc.md", f, "text/markdown")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Files processed: {len(data)}")
        if data:
            print(f"First file: {data[0]['file_name']}")
            print(f"Text preview: {data[0]['file_text'][:100]}...")
        print("[OK] PASSED")
    else:
        print(f"Error: {response.text}")
        print("[FAIL] FAILED")

def test_web_ui():
    """Test web UI"""
    print("\n=== Testing Web UI ===")
    response = requests.get("http://localhost:8002/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Content length: {len(response.content)} bytes")
        print("[OK] PASSED")
    else:
        print("[FAIL] FAILED")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Docling OCR Live API")
    print("=" * 60)
    
    try:
        test_health()
        test_api_info()
        test_pipeline()
        test_formats()
        test_upload_md()
        test_web_ui()
        
        print("\n" + "=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nService is running correctly at http://localhost:8002")
        print("Web UI: http://localhost:8002")
        print("API Docs: http://localhost:8002/docs")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

