"""Unit tests for Rust bindings module."""

import pytest


class TestRustBindings:
    """Test cases for Rust bindings (with graceful fallback)."""
    
    def test_fast_text_processor_creation(self):
        """Test creating FastTextProcessor."""
        try:
            from src.utils.rust_bindings import FastTextProcessor
            processor = FastTextProcessor(max_chunk_size=1000)
            assert processor is not None
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")
    
    def test_fast_text_processor_chunking(self):
        """Test chunking text with FastTextProcessor."""
        try:
            from src.utils.rust_bindings import FastTextProcessor
            processor = FastTextProcessor(max_chunk_size=100)
            text = "This is a long text that needs to be split into chunks"
            chunks = processor.split_into_chunks(text)
            assert isinstance(chunks, list)
            assert len(chunks) > 0
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")
    
    def test_fast_bounding_box_creation(self):
        """Test creating FastBoundingBox."""
        try:
            from src.utils.rust_bindings import FastBoundingBox
            bbox = FastBoundingBox(0, 0, 100, 100)
            assert bbox is not None
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")
    
    def test_fast_bounding_box_iou(self):
        """Test IoU calculation with FastBoundingBox."""
        try:
            from src.utils.rust_bindings import FastBoundingBox
            bbox1 = FastBoundingBox(0, 0, 100, 100)
            bbox2 = FastBoundingBox(50, 50, 150, 150)
            iou = bbox1.iou(bbox2)
            assert isinstance(iou, float)
            assert 0.0 <= iou <= 1.0
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")
    
    def test_fast_bounding_box_contains(self):
        """Test contains method with FastBoundingBox."""
        try:
            from src.utils.rust_bindings import FastBoundingBox
            bbox = FastBoundingBox(0, 0, 100, 100)
            assert bbox.contains(50, 50) is True
            assert bbox.contains(150, 150) is False
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")
    
    def test_fast_bounding_box_area(self):
        """Test area calculation with FastBoundingBox."""
        try:
            from src.utils.rust_bindings import FastBoundingBox
            bbox = FastBoundingBox(0, 0, 100, 100)
            area = bbox.area()
            assert area == 10000
        except ImportError:
            pytest.skip("Rust bindings not available, using Python fallback")


class TestRustBindingsFallback:
    """Test cases for Python fallback when Rust is not available."""
    
    def test_fallback_import(self):
        """Test that module can be imported without Rust."""
        try:
            from src.utils import rust_bindings
            assert rust_bindings is not None
        except ImportError:
            pytest.fail("Module should be importable")
    
    def test_fallback_fast_text_processor(self):
        """Test that Python fallback works for FastTextProcessor."""
        try:
            from src.utils.rust_bindings import FastTextProcessor
            processor = FastTextProcessor(max_chunk_size=50)
            text = "Short text"
            chunks = processor.split_into_chunks(text)
            assert isinstance(chunks, list)
        except ImportError:
            pytest.skip("Rust bindings module issue")
    
    def test_fallback_fast_bounding_box(self):
        """Test that Python fallback works for FastBoundingBox."""
        try:
            from src.utils.rust_bindings import FastBoundingBox
            bbox = FastBoundingBox(10, 20, 30, 40)
            assert bbox.area() == 400
        except ImportError:
            pytest.skip("Rust bindings module issue")
