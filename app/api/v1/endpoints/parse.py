"""Parse base64-encoded documents endpoint"""

import logging
import tempfile
import base64
import zipfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.models.schemas import ParseRequest, ConversionResult
from app.services.converter_manager import get_converter_manager
from app.services.archive_handler import ArchiveHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
converter_manager = get_converter_manager()
archive_handler = ArchiveHandler()


@router.post("/parse", response_model=List[ConversionResult])
async def parse_documents(
    request: ParseRequest,
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
    output_format: str = Query("markdown", regex="^(markdown|html|json|doctags)$", description="Output format: markdown, html, json, doctags"),
    include_doc_tags: bool = Query(True, description="Include structured document data (doc tags) in response"),
    vlm_prompt: str = Query(None, description="Custom prompt for VLM pipeline (optional)"),
):
    """
    Parse base64-encoded documents and convert to Markdown (JSON response)

    Accepts multiple documents in base64 format and returns converted text.
    Supports both single files and archives.

    Args:
        request: Parse request with base64-encoded documents
        pipeline: Pipeline mode - "std" (standard) or "vlm"
        vlm_prompt: Custom prompt for VLM pipeline (optional, overrides default)

    Returns:
        List of conversion results as JSON
    """
    try:
        # Log conversion start
        logger.info(f"Starting batch document conversion", extra={
            "pipeline": pipeline,
            "document_count": len(request.docs),
            "vlm_prompt_provided": bool(vlm_prompt),
            "endpoint": "parse"
        })

        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
        results = []
        
        for doc in request.docs:
            try:
                # Decode base64
                file_bytes = base64.b64decode(doc.data)
                
                # Check file size
                if len(file_bytes) > settings.max_upload_size:
                    results.append(ConversionResult(
                        file_name=doc.filename,
                        file_extension=doc.type,
                        file_text="",
                        error=f"File too large. Max size: {settings.max_upload_size} bytes",
                        pipeline_used=pipeline,
                    ))
                    continue
                
                # Check if file is supported
                if not converter.is_supported_file(doc.filename):
                    # Check if it's an archive
                    if archive_handler.is_archive(doc.filename):
                        # Process archive
                        archive_results = await _process_archive_bytes_json(
                            file_bytes,
                            doc.filename,
                            pipeline,
                            output_format,
                            include_doc_tags
                        )
                        results.extend(archive_results)
                    else:
                        results.append(ConversionResult(
                            file_name=doc.filename,
                            file_extension=doc.type,
                            file_text="",
                            error=f"Unsupported file format: {doc.filename}",
                            pipeline_used=pipeline,
                        ))
                    continue
                
                # Convert file
                result_data = converter.convert_bytes(
                    file_bytes,
                    doc.filename,
                    output_format=output_format,
                    mime_type=doc.type
                )

                results.append(ConversionResult(
                    file_name=doc.filename,
                    file_extension=doc.type,
                    file_text=result_data["text"],
                    metadata=result_data.get("metadata"),
                    doc_tags=result_data.get("doc_tags") if include_doc_tags else None,
                    pipeline_used=pipeline,
                ))
                
            except Exception as e:
                logger.error(f"Error processing document {doc.filename}: {e}")
                results.append(ConversionResult(
                    file_name=doc.filename,
                    file_extension=doc.type,
                    file_text="",
                    error=str(e)
                ))
        
        return results
    
    except Exception as e:
        logger.error(f"Error processing parse request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse/md")
