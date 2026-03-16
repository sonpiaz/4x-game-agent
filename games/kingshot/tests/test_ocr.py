"""Tests for the GameOCR module (games/kingshot/ocr.py)."""
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import pytest
from PIL import Image

from games.kingshot.ocr import GameOCR


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
    """Create a temporary image file for testing (1440x2560)."""
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    # Create a test image with reference dimensions
    img = Image.new("RGB", (1440, 2560), color="white")
    img.save(path)
    yield path
    os.unlink(path)


class TestGameOCRInit:
    """Tests for GameOCR initialization."""

    def test_initialization(self, mock_ocr_instance):
        """Test GameOCR initializes correctly."""
        import sys
        mock_paddleocr = sys.modules['paddleocr']
        
        ocr = GameOCR()
        mock_paddleocr.PaddleOCR.assert_called_once_with(lang="en")
        assert ocr._initialized is True
        assert ocr._cached_path is None
        assert ocr._cached_texts is None

    def test_regions_defined(self, mock_ocr_instance):
        """Test that all expected regions are defined."""
        ocr = GameOCR()
        expected_regions = [
            "top_bar", "power_badge", "gems", "stamina", "rss_food",
            "vip", "quest_bar", "chat_area", "bottom_tabs", "right_panel",
            "center_popup", "building_menu", "building_header", "timer_area",
            "full_screen"
        ]
        for region in expected_regions:
            assert region in ocr.REGIONS


