"""
OCR Configuration Module

Handles all configuration settings for the Smart OCR system.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class OCRConfig:
    """Configuration for the OCR engine."""

    # Language settings
    lang: str = "ch"  # Chinese by default
    use_angle_cls: bool = True  # Enable text angle classification

    # Performance settings
    use_gpu: bool = False  # GPU acceleration
    gpu_mem: int = 500  # GPU memory limit (MB)
    cpu_threads: int = 10  # CPU thread count

    # Detection settings
    det_algorithm: str = "DB"  # Detection algorithm
    det_db_thresh: float = 0.3
    det_db_box_thresh: float = 0.6
    det_db_unclip_ratio: float = 1.5

    # Recognition settings
    rec_algorithm: str = "SVTR_LCNet"
    rec_batch_num: int = 6
    max_text_length: int = 25

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("output"))
    export_formats: List[str] = field(default_factory=lambda: ["txt", "json", "csv"])

    # Logging
    enable_mkldnn: bool = False
    show_log: bool = False

    def __post_init__(self) -> None:
        """Validate and process configuration after initialization."""
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Validate export formats
        valid_formats = {"txt", "json", "csv", "xlsx"}
        for fmt in self.export_formats:
            if fmt not in valid_formats:
                raise ValueError(
                    f"Invalid export format: {fmt}. Valid: {valid_formats}"
                )

    @classmethod
    def from_env(cls) -> "OCRConfig":
        """Create configuration from environment variables."""
        return cls(
            lang=os.getenv("OCR_LANG", "ch"),
            use_gpu=os.getenv("OCR_USE_GPU", "false").lower() == "true",
            output_dir=Path(os.getenv("OCR_OUTPUT_DIR", "output")),
        )

    @classmethod
    def for_chinese(cls) -> "OCRConfig":
        """Optimized configuration for Chinese text recognition."""
        return cls(
            lang="ch",
            use_angle_cls=True,
            det_db_thresh=0.3,
            det_db_box_thresh=0.5,
        )

    @classmethod
    def for_english(cls) -> "OCRConfig":
        """Optimized configuration for English text recognition."""
        return cls(
            lang="en",
            use_angle_cls=False,
        )
