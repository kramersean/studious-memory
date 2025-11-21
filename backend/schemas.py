from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import Category


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    category: Category
    tags: list[str] | None = None
    captured_from: str | None = Field(None, description="Where the note originated, e.g. 'email', 'web'.")


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[Category] = None
    tags: list[str] | None = None


class QuickCaptureRequest(BaseModel):
    title: str
    content: str
    tags: list[str] | None = None
    captured_from: str | None = None


class QuickCaptureResponse(BaseModel):
    suggested_category: Category
    note: NoteOut
    reason: str


class NoteOut(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
