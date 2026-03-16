"""Tests for the OCR engine module (agent/ocr.py)."""
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import pytest
from PIL import Image

from agent.ocr import OCREngine


@pytest.fixture
def mock_ocr_instance():
    """Mock PaddleOCR instance."""
    import sys
    mock_paddleocr = sys.modules['paddleocr']
    instance = MagicMock()
    mock_paddleocr.PaddleOCR.return_value = instance
    yield instance
    mock_paddleocr.PaddleOCR.reset_mock()


@pytest.fixture
def temp_image():
    """Create a temporary image file for testing."""
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    # Create a small test image
    img = Image.new("RGB", (100, 100), color="white")
    img.save(path)
    yield path
    os.unlink(path)


class TestOCREngineInit:
    """Tests for OCREngine initialization."""

    def test_default_language(self, mock_ocr_instance):
        """Test default language is English."""
        import sys
        mock_paddleocr = sys.modules['paddleocr']
        mock_paddleocr.PaddleOCR.reset_mock()
        
        engine = OCREngine()
        mock_paddleocr.PaddleOCR.assert_called_once_with(lang="en")

    def test_custom_language(self, mock_ocr_instance):
        """Test custom language can be specified."""
        import sys
        mock_paddleocr = sys.modules['paddleocr']
        mock_paddleocr.PaddleOCR.reset_mock()
        
        engine = OCREngine(lang="ch")
        mock_paddleocr.PaddleOCR.assert_called_once_with(lang="ch")

    def test_cache_initialized_empty(self, mock_ocr_instance):
        """Test cache is initialized empty."""
        engine = OCREngine()
        assert engine._cached_path is None
        assert engine._cached_texts is None


class TestOCREngineRun:
    """Tests for OCREngine._run method."""

    def test_run_basic_text_extraction(self, mock_ocr_instance, temp_image):
        """Test basic text extraction from OCR results."""
        # Create mock result with proper dict-like behavior
        mock_result = {
            "rec_texts": ["Hello World", "Test Text"],
            "rec_scores": [0.95, 0.88],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [80, 60], [80, 100], [0, 100]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert len(results) == 2
        assert results[0]["text"] == "Hello World"
        assert results[0]["confidence"] == 0.95
        assert results[0]["x"] == 50  # Center of box
        assert results[0]["y"] == 25

    def test_run_filters_low_confidence(self, mock_ocr_instance, temp_image):
        """Test that low confidence results are filtered out."""
        mock_result = {
            "rec_texts": ["High Confidence", "Low Confidence"],
            "rec_scores": [0.95, 0.3],  # Second is below 0.5 threshold
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [80, 60], [80, 100], [0, 100]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert len(results) == 1
        assert results[0]["text"] == "High Confidence"

    def test_run_filters_empty_text(self, mock_ocr_instance, temp_image):
        """Test that empty text results are filtered out."""
        mock_result = {
            "rec_texts": ["Valid Text", "", "   "],
            "rec_scores": [0.95, 0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [80, 60], [80, 100], [0, 100]],
                        [[0, 110], [80, 110], [80, 150], [0, 150]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert len(results) == 1
        assert results[0]["text"] == "Valid Text"

    def test_run_handles_missing_dt_polys(self, mock_ocr_instance, temp_image):
        """Test handling when dt_polys is shorter than rec_texts."""
        mock_result = {
            "rec_texts": ["Text1", "Text2"],
            "rec_scores": [0.95, 0.95],
            "dt_polys": [[[10, 10], [50, 10], [50, 30], [10, 30]]]  # Only one polygon
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert len(results) == 2
        # Second text gets default box
        assert results[1]["x"] == 0
        assert results[1]["y"] == 0

    def test_run_strips_whitespace(self, mock_ocr_instance, temp_image):
        """Test that extracted text is stripped of whitespace."""
        mock_result = {
            "rec_texts": ["  Text with spaces  "],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert results[0]["text"] == "Text with spaces"

    def test_run_rounds_confidence(self, mock_ocr_instance, temp_image):
        """Test that confidence is rounded to 3 decimal places."""
        mock_result = {
            "rec_texts": ["Test"],
            "rec_scores": [0.9555555],  # Should round to 0.956
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine._run(temp_image)

        assert results[0]["confidence"] == 0.956


class TestOCREngineReadAll:
    """Tests for OCREngine.read_all method."""

    def test_read_all_returns_texts(self, mock_ocr_instance, temp_image):
        """Test read_all returns list of text dicts."""
        mock_result = {
            "rec_texts": ["Hello"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        results = engine.read_all(temp_image)

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["text"] == "Hello"

    def test_read_all_uses_cache_on_same_file(self, mock_ocr_instance, temp_image):
        """Test that caching works for same file."""
        mock_result = {
            "rec_texts": ["Hello"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        
        # First call
        results1 = engine.read_all(temp_image)
        # Second call should use cache
        results2 = engine.read_all(temp_image)

        # predict should only be called once due to caching
        assert mock_ocr_instance.predict.call_count == 1
        assert results1 == results2

    def test_read_all_busts_cache_on_different_file(self, mock_ocr_instance, temp_image):
        """Test that cache is busted for different file."""
        mock_result = {
            "rec_texts": ["Hello"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        
        # Create second temp image
        fd, temp_image2 = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        img = Image.new("RGB", (100, 100), color="white")
        img.save(temp_image2)
        
        try:
            # First call
            engine.read_all(temp_image)
            # Second call with different file
            engine.read_all(temp_image2)

            # predict should be called twice
            assert mock_ocr_instance.predict.call_count == 2
        finally:
            os.unlink(temp_image2)

    def test_read_all_handles_oserror_on_mtime(self, mock_ocr_instance, temp_image):
        """Test handling of OSError when getting mtime."""
        mock_result = {
            "rec_texts": ["Hello"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        
        # Mock os.path.getmtime to raise OSError
        with patch("os.path.getmtime", side_effect=OSError("Test error")):
            results = engine.read_all(temp_image)

        assert len(results) == 1
        assert results[0]["text"] == "Hello"


class TestOCREngineReadRegion:
    """Tests for OCREngine.read_region method."""

    def test_read_region_crops_image(self, mock_ocr_instance, temp_image):
        """Test that read_region crops the image before OCR."""
        mock_result = {
            "rec_texts": ["Region Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [50, 0], [50, 25], [0, 25]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped

            crop_box = (10, 20, 110, 70)  # x1, y1, x2, y2
            results = engine.read_region(temp_image, crop_box)

            # Verify crop was called with correct box
            mock_img.crop.assert_called_once_with((10, 20, 110, 70))
            # Verify cropped image was saved
            mock_cropped.save.assert_called_once()

    def test_read_region_adjusts_coordinates(self, mock_ocr_instance, temp_image):
        """Test that coordinates are adjusted to full-image space."""
        mock_result = {
            "rec_texts": ["Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [50, 0], [50, 25], [0, 25]]]  # Center at (25, 12.5)
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        engine = OCREngine()
        
        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped

            crop_box = (100, 200, 200, 300)  # Offset by (100, 200)
            results = engine.read_region(temp_image, crop_box)

            # Coordinates should be adjusted by offset
            # Original center is (25, 12), offset is (100, 200)
            # Result should be (125, 212)
            assert results[0]["x"] == 125  # 100 + 25
            assert results[0]["y"] == 212  # 200 + 12 (rounded from 12.5)
