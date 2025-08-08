async function fetchWitnesses() {
  const resp = await fetch('/api/witnesses');
  const data = await resp.json();
  return data;
}

function populateSelect(select, witnesses) {
  select.innerHTML = '';
  witnesses.forEach(w => {
    const opt = document.createElement('option');
    opt.value = w.id;
    opt.textContent = w.label;
    select.appendChild(opt);
  });
}

async function loadWitnesses() {
  try {
    const witnesses = await fetchWitnesses();
    const baseSelect = document.getElementById('baseSelect');
    const witnessSelect = document.getElementById('witnessSelect');
    populateSelect(baseSelect, witnesses);
    populateSelect(witnessSelect, witnesses);
  } catch (err) {
    console.error('Fehler beim Laden der Zeugen', err);
  }
}

async function compareWitnesses() {
  const baseId = document.getElementById('baseSelect').value;
  const witnessId = document.getElementById('witnessSelect').value;
  if (!baseId || !witnessId) {
    alert('Bitte wählen Sie Basetext und Zeugen aus.');
    return;
  }
  const resp = await fetch(`/api/alignments?base=${encodeURIComponent(baseId)}&witness=${encodeURIComponent(witnessId)}`);
  const data = await resp.json();
  const tbody = document.querySelector('#alignmentTable tbody');
  tbody.innerHTML = '';
    const baseIdVal = baseId;
    const witIdVal = witnessId;
    data.alignments.forEach(al => {
      const tr = document.createElement('tr');
      if (al.base.text !== al.witness.text) tr.classList.add('diff');
      const posTd = document.createElement('td');
      posTd.textContent = al.position;
      const baseTd = document.createElement('td');
      baseTd.textContent = al.base.text;
      // witness cell
      const witTd = document.createElement('td');
      witTd.textContent = al.witness ? al.witness.text : '[—]';
      // store ids for annotation
      if (al.witness && al.witness.id) {
        witTd.dataset.witnessId = witIdVal;
        witTd.dataset.tokenId = al.witness.id;
        witTd.addEventListener('click', handleAnnotation);
      }
      tr.appendChild(posTd);
      tr.appendChild(baseTd);
      tr.appendChild(witTd);
      tbody.appendChild(tr);
    });
    // Markiere bereits vorhandene Annotationen
    highlightAnnotated();
}

async function searchTokens() {
  const query = document.getElementById('searchInput').value.trim();
  const resultsList = document.getElementById('searchResults');
  resultsList.innerHTML = '';
  if (!query) return;
  const witnesses = await fetchWitnesses();
  for (const w of witnesses) {
    const res = await fetch(`/api/witnesses/${encodeURIComponent(w.id)}`);
    const data = await res.json();
    const tokens = data.sections.flatMap(sec => sec.tokens);
    tokens.filter(tok => tok.text.includes(query)).forEach(tok => {
      const li = document.createElement('li');
      li.textContent = `${w.label} – Position ${tok.position}: ${tok.text}`;
      resultsList.appendChild(li);
    });
  }
}

async function uploadWitness() {
  const fileInput = document.getElementById('fileInput');
  const status = document.getElementById('uploadStatus');
  const file = fileInput.files[0];
  if (!file) {
    alert('Bitte wählen Sie eine JSON-Datei aus.');
    return;
  }
  try {
    const text = await file.text();
    const payload = JSON.parse(text);
    const resp = await fetch('/api/witnesses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      status.textContent = 'Zeuge importiert.';
      await loadWitnesses();
    } else {
      const msg = await resp.text();
      status.textContent = 'Fehler beim Import: ' + msg;
    }
  } catch (err) {
    status.textContent = 'Fehler: ' + err;
  }
}

const annotated = new Set();

let annotationsGlobal = [];

async function loadAnnotationsList() {
  const witnessId = document.getElementById('witnessSelect').value;
  if (!witnessId) return;
  const resp = await fetch(`/api/annotations?witness_id=${encodeURIComponent(witnessId)}`);
  const data = await resp.json();
  annotationsGlobal = data;
  const list = document.getElementById('annotationsList');
  list.innerHTML = '';
  data.forEach(ann => {
    const li = document.createElement('li');
    // Anzeige: Token-ID und Annotationstext
    const span = document.createElement('span');
    span.textContent = `${ann.token_id}: ${ann.annotation}`;
    li.appendChild(span);
    // Löschknopf für Annotation
    if (ann.id !== undefined) {
      const btn = document.createElement('button');
      btn.textContent = '×';
      btn.title = 'Annotation löschen';
      btn.classList.add('ann-delete');
      btn.dataset.annId = ann.id;
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteAnnotation(ann.id);
      });
      li.appendChild(btn);
    }
    list.appendChild(li);
  });
  // Highlight annotated tokens in the table
  highlightAnnotated();
}

