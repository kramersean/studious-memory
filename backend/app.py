from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, session_scope
from .models import Category, Note, default_tags, tags_to_list
from .schemas import (
    NoteCreate,
    NoteOut,
    NoteUpdate,
    QuickCaptureRequest,
    QuickCaptureResponse,
)
from .services import ClassificationResult, classify

app = FastAPI(title="Second Brain", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    with session_scope() as session:
        yield session


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/notes", response_model=list[NoteOut])
def list_notes(category: Category | None = None, db: Session = Depends(get_db)):
    query = db.query(Note)
    if category:
        query = query.filter(Note.category == category)
    return [serialize_note(note) for note in query.order_by(Note.updated_at.desc()).all()]


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        tags=default_tags(payload.tags),
        captured_from=payload.captured_from,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return serialize_note(note)


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.category is not None:
        note.category = payload.category
    if payload.tags is not None:
        note.tags = default_tags(payload.tags)
    note.touch()

    db.add(note)
    db.commit()
    db.refresh(note)
    return serialize_note(note)


@app.post("/capture", response_model=QuickCaptureResponse)
def quick_capture(payload: QuickCaptureRequest, db: Session = Depends(get_db)):
    result: ClassificationResult = classify(payload.content, payload.title, payload.tags)

    note = Note(
        title=payload.title,
        content=payload.content,
        category=result.category,
        tags=default_tags(payload.tags),
        captured_from=payload.captured_from or "quick-capture",
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    note_out = serialize_note(note)
    return QuickCaptureResponse(suggested_category=result.category, note=note_out, reason=result.reason)


def serialize_note(note: Note) -> NoteOut:
    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=tags_to_list(note.tags),
        created_at=note.created_at,
        updated_at=note.updated_at,
        captured_from=note.captured_from,
    )
