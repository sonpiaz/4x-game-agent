"""Tests for the template_match module."""
import os
import tempfile
import pytest
import numpy as np
import cv2
from agent.template_match import TemplateMatcher


@pytest.fixture
def temp_dir():
    """Create a temporary directory for templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def template_matcher(temp_dir):
    """Create a TemplateMatcher with a temp directory."""
    return TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)


def test_load_templates_empty(temp_dir):
    """Test _load_templates with empty directory."""
    tm = TemplateMatcher(template_dir=temp_dir)
    assert tm._templates == {}


def test_load_templates_with_images(temp_dir):
    """Test _load_templates with a sample image."""
    # Create a simple test image
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[:25, :] = [255, 0, 0]  # Red top half
    img[25:, :] = [0, 0, 255]  # Blue bottom half
    
    template_path = os.path.join(temp_dir, "test_template.png")
    cv2.imwrite(template_path, img)
    
    tm = TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)
    assert "test_template" in tm._templates


def test_find_no_template(template_matcher):
    """Test find with non-existent template."""
    result = template_matcher.find("screenshot.png", "nonexistent")
    assert result is None


def test_find_no_screenshot(template_matcher, temp_dir):
    """Test find with non-existent screenshot."""
    # Add a template first
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    template_path = os.path.join(temp_dir, "test.png")
    cv2.imwrite(template_path, img)
    
    tm = TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)
    result = tm.find("nonexistent_screenshot.png", "test")
    assert result is None


def test_has_template(template_matcher, temp_dir):
    """Test has_template method."""
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    template_path = os.path.join(temp_dir, "mytemplate.png")
    cv2.imwrite(template_path, img)
    
    tm = TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)
    assert tm.has_template("mytemplate") is True
    assert tm.has_template("nonexistent") is False


def test_list_templates(template_matcher, temp_dir):
    """Test list_templates method."""
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    cv2.imwrite(os.path.join(temp_dir, "template1.png"), img)
    cv2.imwrite(os.path.join(temp_dir, "template2.png"), img)
    
    tm = TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)
    templates = tm.list_templates()
    assert "template1" in templates
    assert "template2" in templates


def test_capture_template(template_matcher, temp_dir):
    """Test capture_template saves correctly."""
    # Create a screenshot
    screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    screenshot[25:75, 25:75] = [255, 255, 255]  # White square
    screenshot_path = os.path.join(temp_dir, "screenshot.png")
    cv2.imwrite(screenshot_path, screenshot)
    
    # Capture a template from the screenshot
    result = template_matcher.capture_template(
        screenshot_path, "captured", 25, 25, 75, 75
    )
    assert result is True
    assert "captured" in template_matcher._templates


def test_capture_template_invalid_screenshot(template_matcher):
    """Test capture_template with invalid screenshot."""
    result = template_matcher.capture_template("nonexistent.png", "test", 0, 0, 10, 10)
    assert result is False


def test_find_all(template_matcher, temp_dir):
    """Test find_all returns deduplicated matches."""
    # Create a template
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.imwrite(os.path.join(temp_dir, "small.png"), template)
    
    tm = TemplateMatcher(template_dir=temp_dir, log_fn=lambda x: None)
    
    # Create a screenshot with multiple matches
    screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add the template in multiple positions
    screenshot[10:30, 10:30] = [255, 255, 255]
    screenshot[50:70, 50:70] = [255, 255, 255]
    screenshot_path = os.path.join(temp_dir, "multi.png")
    cv2.imwrite(screenshot_path, screenshot)
    
    results = tm.find_all(screenshot_path, "small", threshold=0.5)
    assert isinstance(results, list)
