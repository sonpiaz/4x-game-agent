"""Pytest configuration for agent tests."""
import sys
from unittest.mock import MagicMock

# Mock paddleocr before any imports
mock_paddleocr = MagicMock()
sys.modules['paddleocr'] = mock_paddleocr
