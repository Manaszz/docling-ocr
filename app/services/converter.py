"""Document conversion service using Docling"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat

logger = logging.getLogger(__name__)


class DoclingConverterService:
    """Service for converting documents using Docling"""
    
    def __init__(
        self,
        pipeline_mode: str = "standard",
        artifacts_path: Optional[str] = None,
        ocr_config: Optional[Dict[str, Any]] = None,
        vlm_config: Optional[Dict[str, Any]] = None,
        table_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Docling converter
        
        Args:
            pipeline_mode: Pipeline mode - 'standard' or 'vlm'
            artifacts_path: Path to Docling models
            ocr_config: OCR configuration dict
            vlm_config: VLM configuration dict
            table_config: Table processing configuration
        """
        self.pipeline_mode = pipeline_mode
        self.artifacts_path = artifacts_path
        self.ocr_config = ocr_config or {}
        self.vlm_config = vlm_config or {}
        self.table_config = table_config or {}
        self._converter = None
        self._initialize_converter()
    
    def _initialize_converter(self):
        """Initialize DocumentConverter with appropriate pipeline"""
        try:
            if self.pipeline_mode == "vlm":
                self._converter = self._create_vlm_converter()
            else:
                self._converter = self._create_standard_converter()
            
            logger.info(f"Initialized Docling converter in {self.pipeline_mode} mode")
        
        except Exception as e:
            logger.error(f"Error initializing converter: {e}")
            raise
    
    def _create_standard_converter(self) -> DocumentConverter:
        """Create converter with StandardPdfPipeline"""
        
        # Configure OCR
        ocr_enabled = self.ocr_config.get("enabled", True)
        ocr_engine = self.ocr_config.get("engine", "easyocr")
        ocr_languages = self.ocr_config.get("languages", ["en", "ru"])
        ocr_gpu = self.ocr_config.get("gpu", False)
        force_full_page = self.ocr_config.get("force_full_page", False)
        
        # Configure table processing
        table_mode_str = self.table_config.get("mode", "accurate")
        table_mode = (
            TableFormerMode.ACCURATE
            if table_mode_str == "accurate"
            else TableFormerMode.FAST
        )
        do_cell_matching = self.table_config.get("cell_matching", True)
        
        # Create pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = ocr_enabled
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options = TableStructureOptions(
            mode=table_mode,
            do_cell_matching=do_cell_matching,
        )
        
        # Set artifacts path if provided
        if self.artifacts_path:
            pipeline_options.artifacts_path = self.artifacts_path
        
        # Configure OCR engine
        if ocr_enabled and ocr_engine == "easyocr":
            ocr_options = EasyOcrOptions(
                lang=ocr_languages,
                use_gpu=ocr_gpu,
                force_full_page_ocr=force_full_page,
            )
            pipeline_options.ocr_options = ocr_options
        
        # Create converter
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline,
                    pipeline_options=pipeline_options,
                )
            }
        )
        
        return converter
    
    def _create_vlm_converter(self) -> DocumentConverter:
        """Create converter with VlmPipeline"""
        
        if not self.vlm_config:
            raise ValueError("VLM configuration is required for VLM pipeline mode")
        
        # Map response format
        response_format_map = {
            "markdown": ResponseFormat.MARKDOWN,
            "html": ResponseFormat.HTML,
            "doctags": ResponseFormat.DOCTAGS,
        }
        response_format = response_format_map.get(
            self.vlm_config.get("response_format", "markdown"),
            ResponseFormat.MARKDOWN
        )
        
        # Create VLM options
        vlm_options = ApiVlmOptions(
            url=self.vlm_config.get("api_url"),
            params=dict(
                model=self.vlm_config.get("model", "qwen-vl-3b"),
                max_tokens=self.vlm_config.get("max_tokens", 4096),
                temperature=self.vlm_config.get("temperature", 0.0),
            ),
            headers={"Authorization": f"Bearer {self.vlm_config.get('api_key', '')}"},
            prompt="Convert this document page to markdown format.",
            timeout=self.vlm_config.get("timeout", 90),
            response_format=response_format,
        )
        
        # Create pipeline options
        from docling.datamodel.pipeline_options import VlmPipelineOptions
        
        pipeline_options = VlmPipelineOptions(
            vlm_options=vlm_options,
            enable_remote_services=True,
        )
        
        # Set artifacts path if provided
        if self.artifacts_path:
            pipeline_options.artifacts_path = self.artifacts_path
        
        # Create converter
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                )
            }
        )
        
        return converter
    
    def convert_file(
        self,
        file_path: str | Path,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Convert a file to the specified format
        
        Args:
            file_path: Path to file to convert
            output_format: Output format (markdown, html, json, doctags)
        
        Returns:
            Dict with 'text' and optional 'metadata'
        """
        try:
            file_path = Path(file_path)
            
            # Convert document
            result = self._converter.convert(str(file_path))
            
            # Extract text based on format
            if output_format == "markdown":
                text = result.document.export_to_markdown()
            elif output_format == "html":
                text = result.document.export_to_html()
            elif output_format == "json":
                text = result.document.export_to_json()
            elif output_format == "doctags":
                text = result.document.export_to_doctags()
            else:
                # Default to markdown
                text = result.document.export_to_markdown()
            
            # Extract metadata
            metadata = self._extract_metadata(result)
            
            return {
                "text": text,
                "metadata": metadata,
            }
        
        except Exception as e:
            logger.error(f"Error converting file {file_path}: {e}")
            raise
    
    def convert_with_auto_ocr(
        self,
        file_path: str | Path,
        output_format: str = "markdown",
        ocr_mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Convert file with automatic OCR detection for PDFs
        
        Args:
            file_path: Path to file to convert
            output_format: Output format (markdown, html, json, doctags)
            ocr_mode: OCR mode - "auto", "always", "never"
                - auto: detect if PDF is scanned and use OCR accordingly
                - always: always use OCR
                - never: never use OCR
        
        Returns:
            Dict with 'text', 'metadata', and 'ocr_used' flag
        """
        file_path = Path(file_path)
        
        # Determine if OCR should be used
        should_use_ocr = self.ocr_config.get("enabled", True)  # Current setting
        pdf_info = None
        
        if file_path.suffix.lower() == '.pdf' and ocr_mode == "auto":
            # Auto-detect for PDFs
            try:
                from app.utils.pdf_detector import is_pdf_scanned, get_pdf_info
                
                is_scan = is_pdf_scanned(file_path)
                pdf_info = get_pdf_info(file_path)
                
                logger.info(
                    f"PDF auto-detection: is_scan={is_scan}, "
                    f"pages={pdf_info.get('total_pages', 0)}, "
                    f"text_density={pdf_info.get('text_density', 0):.1f}"
                )
                
                should_use_ocr = is_scan
                
            except Exception as e:
                logger.warning(f"Failed to auto-detect PDF type, using current OCR setting: {e}")
        
        elif ocr_mode == "always":
            should_use_ocr = True
        elif ocr_mode == "never":
            should_use_ocr = False
        
        # If OCR setting differs from current, create new converter temporarily
        current_ocr = self.ocr_config.get("enabled", True)
        
        if should_use_ocr != current_ocr:
            logger.info(f"Temporarily {'enabling' if should_use_ocr else 'disabling'} OCR for this conversion")
            
            # Create temporary converter with adjusted OCR
            temp_config = self.ocr_config.copy()
            temp_config["enabled"] = should_use_ocr
            
            temp_converter = DoclingConverterService(
                pipeline_mode=self.pipeline_mode,
                artifacts_path=self.artifacts_path,
                ocr_config=temp_config,
                vlm_config=self.vlm_config,
                table_config=self.table_config,
            )
            
            result = temp_converter.convert_file(file_path, output_format)
        else:
            # Use current converter
            result = self.convert_file(file_path, output_format)
        
        # Add OCR info to result
        result["ocr_used"] = should_use_ocr
        if pdf_info:
            result["pdf_info"] = pdf_info
        
        return result
    
    def convert_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        output_format: str = "markdown",
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert file bytes to the specified format
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            output_format: Output format
            mime_type: Optional MIME type
        
        Returns:
            Dict with 'text' and optional 'metadata'
        """
        # Save to temporary file and convert
        suffix = Path(filename).suffix
        
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        ) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            result = self.convert_file(tmp_path, output_format)
            return result
        finally:
            # Clean up temporary file
            try:
                Path(tmp_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")
    
    def extract_tables(self, file_path: str | Path) -> List[Dict[str, Any]]:
        """
        Extract tables from a document
        
        Args:
            file_path: Path to file
        
        Returns:
            List of table dictionaries
        """
        try:
            file_path = Path(file_path)
            result = self._converter.convert(str(file_path))
            
            tables = []
            for table in result.document.tables:
                tables.append({
                    "data": table.export_to_dataframe().to_dict("records") if hasattr(table, 'export_to_dataframe') else {},
                    "caption": getattr(table, "caption", ""),
                    "bbox": getattr(table, "bbox", None),
                })
            
            return tables
        
        except Exception as e:
            logger.error(f"Error extracting tables from {file_path}: {e}")
            raise
    
    def chunk_document(
        self,
        file_path: str | Path,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Convert and chunk document for RAG
        
        Args:
            file_path: Path to file
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of chunk dictionaries
        """
        try:
            # Convert document
            result = self.convert_file(file_path, output_format="markdown")
            text = result["text"]
            
            # Simple chunking implementation
            chunks = []
            start = 0
            chunk_id = 0
            
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "metadata": result.get("metadata", {}),
                })
                
                start = end - chunk_overlap
                chunk_id += 1
            
            return chunks
        
        except Exception as e:
            logger.error(f"Error chunking document {file_path}: {e}")
            raise
    
    def _extract_metadata(self, result) -> Dict[str, Any]:
        """Extract metadata from conversion result"""
        metadata = {}
        
        try:
            doc = result.document
            
            # Basic metadata
            metadata["num_pages"] = len(doc.pages) if hasattr(doc, "pages") else 0
            metadata["num_tables"] = len(doc.tables) if hasattr(doc, "tables") else 0
            metadata["num_pictures"] = len(doc.pictures) if hasattr(doc, "pictures") else 0
            
            # Document info
            if hasattr(doc, "name"):
                metadata["document_name"] = doc.name
            
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata
    
    @staticmethod
    def get_supported_extensions() -> set:
        """Get set of supported file extensions"""
        return {
            # Primary support (PDF focus)
            '.pdf',
            # Office documents
            '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
            # Images (for OCR)
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif',
            # Other documents
            '.txt', '.md', '.html', '.htm', '.xml',
            # E-books
            '.epub',
        }
    
    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """Check if file is supported"""
        extension = Path(filename).suffix.lower()
        return extension in DoclingConverterService.get_supported_extensions()

