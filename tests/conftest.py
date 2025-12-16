"""
Pytest configuration and fixtures for Smart OCR tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Create a sample OCR configuration for testing."""
    from src.smart_ocr.core.config import OCRConfig
    return OCRConfig(
        lang="ch",
        use_gpu=False,
        show_log=False
    )


@pytest.fixture
def test_images_dir():
    """Path to test images directory."""
    return Path(__file__).parent / "fixtures" / "images"
