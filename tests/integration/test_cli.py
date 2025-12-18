"""
Integration tests for CLI commands.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from smart_ocr.cli import create_parser, main


class TestCLIParser:
    """Test cases for CLI argument parsing."""

    def test_parser_creation(self):
        """Test parser is created correctly."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "smart-ocr"

    def test_version_flag(self):
        """Test version flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["--version"])
        assert args.version is True

    def test_process_command_basic(self):
        """Test basic process command parsing."""
        parser = create_parser()
        args = parser.parse_args(["process", "test.png"])
        assert args.command == "process"
        assert args.input == "test.png"
        assert args.format == "txt"  # default

    def test_process_command_with_options(self):
        """Test process command with all options."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "process",
                "test.png",
                "--output",
                "result.json",
                "--format",
                "json",
                "--lang",
                "en",
                "--gpu",
                "--recursive",
                "--quiet",
            ]
        )
        assert args.output == "result.json"
        assert args.format == "json"
        assert args.lang == "en"
        assert args.gpu is True
        assert args.recursive is True
        assert args.quiet is True

    def test_config_command(self):
        """Test config command parsing."""
        parser = create_parser()
        args = parser.parse_args(["config", "--show"])
        assert args.command == "config"
        assert args.show is True


class TestCLIExecution:
    """Test cases for CLI execution."""

    def test_version_output(self, capsys):
        """Test version command output."""
        result = main(["--version"])
        captured = capsys.readouterr()
        assert "Smart OCR System" in captured.out
        assert result == 0

    def test_no_command_shows_help(self, capsys):
        """Test running without command shows help."""
        result = main([])
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or result == 0

    def test_config_show(self, capsys):
        """Test config show command."""
        result = main(["config", "--show"])
        captured = capsys.readouterr()
        assert "Configuration" in captured.out
        assert result == 0

    def test_process_file_not_found(self, capsys):
        """Test processing non-existent file."""
        result = main(["process", "nonexistent_file.png", "--quiet"])
        assert result == 1

    @patch("smart_ocr.cli.OCREngine")
    def test_process_single_image(self, mock_engine_class, temp_dir, capsys):
        """Test processing a single image."""
        # Create test image
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        img_path = temp_dir / "test.png"
        img = Image.new("RGB", (100, 50), color="white")
        img.save(img_path)

        # Setup mock
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.average_confidence = 0.95
        mock_result.text = "Test OCR output"
        mock_engine.process_image.return_value = mock_result
        mock_engine_class.return_value = mock_engine

        result = main(["process", str(img_path)])

        assert result == 0
        mock_engine.process_image.assert_called_once()

    @patch("smart_ocr.cli.OCREngine")
    def test_process_directory(self, mock_engine_class, temp_dir, capsys):
        """Test processing a directory."""
        # Create test images
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        for i in range(2):
            img = Image.new("RGB", (100, 50), color="white")
            img.save(temp_dir / f"test_{i}.png")

        # Setup mock
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.average_confidence = 0.9
        mock_result.text = "Test"
        mock_engine.process_directory.return_value = [mock_result, mock_result]
        mock_engine_class.return_value = mock_engine

        result = main(["process", str(temp_dir)])

        assert result == 0
        mock_engine.process_directory.assert_called_once()

    @patch("smart_ocr.cli.OCREngine")
    def test_process_with_export(self, mock_engine_class, temp_dir, capsys):
        """Test processing with export."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        img_path = temp_dir / "test.png"
        img = Image.new("RGB", (100, 50), color="white")
        img.save(img_path)

        output_path = temp_dir / "output.json"

        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.average_confidence = 0.95
        mock_result.text = "Test"
        mock_engine.process_image.return_value = mock_result
        mock_engine.export_results.return_value = output_path
        mock_engine_class.return_value = mock_engine

        result = main(
            ["process", str(img_path), "--output", str(output_path), "--format", "json"]
        )

        assert result == 0
        mock_engine.export_results.assert_called_once()
