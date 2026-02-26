#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for ImageManager - COM8

Tests image storage, deduplication, and retrieval functionality.

Author: Josué Amaral (COM8)
Date: February 16, 2026
Phase: 1.3 - ImageManager Implementation
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.translation.docx_html_mapper import ImageData, ImageManager


class TestImageData:
    """Test ImageData dataclass."""
    
    def test_create_image_data(self):
        """Test basic ImageData creation."""
        img = ImageData(
            image_id='IMG001',
            blob=b'\x89PNG\r\n\x1a\n',
            content_type='image/png',
            width_emus=914400,
            height_emus=457200,
            original_rId='rId9',
            blob_hash='abc123'
        )
        
        assert img.image_id == 'IMG001'
        assert img.blob == b'\x89PNG\r\n\x1a\n'
        assert img.content_type == 'image/png'
        assert img.width_emus == 914400
        assert img.height_emus == 457200
    
    def test_get_format_png(self):
        """Test format detection for PNG."""
        img = ImageData('IMG001', b'', 'image/png', 100, 100, 'rId1', None)
        assert img.get_format() == 'png'
    
    def test_get_format_jpeg(self):
        """Test format detection for JPEG."""
        img = ImageData('IMG001', b'', 'image/jpeg', 100, 100, 'rId1', None)
        assert img.get_format() == 'jpg'
    
    def test_get_format_gif(self):
        """Test format detection for GIF."""
        img = ImageData('IMG001', b'', 'image/gif', 100, 100, 'rId1', None)
        assert img.get_format() == 'gif'
    
    def test_get_format_unknown(self):
        """Test format detection for unknown type."""
        img = ImageData('IMG001', b'', 'image/tiff', 100, 100, 'rId1', None)
        assert img.get_format() == 'unknown'
    
    def test_get_width_inches(self):
        """Test EMU to inches conversion for width."""
        img = ImageData('IMG001', b'', 'image/png', 914400, 457200, 'rId1', None)
        assert img.get_width_inches() == 1.0
    
    def test_get_height_inches(self):
        """Test EMU to inches conversion for height."""
        img = ImageData('IMG001', b'', 'image/png', 914400, 457200, 'rId1', None)
        assert img.get_height_inches() == 0.5
    
    def test_dimensions_2_inches(self):
        """Test 2 inch dimensions."""
        img = ImageData('IMG001', b'', 'image/png', 1828800, 914400, 'rId1', None)
        assert img.get_width_inches() == 2.0
        assert img.get_height_inches() == 1.0


