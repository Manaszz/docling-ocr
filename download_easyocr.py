#!/usr/bin/env python3
"""Download EasyOCR models"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import easyocr

print("Downloading EasyOCR models for English and Russian...")
print("This may take a few minutes...")

try:
    # Download models
    reader = easyocr.Reader(['en', 'ru'], gpu=False, verbose=False)
    print("\nModels downloaded successfully!")
    print(f"Models location: {reader.model_storage_directory}")
    
except Exception as e:
    print(f"\nError: {e}")
    sys.exit(1)

