"""PDF type detection utility"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def is_pdf_scanned(file_path: Path, sample_pages: int = 3, min_text_length: int = 100) -> bool:
    """
    Detect if a PDF is a scanned document or digital PDF with text layer
    
    Args:
        file_path: Path to PDF file
        sample_pages: Number of pages to check (default: 3)
        min_text_length: Minimum text length to consider as "digital" (default: 100 chars)
    
    Returns:
        True if PDF appears to be a scan (no text layer)
        False if PDF has embedded text (digital)
    
    Logic:
        - Check first N pages for extractable text
        - If total text < min_text_length, consider it a scan
        - If any page has substantial text, consider it digital
    """
    try:
        import pypdf
        
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            pages_to_check = min(sample_pages, total_pages)
            
            total_text_length = 0
            
            for page_num in range(pages_to_check):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        text_clean = text.strip()
                        total_text_length += len(text_clean)
                        
                        # If any page has substantial text, it's likely digital
                        if len(text_clean) > min_text_length:
                            logger.info(
                                f"PDF appears to be DIGITAL: page {page_num+1} has {len(text_clean)} chars"
                            )
                            return False
                
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            # If total text across all checked pages is minimal, it's a scan
            is_scan = total_text_length < min_text_length
            
            if is_scan:
                logger.info(
                    f"PDF appears to be SCAN: only {total_text_length} chars found in {pages_to_check} pages"
                )
            else:
                logger.info(
                    f"PDF appears to be DIGITAL: {total_text_length} chars found in {pages_to_check} pages"
                )
            
            return is_scan
    
    except ImportError:
        logger.warning("pypdf not installed, cannot auto-detect PDF type. Install with: pip install pypdf")
        return False  # Default to digital (no OCR) if can't detect
    
    except Exception as e:
        logger.error(f"Error detecting PDF type: {e}")
        return False  # Default to digital on error


def get_pdf_info(file_path: Path) -> dict:
    """
    Get PDF information for decision making
    
    Returns:
        dict with:
            - is_scanned: bool
            - total_pages: int
            - has_text: bool
            - text_density: float (chars per page)
    """
    try:
        import pypdf
        
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            # Check first 3 pages
            sample_pages = min(3, total_pages)
            total_chars = 0
            
            for i in range(sample_pages):
                try:
                    text = pdf_reader.pages[i].extract_text()
                    if text:
                        total_chars += len(text.strip())
                except:
                    pass
            
            text_density = total_chars / sample_pages if sample_pages > 0 else 0
            has_text = total_chars > 100
            is_scanned = not has_text
            
            return {
                "is_scanned": is_scanned,
                "total_pages": total_pages,
                "has_text": has_text,
                "text_density": text_density,
                "recommendation": "ocr" if is_scanned else "no-ocr"
            }
    
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return {
            "is_scanned": False,
            "total_pages": 0,
            "has_text": False,
            "text_density": 0,
            "recommendation": "no-ocr",
            "error": str(e)
        }


