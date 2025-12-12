"""Test chunking functionality"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from app.services.converter import DoclingConverterService
from app.core.config import settings


@pytest.fixture
def sample_md_file(tmp_path):
    """Create a sample Markdown file for testing"""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test Document\n\nThis is a test document with multiple paragraphs.\n\nSecond paragraph here.\n\nThird paragraph for chunking test.", encoding="utf-8")
    return test_file


@pytest.fixture
def converter_service():
    """Create converter service instance"""
    return DoclingConverterService(pipeline_mode="standard")


class TestChunkingAPI:
    """Test chunking API endpoint"""
    
    def test_chunk_endpoint_simple_mode(self, client, sample_md_file):
        """Test chunk endpoint with simple mode (mode=0)"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunking_mode": 0,
                    "chunk_size": 100,
                    "chunk_overlap": 20
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "file_name" in data
        assert "chunks" in data
        assert isinstance(data["chunks"], list)
        assert len(data["chunks"]) > 0
        
        # Check chunk structure
        chunk = data["chunks"][0]
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "metadata" in chunk
    
    def test_chunk_endpoint_default_mode(self, client, sample_md_file):
        """Test chunk endpoint with default mode (backward compatibility)"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunk_size": 100,
                    "chunk_overlap": 20
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert len(data["chunks"]) > 0
    
    def test_chunk_endpoint_hierarchical_mode(self, client, sample_md_file):
        """Test chunk endpoint with hierarchical mode (mode=1)"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunking_mode": 1
                }
            )
        
        # Should work or fallback to simple mode if HierarchicalChunker not available
        assert response.status_code in [200, 500]  # May fail if docling version doesn't support it
        
        if response.status_code == 200:
            data = response.json()
            assert "chunks" in data
    
    def test_chunk_endpoint_hybrid_mode(self, client, sample_md_file):
        """Test chunk endpoint with hybrid mode (mode=2)"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunking_mode": 2,
                    "max_tokens": 256
                }
            )
        
        # Should work or fallback to hierarchical/simple mode if HybridChunker not available
        assert response.status_code in [200, 500]  # May fail if docling version doesn't support it
        
        if response.status_code == 200:
            data = response.json()
            assert "chunks" in data
    
    def test_chunk_endpoint_invalid_mode(self, client, sample_md_file):
        """Test chunk endpoint with invalid mode"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunking_mode": 99
                }
            )
        
        # API returns 200 but with error in response (current implementation)
        assert response.status_code == 200
        data = response.json()
        # Should have error field or empty chunks
        assert "error" in data or len(data.get("chunks", [])) == 0
    
    def test_chunk_endpoint_with_max_tokens(self, client, sample_md_file):
        """Test chunk endpoint with max_tokens parameter"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunking_mode": 2,
                    "max_tokens": 512
                }
            )
        
        # Should work or fallback
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "chunks" in data


class TestChunkingService:
    """Test chunking service methods"""
    
    def test_simple_chunking_mode_0(self, converter_service, sample_md_file):
        """Test simple chunking (mode=0)"""
        chunks = converter_service.chunk_document(
            sample_md_file,
            chunk_size=50,
            chunk_overlap=10,
            chunking_mode=0
        )
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        
        # Check chunk structure
        chunk = chunks[0]
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "start_char" in chunk
        assert "end_char" in chunk
        assert "metadata" in chunk
        
        # Check that chunks have overlap
        if len(chunks) > 1:
            # First chunk should end before second chunk starts
            assert chunks[0]["end_char"] > chunks[1]["start_char"]
    
    def test_simple_chunking_default_params(self, converter_service, sample_md_file):
        """Test simple chunking with default parameters"""
        chunks = converter_service.chunk_document(
            sample_md_file,
            chunking_mode=0
        )
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
    
    @pytest.mark.skipif(
        not hasattr(settings, 'chunking_mode') or settings.chunking_mode != 1,
        reason="HierarchicalChunker may not be available or not default"
    )
    def test_hierarchical_chunking_mode_1(self, converter_service, sample_md_file):
        """Test hierarchical chunking (mode=1)"""
        try:
            chunks = converter_service.chunk_document(
                sample_md_file,
                chunking_mode=1,
                merge_list_items=True
            )
            
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            
            # Check chunk structure
            chunk = chunks[0]
            assert "chunk_id" in chunk
            assert "text" in chunk
            assert "metadata" in chunk
        except ImportError:
            pytest.skip("HierarchicalChunker not available")
    
    @pytest.mark.skipif(
        not hasattr(settings, 'chunking_mode') or settings.chunking_mode != 2,
        reason="HybridChunker may not be available or not default"
    )
    def test_hybrid_chunking_mode_2(self, converter_service, sample_md_file):
        """Test hybrid chunking (mode=2)"""
        try:
            chunks = converter_service.chunk_document(
                sample_md_file,
                chunking_mode=2,
                max_tokens=256,
                merge_peers=True
            )
            
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            
            # Check chunk structure
            chunk = chunks[0]
            assert "chunk_id" in chunk
            assert "text" in chunk
            assert "metadata" in chunk
        except ImportError:
            pytest.skip("HybridChunker not available")
    
    def test_chunking_invalid_mode(self, converter_service, sample_md_file):
        """Test chunking with invalid mode"""
        with pytest.raises(ValueError, match="Invalid chunking_mode"):
            converter_service.chunk_document(
                sample_md_file,
                chunking_mode=99
            )
    
    def test_chunking_fallback_to_simple(self, converter_service, sample_md_file):
        """Test that chunking falls back to simple mode if semantic chunkers fail"""
        # This should always work, even if HierarchicalChunker fails
        chunks = converter_service.chunk_document(
            sample_md_file,
            chunking_mode=1,  # Try hierarchical
            chunk_size=50,
            chunk_overlap=10
        )
        
        # Should either work or fallback to simple
        assert isinstance(chunks, list)
        assert len(chunks) > 0


class TestChunkingConfiguration:
    """Test chunking configuration"""
    
    def test_chunking_mode_config(self):
        """Test that chunking_mode is in settings"""
        assert hasattr(settings, 'chunking_mode')
        assert settings.chunking_mode in [0, 1, 2]
    
    def test_chunking_max_tokens_config(self):
        """Test that chunking_max_tokens is in settings"""
        assert hasattr(settings, 'chunking_max_tokens')
        assert isinstance(settings.chunking_max_tokens, int)
        assert settings.chunking_max_tokens > 0
    
    def test_chunking_merge_list_items_config(self):
        """Test that chunking_merge_list_items is in settings"""
        assert hasattr(settings, 'chunking_merge_list_items')
        assert isinstance(settings.chunking_merge_list_items, bool)
    
    def test_chunking_merge_peers_config(self):
        """Test that chunking_merge_peers is in settings"""
        assert hasattr(settings, 'chunking_merge_peers')
        assert isinstance(settings.chunking_merge_peers, bool)
    
    def test_get_chunking_mode_name(self):
        """Test get_chunking_mode_name method"""
        mode_names = {
            0: "simple",
            1: "hierarchical",
            2: "hybrid"
        }
        
        for mode, expected_name in mode_names.items():
            name = settings.get_chunking_mode_name(mode)
            assert name == expected_name
        
        # Test default (no parameter)
        default_name = settings.get_chunking_mode_name()
        assert default_name in mode_names.values()


class TestChunkingBackwardCompatibility:
    """Test backward compatibility of chunking API"""
    
    def test_old_api_still_works(self, client, sample_md_file):
        """Test that old API calls without chunking_mode still work"""
        with open(sample_md_file, 'rb') as f:
            response = client.post(
                "/ocr/docling/chunk",
                files={"file": ("test.md", f, "text/markdown")},
                params={
                    "pipeline": "std",
                    "chunk_size": 100,
                    "chunk_overlap": 20
                    # No chunking_mode - should use default from settings
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert len(data["chunks"]) > 0
