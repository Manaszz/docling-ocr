"""Health check endpoint"""

import logging
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from app import __version__

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns system status, version, and configuration info
    """
    try:
        # Get Docling version
        import docling
        docling_version = docling.__version__
    except:
        docling_version = "unknown"
    
    # Check if models are loaded (simplified check)
    models_loaded = True
    try:
        artifacts_path = settings.get_artifacts_path()
        models_loaded = artifacts_path.exists() if artifacts_path else False
    except:
        models_loaded = False
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        pipeline_mode=settings.docling_pipeline_mode,
        docling_version=docling_version,
        models_loaded=models_loaded,
        ocr_enabled=settings.docling_ocr_enabled,
        vlm_enabled=settings.docling_vlm_enabled,
    )