function highlightAnnotated() {
  const cells = document.querySelectorAll('#alignmentTable td[data-token-id]');
  cells.forEach(cell => {
    const tokenId = cell.dataset.tokenId;
    cell.classList.toggle('annotated', annotationsGlobal.some(a => a.token_id === tokenId));
  });
}

async function loadLogs() {
  const resp = await fetch('/api/logs');
  const data = await resp.json();
  const pre = document.getElementById('logsPre');
  pre.textContent = data.logs.join('\n');
}

async function handleAnnotation(event) {
  const cell = event.currentTarget;
  const witnessId = cell.dataset.witnessId;
  const tokenId = cell.dataset.tokenId;
  if (!witnessId || !tokenId) return;
  const note = prompt('Annotation für Token ' + tokenId + ':');
  if (!note) return;
  try {
    const resp = await fetch('/api/annotations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ witness_id: witnessId, token_id: tokenId, annotation: note })
    });
    if (resp.ok) {
      annotated.add(tokenId);
      cell.classList.add('annotated');
      alert('Annotation gespeichert.');
    } else {
      const text = await resp.text();
      alert('Fehler beim Speichern: ' + text);
    }
  } catch (err) {
    alert('Fehler: ' + err);
  }
}

/**
 * Löscht eine vorhandene Annotation per API. Nach erfolgreichem Entfernen wird die
 * Liste neu geladen und die Hervorhebung aktualisiert. Es wird eine Bestätigungs-
 * abfrage gestellt, um versehentliches Löschen zu vermeiden.
 *
 * @param {number|string} annId Die ID der zu löschenden Annotation
 */
async function deleteAnnotation(annId) {
  if (!confirm('Möchten Sie diese Annotation wirklich löschen?')) {
    return;
  }
  try {
    const resp = await fetch(`/api/annotations/${encodeURIComponent(annId)}`, { method: 'DELETE' });
    if (resp.status === 204) {
      // Liste und Hervorhebung aktualisieren
      await loadAnnotationsList();
    } else {
      const text = await resp.text();
      alert('Fehler beim Löschen: ' + text);
    }
  } catch (err) {
    alert('Fehler: ' + err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadWitnesses();
  document.getElementById('compareBtn').addEventListener('click', compareWitnesses);
  document.getElementById('searchBtn').addEventListener('click', searchTokens);
  document.getElementById('uploadBtn').addEventListener('click', uploadWitness);
  document.getElementById('loadAnnotationsBtn').addEventListener('click', loadAnnotationsList);
  document.getElementById('loadLogsBtn').addEventListener('click', loadLogs);
  document.getElementById('deleteBtn').addEventListener('click', deleteWitness);
  document.getElementById('exportBtn').addEventListener('click', exportWitness);
});

/**
 * Exportiert den aktuell ausgewählten Zeugen als JSON-Datei. Es wird lediglich
 * ein GET-Request auf den API-Endpunkt `/api/export/<id>` ausgeführt, wodurch
 * der Browser den Download automatisch startet.
 */
function exportWitness() {
  const witnessId = document.getElementById('witnessSelect').value;
  if (!witnessId) {
    alert('Bitte wählen Sie einen Zeugen aus.');
    return;
  }
  // Leitet den Browser um, sodass der Download erfolgt
  window.location.href = `/api/export/${encodeURIComponent(witnessId)}`;
}

/**
 * Löscht den aktuell ausgewählten Zeugen inklusive zugehöriger Annotationen.
 * Nach erfolgreichem Entfernen werden die Dropdowns aktualisiert, die
 * Vergleichstabelle geleert und etwaige Hervorhebungen entfernt. Fehlende
 * Felder oder Fehlermeldungen werden dem Benutzer angezeigt. Alle
 * API‑Interaktionen werden im Server‑Log festgehalten.
 */
async function deleteWitness() {
  const witnessId = document.getElementById('witnessSelect').value;
  if (!witnessId) {
    alert('Bitte wählen Sie einen Zeugen aus.');
    return;
  }
  if (!confirm('Möchten Sie diesen Zeugen wirklich löschen?')) {
    return;
  }
  try {
    const resp = await fetch(`/api/witnesses/${encodeURIComponent(witnessId)}`, { method: 'DELETE' });
    if (resp.status === 204) {
      alert('Zeuge gelöscht.');
      // Nach dem Löschen die Zeugenliste neu laden
      await loadWitnesses();
      // Tabelle und Annotationen zurücksetzen
      document.querySelector('#alignmentTable tbody').innerHTML = '';
      document.getElementById('annotationsList').innerHTML = '';
      annotationsGlobal = [];
      highlightAnnotated();
    } else {
      const text = await resp.text();
      alert('Fehler beim Löschen: ' + text);
    }
  } catch (err) {
    alert('Fehler: ' + err);
  }
}