"""Advanced features endpoints - table extraction, chunking, etc."""

import logging
import tempfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.core.config import settings
from app.models.schemas import TableExtractionResult, ChunkResult, FormatInfo
from app.services.converter_manager import get_converter_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize converter manager
converter_manager = get_converter_manager()


@router.post("/extract/tables", response_model=TableExtractionResult)
async def extract_tables(
    file: UploadFile = File(...),
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
):
    """
    Extract tables from document
    
    Returns structured table data with rows and columns
    
    Args:
        file: Document file (PDF, DOCX, etc.)
        pipeline: Pipeline mode - "std" (standard) or "vlm"
    
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
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline)
        
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
        result = converter.extract_tables(temp_file_path)

        return TableExtractionResult(
            file_name=file.filename,
            tables=result["tables"],
            doc_tags=result.get("doc_tags"),
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
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
    chunk_size: int = Query(1000, description="Chunk size in characters (for mode=0)"),
    chunk_overlap: int = Query(200, description="Overlap between chunks (for mode=0)"),
    chunking_mode: int = Query(None, description="Chunking mode: 0=simple, 1=hierarchical, 2=hybrid"),
    max_tokens: int = Query(None, description="Maximum tokens per chunk (for mode=2)"),
    merge_list_items: bool = Query(None, description="Merge list items into single chunk (for mode=1)"),
    merge_peers: bool = Query(None, description="Merge peer chunks in same section (for mode=2)"),
):
    """
    Convert and chunk document for RAG applications
    
    Returns document split into chunks with metadata
    
    Args:
        file: Document file
        pipeline: Pipeline mode - "std" (standard) or "vlm"
        chunk_size: Maximum chunk size in characters (for mode=0, simple chunking)
        chunk_overlap: Overlap between consecutive chunks (for mode=0, simple chunking)
        chunking_mode: Chunking mode - 0=simple (character-based), 1=hierarchical (semantic), 2=hybrid (hierarchical + tokens)
        max_tokens: Maximum tokens per chunk (for mode=2, hybrid chunking)
        merge_list_items: Merge list items into single chunk (for mode=1, hierarchical chunking)
        merge_peers: Merge peer chunks in same section (for mode=2, hybrid chunking)
    
    Returns:
        Chunked document
    """
    # Use default values from settings if not provided (backward compatibility)
    if chunking_mode is None:
        chunking_mode = settings.chunking_mode
    
    if max_tokens is None and chunking_mode == 2:
        max_tokens = settings.chunking_max_tokens
    
    if merge_list_items is None:
        merge_list_items = settings.chunking_merge_list_items
    
    if merge_peers is None:
        merge_peers = settings.chunking_merge_peers
    
    # For backward compatibility: if chunking_mode is 0 and enable_chunking is False,
    # use default chunk_size and chunk_overlap from settings
    if chunking_mode == 0 and not settings.enable_chunking and chunk_size == 1000:
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap
    
    temp_file_path = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline)
        
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
        
        # Chunk document with all parameters
        chunks = converter.chunk_document(
            temp_file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_mode=chunking_mode,
            max_tokens=max_tokens,
            merge_list_items=merge_list_items,
            merge_peers=merge_peers
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
    from app.services.converter import DoclingConverterService
    
    return FormatInfo(
        input_formats=sorted(list(DoclingConverterService.get_supported_extensions())),
        output_formats=["markdown", "html", "json", "doctags"],
        archive_formats=sorted(list(ArchiveHandler.ARCHIVE_EXTENSIONS)),
    )

