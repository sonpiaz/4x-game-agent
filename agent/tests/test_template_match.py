"""Tests for the template matching module."""
import os

import cv2
import numpy as np
import pytest

from agent.template_match import TemplateMatcher


@pytest.fixture
def template_env(tmp_path):
    """Fixture providing a temp template dir, sample template icon, and matcher."""
    template_dir = str(tmp_path / "templates")
    os.makedirs(template_dir, exist_ok=True)

    # Create a distinct 30x30 template icon
    icon = np.zeros((30, 30, 3), dtype=np.uint8)
    cv2.rectangle(icon, (4, 4), (26, 26), (0, 255, 0), -1)
    cv2.circle(icon, (15, 15), 5, (0, 0, 255), -1)

    template_file = os.path.join(template_dir, "btn_upgrade.png")
    cv2.imwrite(template_file, icon)

    matcher = TemplateMatcher(template_dir, log_fn=lambda x: None)

    return {
        "template_dir": template_dir,
        "icon": icon,
        "matcher": matcher,
        "tmp_path": tmp_path,
    }


def test_load_templates(template_env):
    """Test that templates are discovered and loaded correctly."""
    matcher = template_env["matcher"]
    assert matcher.has_template("btn_upgrade")
    assert "btn_upgrade" in matcher.list_templates()

    # Non-png files or subdirectories should not be loaded as templates
    extra_txt = os.path.join(template_env["template_dir"], "notes.txt")
    with open(extra_txt, "w") as f:
        f.write("ignore this")

    new_matcher = TemplateMatcher(template_env["template_dir"], log_fn=lambda x: None)
    assert new_matcher.list_templates() == ["btn_upgrade"]


def test_load_templates_nonexistent_or_empty_dir(tmp_path):
    """Test initializing with empty or non-existent directories."""
    # Non-existent directory should be automatically created and have 0 templates
    non_existent = str(tmp_path / "new_templates")
    matcher = TemplateMatcher(non_existent, log_fn=lambda x: None)
    assert os.path.exists(non_existent)
    assert matcher.list_templates() == []
    assert not matcher.has_template("anything")


def test_find_known_image(template_env):
    """Test finding a template in a known screenshot."""
    matcher = template_env["matcher"]
    icon = template_env["icon"]
    tmp_path = template_env["tmp_path"]

    # Create a 200x200 canvas and place the 30x30 icon at (70:100, 85:115)
    # Expected center: cx = 85 + 15 = 100, cy = 70 + 15 = 85
    screen = np.full((200, 200, 3), 120, dtype=np.uint8)
    screen[70:100, 85:115] = icon
    screen_path = str(tmp_path / "screen.png")
    cv2.imwrite(screen_path, screen)

    match = matcher.find(screen_path, "btn_upgrade", threshold=0.8)
    assert match is not None
    cx, cy, conf = match
    assert abs(cx - 100) <= 1
    assert abs(cy - 85) <= 1
    assert conf >= 0.95


def test_find_multi_scale(template_env):
    """Test multi-scale search when template is slightly scaled."""
    matcher = template_env["matcher"]
    icon = template_env["icon"]
    tmp_path = template_env["tmp_path"]

    # Resize icon by 0.9 scale -> 27x27
    scaled = cv2.resize(icon, (27, 27))
    screen = np.full((200, 200, 3), 120, dtype=np.uint8)
    screen[50:77, 50:77] = scaled
    screen_path = str(tmp_path / "screen_scaled.png")
    cv2.imwrite(screen_path, screen)

    # Multi-scale loop activates when scale=1.0 match fails
    match = matcher.find(screen_path, "btn_upgrade", threshold=0.7)
    assert match is not None
    cx, cy, conf = match
    # Expected center: 50 + 13 = 63
    assert abs(cx - 63) <= 2
    assert abs(cy - 63) <= 2
    assert conf >= 0.7


def test_find_missing_template_or_image(template_env):
    """Test edge cases: missing template name or non-existent screenshot."""
    matcher = template_env["matcher"]
    tmp_path = template_env["tmp_path"]

    screen_path = str(tmp_path / "screen_empty.png")
    screen = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(screen_path, screen)

    # Template does not exist
    assert matcher.find(screen_path, "non_existent") is None

    # Screenshot does not exist
    assert matcher.find(str(tmp_path / "does_not_exist.png"), "btn_upgrade") is None

    # Template not present on screen (below threshold)
    assert matcher.find(screen_path, "btn_upgrade", threshold=0.9) is None


def test_capture_template(template_env):
    """Test capturing a region as a new template and saving to disk."""
    matcher = template_env["matcher"]
    tmp_path = template_env["tmp_path"]

    screen = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.circle(screen, (50, 50), 10, (255, 0, 0), -1)
    screen_path = str(tmp_path / "screen_capture.png")
    cv2.imwrite(screen_path, screen)

    # Capture a 40x40 region
    ok = matcher.capture_template(screen_path, "new_circle", 30, 30, 70, 70)
    assert ok is True
    assert matcher.has_template("new_circle")
    assert "new_circle" in matcher.list_templates()

    # Verify file saved on disk
    saved_path = os.path.join(template_env["template_dir"], "new_circle.png")
    assert os.path.exists(saved_path)

    # Verify invalid crop coordinates or missing file return False
    assert matcher.capture_template(screen_path, "invalid", 50, 50, 50, 50) is False
    assert matcher.capture_template(str(tmp_path / "missing.png"), "err", 10, 10, 20, 20) is False


def test_find_all_and_deduplication(template_env):
    """Test finding multiple occurrences and deduplication logic."""
    matcher = template_env["matcher"]
    icon = template_env["icon"]
    tmp_path = template_env["tmp_path"]

    screen = np.full((300, 300, 3), 120, dtype=np.uint8)
    # Place button at position A: (50, 50)
    screen[50:80, 50:80] = icon
    # Place button at position B: (200, 200) - far from A
    screen[200:230, 200:230] = icon
    # Place button at position C: (55, 55) - close to A (<50px, should be deduped)
    screen[55:85, 55:85] = icon

    screen_path = str(tmp_path / "screen_multi.png")
    cv2.imwrite(screen_path, screen)

    matches = matcher.find_all(screen_path, "btn_upgrade", threshold=0.8, max_results=10)
    assert len(matches) == 2  # Pos A and Pos B, with Pos C deduped

    # Test max_results constraint
    limited = matcher.find_all(screen_path, "btn_upgrade", threshold=0.8, max_results=1)
    assert len(limited) == 1

    # Missing template or missing file edge cases
    assert matcher.find_all(screen_path, "non_existent") == []
    assert matcher.find_all(str(tmp_path / "no_file.png"), "btn_upgrade") == []
