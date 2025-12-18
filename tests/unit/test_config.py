"""
Unit tests for OCR configuration.
"""

from pathlib import Path

import pytest

from smart_ocr.core.config import OCRConfig


class TestOCRConfig:
    """Test cases for OCRConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OCRConfig()
        assert config.lang == "ch"
        assert config.use_angle_cls is True
        assert config.use_gpu is False

    def test_chinese_preset(self):
        """Test Chinese language preset."""
        config = OCRConfig.for_chinese()
        assert config.lang == "ch"
        assert config.use_angle_cls is True

    def test_english_preset(self):
        """Test English language preset."""
        config = OCRConfig.for_english()
        assert config.lang == "en"
        assert config.use_angle_cls is False

    def test_invalid_export_format(self):
        """Test that invalid export format raises error."""
        with pytest.raises(ValueError):
            OCRConfig(export_formats=["invalid_format"])

    def test_output_dir_creation(self, temp_dir):
        """Test that output directory is created automatically."""
        output_path = temp_dir / "new_output"
        config = OCRConfig(output_dir=output_path)
        assert output_path.exists()

    def test_custom_settings(self):
        """Test custom configuration settings."""
        config = OCRConfig(lang="en", use_gpu=True, cpu_threads=8, det_db_thresh=0.5)
        assert config.lang == "en"
        assert config.use_gpu is True
        assert config.cpu_threads == 8
        assert config.det_db_thresh == 0.5
