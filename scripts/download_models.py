#!/usr/bin/env python3
"""
Download Docling models for offline use

This script downloads all necessary Docling models to a local directory
for use in air-gapped/offline environments.
"""

import argparse
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_models(output_dir: str = "./models", force: bool = False):
    """
    Download all Docling models
    
    Args:
        output_dir: Directory to save models
        force: Force re-download even if models exist
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading Docling models to: {output_path.absolute()}")
    
    try:
        # Import docling utilities
        from docling.utils.model_downloader import download_models as dl_models
        
        logger.info("Starting model download...")
        
        # Download all models
        dl_models(
            output_dir=output_path,
            force=force,
            with_easyocr=True,  # Include EasyOCR models
            progress=True
        )
        
        logger.info("✓ Model download completed successfully!")
        logger.info(f"Models saved to: {output_path.absolute()}")
        logger.info("\nTo use these models, set environment variable:")
        logger.info(f"  DOCLING_ARTIFACTS_PATH={output_path.absolute()}")
        
        return True
        
    except ImportError as e:
        logger.error("Failed to import docling. Please install docling first:")
        logger.error("  pip install docling")
        return False
        
    except Exception as e:
        logger.error(f"Error downloading models: {e}")
        return False


def verify_models(models_dir: str = "./models"):
    """
    Verify that models are downloaded and accessible
    
    Args:
        models_dir: Directory containing models
    """
    models_path = Path(models_dir)
    
    if not models_path.exists():
        logger.error(f"Models directory not found: {models_path}")
        return False
    
    logger.info(f"Checking models in: {models_path.absolute()}")
    
    # Check for expected model files/directories
    expected_items = [
        "layout",
        "tableformer",
    ]
    
    found_items = []
    for item in expected_items:
        item_path = models_path / item
        if item_path.exists():
            found_items.append(item)
            logger.info(f"  ✓ Found: {item}")
        else:
            logger.warning(f"  ✗ Missing: {item}")
    
    if found_items:
        logger.info(f"\nFound {len(found_items)}/{len(expected_items)} model components")
        return True
    else:
        logger.error("No models found!")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download Docling models for offline use"
    )
    parser.add_argument(
        "-o", "--output",
        default="./models",
        help="Output directory for models (default: ./models)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force re-download even if models exist"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing models instead of downloading"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_models(args.output)
    else:
        success = download_models(args.output, args.force)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

