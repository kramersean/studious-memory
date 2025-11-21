from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text

from .database import Base


class Category(StrEnum):
    PROJECTS = "projects"
    AREAS = "areas"
    RESOURCES = "resources"
    ARCHIVES = "archives"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(Category), nullable=False)
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
