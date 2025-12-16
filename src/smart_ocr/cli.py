"""
Smart OCR Command Line Interface

Provides CLI commands for OCR processing.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core.config import OCRConfig
from .core.ocr_engine import OCREngine


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="smart-ocr",
        description="Smart OCR System - Enterprise-grade Chinese OCR Solution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  smart-ocr process image.png

  # Process all images in a directory
  smart-ocr process ./documents/ --recursive

  # Export results to different formats
  smart-ocr process image.png --output result.json --format json

  # Use GPU acceleration
  smart-ocr process image.png --gpu

  # Process with English language
  smart-ocr process image.png --lang en
        """
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process image(s) for OCR"
    )
    process_parser.add_argument(
        "input",
        type=str,
        help="Input image file or directory"
    )
    process_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path"
    )
    process_parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["txt", "json", "csv"],
        default="txt",
        help="Output format (default: txt)"
    )
    process_parser.add_argument(
        "--lang", "-l",
        type=str,
        default="ch",
        help="Language for OCR (default: ch for Chinese)"
    )
    process_parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU acceleration"
    )
    process_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Process directories recursively"
    )
    process_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output"
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show or modify configuration"
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration"
    )

    return parser


def process_command(args: argparse.Namespace) -> int:
    """Handle the process command."""
    input_path = Path(args.input)

    # Create configuration
    config = OCRConfig(
        lang=args.lang,
        use_gpu=args.gpu,
        show_log=not args.quiet
    )

    # Initialize engine
    engine = OCREngine(config)

    # Process input
    if input_path.is_file():
        results = [engine.process_image(input_path)]
        if not args.quiet:
            print(f"Processed: {input_path}")
            print(f"Confidence: {results[0].average_confidence:.2%}")
            print("-" * 40)
            print(results[0].text)
    elif input_path.is_dir():
        results = engine.process_directory(
            input_path,
            recursive=args.recursive
        )
        if not args.quiet:
            print(f"Processed {len(results)} images")
    else:
        print(f"Error: Input not found: {input_path}", file=sys.stderr)
        return 1

    # Export if output specified
    if args.output:
        output_path = engine.export_results(
            results,
            output_path=args.output,
            format=args.format
        )
        if not args.quiet:
            print(f"Results exported to: {output_path}")

    return 0


def config_command(args: argparse.Namespace) -> int:
    """Handle the config command."""
    if args.show:
        config = OCRConfig()
        print("Current OCR Configuration:")
        print("-" * 40)
        for field_name in config.__dataclass_fields__:
            value = getattr(config, field_name)
            print(f"  {field_name}: {value}")
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.version:
        from . import __version__
        print(f"Smart OCR System v{__version__}")
        return 0

    if args.command == "process":
        return process_command(args)
    elif args.command == "config":
        return config_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
