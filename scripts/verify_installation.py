#!/usr/bin/env python3
"""
Verify Docling OCR installation

This script checks that all dependencies and components are properly installed.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check Python version"""
    logger.info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        logger.info(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"  ✗ Python {version.major}.{version.minor} (requires 3.10+)")
        return False


def check_dependencies():
    """Check required Python packages"""
    logger.info("Checking Python dependencies...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("docling", "Docling"),
        ("easyocr", "EasyOCR"),
        ("PIL", "Pillow"),
        ("cv2", "OpenCV"),
    ]
    
    all_good = True
    
    for module_name, display_name in required_packages:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            logger.info(f"  ✓ {display_name} ({version})")
        except ImportError:
            logger.error(f"  ✗ {display_name} (not installed)")
            all_good = False
    
    return all_good


def check_models(models_dir="./models"):
    """Check if Docling models are downloaded"""
    logger.info("Checking Docling models...")
    
    models_path = Path(models_dir)
    
    if not models_path.exists():
        logger.warning(f"  ✗ Models directory not found: {models_path}")
        logger.info("    Run: python scripts/download_models.py")
        return False
    
    # Check for model subdirectories
    has_models = any(models_path.iterdir())
    
    if has_models:
        logger.info(f"  ✓ Models directory exists: {models_path.absolute()}")
        return True
    else:
        logger.warning("  ✗ Models directory is empty")
        logger.info("    Run: python scripts/download_models.py")
        return False


def check_directories():
    """Check required directories"""
    logger.info("Checking directories...")
    
    required_dirs = [
        "app",
        "app/api",
        "app/core",
        "app/models",
        "app/services",
        "temp",
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            logger.info(f"  ✓ {dir_name}/")
        else:
            logger.error(f"  ✗ {dir_name}/ (missing)")
            all_good = False
    
    return all_good


def check_env_file():
    """Check environment configuration"""
    logger.info("Checking environment configuration...")
    
    if Path(".env").exists():
        logger.info("  ✓ .env file exists")
        return True
    elif Path("env.example").exists():
        logger.warning("  ✗ .env file not found")
        logger.info("    Copy env.example to .env and configure:")
        logger.info("    cp env.example .env")
        return False
    else:
        logger.error("  ✗ No environment files found")
        return False


def main():
    logger.info("=" * 60)
    logger.info("Docling OCR Installation Verification")
    logger.info("=" * 60)
    logger.info("")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Models", check_models()),
        ("Directories", check_directories()),
        ("Environment", check_env_file()),
    ]
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    
    for name, status in checks:
        status_str = "✓ PASS" if status else "✗ FAIL"
        logger.info(f"{name:.<40} {status_str}")
    
    all_passed = all(status for _, status in checks)
    
    logger.info("")
    if all_passed:
        logger.info("✓ All checks passed! Installation is ready.")
        logger.info("")
        logger.info("To start the service:")
        logger.info("  uvicorn app.main:app --host 0.0.0.0 --port 8002")
        logger.info("Or with Docker:")
        logger.info("  docker-compose up -d")
        return 0
    else:
        logger.error("✗ Some checks failed. Please resolve the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

