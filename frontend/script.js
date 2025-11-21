const API_BASE = 'http://localhost:8000';

const captureForm = document.getElementById('capture-form');
const captureTitle = document.getElementById('capture-title');
const captureContent = document.getElementById('capture-content');
const captureTags = document.getElementById('capture-tags');
const captureSource = document.getElementById('capture-source');
const captureResult = document.getElementById('capture-result');
const filterSelect = document.getElementById('filter');
const notesContainer = document.getElementById('notes');

const BUCKET_LABELS = {
  project: 'Project',
  area: 'Area',
  resource: 'Resource',
  archive: 'Archive',
};

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || 'Request failed');
  }
  return res.json();
}

function parseTags(raw) {
  return raw
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);
}

async function loadNotes() {
  const bucket = filterSelect.value;
  const url = bucket ? `${API_BASE}/notes?para_bucket=${bucket}` : `${API_BASE}/notes`;
  const notes = await fetchJSON(url);
  renderNotes(notes);
}

function renderNotes(notes) {
  if (!notes.length) {
    notesContainer.innerHTML = '<p class="muted">No notes yet.</p>';
    return;
  }

  notesContainer.innerHTML = '';
  notes.forEach((note) => {
    const card = document.createElement('div');
    card.className = 'card';

    const header = document.createElement('div');
    header.className = 'note-header';
    header.innerHTML = `<strong>${note.title}</strong><span class="badge bucket-${note.para_bucket}">${BUCKET_LABELS[note.para_bucket] || note.para_bucket}</span>`;

    const paraControls = document.createElement('div');
    paraControls.className = 'para-controls';
    const select = document.createElement('select');
    select.className = 'bucket-select';
    Object.entries(BUCKET_LABELS).forEach(([value, label]) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label;
      if (note.para_bucket === value) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    select.addEventListener('change', async (event) => {
      try {
        await updateParaBucket(note.id, event.target.value, note.area_name, note.project_outcome);
        await loadNotes();
      } catch (err) {
        alert(err.message);
        select.value = note.para_bucket;
      }
    });
    paraControls.appendChild(select);
    header.appendChild(paraControls);

    const meta = document.createElement('div');
    meta.className = 'note-meta';
    const updated = new Date(note.updated_at).toLocaleString();
    const tags = note.tags ? note.tags.join(', ') : '';
    const confidence = note.classification_confidence
      ? ` · ${Math.round(note.classification_confidence * 100)}% confidence`
      : '';
    meta.textContent = `${updated}${tags ? ' · ' + tags : ''}${confidence}`;

    const content = document.createElement('div');
    content.className = 'note-content';
    content.textContent = note.content;

    const area = document.createElement('div');
    area.className = 'note-area';
    area.textContent = note.area_name ? `Area: ${note.area_name}` : '';

    card.appendChild(header);
    card.appendChild(meta);
    card.appendChild(content);
    if (note.area_name) {
      card.appendChild(area);
    }
    notesContainer.appendChild(card);
  });
}

async function updateParaBucket(id, para_bucket, area_name, project_outcome) {
  return fetchJSON(`${API_BASE}/notes/${id}/para`, {
    method: 'PATCH',
    body: JSON.stringify({ para_bucket, area_name, project_outcome }),
  });
}

captureForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  captureResult.classList.add('hidden');

  const payload = {
    title: captureTitle.value,
    content: captureContent.value,
    tags: parseTags(captureTags.value),
    captured_from: captureSource.value,
  };

  try {
    const response = await fetchJSON(`${API_BASE}/capture`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    captureResult.classList.remove('hidden');
    captureResult.innerHTML = `
      <div class="note-header">
        <strong>Suggested: ${BUCKET_LABELS[response.suggested_bucket] || response.suggested_bucket}</strong>
        <span class="badge bucket-${response.note.para_bucket}">${BUCKET_LABELS[response.note.para_bucket] || response.note.para_bucket}</span>
      </div>
      <div class="note-meta">${response.reason} · ${Math.round(response.confidence * 100)}% confidence</div>
      <div class="note-content">${response.note.title}: ${response.note.content}</div>
      ${response.area_name ? `<div class="note-area">Area: ${response.area_name}</div>` : ''}
      ${response.project_outcome ? `<div class="note-area">Outcome: ${response.project_outcome}</div>` : ''}
    `;

    captureForm.reset();
    loadNotes();
  } catch (err) {
    alert(err.message);
  }
});

filterSelect.addEventListener('change', () => {
  loadNotes();
});

loadNotes();