class TestImageManager:
    """Test ImageManager class."""
    
    def test_add_single_image(self):
        """Test adding single image."""
        manager = ImageManager()
        
        image_id = manager.add_image(
            blob=b'\x89PNG\r\n\x1a\n' + b'\x00' * 100,
            content_type='image/png',
            width_emus=914400,
            height_emus=457200,
            original_rId='rId9'
        )
        
        assert image_id == 'IMG001'
        
        # Verify storage
        img = manager.get_image('IMG001')
        assert img is not None
        assert img.image_id == 'IMG001'
        assert img.content_type == 'image/png'
        assert img.original_rId == 'rId9'
    
    def test_add_multiple_images(self):
        """Test adding multiple images with sequential IDs."""
        manager = ImageManager()
        
        id1 = manager.add_image(b'blob1', 'image/png', 914400, 457200, 'rId1')
        id2 = manager.add_image(b'blob2', 'image/jpeg', 914400, 457200, 'rId2')
        id3 = manager.add_image(b'blob3', 'image/gif', 914400, 457200, 'rId3')
        
        assert id1 == 'IMG001'
        assert id2 == 'IMG002'
        assert id3 == 'IMG003'
    
    def test_deduplication_same_blob(self):
        """Test deduplication: same blob returns same ID."""
        manager = ImageManager()
        
        blob = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        # Add first time
        id1 = manager.add_image(blob, 'image/png', 914400, 457200, 'rId9')
        
        # Add same blob again (different rId)
        id2 = manager.add_image(blob, 'image/png', 914400, 457200, 'rId10')
        
        assert id1 == id2 == 'IMG001'
        
        # Statistics should show deduplication
        stats = manager.get_statistics()
        assert stats['total_images'] == 1  # Only one unique blob
        assert stats['unique_blobs'] == 1
        assert stats['duplicates'] == 0
    
    def test_deduplication_different_dimensions(self):
        """Test deduplication works even with different dimensions."""
        manager = ImageManager()
        
        blob = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        # Same blob, different dimensions
        id1 = manager.add_image(blob, 'image/png', 914400, 457200, 'rId9')
        id2 = manager.add_image(blob, 'image/png', 1828800, 914400, 'rId10')
        
        # Should be same ID (deduplication based on blob, not dimensions)
        assert id1 == id2 == 'IMG001'
    
    def test_get_nonexistent_image(self):
        """Test retrieving non-existent image returns None."""
        manager = ImageManager()
        
        img = manager.get_image('IMG999')
        assert img is None
    
    def test_generate_placeholder(self):
        """Test HTML placeholder generation."""
        manager = ImageManager()
        
        placeholder = manager.generate_placeholder('IMG001')
        assert placeholder == '<span data-image="IMG001"></span>'
    
    def test_get_statistics_empty(self):
        """Test statistics for empty manager."""
        manager = ImageManager()
        
        stats = manager.get_statistics()
        assert stats['total_images'] == 0
        assert stats['unique_blobs'] == 0
        assert stats['duplicates'] == 0
        assert stats['total_bytes'] == 0
        assert stats['total_mb'] == 0.0
    
    def test_get_statistics_with_images(self):
        """Test statistics with multiple images."""
        manager = ImageManager()
        
        # Add 2 unique images
        blob1 = b'\x00' * 1000  # 1000 bytes
        blob2 = b'\xff' * 2000  # 2000 bytes
        
        manager.add_image(blob1, 'image/png', 914400, 457200, 'rId1')
        manager.add_image(blob2, 'image/jpeg', 914400, 457200, 'rId2')
        
        stats = manager.get_statistics()
        assert stats['total_images'] == 2
        assert stats['unique_blobs'] == 2
        assert stats['duplicates'] == 0
        assert stats['total_bytes'] == 3000
        assert abs(stats['total_mb'] - 3000 / (1024 * 1024)) < 0.0001
    
    def test_clear(self):
        """Test clearing all images."""
        manager = ImageManager()
        
        # Add images
        manager.add_image(b'blob1', 'image/png', 914400, 457200, 'rId1')
        manager.add_image(b'blob2', 'image/jpeg', 914400, 457200, 'rId2')
        
        # Clear
        manager.clear()
        
        # Verify empty
        stats = manager.get_statistics()
        assert stats['total_images'] == 0
        
        # Verify counter reset
        id1 = manager.add_image(b'blob3', 'image/gif', 914400, 457200, 'rId3')
        assert id1 == 'IMG001'  # Counter reset to 1
    
    def test_blob_hash_stored(self):
        """Test that blob hash is stored in ImageData."""
        manager = ImageManager()
        
        blob = b'\x89PNG\r\n\x1a\n'
        image_id = manager.add_image(blob, 'image/png', 914400, 457200, 'rId9')
        
        img = manager.get_image(image_id)
        assert img.blob_hash is not None
        assert len(img.blob_hash) == 64  # SHA256 hash is 64 hex chars
    
    def test_three_digit_padding(self):
        """Test that IDs are zero-padded to 3 digits."""
        manager = ImageManager()
        
        # Add 10 images
        for i in range(10):
            manager.add_image(bytes([i]), 'image/png', 914400, 457200, f'rId{i}')
        
        # Check IDs
        assert manager.get_image('IMG001') is not None
        assert manager.get_image('IMG009') is not None
        assert manager.get_image('IMG010') is not None
        
        # ID 10 should not have extra zero
        img10 = manager.get_image('IMG010')
        assert img10.image_id == 'IMG010'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
