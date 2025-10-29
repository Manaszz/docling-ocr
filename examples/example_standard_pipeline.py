#!/usr/bin/env python3
"""
Example: Using Docling OCR API with Standard Pipeline

This example demonstrates how to use the Docling OCR API
with the standard pipeline for document conversion.
"""

import requests
import base64
import json
from pathlib import Path


# Configuration
API_BASE_URL = "http://localhost:8002/ocr/docling"


def upload_file_example(file_path: str):
    """
    Example: Upload a file and get JSON response
    """
    print(f"\n=== Upload File Example ===")
    print(f"File: {file_path}")
    
    url = f"{API_BASE_URL}/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        results = response.json()
        print(f"\nSuccess! Converted {len(results)} file(s)")
        
        for result in results:
            print(f"\nFile: {result['file_name']}")
            if result.get('metadata'):
                print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
            print(f"Text preview: {result['file_text'][:200]}...")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def upload_file_get_md(file_path: str, output_path: str):
    """
    Example: Upload a file and get MD file
    """
    print(f"\n=== Upload File Get MD Example ===")
    print(f"File: {file_path}")
    print(f"Output: {output_path}")
    
    url = f"{API_BASE_URL}/upload/md"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"\nSuccess! Saved to {output_path}")
    else:
        print(f"Error: {response.status_code}")


def parse_base64_example(file_path: str):
    """
    Example: Parse base64-encoded file
    """
    print(f"\n=== Parse Base64 Example ===")
    print(f"File: {file_path}")
    
    url = f"{API_BASE_URL}/parse"
    
    # Read and encode file
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
    
    # Prepare request
    payload = {
        "is_base64_or_document": True,
        "docs": [
            {
                "filename": Path(file_path).name,
                "data": file_base64,
                "type": "application/pdf"  # Adjust based on file type
            }
        ]
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        results = response.json()
        print(f"\nSuccess! Converted {len(results)} file(s)")
        
        for result in results:
            print(f"\nFile: {result['file_name']}")
            print(f"Text preview: {result['file_text'][:200]}...")
    else:
        print(f"Error: {response.status_code}")


def check_health():
    """
    Example: Check API health and status
    """
    print(f"\n=== Health Check ===")
    
    url = f"{API_BASE_URL}/health"
    response = requests.get(url)
    
    if response.status_code == 200:
        health = response.json()
        print(f"\nStatus: {health['status']}")
        print(f"Version: {health['version']}")
        print(f"Pipeline Mode: {health['pipeline_mode']}")
        print(f"Models Loaded: {health['models_loaded']}")
        print(f"OCR Enabled: {health['ocr_enabled']}")
    else:
        print(f"Error: {response.status_code}")


def get_supported_formats():
    """
    Example: Get supported formats
    """
    print(f"\n=== Supported Formats ===")
    
    url = f"{API_BASE_URL}/formats"
    response = requests.get(url)
    
    if response.status_code == 200:
        formats = response.json()
        print(f"\nInput formats: {', '.join(formats['input_formats'])}")
        print(f"\nOutput formats: {', '.join(formats['output_formats'])}")
        print(f"\nArchive formats: {', '.join(formats['archive_formats'])}")
    else:
        print(f"Error: {response.status_code}")


def main():
    """
    Run examples
    """
    print("=" * 60)
    print("Docling OCR API - Standard Pipeline Examples")
    print("=" * 60)
    
    # Check health first
    check_health()
    
    # Get supported formats
    get_supported_formats()
    
    # Example with a test file
    test_file = "test_document.pdf"
    
    if Path(test_file).exists():
        # Upload and get JSON
        upload_file_example(test_file)
        
        # Upload and get MD file
        upload_file_get_md(test_file, "output.md")
        
        # Parse base64
        parse_base64_example(test_file)
    else:
        print(f"\n⚠️  Test file '{test_file}' not found.")
        print("Create a test file or update the file path in the script.")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

