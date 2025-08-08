// Reading Environment – JavaScript logic
//
// This script loads a JSON export from the EPE and displays a simple
// alignment table.  Users can choose which witnesses to view and select
// the base text.  Variant tokens are highlighted.

let editionData = null;
const jsonInput = document.getElementById('jsonInput');
const editionControls = document.getElementById('editionControls');
const editionView = document.getElementById('editionView');
const baseSelect = document.getElementById('baseSelect');
const witnessCheckboxes = document.getElementById('witnessCheckboxes');
const editionTable = document.getElementById('editionTable');

jsonInput.addEventListener('change', async (evt) => {
  const file = evt.target.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    editionData = JSON.parse(text);
    populateControls();
  } catch (e) {
    alert('Could not parse JSON: ' + e.message);
  }
});

function populateControls() {
  if (!editionData) return;
  // populate baseSelect
  baseSelect.innerHTML = '';
  editionData.witnesses.forEach(w => {
    const opt = document.createElement('option');
    opt.value = w.id;
    opt.textContent = w.name;
    baseSelect.appendChild(opt);
  });
  // populate witness checkboxes (all except first by default)
  witnessCheckboxes.innerHTML = '';
  editionData.witnesses.forEach((w, idx) => {
    const label = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = w.id;
    // By default check all witnesses except the first
    checkbox.checked = idx !== 0;
    checkbox.addEventListener('change', renderEdition);
    label.appendChild(checkbox);
    const span = document.createElement('span');
    span.textContent = w.name;
    label.appendChild(span);
    witnessCheckboxes.appendChild(label);
  });
  baseSelect.addEventListener('change', renderEdition);
  editionControls.classList.remove('hidden');
  editionView.classList.remove('hidden');
  renderEdition();
}

function renderEdition() {
  if (!editionData) return;
  // Determine selected base
  const baseId = baseSelect.value || editionData.witnesses[0].id;
  // Determine selected witnesses (others)
  const selectedIds = [];
  const checkboxes = witnessCheckboxes.querySelectorAll('input[type=checkbox]');
  checkboxes.forEach(cb => {
    if (cb.checked) selectedIds.push(cb.value);
  });
  // Always include base in selected if not already
  if (!selectedIds.includes(baseId)) {
    selectedIds.unshift(baseId);
  }
  // gather witness objects
  const selectedWitnesses = selectedIds.map(id => editionData.witnesses.find(w => w.id === id)).filter(Boolean);
  // Determine maximum token length
  const maxLen = Math.max(...selectedWitnesses.map(w => w.tokens.length));
  // Build table
  editionTable.innerHTML = '';
  const table = document.createElement('table');
  // header
  const thead = document.createElement('thead');
  const trh = document.createElement('tr');
  const thIndex = document.createElement('th');
  thIndex.textContent = 'Token#';
  trh.appendChild(thIndex);
  selectedWitnesses.forEach(w => {
    const th = document.createElement('th');
    th.textContent = w.name;
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  for (let idx = 0; idx < maxLen; idx++) {
    const tr = document.createElement('tr');
    const tdIndex = document.createElement('td');
    tdIndex.textContent = idx;
    tr.appendChild(tdIndex);
    const baseToken = selectedWitnesses[0].tokens[idx] || '';
    selectedWitnesses.forEach((w, wIndex) => {
      const td = document.createElement('td');
      const tok = w.tokens[idx] || '';
      td.textContent = tok;
      if (wIndex > 0 && tok !== baseToken) {
        td.classList.add('variant');
      }
      // annotation indicator
      const annos = editionData.annotations && editionData.annotations[w.id] && editionData.annotations[w.id][idx];
      if (annos && annos.length > 0) {
        td.title = annos.map(a => `${a.key}: ${a.value}`).join('\n');
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  editionTable.appendChild(table);
}