"""Advanced features endpoints - table extraction, chunking, etc."""

import logging
import tempfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.core.config import settings
from app.models.schemas import TableExtractionResult, ChunkResult, FormatInfo
from app.services.converter import DoclingConverterService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize converter
def get_converter():
    """Get converter instance with current settings"""
    ocr_config = {
        "enabled": settings.docling_ocr_enabled,
        "engine": settings.docling_ocr_engine,
        "languages": settings.get_ocr_languages(),
        "gpu": settings.docling_ocr_gpu,
        "force_full_page": settings.docling_ocr_force_full_page,
    }
    
    table_config = {
        "mode": settings.docling_table_mode,
        "cell_matching": settings.docling_table_cell_matching,
    }
    
    vlm_config = settings.get_vlm_config()
    
    return DoclingConverterService(
        pipeline_mode=settings.docling_pipeline_mode,
        artifacts_path=str(settings.get_artifacts_path()),
        ocr_config=ocr_config,
        vlm_config=vlm_config,
        table_config=table_config,
    )


converter = get_converter()


@router.post("/extract/tables", response_model=TableExtractionResult)
async def extract_tables(
    file: UploadFile = File(...),
):
    """
    Extract tables from document
    
    Returns structured table data with rows and columns
    
    Args:
        file: Document file (PDF, DOCX, etc.)
    
    Returns:
        Table extraction results
    """
    if not settings.enable_table_extraction:
        raise HTTPException(
            status_code=403,
            detail="Table extraction is disabled"
        )
    
    temp_file_path = None
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_upload_size} bytes"
            )
        
        # Save to temporary file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        ) as tmp_file:
            tmp_file.write(file_content)
            temp_file_path = Path(tmp_file.name)
        
        # Extract tables
        tables = converter.extract_tables(temp_file_path)
        
        return TableExtractionResult(
            file_name=file.filename,
            tables=tables,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting tables: {e}", exc_info=True)
        return TableExtractionResult(
            file_name=file.filename,
            tables=[],
            error=str(e)
        )
    
    finally:
        # Cleanup temp file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass


@router.post("/chunk", response_model=ChunkResult)
async def chunk_document(
    file: UploadFile = File(...),
    chunk_size: int = Query(1000, description="Chunk size in characters"),
    chunk_overlap: int = Query(200, description="Overlap between chunks"),
):
    """
    Convert and chunk document for RAG applications
    
    Returns document split into chunks with metadata
    
    Args:
        file: Document file
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between consecutive chunks
    
    Returns:
        Chunked document
    """
    if not settings.enable_chunking and chunk_size != settings.chunk_size:
        # Use default settings if chunking is not explicitly enabled
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap
    
    temp_file_path = None
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_upload_size} bytes"
            )
        
        # Save to temporary file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        ) as tmp_file:
            tmp_file.write(file_content)
            temp_file_path = Path(tmp_file.name)
        
        # Chunk document
        chunks = converter.chunk_document(
            temp_file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return ChunkResult(
            file_name=file.filename,
            chunks=chunks,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error chunking document: {e}", exc_info=True)
        return ChunkResult(
            file_name=file.filename,
            chunks=[],
            error=str(e)
        )
    
    finally:
        # Cleanup temp file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass


@router.get("/formats", response_model=FormatInfo)
async def get_supported_formats():
    """
    Get information about supported file formats
    
    Returns lists of supported input and output formats
    """
    from app.services.archive_handler import ArchiveHandler
    
    return FormatInfo(
        input_formats=sorted(list(converter.get_supported_extensions())),
        output_formats=["markdown", "html", "json", "doctags"],
        archive_formats=sorted(list(ArchiveHandler.ARCHIVE_EXTENSIONS)),
    )

