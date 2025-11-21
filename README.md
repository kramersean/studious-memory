# Second Brain (PARA)

A lightweight full-stack prototype for an AI-assisted second brain using the PARA framework (Projects, Areas, Resources, Archives) with quick capture and heuristic categorization.

## Features
- FastAPI backend with SQLite storage and SQLAlchemy ORM
- Quick capture endpoint that suggests PARA bucket via keyword heuristics while preserving user control
- REST endpoints to list, create, and update notes
- Minimal frontend for capturing ideas and browsing organized notes

## Getting started

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

### Frontend
Serve the static assets from `frontend/` using any web server, for example:
```bash
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000` in your browser. The frontend expects the API at `http://localhost:8000`.

### End-to-end demo
1) Start the backend (in one terminal):
```bash
uvicorn backend.app:app --reload --port 8000
```
2) Serve the frontend (in another terminal):
```bash
cd frontend
python -m http.server 3000
```
3) Open the app: http://localhost:3000
4) Try a quick capture: enter a title/content and press **Quick Capture**. The backend will suggest a PARA bucket, store the note, and the UI will show the result immediately.
5) Browse buckets: use the **Filter by PARA** buttons to view notes by Projects, Areas, Resources, or Archives.

You can also exercise the API directly with curl:
```bash
curl -X POST http://localhost:8000/capture \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Draft launch plan",
    "content": "Outline tasks and milestones for Q3 release",
    "tags": ["launch", "roadmap"],
    "captured_from": "curl-demo"
  }'
```
The response returns the stored note plus the suggested PARA bucket, confidence, and reasoning.

## API quick reference
- `GET /health` – service status
- `GET /notes?para_bucket={project|area|resource|archive}` – list notes, optionally filtered
- `POST /notes` – create a note with explicit PARA bucket and optional area/project metadata
- `PATCH /notes/{id}` – update note fields, marking overrides when the PARA bucket changes
- `PATCH /notes/{id}/para` – shortcut endpoint to change the PARA bucket (records original bucket and user override)
- `POST /capture` – quick capture that auto-categorizes using heuristics and returns the suggested bucket with rationale

Notes are stored with timestamps, optional tags, and source metadata for future retrieval.
