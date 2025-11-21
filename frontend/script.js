const API_BASE = 'http://localhost:8000';

const captureForm = document.getElementById('capture-form');
const captureTitle = document.getElementById('capture-title');
const captureContent = document.getElementById('capture-content');
const captureTags = document.getElementById('capture-tags');
const captureSource = document.getElementById('capture-source');
const captureResult = document.getElementById('capture-result');
const filterSelect = document.getElementById('filter');
const notesContainer = document.getElementById('notes');

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
  const category = filterSelect.value;
  const url = category ? `${API_BASE}/notes?category=${category}` : `${API_BASE}/notes`;
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
    header.innerHTML = `<strong>${note.title}</strong><span class="badge">${note.category}</span>`;

    const meta = document.createElement('div');
    meta.className = 'note-meta';
    const updated = new Date(note.updated_at).toLocaleString();
    meta.textContent = `${updated}${note.tags ? ' · ' + note.tags.join(', ') : ''}`;

    const content = document.createElement('div');
    content.className = 'note-content';
    content.textContent = note.content;

    card.appendChild(header);
    card.appendChild(meta);
    card.appendChild(content);
    notesContainer.appendChild(card);
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
        <strong>Suggested: ${response.suggested_category}</strong>
        <span class="badge">${response.note.category}</span>
      </div>
      <div class="note-meta">${response.reason}</div>
      <div class="note-content">${response.note.title}: ${response.note.content}</div>
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
