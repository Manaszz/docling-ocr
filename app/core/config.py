"""Application configuration"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_version: str = "1.1.0"
    api_title: str = "Docling OCR API"
    api_description: str = "API for converting documents to Markdown using Docling"
    api_prefix: str = "/ocr/docling"
    
    # Localization
    default_language: str = "ru"  # ru or en
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8002
    workers: int = 4
    log_level: str = "info"
    
    # File Upload Limits
    max_upload_size: int = 104857600  # 100MB
    max_files_in_archive: int = 100
    temp_files_ttl: int = 3600
    temp_dir: str = "temp"
    
    # Docling Configuration
    docling_artifacts_path: str = "./models"
    docling_pipeline_mode: str = "standard"  # standard or vlm
    
    # OCR Configuration (Standard Pipeline)
    docling_ocr_enabled: bool = True
    docling_ocr_engine: str = "easyocr"  # easyocr, tesseract, rapidocr
    docling_ocr_languages: str = "en,ru"
    docling_ocr_gpu: bool = False
    docling_ocr_force_full_page: bool = False
    
    # Table Processing
    docling_table_mode: str = "accurate"  # fast or accurate
    docling_table_cell_matching: bool = True
    
    # VLM Configuration (VLM Pipeline)
    docling_vlm_enabled: bool = False
    docling_vlm_api_url: str = "http://localhost:8000/v1/chat/completions"
    docling_vlm_api_key: str = "not-needed"
    docling_vlm_model: str = "qwen-vl-3b"
    docling_vlm_timeout: int = 90
    docling_vlm_temperature: float = 0.0
    docling_vlm_max_tokens: int = 4096
    docling_vlm_response_format: str = "markdown"  # markdown, html, doctags
    docling_vlm_prompt: str = "Convert this page to docling."  # Original Docling default: "Convert this page to docling."
    
    # Archive Processing
    preserve_structure: bool = True
    extract_timeout: int = 300
    
    # Output Configuration
    default_output_format: str = "markdown"  # markdown, html, json, doctags
    enable_chunking: bool = False
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Chunking Configuration
    chunking_mode: int = 0  # 0=simple (character-based), 1=hierarchical (semantic), 2=hybrid (hierarchical + tokens)
    chunking_max_tokens: int = 512  # Maximum tokens per chunk for hybrid mode (mode=2)
    chunking_merge_list_items: bool = True  # Merge list items into single chunk for hierarchical mode (mode=1)
    chunking_merge_peers: bool = True  # Merge peer chunks in same section for hybrid mode (mode=2)
    
    # Advanced Features
    enable_table_extraction: bool = True
    enable_visual_grounding: bool = False
    enable_metadata_extraction: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_ocr_languages(self) -> List[str]:
        """Parse OCR languages from comma-separated string"""
        return [lang.strip() for lang in self.docling_ocr_languages.split(",")]
    
    def get_vlm_config(self) -> Optional[dict]:
        """Get VLM configuration if enabled"""
        if not self.docling_vlm_enabled:
            return None

        return {
            "api_url": self.docling_vlm_api_url,
            "api_key": self.docling_vlm_api_key,
            "model": self.docling_vlm_model,
            "timeout": self.docling_vlm_timeout,
            "temperature": self.docling_vlm_temperature,
            "max_tokens": self.docling_vlm_max_tokens,
            "response_format": self.docling_vlm_response_format,
            "prompt": self.docling_vlm_prompt,
        }
    
    def get_artifacts_path(self) -> Path:
        """Get absolute path to artifacts directory"""
        path = Path(self.docling_artifacts_path)
        if not path.is_absolute():
            # Make relative to project root
            path = Path(__file__).parent.parent.parent / path
        return path
    
    def get_chunking_mode_name(self, mode: Optional[int] = None) -> str:
        """Get human-readable name for chunking mode"""
        if mode is None:
            mode = self.chunking_mode
        
        mode_names = {
            0: "simple",
            1: "hierarchical",
            2: "hybrid"
        }
        return mode_names.get(mode, "simple")


# Global settings instance
settings = Settings()

