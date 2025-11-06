"""Pydantic models for API requests and responses"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    """Single document input for parsing"""
    filename: str = Field(..., description="Original filename")
    data: str = Field(..., description="Base64-encoded file data")
    type: str = Field(..., description="MIME type")


class ParseRequest(BaseModel):
    """Request model for parsing base64-encoded documents"""
    is_base64_or_document: bool = Field(
        True,
        description="Whether the data is base64-encoded"
    )
    docs: List[DocumentInput] = Field(..., description="List of documents to parse")


class ConversionResult(BaseModel):
    """Result of document conversion"""
    file_name: str = Field(..., description="Original filename")
    file_extension: str = Field(..., description="File extension or MIME type")
    file_text: str = Field(..., description="Converted markdown text")
    error: Optional[str] = Field(None, description="Error message if conversion failed")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Document metadata (page count, tables, etc.)"
    )
    pipeline_used: Optional[str] = Field(None, description="Pipeline used for conversion (std/vlm)")


class TableExtractionResult(BaseModel):
    """Result of table extraction"""
    file_name: str
    tables: List[Dict[str, Any]] = Field(
        ...,
        description="List of extracted tables with structure"
    )
    error: Optional[str] = None


class ChunkResult(BaseModel):
    """Result of document chunking"""
    file_name: str
    chunks: List[Dict[str, Any]] = Field(
        ...,
        description="List of text chunks with metadata"
    )
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    default_pipeline: str = Field(..., description="Default pipeline mode (std/vlm)")
    docling_version: Optional[str] = Field(None, description="Docling library version")
    pipelines: Dict[str, Any] = Field(..., description="Status of available pipelines")
    ocr_enabled: bool = Field(..., description="Whether OCR is enabled in standard pipeline")
    vlm_enabled: bool = Field(..., description="Whether VLM pipeline is available")


class PipelineConfig(BaseModel):
    """Pipeline configuration"""
    mode: str = Field(..., description="Pipeline mode: standard or vlm")
    ocr_enabled: Optional[bool] = None
    ocr_engine: Optional[str] = None
    ocr_languages: Optional[List[str]] = None
    vlm_enabled: Optional[bool] = None
    vlm_model: Optional[str] = None


class FormatInfo(BaseModel):
    """Information about supported formats"""
    input_formats: List[str] = Field(..., description="Supported input file formats")
    output_formats: List[str] = Field(..., description="Supported output formats")
    archive_formats: List[str] = Field(..., description="Supported archive formats")