async def parse_documents_md(
    request: ParseRequest,
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
    structured: bool = Query(
        False,
        description="Preserve folder structure in archives"
    )
):
    """
    Parse base64-encoded documents and return as MD file(s)
    
    Returns single .md file or .zip archive with multiple MD files
    
    Args:
        request: Parse request with base64-encoded documents
        pipeline: Pipeline mode - "std" (standard) or "vlm"
        structured: Preserve folder structure in archives (default: false)
    
    Returns:
        MD file or ZIP archive with MD files
    """
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
        output_files = []
        
        for doc in request.docs:
            try:
                # Decode base64
                file_bytes = base64.b64decode(doc.data)
                
                # Check file size
                if len(file_bytes) > settings.max_upload_size:
                    continue
                
                # Check if file is supported
                if not converter.is_supported_file(doc.filename):
                    # Check if it's an archive
                    if archive_handler.is_archive(doc.filename):
                        # Process archive - returns list of (path, filename) tuples
                        archive_files = await _process_archive_bytes_md(
                            file_bytes,
                            doc.filename,
                            pipeline,
                            structured
                        )
                        output_files.extend(archive_files)
                    continue
                
                # Convert file
                result_data = converter.convert_bytes(
                    file_bytes,
                    doc.filename,
                    output_format="markdown",
                    mime_type=doc.type
                )
                
                # Save to temporary file
                md_filename = Path(doc.filename).stem + ".md"
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.md',
                    delete=False,
                    encoding='utf-8'
                ) as tmp_file:
                    tmp_file.write(result_data["text"])
                    output_files.append((tmp_file.name, md_filename))
                
            except Exception as e:
                logger.error(f"Error processing document {doc.filename}: {e}")
        
        # Return results
        if len(output_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="No files could be converted"
            )
        elif len(output_files) == 1:
            # Single file - return directly
            file_path, filename = output_files[0]
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="text/markdown"
            )
        else:
            # Multiple files - create archive
            zip_path = tempfile.mktemp(suffix='.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path, filename in output_files:
                    zip_ref.write(file_path, arcname=filename)
                    # Clean up temp file
                    try:
                        Path(file_path).unlink()
                    except:
                        pass
            
            def iter_file():
                with open(zip_path, 'rb') as f:
                    yield from f
                # Clean up zip file after sending
                try:
                    Path(zip_path).unlink()
                except:
                    pass
            
            response = StreamingResponse(
                iter_file(),
                media_type="application/zip"
            )
            response.headers["Content-Disposition"] = \
                'attachment; filename="converted_documents.zip"'
            
            return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing parse request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _process_archive_bytes_json(
    archive_bytes: bytes,
    filename: str,
    pipeline: str,
    output_format: str = "markdown",
    include_doc_tags: bool = True
) -> List[ConversionResult]:
    """Process archive from bytes and return JSON results"""
    
    extract_dir = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
        # Save archive to temp file
        with tempfile.NamedTemporaryFile(
            suffix=Path(filename).suffix,
            delete=False
        ) as tmp_archive:
            tmp_archive.write(archive_bytes)
            archive_path = Path(tmp_archive.name)
        
        # Extract archive
        extract_dir = Path(tempfile.mkdtemp(prefix='extract_'))
        archive_handler.extract_archive(
            archive_path,
            extract_dir,
            timeout=settings.extract_timeout
        )
        
        # Find all supported files
        supported_extensions = converter.get_supported_extensions()
        files = archive_handler.find_files_in_directory(
            extract_dir,
            supported_extensions,
            max_files=settings.max_files_in_archive
        )
        
        if not files:
            return [ConversionResult(
                file_name=filename,
                file_extension=Path(filename).suffix,
                file_text="",
                error="No supported files found in archive",
                pipeline_used=pipeline,
            )]
        
        # Convert all files
        results = []
        for file_path in files:
            try:
                result_data = converter.convert_file(
                    file_path,
                    output_format=output_format
                )
                results.append(ConversionResult(
                    file_name=str(file_path.relative_to(extract_dir)),
                    file_extension=file_path.suffix,
                    file_text=result_data["text"],
                    metadata=result_data.get("metadata"),
                    doc_tags=result_data.get("doc_tags") if include_doc_tags else None,
                    pipeline_used=pipeline,
                ))
            except Exception as e:
                logger.error(f"Error converting {file_path}: {e}")
                results.append(ConversionResult(
                    file_name=str(file_path.relative_to(extract_dir)),
                    file_extension=file_path.suffix,
                    file_text="",
                    error=str(e),
                    pipeline_used=pipeline,
                ))
        
        return results
        
    finally:
        # Cleanup
        if extract_dir:
            archive_handler.cleanup_directory(extract_dir)
        try:
            archive_path.unlink()
        except:
            pass


async def _process_archive_bytes_md(
    archive_bytes: bytes,
    filename: str,
    pipeline: str,
    structured: bool
) -> List[tuple]:
    """Process archive from bytes and return list of (path, filename) tuples"""
    
    extract_dir = None
    output_dir = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
        # Save archive to temp file
        with tempfile.NamedTemporaryFile(
            suffix=Path(filename).suffix,
            delete=False
        ) as tmp_archive:
            tmp_archive.write(archive_bytes)
            archive_path = Path(tmp_archive.name)
        
        # Extract archive
        extract_dir = Path(tempfile.mkdtemp(prefix='extract_'))
        archive_handler.extract_archive(
            archive_path,
            extract_dir,
            timeout=settings.extract_timeout
        )
        
        # Find all supported files
        supported_extensions = converter.get_supported_extensions()
        files = archive_handler.find_files_in_directory(
            extract_dir,
            supported_extensions,
            max_files=settings.max_files_in_archive
        )
        
        if not files:
            return []
        
        # Convert all files
        output_files = []
        output_dir = Path(tempfile.mkdtemp(prefix='output_'))
        
        for file_path in files:
            try:
                result_data = converter.convert_file(
                    file_path,
                    output_format="markdown"
                )
                
                # Determine output path
                if structured:
                    relative_path = file_path.relative_to(extract_dir)
                    output_path = output_dir / relative_path.with_suffix('.md')
                else:
                    output_path = output_dir / (file_path.stem + '.md')
                
                # Create directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save markdown file
                output_path.write_text(result_data["text"], encoding='utf-8')
                
                # Add to output list
                if structured:
                    arcname = str(relative_path.with_suffix('.md'))
                else:
                    arcname = output_path.name
                
                output_files.append((str(output_path), arcname))
                
            except Exception as e:
                logger.error(f"Error converting {file_path}: {e}")
        
        return output_files
        
    finally:
        # Cleanup
        if extract_dir:
            archive_handler.cleanup_directory(extract_dir)
        # Note: output_dir will be cleaned up after creating zip
        try:
            archive_path.unlink()
        except:
            pass