class TestGameOCRRunOCR:
    """Tests for GameOCR._run_ocr method."""

    def test_run_ocr_basic(self, mock_ocr_instance, temp_image):
        """Test basic OCR run."""
        mock_result = {
            "rec_texts": ["Power: 12345"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr._run_ocr(temp_image)

        assert len(results) == 1
        assert results[0]["text"] == "Power: 12345"
        assert "confidence" in results[0]
        assert "x" in results[0]
        assert "y" in results[0]

    def test_run_ocr_filters_by_confidence_and_empty(self, mock_ocr_instance, temp_image):
        """Test filtering of low confidence and empty text."""
        mock_result = {
            "rec_texts": ["Valid", "", "LowConf"],
            "rec_scores": [0.95, 0.9, 0.3],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [100, 60], [100, 110], [0, 110]],
                        [[0, 120], [100, 120], [100, 170], [0, 170]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr._run_ocr(temp_image)

        assert len(results) == 1
        assert results[0]["text"] == "Valid"


class TestGameOCRGetCachedOrRead:
    """Tests for GameOCR._get_cached_or_read method."""

    def test_cache_miss(self, mock_ocr_instance, temp_image):
        """Test cache miss triggers OCR run."""
        mock_result = {
            "rec_texts": ["Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr._get_cached_or_read(temp_image)

        assert len(results) == 1
        assert ocr._cached_path is not None
        assert ocr._cached_texts is not None

    def test_cache_hit_same_file(self, mock_ocr_instance, temp_image):
        """Test cache hit for same file."""
        mock_result = {
            "rec_texts": ["Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        
        # First call
        ocr._get_cached_or_read(temp_image)
        # Second call - should use cache
        results = ocr._get_cached_or_read(temp_image)

        # predict should only be called once
        assert mock_ocr_instance.predict.call_count == 1
        assert len(results) == 1

    def test_cache_bust_on_mtime_change(self, mock_ocr_instance, temp_image):
        """Test cache is busted when file mtime changes."""
        mock_result = {
            "rec_texts": ["Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        
        # First call
        ocr._get_cached_or_read(temp_image)
        
        # Simulate file change by modifying mtime
        with patch("os.path.getmtime", return_value=999999999):
            ocr._get_cached_or_read(temp_image)

        # predict should be called twice
        assert mock_ocr_instance.predict.call_count == 2


class TestGameOCRReadRegion:
    """Tests for GameOCR.read_region method."""

    def test_read_region_full_screen(self, mock_ocr_instance, temp_image):
        """Test full_screen region uses cache."""
        mock_result = {
            "rec_texts": ["Full Screen Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr.read_region(temp_image, "full_screen")

        assert len(results) == 1
        assert results[0]["text"] == "Full Screen Text"

    def test_read_region_specific_region(self, mock_ocr_instance, temp_image):
        """Test specific region crops and OCRs."""
        mock_result = {
            "rec_texts": ["Power"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [50, 0], [50, 25], [0, 25]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped
            mock_img.size = (1440, 2560)

            ocr = GameOCR()
            results = ocr.read_region(temp_image, "power_badge")

            # Verify crop was called
            mock_img.crop.assert_called_once()
            # Verify coordinates are adjusted
            assert results[0]["x"] > 0  # Should be offset by crop position

    def test_read_region_invalid_region(self, mock_ocr_instance, temp_image):
        """Test invalid region falls back to full screen."""
        mock_result = {
            "rec_texts": ["Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr.read_region(temp_image, "nonexistent_region")

        assert len(results) == 1


class TestGameOCRReadAllText:
    """Tests for GameOCR.read_all_text method."""

    def test_read_all_text(self, mock_ocr_instance, temp_image):
        """Test read_all_text returns all texts."""
        mock_result = {
            "rec_texts": ["Line1", "Line2", "Line3"],
            "rec_scores": [0.95, 0.94, 0.93],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [100, 60], [100, 110], [0, 110]],
                        [[0, 120], [100, 120], [100, 170], [0, 170]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        results = ocr.read_all_text(temp_image)

        assert len(results) == 3
        assert results[0]["text"] == "Line1"
        assert results[1]["text"] == "Line2"
        assert results[2]["text"] == "Line3"


class TestGameOCRReadGameState:
    """Tests for GameOCR.read_game_state method."""

    def test_read_game_state_structure(self, mock_ocr_instance, temp_image):
        """Test game state has all expected fields."""
        mock_result = {
            "rec_texts": ["Test"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        expected_keys = [
            "power", "gems", "stamina", "stamina_max", "food",
            "vip_level", "quest_text", "active_timers", "screen_texts",
            "has_popup", "popup_texts"
        ]
        for key in expected_keys:
            assert key in state

    def test_extract_power(self, mock_ocr_instance, temp_image):
        """Test power extraction from top-left region."""
        mock_result = {
            "rec_texts": ["100000"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]  # y < 200, x < 500
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["power"] == 100000

    def test_extract_gems(self, mock_ocr_instance, temp_image):
        """Test gems extraction from top-right region."""
        mock_result = {
            "rec_texts": ["4492"],
            "rec_scores": [0.95],
            "dt_polys": [[[1000, 0], [1100, 0], [1100, 50], [1000, 50]]]  # x > 900, y < 100
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["gems"] == 4492

    def test_extract_stamina(self, mock_ocr_instance, temp_image):
        """Test stamina extraction (format: XX/XX)."""
        mock_result = {
            "rec_texts": ["24/24"],
            "rec_scores": [0.95],
            "dt_polys": [[[300, 0], [400, 0], [400, 50], [300, 50]]]  # y < 100
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["stamina"] == 24
        assert state["stamina_max"] == 24

    def test_extract_vip_level(self, mock_ocr_instance, temp_image):
        """Test VIP level extraction."""
        mock_result = {
            "rec_texts": ["VIP 5"],
            "rec_scores": [0.95],
            "dt_polys": [[[1300, 60], [1400, 60], [1400, 110], [1300, 110]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["vip_level"] == 5

    def test_extract_timers(self, mock_ocr_instance, temp_image):
        """Test timer extraction (HH:MM:SS format)."""
        mock_result = {
            "rec_texts": ["01:30:45", "05:00"],
            "rec_scores": [0.95, 0.94],
            "dt_polys": [[[500, 500], [600, 500], [600, 550], [500, 550]],
                        [[700, 500], [770, 500], [770, 550], [700, 550]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert len(state["active_timers"]) == 2
        assert state["active_timers"][0]["timer"] == "01:30:45"
        assert state["active_timers"][1]["timer"] == "05:00"

    def test_detect_popup(self, mock_ocr_instance, temp_image):
        """Test popup detection."""
        mock_result = {
            "rec_texts": ["Confirmation"],
            "rec_scores": [0.95],
            "dt_polys": [[[500, 800], [700, 800], [700, 900], [500, 900]]]  # Center area
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["has_popup"] is True
        assert "Confirmation" in state["popup_texts"]

    def test_extract_food_with_suffix(self, mock_ocr_instance, temp_image):
        """Test food extraction with K/M/B suffix."""
        mock_result = {
            "rec_texts": ["397.7K"],
            "rec_scores": [0.95],
            "dt_polys": [[[550, 0], [700, 0], [700, 50], [550, 50]]]  # rss_food region
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        state = ocr.read_game_state(temp_image)

        assert state["food"] == 397700  # 397.7 * 1000


class TestGameOCRReadBuildingName:
    """Tests for GameOCR.read_building_name method."""

    def test_read_building_name(self, mock_ocr_instance, temp_image):
        """Test building name reads from header region."""
        mock_result = {
            "rec_texts": ["Castle Lv.5"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped
            mock_img.size = (1440, 2560)

            ocr = GameOCR()
            results = ocr.read_building_name(temp_image)

            # Should crop to building_header region
            mock_img.crop.assert_called_once()
            assert len(results) == 1


class TestGameOCRReadTimersTargeted:
    """Tests for GameOCR.read_timers_targeted method."""

    def test_read_timers_from_regions(self, mock_ocr_instance, temp_image):
        """Test reading timers from specific regions."""
        mock_result = {
            "rec_texts": ["01:30:45"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped
            mock_img.size = (1440, 2560)

            ocr = GameOCR()
            regions = [(100, 200, 50, 30)]  # x, y, w, h
            results = ocr.read_timers_targeted(temp_image, regions)

            assert len(results) == 1
            assert results[0]["timer"] == "01:30:45"

    def test_read_timers_multiple_regions(self, mock_ocr_instance, temp_image):
        """Test reading timers from multiple regions."""
        call_count = [0]
        def side_effect(image_path):
            call_count[0] += 1
            return [{
                "rec_texts": [f"Timer{call_count[0]}"],
                "rec_scores": [0.95],
                "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
            }]
        
        mock_ocr_instance.predict.side_effect = side_effect

        with patch("PIL.Image.open") as mock_open:
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_cropped = MagicMock()
            mock_img.crop.return_value = mock_cropped
            mock_img.size = (1440, 2560)

            ocr = GameOCR()
            regions = [(100, 200, 50, 30), (200, 300, 50, 30)]
            ocr.read_timers_targeted(temp_image, regions)

            # Should crop twice (once per region)
            assert mock_img.crop.call_count == 2


class TestGameOCRDetectScreenType:
    """Tests for GameOCR.detect_screen_type method."""

    def test_detect_home_city_by_tabs(self, mock_ocr_instance, temp_image):
        """Test home_city detection via bottom tabs."""
        mock_result = {
            "rec_texts": ["Conquest", "Heroes", "Backpack", "Alliance"],
            "rec_scores": [0.95, 0.95, 0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]] * 4
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "home_city"

    def test_detect_popup_quit(self, mock_ocr_instance, temp_image):
        """Test popup_quit detection."""
        mock_result = {
            "rec_texts": ["Quit Game"],
            "rec_scores": [0.95],
            "dt_polys": [[[500, 800], [700, 800], [700, 900], [500, 900]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "popup_quit"

    def test_detect_battle_prep(self, mock_ocr_instance, temp_image):
        """Test battle_prep detection."""
        mock_result = {
            "rec_texts": ["Quick Deploy", "Fight"],
            "rec_scores": [0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [100, 60], [100, 110], [0, 110]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "battle_prep"

    def test_detect_battle_active(self, mock_ocr_instance, temp_image):
        """Test battle_active detection."""
        mock_result = {
            "rec_texts": ["Auto", "x1"],
            "rec_scores": [0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[0, 60], [100, 60], [100, 110], [0, 110]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "battle_active"

    def test_detect_battle_result_victory(self, mock_ocr_instance, temp_image):
        """Test battle_result detection via Victory."""
        mock_result = {
            "rec_texts": ["Victory!"],
            "rec_scores": [0.95],
            "dt_polys": [[[600, 400], [800, 400], [800, 600], [600, 600]]]  # Center top
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "battle_result"

    def test_detect_building_menu(self, mock_ocr_instance, temp_image):
        """Test building_menu detection."""
        mock_result = {
            "rec_texts": ["Upgrade", "Lv.5", "Requirements"],
            "rec_scores": [0.95, 0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]] * 3
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "building_menu"

    def test_detect_unknown_screen(self, mock_ocr_instance, temp_image):
        """Test unknown screen fallback."""
        mock_result = {
            "rec_texts": ["Random Text"],
            "rec_scores": [0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "unknown"

    def test_detect_home_city_by_power_and_vip(self, mock_ocr_instance, temp_image):
        """Test home_city detection via power badge and VIP."""
        mock_result = {
            "rec_texts": ["100000", "VIP 3"],
            "rec_scores": [0.95, 0.95],
            "dt_polys": [[[0, 0], [100, 0], [100, 50], [0, 50]],
                        [[1300, 0], [1400, 0], [1400, 50], [1300, 50]]]
        }
        mock_ocr_instance.predict.return_value = [mock_result]

        ocr = GameOCR()
        screen_type = ocr.detect_screen_type(temp_image)

        assert screen_type == "home_city"
