"""Tests for the template_match module."""
import os
import tempfile
import pytest
import numpy as np
import cv2

from agent.template_match import TemplateMatcher


@pytest.fixture
def temp_template_dir():
    """Create a temporary directory for templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_screenshot_dir():
    """Create a temporary directory for screenshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def template_matcher(temp_template_dir):
    """Create a TemplateMatcher with a temp directory."""
    return TemplateMatcher(
        template_dir=temp_template_dir,
        log_fn=lambda x: None
    )


def create_test_image(width: int, height: int, color=(255, 0, 0), pattern=None):
    """Create a test image with a solid color and optional pattern."""
    img = np.full((height, width, 3), color, dtype=np.uint8)
    
    # Add a unique pattern to make matching more robust
    if pattern is None:
        # Add diagonal stripes
        for i in range(0, min(width, height), 5):
            if i + 3 < width and i + 3 < height:
                cv2.line(img, (i, 0), (i, height-1), (255, 255, 255), 2)
    elif pattern == 'circle':
        cv2.circle(img, (width//2, height//2), min(width, height)//4, (255, 255, 255), -1)
    elif pattern == 'rect':
        cv2.rectangle(img, (width//4, height//4), (3*width//4, 3*height//4), (255, 255, 255), -1)
    
    return img


def create_screenshot_with_template(template, x, y, bg_color=(100, 100, 100)):
    """Create a screenshot with a template placed at (x, y)."""
    h, w = template.shape[:2]
    screen = np.full((1080, 1920, 3), bg_color, dtype=np.uint8)
    
    # Add noise to background to avoid false matches
    noise = np.random.randint(0, 10, screen.shape, dtype=np.uint8)
    screen = cv2.add(screen, noise)
    
    screen[y:y+h, x:x+w] = template
    return screen


class TestTemplateMatcherInit:
    """Tests for TemplateMatcher initialization."""

    def test_init_creates_directory(self, temp_template_dir):
        """Test that init creates template directory if it doesn't exist."""
        non_existent_dir = os.path.join(temp_template_dir, "new_templates")
        assert not os.path.exists(non_existent_dir)
        matcher = TemplateMatcher(template_dir=non_existent_dir)
        assert os.path.exists(non_existent_dir)

    def test_init_loads_existing_templates(self, temp_template_dir):
        """Test that init loads existing templates from directory."""
        # Create a template image
        template = create_test_image(50, 50, color=(0, 255, 0))
        template_path = os.path.join(temp_template_dir, "green_box.png")
        cv2.imwrite(template_path, template)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        assert matcher.has_template("green_box")
        assert "green_box" in matcher.list_templates()

    def test_init_empty_directory(self, temp_template_dir):
        """Test that init handles empty template directory."""
        matcher = TemplateMatcher(template_dir=temp_template_dir)
        assert matcher.list_templates() == []
        assert not matcher.has_template("anything")


class TestFind:
    """Tests for the find method."""

    def test_find_template_success(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test successfully finding a template."""
        # Create and save a template
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Reload matcher to pick up the template
        matcher = TemplateMatcher(template_dir=temp_template_dir)

        # Create screenshot with template at known position
        screen = create_screenshot_with_template(template, x=100, y=200)
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        # Find the template
        result = matcher.find(screenshot_path, "target", threshold=0.7)
        assert result is not None
        x, y, confidence = result
        # Template center should be at (100+25, 200+25) = (125, 225)
        assert abs(x - 125) <= 2
        assert abs(y - 225) <= 2
        assert confidence >= 0.7

    def test_find_template_not_found(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test when template doesn't exist in screenshot."""
        # Create template
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Create screenshot without the template (different background)
        screen = create_test_image(1080, 1920, color=(200, 200, 200))
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        result = matcher.find(screenshot_path, "target", threshold=0.9)
        assert result is None

    def test_find_unknown_template(self, template_matcher, temp_screenshot_dir):
        """Test finding a template that hasn't been loaded."""
        screen = create_test_image(1080, 1920, color=(100, 100, 100))
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        result = template_matcher.find(screenshot_path, "nonexistent", threshold=0.7)
        assert result is None

    def test_find_invalid_screenshot(self, template_matcher, temp_template_dir):
        """Test finding with invalid screenshot path."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        result = matcher.find("/nonexistent/path.png", "target")
        assert result is None

    def test_find_with_custom_threshold(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test find with different threshold values."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Create screenshot with template
        screen = create_screenshot_with_template(template, x=100, y=200)
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)

        # Should find with low threshold
        result_low = matcher.find(screenshot_path, "target", threshold=0.3)
        assert result_low is not None

        # Should still find with high threshold (exact match)
        result_high = matcher.find(screenshot_path, "target", threshold=0.95)
        assert result_high is not None


class TestFindAll:
    """Tests for the find_all method."""

    def test_find_all_single_match(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test find_all with single occurrence."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        screen = create_screenshot_with_template(template, x=100, y=200)
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        results = matcher.find_all(screenshot_path, "target", threshold=0.7)

        assert len(results) == 1
        x, y, conf = results[0]
        assert abs(x - 125) <= 2
        assert abs(y - 225) <= 2

    def test_find_all_multiple_matches(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test find_all with multiple occurrences."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Create screenshot with template at multiple positions
        h, w = template.shape[:2]
        screen = np.full((1080, 1920, 3), (100, 100, 100), dtype=np.uint8)
        positions = [(100, 200), (500, 400), (1000, 800)]
        for x, y in positions:
            screen[y:y+h, x:x+w] = template

        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        results = matcher.find_all(screenshot_path, "target", threshold=0.7)

        assert len(results) == 3
        # Results should be sorted by confidence (descending)
        for i in range(len(results) - 1):
            assert results[i][2] >= results[i + 1][2]

    def test_find_all_max_results(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test find_all respects max_results parameter."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Create screenshot with template at many positions (spaced far apart)
        h, w = template.shape[:2]
        screen = np.full((1080, 1920, 3), (100, 100, 100), dtype=np.uint8)
        for i in range(10):
            x = 50 + i * 150
            y = 50 + i * 100
            screen[y:y+h, x:x+w] = template

        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        results = matcher.find_all(screenshot_path, "target", threshold=0.7, max_results=3)

        assert len(results) <= 3

    def test_find_all_deduplication(self, template_matcher, temp_template_dir, temp_screenshot_dir):
        """Test that find_all deduplicates close matches."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        # Create screenshot with overlapping templates (should dedupe)
        h, w = template.shape[:2]
        screen = np.full((1080, 1920, 3), (100, 100, 100), dtype=np.uint8)
        # Place templates close together (within 50px)
        positions = [(100, 200), (105, 205), (110, 210)]
        for x, y in positions:
            screen[y:y+h, x:x+w] = template

        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        results = matcher.find_all(screenshot_path, "target", threshold=0.7)

        # Should dedupe to single result
        assert len(results) == 1

    def test_find_all_unknown_template(self, template_matcher, temp_screenshot_dir):
        """Test find_all with unknown template."""
        screen = create_test_image(1080, 1920, color=(100, 100, 100))
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        results = template_matcher.find_all(screenshot_path, "nonexistent")
        assert results == []

    def test_find_all_invalid_screenshot(self, template_matcher, temp_template_dir):
        """Test find_all with invalid screenshot."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "target.png"), template)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        results = matcher.find_all("/nonexistent/path.png", "target")
        assert results == []


class TestCaptureTemplate:
    """Tests for the capture_template method."""

    def test_capture_template_success(self, template_matcher, temp_screenshot_dir, temp_template_dir):
        """Test successfully capturing a template from a screenshot."""
        # Create screenshot with a distinct region
        screen = create_test_image(1080, 1920, color=(100, 100, 100))
        # Add a distinct region
        screen[200:250, 300:350] = (255, 0, 0)

        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        # Capture the region
        result = template_matcher.capture_template(
            screenshot_path, "captured_target",
            x1=300, y1=200, x2=350, y2=250
        )

        assert result is True
        assert template_matcher.has_template("captured_target")

        # Verify file was saved
        template_path = os.path.join(temp_template_dir, "captured_target.png")
        assert os.path.exists(template_path)

        # Verify template can be loaded
        loaded = cv2.imread(template_path)
        assert loaded.shape[:2] == (50, 50)

    def test_capture_template_invalid_region(self, template_matcher, temp_screenshot_dir):
        """Test capturing with invalid region."""
        screen = create_test_image(1080, 1920, color=(100, 100, 100))
        screenshot_path = os.path.join(temp_screenshot_dir, "screen.png")
        cv2.imwrite(screenshot_path, screen)

        # Invalid region (y2 < y1)
        result = template_matcher.capture_template(
            screenshot_path, "invalid",
            x1=300, y1=250, x2=350, y2=200
        )

        assert result is False

    def test_capture_template_invalid_screenshot(self, template_matcher):
        """Test capturing from invalid screenshot path."""
        result = template_matcher.capture_template(
            "/nonexistent/path.png", "target",
            x1=100, y1=100, x2=150, y2=150
        )
        assert result is False


class TestHasTemplate:
    """Tests for the has_template method."""

    def test_has_template_true(self, template_matcher, temp_template_dir):
        """Test has_template returns True for existing template."""
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "exists.png"), template)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        assert matcher.has_template("exists") is True

    def test_has_template_false(self, template_matcher):
        """Test has_template returns False for non-existent template."""
        assert template_matcher.has_template("nonexistent") is False


class TestListTemplates:
    """Tests for the list_templates method."""

    def test_list_templates_empty(self, template_matcher):
        """Test listing templates when none exist."""
        assert template_matcher.list_templates() == []

    def test_list_templates_multiple(self, template_matcher, temp_template_dir):
        """Test listing multiple templates."""
        # Create multiple templates
        for name in ["template1", "template2", "template3"]:
            template = create_test_image(50, 50, color=(0, 255, 0))
            cv2.imwrite(os.path.join(temp_template_dir, f"{name}.png"), template)

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        templates = matcher.list_templates()

        assert len(templates) == 3
        assert "template1" in templates
        assert "template2" in templates
        assert "template3" in templates

    def test_list_templates_non_png_ignored(self, template_matcher, temp_template_dir):
        """Test that non-PNG files are ignored."""
        # Create a PNG template
        template = create_test_image(50, 50, color=(0, 255, 0))
        cv2.imwrite(os.path.join(temp_template_dir, "valid.png"), template)

        # Create a non-PNG file
        with open(os.path.join(temp_template_dir, "ignore.txt"), "w") as f:
            f.write("not an image")

        matcher = TemplateMatcher(template_dir=temp_template_dir)
        templates = matcher.list_templates()

        assert templates == ["valid"]


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_workflow(self, temp_template_dir, temp_screenshot_dir):
        """Test the complete template matching workflow."""
        matcher = TemplateMatcher(template_dir=temp_template_dir)

        # Step 1: Create a screenshot with a pattern
        screen = np.full((1080, 1920, 3), (200, 200, 200), dtype=np.uint8)
        # Draw a unique button-like shape with pattern
        cv2.rectangle(screen, (400, 300), (500, 350), (0, 100, 200), -1)
        cv2.circle(screen, (450, 325), 10, (255, 255, 255), -1)  # Add unique pattern
        
        # Add noise to background
        noise = np.random.randint(0, 20, screen.shape, dtype=np.uint8)
        screen = cv2.add(screen, noise)

        screenshot_path = os.path.join(temp_screenshot_dir, "game_screen.png")
        cv2.imwrite(screenshot_path, screen)

        # Step 2: Capture the button as a template
        success = matcher.capture_template(
            screenshot_path, "blue_button",
            x1=400, y1=300, x2=500, y2=350
        )
        assert success is True

        # Step 3: Create a new screenshot with the button elsewhere
        screen2 = np.full((1080, 1920, 3), (200, 200, 200), dtype=np.uint8)
        noise2 = np.random.randint(0, 20, screen2.shape, dtype=np.uint8)
        screen2 = cv2.add(screen2, noise2)
        cv2.rectangle(screen2, (800, 600), (900, 650), (0, 100, 200), -1)
        cv2.circle(screen2, (850, 625), 10, (255, 255, 255), -1)

        screenshot_path2 = os.path.join(temp_screenshot_dir, "game_screen2.png")
        cv2.imwrite(screenshot_path2, screen2)

        # Step 4: Find the button in the new screenshot
        result = matcher.find(screenshot_path2, "blue_button", threshold=0.7)
        assert result is not None
        x, y, conf = result
        # Center of 800,600 to 900,650 is (850, 625)
        assert abs(x - 850) <= 5
        assert abs(y - 625) <= 5
        assert conf >= 0.7

    def test_multiple_template_types(self, temp_template_dir, temp_screenshot_dir):
        """Test managing multiple different template types."""
        matcher = TemplateMatcher(template_dir=temp_template_dir)

        # Create templates of different sizes and colors
        templates = {
            "red_small": (create_test_image(30, 30, (255, 0, 0)), 100, 100),
            "green_medium": (create_test_image(60, 60, (0, 255, 0)), 400, 200),
            "blue_large": (create_test_image(90, 90, (0, 0, 255)), 800, 500),
        }

        # Create screenshot with all templates
        screen = np.full((1080, 1920, 3), (50, 50, 50), dtype=np.uint8)
        for name, (template, x, y) in templates.items():
            h, w = template.shape[:2]
            screen[y:y+h, x:x+w] = template
            cv2.imwrite(os.path.join(temp_template_dir, f"{name}.png"), template)

        screenshot_path = os.path.join(temp_screenshot_dir, "multi.png")
        cv2.imwrite(screenshot_path, screen)

        # Reload matcher to pick up templates
        matcher = TemplateMatcher(template_dir=temp_template_dir)

        # Verify all templates are loaded
        assert len(matcher.list_templates()) == 3

        # Find each template
        for name, (template, expected_x, expected_y) in templates.items():
            result = matcher.find(screenshot_path, name, threshold=0.7)
            assert result is not None, f"Failed to find {name}"
            x, y, conf = result
            h, w = template.shape[:2]
            expected_cx = expected_x + w // 2
            expected_cy = expected_y + h // 2
            assert abs(x - expected_cx) <= 2
            assert abs(y - expected_cy) <= 2
