from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text

from .database import Base


class ParaBucket(StrEnum):
    PROJECT = "project"
    AREA = "area"
    RESOURCE = "resource"
    ARCHIVE = "archive"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    para_bucket = Column(Enum(ParaBucket), nullable=False)
    area_name = Column(String(255), nullable=True)
    project_outcome = Column(Text, nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classified_by = Column(String(50), nullable=True)
    user_overridden = Column(Boolean, default=False, nullable=False)
    original_para_bucket = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    tags = Column(String(255), nullable=True)
    captured_from = Column(String(255), nullable=True)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


def default_tags(tags: Optional[list[str]]) -> str | None:
    if not tags:
        return None
    cleaned = [tag.strip() for tag in tags if tag.strip()]
    return ",".join(cleaned) if cleaned else None


def tags_to_list(tag_string: str | None) -> list[str] | None:
    if not tag_string:
        return None
    return [tag for tag in tag_string.split(",") if tag]
