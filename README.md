# Smart OCR System

**Enterprise-grade Chinese OCR Solution powered by PaddleOCR**

高性能中文 OCR 智能辨識系統，支援批量處理與多格式匯出。

## Features

- **Chinese Optimized** - 使用 PaddleOCR 引擎，針對中文辨識優化
- **Batch Processing** - 支援資料夾批量處理，遞迴掃描子目錄
- **Multi-format Export** - 支援 TXT、JSON、CSV 多種格式匯出
- **CLI Interface** - 簡潔的命令列介面，易於整合自動化流程
- **Configurable** - 靈活的配置選項，可調整辨識參數

## Requirements

- Python 3.10+
- PaddlePaddle 2.5+
- PaddleOCR 2.7+

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/bheadwei/smart-ocr-system.git
cd smart-ocr-system

# Create virtual environment with Python 3.10
uv venv --python 3.10

# Activate virtual environment
# Windows (Git Bash)
source .venv/Scripts/activate
# Windows (CMD)
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install dependencies
uv pip install paddlepaddle paddleocr Pillow numpy opencv-python

# Install the package in editable mode
uv pip install -e .
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install paddlepaddle paddleocr Pillow numpy opencv-python
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Process a single image
smart-ocr process image.png

# Process with output file
smart-ocr process image.png -o result.txt

# Process all images in a directory
smart-ocr process ./documents/

# Process directory recursively
smart-ocr process ./documents/ --recursive

# Export as JSON
smart-ocr process image.png -o result.json -f json

# Export as CSV
smart-ocr process ./documents/ -o results.csv -f csv

# Use GPU acceleration
smart-ocr process image.png --gpu

# Process English text
smart-ocr process image.png --lang en

# Quiet mode (suppress output)
smart-ocr process image.png -q
```

### Python API

```python
from smart_ocr import OCREngine, OCRConfig

# Create configuration
config = OCRConfig.for_chinese()  # Optimized for Chinese

# Initialize engine
engine = OCREngine(config)

# Process single image
result = engine.process_image("document.png")
print(result.text)
print(f"Confidence: {result.average_confidence:.2%}")

# Process directory
results = engine.process_directory("./documents/", recursive=True)

# Export results
engine.export_results(results, "output.json", format="json")
```

### Configuration Options

```python
from smart_ocr import OCRConfig

config = OCRConfig(
    lang="ch",              # Language: "ch" for Chinese, "en" for English
    use_gpu=False,          # Enable GPU acceleration
    use_angle_cls=True,     # Enable text angle classification
    det_db_thresh=0.3,      # Detection threshold
    det_db_box_thresh=0.6,  # Box detection threshold
    export_formats=["txt", "json", "csv"],  # Enabled export formats
)
```

## Project Structure

```
smart-ocr-system/
├── src/smart_ocr/           # Source code
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command line interface
│   └── core/
│       ├── config.py        # Configuration management
│       └── ocr_engine.py    # OCR processing engine
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── conftest.py          # Pytest fixtures
├── data/                    # Sample images
├── output/                  # Output directory
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Development

### Install dev dependencies

```bash
uv pip install pytest pytest-cov black isort flake8 mypy
```

### Run tests

```bash
pytest tests/
```

### Code formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type checking

```bash
mypy src/
```

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tiff)

## Export Formats

| Format | Description |
|--------|-------------|
| TXT | Plain text, one file per image |
| JSON | Structured data with confidence scores and bounding boxes |
| CSV | Tabular format for spreadsheet analysis |

## Performance Tips

1. **GPU Acceleration**: Use `--gpu` flag for faster processing on NVIDIA GPUs
2. **Batch Processing**: Process directories instead of individual files for better throughput
3. **Language Setting**: Set correct language (`--lang`) for optimal recognition accuracy

## License

MIT License

## Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Awesome multilingual OCR toolkit
- [PaddlePaddle](https://www.paddlepaddle.org.cn/) - Deep learning platform
