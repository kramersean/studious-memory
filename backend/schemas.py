from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import ParaBucket


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: list[str] | None = None
    captured_from: str | None = Field(None, description="Where the note originated, e.g. 'email', 'web'.")


class NoteCreate(NoteBase):
    para_bucket: ParaBucket
    area_name: str | None = None
    project_outcome: str | None = None
    classification_confidence: float | None = Field(1.0, ge=0.0, le=1.0)
    classified_by: str | None = "user"
    user_overridden: bool = False
    original_para_bucket: str | None = None


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    para_bucket: Optional[ParaBucket] = None
    area_name: Optional[str] = None
    project_outcome: Optional[str] = None
    classification_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    classified_by: Optional[str] = None
    user_overridden: Optional[bool] = None
    original_para_bucket: Optional[str] = None
    tags: list[str] | None = None
    captured_from: Optional[str] = None


class ParaUpdate(BaseModel):
    para_bucket: ParaBucket
    area_name: str | None = None
    project_outcome: str | None = None


class QuickCaptureRequest(BaseModel):
    title: str
    content: str
    tags: list[str] | None = None
    captured_from: str | None = None


class QuickCaptureResponse(BaseModel):
    suggested_bucket: ParaBucket
    note: NoteOut
    reason: str
    confidence: float
    area_name: str | None
    project_outcome: str | None


class NoteOut(NoteBase):
    id: int
    para_bucket: ParaBucket
    area_name: str | None = None
    project_outcome: str | None = None
    classification_confidence: float | None = None
    classified_by: str | None = None
    user_overridden: bool = False
    original_para_bucket: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
