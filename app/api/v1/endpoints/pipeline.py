"""Pipeline configuration endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.core.config import settings
from app.services.converter_manager import get_converter_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class OCRToggle(BaseModel):
    """OCR toggle request"""
    enabled: bool


@router.get("")
async def get_pipeline_status() -> Dict[str, Any]:
    """
    Get current pipeline status
    
    Returns information about both pipeline modes and their availability.
    Note: With dual pipeline support, you can use either pipeline via ?pipeline= parameter.
    """
    manager = get_converter_manager()
    status = manager.get_status()
    
    return {
        "pipelines": {
            "std": {
                "name": "Standard Pipeline",
                "available": status["standard"]["available"],
                "loaded": status["standard"]["loaded"],
                "ocr_enabled": settings.docling_ocr_enabled,
                "ocr_engine": settings.docling_ocr_engine,
                "ocr_languages": settings.get_ocr_languages(),
            },
            "vlm": {
                "name": "VLM Pipeline",
                "available": status["vlm"]["available"],
                "loaded": status["vlm"]["loaded"],
                "enabled": status["vlm"]["enabled"],
                "model": status["vlm"]["model"],
            }
        },
        "usage": {
            "info": "Both pipelines available simultaneously",
            "parameter": "Use ?pipeline=std or ?pipeline=vlm on any endpoint",
            "default": "std (standard pipeline)"
        }
    }


@router.post("/ocr/toggle")
async def toggle_ocr(toggle: OCRToggle):
    """
    Toggle OCR on/off for standard pipeline
    
    Args:
        toggle: OCR toggle request
    
    Returns:
        Current OCR status
    
    Note: Changes affect new converter instances. Already loaded converters not affected.
    """
    settings.docling_ocr_enabled = toggle.enabled
    
    logger.info(f"OCR {'enabled' if toggle.enabled else 'disabled'} via API")
    
    return {
        "ocr_enabled": settings.docling_ocr_enabled,
        "message": f"OCR {'enabled' if toggle.enabled else 'disabled'} for standard pipeline.",
        "note": "Affects new requests only. Service restart recommended for full effect."
    }

