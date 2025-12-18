"""
Pytest configuration and fixtures for Smart OCR tests.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Create a sample OCR configuration for testing."""
    from smart_ocr.core.config import OCRConfig

    return OCRConfig(lang="ch", use_gpu=False, show_log=False)


@pytest.fixture
def test_images_dir():
    """Path to test images directory."""
    return Path(__file__).parent / "fixtures" / "images"


@pytest.fixture
def mock_paddle_result():
    """Create a mock PaddleOCR v3.x result object."""
    mock_result = MagicMock()
    mock_result.rec_texts = ["測試文字", "第二行"]
    mock_result.rec_scores = [0.95, 0.88]
    mock_result.dt_polys = None
    return mock_result


@pytest.fixture
def mock_paddle_ocr(mock_paddle_result):
    """Create a mocked PaddleOCR instance."""
    mock_ocr = MagicMock()
    mock_ocr.predict.return_value = [mock_paddle_result]
    return mock_ocr


@pytest.fixture
def sample_image(temp_dir):
    """Create a simple test image file."""
    try:
        from PIL import Image

        img_path = temp_dir / "test_image.png"
        img = Image.new("RGB", (100, 50), color="white")
        img.save(img_path)
        return img_path
    except ImportError:
        pytest.skip("Pillow not installed")
