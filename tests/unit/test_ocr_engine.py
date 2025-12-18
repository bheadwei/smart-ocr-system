"""
Unit tests for OCR engine.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from smart_ocr.core.config import OCRConfig
from smart_ocr.core.ocr_engine import OCREngine, OCRLine, OCRResult


class TestOCRLine:
    """Test cases for OCRLine class."""

    def test_create_line(self):
        """Test creating an OCR line."""
        line = OCRLine("測試文字", 0.95, [[0, 0], [100, 0], [100, 20], [0, 20]])
        assert line.text == "測試文字"
        assert line.confidence == 0.95
        assert len(line.bbox) == 4

    def test_to_dict(self):
        """Test converting line to dictionary."""
        line = OCRLine("Hello", 0.88, [[0, 0], [50, 0], [50, 10], [0, 10]])
        result = line.to_dict()
        assert result["text"] == "Hello"
        assert result["confidence"] == 0.88
        assert "bbox" in result


class TestOCRResult:
    """Test cases for OCRResult class."""

    def test_text_property(self):
        """Test combined text output."""
        lines = [OCRLine("Line 1", 0.9, []), OCRLine("Line 2", 0.85, [])]
        result = OCRResult(Path("test.png"), lines)
        assert result.text == "Line 1\nLine 2"

    def test_average_confidence(self):
        """Test average confidence calculation."""
        lines = [OCRLine("A", 0.8, []), OCRLine("B", 1.0, [])]
        result = OCRResult(Path("test.png"), lines)
        assert result.average_confidence == 0.9

    def test_empty_result(self):
        """Test empty result handling."""
        result = OCRResult(Path("test.png"), [])
        assert result.text == ""
        assert result.average_confidence == 0.0

    def test_to_dict(self):
        """Test dictionary conversion."""
        lines = [OCRLine("Test", 0.95, [])]
        result = OCRResult(Path("test.png"), lines)
        data = result.to_dict()
        assert "source_file" in data
        assert "text" in data
        assert "lines" in data

    def test_from_paddle_result_v3(self, mock_paddle_result):
        """Test parsing PaddleOCR v3.x result format."""
        result = OCRResult.from_paddle_result([mock_paddle_result], Path("test.png"))
        assert len(result.lines) == 2
        assert result.lines[0].text == "測試文字"
        assert result.lines[0].confidence == 0.95


class TestOCREngine:
    """Test cases for OCREngine class."""

    def test_init_default_config(self):
        """Test engine initialization with default config."""
        engine = OCREngine()
        assert engine.config is not None
        assert engine.config.lang == "ch"
        assert engine._initialized is False

    def test_init_custom_config(self):
        """Test engine initialization with custom config."""
        config = OCRConfig(lang="en", use_gpu=True)
        engine = OCREngine(config)
        assert engine.config.lang == "en"
        assert engine.config.use_gpu is True

    def test_file_not_found(self, sample_config):
        """Test handling of non-existent file."""
        engine = OCREngine(sample_config)
        engine._initialized = True
        engine._ocr = MagicMock()

        with pytest.raises(FileNotFoundError):
            engine.process_image("nonexistent.png")

    def test_directory_not_found(self, sample_config):
        """Test handling of non-existent directory."""
        engine = OCREngine(sample_config)
        engine._initialized = True
        engine._ocr = MagicMock()

        with pytest.raises(NotADirectoryError):
            engine.process_directory("nonexistent_dir")

    def test_process_image(self, sample_image, mock_paddle_ocr):
        """Test image processing with mocked PaddleOCR."""
        engine = OCREngine()
        engine._ocr = mock_paddle_ocr
        engine._initialized = True

        result = engine.process_image(sample_image)
        assert isinstance(result, OCRResult)
        mock_paddle_ocr.predict.assert_called_once()

    def test_process_directory(self, temp_dir, sample_config):
        """Test directory processing."""
        # Create test images
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        for i in range(3):
            img = Image.new("RGB", (100, 50), color="white")
            img.save(temp_dir / f"test_{i}.png")

        engine = OCREngine(sample_config)
        engine._initialized = True
        mock_ocr = MagicMock()
        mock_result = MagicMock()
        mock_result.rec_texts = ["Test"]
        mock_result.rec_scores = [0.9]
        mock_result.dt_polys = None
        mock_ocr.predict.return_value = [mock_result]
        engine._ocr = mock_ocr

        results = engine.process_directory(temp_dir)
        assert len(results) == 3

    def test_invalid_export_format(self, sample_config, temp_dir):
        """Test invalid export format raises error."""
        sample_config.export_formats = ["json"]
        engine = OCREngine(sample_config)

        with pytest.raises(ValueError):
            engine.export_results([], format="xml")

    def test_export_json(self, sample_config, temp_dir):
        """Test JSON export."""
        sample_config.output_dir = temp_dir
        engine = OCREngine(sample_config)

        lines = [OCRLine("Test", 0.95, [])]
        results = [OCRResult(Path("test.png"), lines)]

        output = engine.export_results(results, format="json")
        assert output.exists()
        assert output.suffix == ".json"

    def test_export_csv(self, sample_config, temp_dir):
        """Test CSV export."""
        sample_config.output_dir = temp_dir
        engine = OCREngine(sample_config)

        lines = [OCRLine("Test", 0.95, [[0, 0], [10, 0], [10, 10], [0, 10]])]
        results = [OCRResult(Path("test.png"), lines)]

        output = engine.export_results(results, format="csv")
        assert output.exists()
        assert output.suffix == ".csv"

    def test_export_txt(self, sample_config, temp_dir):
        """Test TXT export."""
        sample_config.output_dir = temp_dir
        engine = OCREngine(sample_config)

        lines = [OCRLine("Test", 0.95, [])]
        results = [OCRResult(Path("test.png"), lines)]

        output = engine.export_results(results, format="txt")
        assert output.exists()
        assert output.suffix == ".txt"
