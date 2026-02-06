#!/usr/bin/env python3
"""
Download RapidOCR/PP-OCR models for offline deployment.

RapidOCR uses PaddleOCR models (PP-OCRv4) in ONNX format.
This script downloads the required model files for air-gapped environments.

Usage:
    python scripts/download_rapidocr_models.py -o ./models/rapidocr

Model files downloaded:
    - ch_PP-OCRv4_det_infer.onnx    (~4.5 MB) - Text detection
    - ch_PP-OCRv4_rec_infer.onnx    (~10 MB)  - Text recognition
    - ch_ppocr_mobile_v2.0_cls_infer.onnx (~1.4 MB) - Text orientation classification
    - ppocr_keys_v1.txt             (~300 KB) - Character dictionary (6000+ chars)
"""

import os
import sys
import urllib.request
import hashlib
from pathlib import Path
from typing import Optional

# Model URLs from HuggingFace RapidOCR repository
MODELS = {
    "ch_PP-OCRv4_det_infer.onnx": {
        "url": "https://huggingface.co/SWHL/RapidOCR/resolve/main/models/ch_PP-OCRv4_det_infer.onnx",
        "description": "Text detection model (PP-OCRv4)",
        "size_mb": 4.5,
    },
    "ch_PP-OCRv4_rec_infer.onnx": {
        "url": "https://huggingface.co/SWHL/RapidOCR/resolve/main/models/ch_PP-OCRv4_rec_infer.onnx",
        "description": "Text recognition model (PP-OCRv4)",
        "size_mb": 10,
    },
    "ch_ppocr_mobile_v2.0_cls_infer.onnx": {
        "url": "https://huggingface.co/SWHL/RapidOCR/resolve/main/models/ch_ppocr_mobile_v2.0_cls_infer.onnx",
        "description": "Text orientation classification model",
        "size_mb": 1.4,
    },
    "ppocr_keys_v1.txt": {
        "url": "https://huggingface.co/SWHL/RapidOCR/resolve/main/models/ppocr_keys_v1.txt",
        "description": "Character dictionary (6000+ characters)",
        "size_mb": 0.3,
    },
}


def download_file(url: str, dest: Path, description: str = "") -> bool:
    """Download a file with progress indication."""
    try:
        print(f"Downloading: {dest.name}")
        if description:
            print(f"  Description: {description}")
        print(f"  URL: {url}")
        
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                sys.stdout.write(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest, reporthook=show_progress)
        print()  # New line after progress
        return True
        
    except Exception as e:
        print(f"\n  ERROR: Failed to download {dest.name}: {e}")
        return False


def verify_models(output_dir: Path) -> bool:
    """Verify all required models are present."""
    print("\nVerifying models...")
    all_present = True
    
    for filename in MODELS.keys():
        filepath = output_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  [OK] {filename} ({size_mb:.2f} MB)")
        else:
            print(f"  [MISSING] {filename}")
            all_present = False
    
    return all_present


def download_models(output_dir: str = "./models/rapidocr", force: bool = False) -> bool:
    """
    Download all RapidOCR models.
    
    Args:
        output_dir: Directory to save models
        force: Force re-download even if files exist
    
    Returns:
        True if all models downloaded successfully
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("RapidOCR/PaddleOCR Model Downloader")
    print("=" * 60)
    print(f"\nOutput directory: {output_path.absolute()}")
    print(f"Total models to download: {len(MODELS)}")
    
    total_size = sum(m["size_mb"] for m in MODELS.values())
    print(f"Total size (approx): {total_size:.1f} MB")
    print()
    
    success_count = 0
    skip_count = 0
    
    for filename, info in MODELS.items():
        dest = output_path / filename
        
        if dest.exists() and not force:
            print(f"[SKIP] {filename} already exists")
            skip_count += 1
            success_count += 1
            continue
        
        if download_file(info["url"], dest, info["description"]):
            success_count += 1
            print(f"  [OK] Downloaded successfully")
        else:
            print(f"  [FAIL] Download failed")
    
    print()
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Total models: {len(MODELS)}")
    print(f"Downloaded: {success_count - skip_count}")
    print(f"Skipped (already exist): {skip_count}")
    print(f"Failed: {len(MODELS) - success_count}")
    
    if success_count == len(MODELS):
        print(f"\n[SUCCESS] All models saved to: {output_path.absolute()}")
        
        # Print usage instructions
        print("\n" + "=" * 60)
        print("Usage Instructions")
        print("=" * 60)
        print("""
To use these models with Docling OCR API:

1. Set environment variables:
   export DOCLING_OCR_ENGINE=rapidocr
   export DOCLING_RAPIDOCR_MODELS_PATH={output_path}

2. Or update .env file:
   DOCLING_OCR_ENGINE=rapidocr
   DOCLING_RAPIDOCR_MODELS_PATH={output_path}

3. For Kubernetes deployment, add volume mount:
   volumeMounts:
     - name: models-volume
       mountPath: /root/.cache/rapidocr/models
       subPath: rapidocr-models

4. For Docker, the docker-compose.yml already includes:
   - ../models/rapidocr:/root/.cache/rapidocr/models
""".format(output_path=output_path.absolute()))
        
        return True
    else:
        print("\n[WARNING] Some models failed to download. Please retry.")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download RapidOCR/PaddleOCR models for offline deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download to default location
    python download_rapidocr_models.py
    
    # Download to custom location
    python download_rapidocr_models.py -o /path/to/models
    
    # Force re-download
    python download_rapidocr_models.py --force
    
    # Verify existing models
    python download_rapidocr_models.py --verify
"""
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./models/rapidocr",
        help="Output directory for models (default: ./models/rapidocr)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if files exist"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify existing models, don't download"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        output_path = Path(args.output)
        if verify_models(output_path):
            print("\n[OK] All models present")
            sys.exit(0)
        else:
            print("\n[FAIL] Some models missing")
            sys.exit(1)
    
    success = download_models(args.output, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
