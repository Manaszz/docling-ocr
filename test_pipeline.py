"""Test script to verify pipeline parameter is correctly passed"""
import requests
import sys

def test_pipeline(url_base="http://localhost:8002"):
    """Test both std and vlm pipelines"""
    
    # Create a simple test file
    test_file_content = b"Test content"
    files = {'file': ('test.txt', test_file_content, 'text/plain')}
    
    print("Testing Standard Pipeline...")
    response = requests.post(
        f"{url_base}/ocr/docling/upload",
        files=files,
        params={"pipeline": "std"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Pipeline used: {data[0].get('pipeline_used', 'unknown')}")
    else:
        print(f"Error: {response.text}")
    
    print("\nTesting VLM Pipeline...")
    response = requests.post(
        f"{url_base}/ocr/docling/upload",
        files=files,
        params={"pipeline": "vlm"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Pipeline used: {data[0].get('pipeline_used', 'unknown')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    test_pipeline(url)

