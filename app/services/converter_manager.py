"""Converter Manager for handling multiple pipeline modes"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from app.services.converter import DoclingConverterService
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConverterManager:
    """Manages multiple converter instances (standard and VLM pipelines)"""
    
    def __init__(self):
        self._converters: Dict[str, Optional[DoclingConverterService]] = {
            "std": None,
            "vlm": None
        }
        self._initialized = False
    
    def initialize(self):
        """Initialize standard converter (VLM is lazy-loaded)"""
        if self._initialized:
            return
        
        logger.info("Initializing ConverterManager...")
        
        # Always initialize standard pipeline
        try:
            self._converters["std"] = self._create_standard_converter()
            logger.info("Standard pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize standard pipeline: {e}")
            raise
        
        self._initialized = True
        logger.info("ConverterManager initialization complete")
    
    def get_converter(self, pipeline: str = "std", custom_vlm_prompt: Optional[str] = None) -> DoclingConverterService:
        """
        Get converter instance for specified pipeline

        Args:
            pipeline: Pipeline mode - "std" (standard) or "vlm"
            custom_vlm_prompt: Custom prompt for VLM pipeline (optional)

        Returns:
            DoclingConverterService instance

        Raises:
            ValueError: If pipeline is invalid or VLM not configured
        """
        if pipeline not in ["std", "vlm"]:
            raise ValueError(f"Invalid pipeline mode: {pipeline}. Must be 'std' or 'vlm'")
        
        # Ensure manager is initialized
        if not self._initialized:
            self.initialize()
        
        # Get or create converter
        converter = self._converters.get(pipeline)

        # Log converter usage
        logger.info(f"ConverterManager.get_converter called - Pipeline: '{pipeline}', Custom prompt: {bool(custom_vlm_prompt)}")
        
        if custom_vlm_prompt:
            logger.info(f"Using {pipeline} pipeline with custom VLM prompt", extra={
                "pipeline": pipeline,
                "custom_prompt": True,
                "prompt_preview": custom_vlm_prompt[:50] + ("..." if len(custom_vlm_prompt) > 50 else "")
            })
        else:
            logger.info(f"Using {pipeline} pipeline (default prompt)", extra={
                "pipeline": pipeline,
                "custom_prompt": False
            })

        if converter is None:
            if pipeline == "vlm":
                # Lazy initialization for VLM
                logger.info("Lazy-loading VLM pipeline...")
                try:
                    converter = self._create_vlm_converter(custom_vlm_prompt)
                    self._converters["vlm"] = converter
                    logger.info("VLM pipeline initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize VLM pipeline: {e}")
                    raise ValueError(
                        f"VLM pipeline not available: {str(e)}. "
                        "Please check VLM configuration (DOCLING_VLM_ENABLED, DOCLING_VLM_API_URL)"
                    )
            else:
                raise RuntimeError(f"Standard pipeline not initialized")
        
        return converter
    
    def _create_standard_converter(self) -> DoclingConverterService:
        """Create standard pipeline converter"""
        ocr_config = {
            "enabled": settings.docling_ocr_enabled,
            "engine": settings.docling_ocr_engine,
            "languages": settings.get_ocr_languages(),
            "gpu": settings.docling_ocr_gpu,
            "force_full_page": settings.docling_ocr_force_full_page,
            # RapidOCR specific configuration
            "rapidocr": settings.get_rapidocr_config(),
        }
        
        table_config = {
            "mode": settings.docling_table_mode,
            "cell_matching": settings.docling_table_cell_matching,
        }
        
        return DoclingConverterService(
            pipeline_mode="standard",
            artifacts_path=str(settings.get_artifacts_path()),
            ocr_config=ocr_config,
            vlm_config=None,
            table_config=table_config,
        )
    
    def _create_vlm_converter(self, custom_vlm_prompt: Optional[str] = None) -> DoclingConverterService:
        """Create VLM pipeline converter"""
        if not settings.docling_vlm_enabled:
            raise ValueError("VLM pipeline is disabled in configuration")

        vlm_config = settings.get_vlm_config()
        if not vlm_config:
            raise ValueError("VLM configuration not available")

        return DoclingConverterService(
            pipeline_mode="vlm",
            artifacts_path=str(settings.get_artifacts_path()),
            ocr_config=None,
            vlm_config=vlm_config,
            table_config=None,
            custom_vlm_prompt=custom_vlm_prompt,
        )
    
    def is_pipeline_available(self, pipeline: str) -> bool:
        """Check if pipeline is available"""
        if pipeline == "std":
            return True  # Standard always available
        elif pipeline == "vlm":
            return settings.docling_vlm_enabled and bool(settings.get_vlm_config())
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all pipelines"""
        return {
            "initialized": self._initialized,
            "standard": {
                "available": True,
                "loaded": self._converters.get("std") is not None
            },
            "vlm": {
                "available": self.is_pipeline_available("vlm"),
                "loaded": self._converters.get("vlm") is not None,
                "enabled": settings.docling_vlm_enabled,
                "model": settings.docling_vlm_model if settings.docling_vlm_enabled else None
            }
        }


# Global converter manager instance
converter_manager = ConverterManager()


def get_converter_manager() -> ConverterManager:
    """Get the global converter manager instance"""
    if not converter_manager._initialized:
        converter_manager.initialize()
    return converter_manager

