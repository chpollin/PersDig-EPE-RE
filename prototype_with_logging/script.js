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

document.addEventListener('DOMContentLoaded', () => {
  loadWitnesses();
  document.getElementById('compareBtn').addEventListener('click', compareWitnesses);
  document.getElementById('searchBtn').addEventListener('click', searchTokens);
  document.getElementById('uploadBtn').addEventListener('click', uploadWitness);
});