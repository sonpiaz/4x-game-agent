"""Tests for the OCR Engine module."""
import os
import sys
import time
from unittest.mock import MagicMock

import pytest
from PIL import Image

# Ensure paddleocr is mocked if not installed in the environment
if "paddleocr" not in sys.modules:
    sys.modules["paddleocr"] = MagicMock()

from agent.ocr import OCREngine


@pytest.fixture
def mock_ocr_engine():
    """Fixture providing an OCREngine instance with a mocked PaddleOCR backend."""
    engine = OCREngine(lang="en")
    engine._ocr = MagicMock()
    return engine


@pytest.fixture
def sample_image(tmp_path):
    """Fixture providing a sample RGB image file."""
    img_path = str(tmp_path / "sample.png")
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(img_path)
    return img_path


def test_run_parsing_and_filtering(mock_ocr_engine, sample_image):
    """Test OCREngine._run parses detected text, bounding boxes, and filters low scores."""
    mock_ocr_engine._ocr.predict.return_value = [
        {
            "rec_texts": ["Build", "  \n ", "Level Up", "LowConfText"],
            "rec_scores": [0.9543, 0.9999, 0.8812, 0.421],
            "dt_polys": [
                [[10, 10], [50, 10], [50, 30], [10, 30]],
                [[60, 10], [80, 10], [80, 30], [60, 30]],
                [[100, 100], [200, 100], [200, 150], [100, 150]],
                [[0, 0], [10, 0], [10, 10], [0, 10]],
            ],
        }
    ]

    results = mock_ocr_engine._run(sample_image)

    # Low score (0.421 < 0.5) and whitespace-only text should be skipped
    assert len(results) == 2

    # Check "Build" parsed coordinates: cx=(10+50)//2=30, cy=(10+30)//2=20
    assert results[0] == {
        "text": "Build",
        "confidence": 0.954,
        "x": 30,
        "y": 20,
    }

    # Check "Level Up" parsed coordinates: cx=(100+200)//2=150, cy=(100+150)//2=125
    assert results[1] == {
        "text": "Level Up",
        "confidence": 0.881,
        "x": 150,
        "y": 125,
    }


def test_read_all_caching_behavior(mock_ocr_engine, sample_image, tmp_path):
    """Test OCREngine.read_all returns cached results unless mtime or path changes."""
    mock_ocr_engine._ocr.predict.return_value = [
        {
            "rec_texts": ["CachedText"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [20, 0], [20, 20], [0, 20]]],
        }
    ]

    # First call: should invoke predict
    first_res = mock_ocr_engine.read_all(sample_image)
    assert len(first_res) == 1
    assert first_res[0]["text"] == "CachedText"
    assert mock_ocr_engine._ocr.predict.call_count == 1

    # Second call with same unmodified file: should hit cache without calling predict again
    second_res = mock_ocr_engine.read_all(sample_image)
    assert second_res == first_res
    assert mock_ocr_engine._ocr.predict.call_count == 1

    # Invalidate cache by updating file mtime
    time.sleep(0.01)
    new_mtime = time.time() + 10
    os.utime(sample_image, (new_mtime, new_mtime))

    third_res = mock_ocr_engine.read_all(sample_image)
    assert third_res == first_res
    assert mock_ocr_engine._ocr.predict.call_count == 2

    # Different image file: should also invoke predict
    other_img = str(tmp_path / "other.png")
    Image.new("RGB", (50, 50), color=(0, 0, 0)).save(other_img)
    mock_ocr_engine.read_all(other_img)
    assert mock_ocr_engine._ocr.predict.call_count == 3


def test_read_region_coordinate_adjustment(mock_ocr_engine, sample_image):
    """Test OCREngine.read_region crops image and offsets coordinates back to full image space."""
    mock_ocr_engine._ocr.predict.return_value = [
        {
            "rec_texts": ["Attack"],
            "rec_scores": [0.92],
            "dt_polys": [[[10, 10], [30, 10], [30, 20], [10, 20]]],
        }
    ]

    # Crop box: x1=50, y1=80, x2=150, y2=180
    # Inside the cropped image, text center is: cx=(10+30)//2=20, cy=(10+20)//2=15
    # Adjusted to full image space: x = 20 + 50 = 70, y = 15 + 80 = 95
    results = mock_ocr_engine.read_region(sample_image, (50, 80, 150, 180))

    assert len(results) == 1
    assert results[0] == {
        "text": "Attack",
        "confidence": 0.92,
        "x": 70,
        "y": 95,
    }


def test_edge_cases_empty_results_and_missing_file(mock_ocr_engine):
    """Test edge cases: empty image detection, missing file, and missing polygons."""
    # 1. Empty detection results
    mock_ocr_engine._ocr.predict.return_value = []
    assert mock_ocr_engine._run("dummy.png") == []

    # 2. Result with empty text/scores
    mock_ocr_engine._ocr.predict.return_value = [{"rec_texts": [], "rec_scores": []}]
    assert mock_ocr_engine._run("dummy.png") == []

    # 3. Missing dt_polys fallback: polygon defaults to [[0, 0]] * 4 -> (0, 0)
    mock_ocr_engine._ocr.predict.return_value = [
        {
            "rec_texts": ["NoPolyText"],
            "rec_scores": [0.9],
            "dt_polys": [],
        }
    ]
    res = mock_ocr_engine._run("dummy.png")
    assert len(res) == 1
    assert res[0]["x"] == 0
    assert res[0]["y"] == 0

    # 4. read_all with non-existent file handles OSError gracefully
    mock_ocr_engine._ocr.predict.return_value = []
    non_existent = "/tmp/does_not_exist_4x.png"
    assert mock_ocr_engine.read_all(non_existent) == []
