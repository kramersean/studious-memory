from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, session_scope
from .models import Note, ParaBucket, default_tags, tags_to_list
from .schemas import (
    NoteCreate,
    NoteOut,
    NoteUpdate,
    ParaUpdate,
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
def list_notes(para_bucket: ParaBucket | None = None, db: Session = Depends(get_db)):
    query = db.query(Note)
    if para_bucket:
        query = query.filter(Note.para_bucket == para_bucket)
    return [serialize_note(note) for note in query.order_by(Note.updated_at.desc()).all()]


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(
        title=payload.title,
        content=payload.content,
        para_bucket=payload.para_bucket,
        area_name=payload.area_name,
        project_outcome=payload.project_outcome,
        classification_confidence=payload.classification_confidence,
        classified_by=payload.classified_by,
        user_overridden=payload.user_overridden,
        original_para_bucket=payload.original_para_bucket,
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
    if payload.para_bucket is not None and payload.para_bucket != note.para_bucket:
        if note.original_para_bucket is None:
            note.original_para_bucket = note.para_bucket.value
        note.para_bucket = payload.para_bucket
        note.user_overridden = True
    if payload.area_name is not None:
        note.area_name = payload.area_name
    if payload.project_outcome is not None:
        note.project_outcome = payload.project_outcome
    if payload.classification_confidence is not None:
        note.classification_confidence = payload.classification_confidence
    if payload.classified_by is not None:
        note.classified_by = payload.classified_by
    if payload.user_overridden is not None:
        note.user_overridden = payload.user_overridden
    if payload.original_para_bucket is not None:
        note.original_para_bucket = payload.original_para_bucket
    if payload.tags is not None:
        note.tags = default_tags(payload.tags)
    if payload.captured_from is not None:
        note.captured_from = payload.captured_from
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
        para_bucket=result.bucket,
        area_name=result.area_name,
        project_outcome=result.project_outcome,
        classification_confidence=result.confidence,
        classified_by=result.method,
        user_overridden=False,
        tags=default_tags(payload.tags),
        captured_from=payload.captured_from or "quick-capture",
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    note_out = serialize_note(note)
    return QuickCaptureResponse(
        suggested_bucket=result.bucket,
        note=note_out,
        reason=result.reason,
        confidence=result.confidence,
        area_name=result.area_name,
        project_outcome=result.project_outcome,
    )


@app.patch("/notes/{note_id}/para", response_model=NoteOut)
def override_para(note_id: int, payload: ParaUpdate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.original_para_bucket is None:
        note.original_para_bucket = note.para_bucket.value

    note.para_bucket = payload.para_bucket
    note.area_name = payload.area_name
    note.project_outcome = payload.project_outcome
    note.user_overridden = True
    note.classified_by = note.classified_by or "heuristic"

    note.touch()

    db.add(note)
    db.commit()
    db.refresh(note)
    return serialize_note(note)


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def serialize_note(note: Note) -> NoteOut:
    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        para_bucket=note.para_bucket,
        area_name=note.area_name,
        project_outcome=note.project_outcome,
        classification_confidence=note.classification_confidence,
        classified_by=note.classified_by,
        user_overridden=note.user_overridden,
        original_para_bucket=note.original_para_bucket,
        tags=tags_to_list(note.tags),
        created_at=note.created_at,
        updated_at=note.updated_at,
        captured_from=note.captured_from,
    )
