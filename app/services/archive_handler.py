"""Archive handling service"""

import logging
import shutil
import zipfile
import rarfile
import py7zr
from pathlib import Path
from typing import List, Tuple, Optional
from tempfile import mkdtemp

logger = logging.getLogger(__name__)


class ArchiveHandler:
    """Service for handling archive files"""
    
    # Supported archive extensions
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z'}
    
    @staticmethod
    def is_archive(filename: str) -> bool:
        """Check if file is a supported archive"""
        extension = Path(filename).suffix.lower()
        return extension in ArchiveHandler.ARCHIVE_EXTENSIONS
    
    @staticmethod
    def extract_archive(
        archive_path: Path,
        extract_to: Optional[Path] = None,
        timeout: int = 300
    ) -> Path:
        """
        Extract archive to a directory
        
        Args:
            archive_path: Path to archive file
            extract_to: Directory to extract to (creates temp dir if None)
            timeout: Extraction timeout in seconds
            
        Returns:
            Path to extraction directory
            
        Raises:
            ValueError: If archive format is not supported
            Exception: If extraction fails
        """
        if extract_to is None:
            extract_to = Path(mkdtemp(prefix='archive_'))
        else:
            extract_to.mkdir(parents=True, exist_ok=True)
        
        extension = archive_path.suffix.lower()
        
        try:
            if extension == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            
            elif extension == '.rar':
                with rarfile.RarFile(archive_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_to)
            
            elif extension == '.7z':
                with py7zr.SevenZipFile(archive_path, 'r') as sevenz_ref:
                    sevenz_ref.extractall(extract_to)
            
            else:
                raise ValueError(f"Unsupported archive format: {extension}")
            
            logger.info(f"Extracted archive {archive_path.name} to {extract_to}")
            return extract_to
            
        except Exception as e:
            logger.error(f"Error extracting archive {archive_path}: {e}")
            raise
    
    @staticmethod
    def find_files_in_directory(
        directory: Path,
        supported_extensions: set,
        max_files: Optional[int] = None
    ) -> List[Path]:
        """
        Find all supported files in directory (recursively)
        
        Args:
            directory: Directory to search
            supported_extensions: Set of supported file extensions
            max_files: Maximum number of files to return
            
        Returns:
            List of file paths
        """
        files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() in supported_extensions:
                    files.append(file_path)
                    
                    if max_files and len(files) >= max_files:
                        logger.warning(
                            f"Reached max files limit ({max_files}), "
                            "stopping search"
                        )
                        break
        
        return files
    
    @staticmethod
    def create_archive(
        source_dir: Path,
        output_path: Path,
        preserve_structure: bool = True,
        archive_format: str = 'zip'
    ) -> Path:
        """
        Create archive from directory
        
        Args:
            source_dir: Directory with files to archive
            output_path: Path for output archive
            preserve_structure: Preserve directory structure in archive
            archive_format: Archive format ('zip', 'tar', etc.)
            
        Returns:
            Path to created archive
        """
        if archive_format == 'zip':
            with zipfile.ZipFile(
                output_path,
                'w',
                zipfile.ZIP_DEFLATED
            ) as zip_ref:
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        if preserve_structure:
                            arcname = file_path.relative_to(source_dir)
                        else:
                            arcname = file_path.name
                        
                        zip_ref.write(file_path, arcname=arcname)
        
        else:
            raise ValueError(f"Unsupported archive format: {archive_format}")
        
        logger.info(f"Created archive {output_path}")
        return output_path
    
    @staticmethod
    def cleanup_directory(directory: Path):
        """
        Remove directory and all its contents
        
        Args:
            directory: Directory to remove
        """
        try:
            if directory.exists():
                shutil.rmtree(directory)
                logger.debug(f"Cleaned up directory {directory}")
        except Exception as e:
            logger.warning(f"Failed to cleanup directory {directory}: {e}")

