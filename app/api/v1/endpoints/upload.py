"""Upload and convert files endpoint"""

import logging
import tempfile
import zipfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.models.schemas import ConversionResult
from app.services.converter_manager import get_converter_manager
from app.services.archive_handler import ArchiveHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
converter_manager = get_converter_manager()
archive_handler = ArchiveHandler()


@router.post("/upload", response_model=List[ConversionResult])
async def upload_file(
    file: UploadFile = File(...),
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
    ocr_mode: str = Query("auto", description="OCR mode: auto (detect), always, never"),
    output_format: str = Query("markdown", regex="^(markdown|html|json|doctags)$", description="Output format: markdown, html, json, doctags"),
    include_doc_tags: bool = Query(True, description="Include structured document data (doc tags) in response"),
    vlm_prompt: str = Query(None, description="Custom prompt for VLM pipeline (optional)"),
):
    """
    Upload and convert file (JSON response)

    Accepts single file or archive. Returns conversion results as JSON.

    Args:
        file: File to convert
        pipeline: Pipeline mode - "std" (standard) or "vlm" (Vision-Language Model)
        ocr_mode: OCR mode - "auto" (auto-detect for PDFs), "always", or "never" (only for std pipeline)
        output_format: Output format - "markdown", "html", "json", or "doctags"
        include_doc_tags: Include structured document data (doc tags) in response
        vlm_prompt: Custom prompt for VLM pipeline (optional, overrides default)

    Returns:
        List of conversion results with pipeline and OCR usage info
    """
    temp_file_path = None

    try:
        # Log conversion start
        file_content = await file.read()
        logger.info(f"Starting file conversion - Pipeline: {pipeline}, File: {file.filename}, Size: {len(file_content)} bytes", extra={
            "pipeline": pipeline,
            "file_name": file.filename,
            "file_size": len(file_content),
            "vlm_prompt_provided": bool(vlm_prompt),
            "endpoint": "upload"
        })
        
        if vlm_prompt:
            logger.info(f"Custom VLM prompt provided: {vlm_prompt[:100]}...")

        # Reset file pointer
        await file.seek(0)

        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
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
        
        # Check if it's an archive
        if archive_handler.is_archive(file.filename):
            results = await _process_archive_json(temp_file_path, file.filename, pipeline, ocr_mode, output_format, include_doc_tags, vlm_prompt)
        elif converter.is_supported_file(file.filename):
            # Convert single file
            result_data = converter.convert_with_auto_ocr(
                temp_file_path,
                output_format=output_format,
                ocr_mode=ocr_mode
            )

            # Add OCR info to metadata
            metadata = result_data.get("metadata", {})
            if "ocr_used" in result_data:
                metadata["ocr_used"] = result_data["ocr_used"]
            if "pdf_info" in result_data:
                metadata["pdf_info"] = result_data["pdf_info"]

            results = [ConversionResult(
                file_name=file.filename,
                file_extension=suffix,
                file_text=result_data["text"],
                metadata=metadata,
                doc_tags=result_data.get("doc_tags") if include_doc_tags else None,
                pipeline_used=pipeline,
            )]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file.filename}"
            )
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass


@router.post("/upload/md")
async def upload_file_md(
    file: UploadFile = File(...),
    pipeline: str = Query("std", regex="^(std|vlm)$", description="Pipeline mode: std (standard) or vlm"),
    structured: bool = Query(
        False,
        description="Preserve folder structure in archives"
    ),
    vlm_prompt: str = Query(None, description="Custom prompt for VLM pipeline (optional)"),
):
    """
    Upload and convert file - return as MD file(s)

    Returns single .md file or .zip archive with multiple MD files.

    Args:
        file: File to convert
        pipeline: Pipeline mode - "std" (standard) or "vlm"
        structured: Preserve folder structure in archives
        vlm_prompt: Custom prompt for VLM pipeline (optional, overrides default)

    Returns:
        MD file or ZIP archive
    """
    temp_file_path = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
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
        
        # Check if it's an archive
        if archive_handler.is_archive(file.filename):
            return await _process_archive_md(temp_file_path, file.filename, pipeline, structured, vlm_prompt)
        
        elif converter.is_supported_file(file.filename):
            # Convert single file
            result_data = converter.convert_with_auto_ocr(
                temp_file_path,
                output_format="markdown",
                ocr_mode="auto"  # Default to auto for MD endpoint
            )
            
            # Save to temporary MD file
            md_filename = Path(file.filename).stem + ".md"
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.md',
                delete=False,
                encoding='utf-8'
            ) as md_file:
                md_file.write(result_data["text"])
                md_path = md_file.name
            
            return FileResponse(
                path=md_path,
                filename=md_filename,
                media_type="text/markdown"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file.filename}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except:
                pass


async def _process_archive_json(
    archive_path: Path,
    filename: str,
    pipeline: str = "std",
    ocr_mode: str = "auto",
    output_format: str = "markdown",
    include_doc_tags: bool = True,
    vlm_prompt: str = None
) -> List[ConversionResult]:
    """Process archive and return JSON results"""
    
    extract_dir = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
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
                # Always use convert_with_auto_ocr for consistent result structure
                result_data = converter.convert_with_auto_ocr(
                    file_path,
                    output_format=output_format,
                    ocr_mode=ocr_mode
                )

                # Add OCR info to metadata
                metadata = result_data.get("metadata", {})
                if "ocr_used" in result_data:
                    metadata["ocr_used"] = result_data["ocr_used"]
                if "pdf_info" in result_data:
                    metadata["pdf_info"] = result_data["pdf_info"]

                results.append(ConversionResult(
                    file_name=str(file_path.relative_to(extract_dir)),
                    file_extension=file_path.suffix,
                    file_text=result_data["text"],
                    metadata=metadata,
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


async def _process_archive_md(
    archive_path: Path,
    filename: str,
    pipeline: str,
    structured: bool,
    vlm_prompt: str = None
):
    """Process archive and return as ZIP of MD files"""
    
    extract_dir = None
    output_dir = None
    
    try:
        # Get converter for specified pipeline
        converter = converter_manager.get_converter(pipeline, vlm_prompt)
        
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
            raise HTTPException(
                status_code=400,
                detail="No supported files found in archive"
            )
        
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
        
        # Create ZIP archive
        zip_path = tempfile.mktemp(suffix='.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for file_path, arcname in output_files:
                zip_ref.write(file_path, arcname=arcname)
        
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
            f'attachment; filename="converted_{Path(filename).stem}.zip"'
        
        return response
        
    finally:
        # Cleanup
        if extract_dir:
            archive_handler.cleanup_directory(extract_dir)
        if output_dir:
            archive_handler.cleanup_directory(output_dir)

