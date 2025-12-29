"""
OCR-related Pydantic models (DTOs).
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field


class StructuredField(BaseModel):
    """Structured data field from OCR."""

    key: str
    value: str
    confidence: float = Field(..., ge=0, le=1)


class TableData(BaseModel):
    """Table data from OCR."""

    headers: List[str]
    rows: List[List[str]]


class StructuredData(BaseModel):
    """Structured data extracted by OCR."""

    type: Optional[str] = None  # Document type (invoice, receipt, etc.)
    fields: List[StructuredField] = []
    tables: List[TableData] = []


class OCRTaskBase(BaseModel):
    """Base OCR task fields."""

    original_filename: str
    file_type: Literal["image", "pdf"]
    file_size: int
    page_count: int = 1


class OCRTaskResponse(OCRTaskBase):
    """OCR task response."""

    id: str
    user_id: str
    status: Literal["uploaded", "processing", "completed", "failed"]
    progress: int = Field(..., ge=0, le=100)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCRTaskListResponse(BaseModel):
    """OCR task list response."""

    tasks: List[OCRTaskResponse]
    total: int


class OCRResultBase(BaseModel):
    """Base OCR result fields."""

    page_number: int
    extracted_text: str
    confidence: float = Field(..., ge=0, le=1)


class OCRResultDetail(OCRResultBase):
    """Single page OCR result."""

    structured_data: Optional[StructuredData] = None


class OCRResultResponse(BaseModel):
    """OCR result response (all pages)."""

    task_id: str
    status: Literal["uploaded", "processing", "completed", "failed"]
    results: List[OCRResultDetail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OCRResultUpdate(BaseModel):
    """Update OCR result request."""

    page_number: int
    extracted_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None


class OCRProgressMessage(BaseModel):
    """WebSocket progress message."""

    type: str = "progress"
    task_id: str
    progress: int = Field(..., ge=0, le=100)
    status: Literal["uploaded", "processing", "completed", "failed"]
    timestamp: datetime
