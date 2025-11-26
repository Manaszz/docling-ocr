"""Health check endpoint"""

import logging
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.services.converter_manager import get_converter_manager
from app import __version__

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns system status, version, and pipeline configuration info
    """
    try:
        # Get Docling version
        import docling
        docling_version = docling.__version__
    except:
        docling_version = "unknown"
    
    # Get converter manager status
    try:
        manager = get_converter_manager()
        pipeline_status = manager.get_status()
    except Exception as e:
        logger.error(f"Error getting converter manager status: {e}")
        pipeline_status = {
            "initialized": False,
            "standard": {"available": True, "loaded": False},
            "vlm": {"available": False, "loaded": False, "enabled": False, "model": None}
        }
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        default_pipeline="std",  # Default is always standard
        docling_version=docling_version,
        pipelines=pipeline_status,
        ocr_enabled=settings.docling_ocr_enabled,
        vlm_enabled=pipeline_status["vlm"]["available"],
        models_loaded=pipeline_status["standard"]["loaded"],
    )

