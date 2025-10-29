"""Pipeline configuration endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import PipelineConfig
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class OCRToggle(BaseModel):
    """OCR toggle request"""
    enabled: bool


@router.get("", response_model=PipelineConfig)
async def get_pipeline_config():
    """
    Get current pipeline configuration
    
    Returns information about the active pipeline mode and settings
    """
    return PipelineConfig(
        mode=settings.docling_pipeline_mode,
        ocr_enabled=settings.docling_ocr_enabled if settings.docling_pipeline_mode == "standard" else None,
        ocr_engine=settings.docling_ocr_engine if settings.docling_pipeline_mode == "standard" else None,
        ocr_languages=settings.get_ocr_languages() if settings.docling_pipeline_mode == "standard" else None,
        vlm_enabled=settings.docling_vlm_enabled if settings.docling_pipeline_mode == "vlm" else None,
        vlm_model=settings.docling_vlm_model if settings.docling_pipeline_mode == "vlm" else None,
    )


@router.post("", response_model=PipelineConfig)
async def set_pipeline_config(config: PipelineConfig):
    """
    Set pipeline configuration
    
    Note: This changes the configuration for the current instance only.
    For permanent changes, modify the .env file.
    
    Args:
        config: New pipeline configuration
    
    Returns:
        Updated pipeline configuration
    """
    if config.mode not in ["standard", "vlm"]:
        raise HTTPException(
            status_code=400,
            detail="Pipeline mode must be 'standard' or 'vlm'"
        )
    
    # Update settings
    settings.docling_pipeline_mode = config.mode
    
    if config.ocr_enabled is not None:
        settings.docling_ocr_enabled = config.ocr_enabled
    
    if config.ocr_engine is not None:
        settings.docling_ocr_engine = config.ocr_engine
    
    if config.vlm_enabled is not None:
        settings.docling_vlm_enabled = config.vlm_enabled
    
    if config.vlm_model is not None:
        settings.docling_vlm_model = config.vlm_model
    
    logger.info(f"Pipeline configuration updated to {config.mode} mode")
    
    # Note: Converter needs to be reinitialized for changes to take effect
    # This would require a service restart in production
    
    return await get_pipeline_config()


@router.post("/ocr/toggle")
async def toggle_ocr(toggle: OCRToggle):
    """
    Toggle OCR on/off
    
    Args:
        toggle: OCR toggle request
    
    Returns:
        Current OCR status
    """
    settings.docling_ocr_enabled = toggle.enabled
    
    logger.info(f"OCR {'enabled' if toggle.enabled else 'disabled'} via API")
    
    # Note: Service restart required for changes to take full effect
    
    return {
        "ocr_enabled": settings.docling_ocr_enabled,
        "message": f"OCR {'enabled' if toggle.enabled else 'disabled'}. Service restart recommended.",
        "restart_required": True
    }

