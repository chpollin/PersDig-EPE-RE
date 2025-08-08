// Edition Production Environment – JavaScript logic
//
// This script implements a minimal client‑side edition preparation
// workflow.  Witnesses are imported as plain text files, tokenized
// according to a user supplied regex, aligned naïvely by index,
// annotated on demand and exported to TEI or JSON.

// Data structures
const witnesses = [];
let regexPattern = /\S+/g; // default pattern splits on whitespace
let alignment = []; // array of arrays representing aligned tokens
const annotations = {}; // nested map: witnessId -> tokenIndex -> list of {key,value}

// DOM references
const fileInput = document.getElementById('fileInput');
const regexInput = document.getElementById('regexInput');
const tokenizeBtn = document.getElementById('tokenizeBtn');
const witnessList = document.getElementById('witnessList');
const alignBtn = document.getElementById('alignBtn');
const alignmentTable = document.getElementById('alignmentTable');
const annotationEditor = document.getElementById('annotationEditor');
const annoListEl = document.getElementById('annoList');
const annoTokenIdEl = document.getElementById('annoTokenId');
const annoKeyInput = document.getElementById('annoKey');
const annoValueInput = document.getElementById('annoValue');
const addAnnoBtn = document.getElementById('addAnnoBtn');
const closeAnnoBtn = document.getElementById('closeAnnoBtn');
const exportTeiBtn = document.getElementById('exportTeiBtn');
const exportJsonBtn = document.getElementById('exportJsonBtn');

// Selected cell state
let selectedCell = null; // {witnessId, tokenIndex}

// Helper: load sample witnesses on start
async function loadSampleWitnesses() {
  const samples = ['witness1.txt', 'witness2.txt'];
  for (const fname of samples) {
    try {
      const response = await fetch('sample/' + fname);
      const text = await response.text();
      const id = fname.replace(/\.txt$/, '');
      const witness = { id, name: fname, text, tokens: [] };
      witnesses.push(witness);
    } catch (e) {
      console.warn('Could not load sample', fname, e);
    }
  }
  renderWitnessList();
}

// File upload handler
fileInput.addEventListener('change', async (event) => {
  const files = Array.from(event.target.files);
  for (const file of files) {
    const text = await file.text();
    const id = file.name.replace(/\.[^.]+$/, '');
    const witness = { id, name: file.name, text, tokens: [] };
    witnesses.push(witness);
  }
  renderWitnessList();
});

// Tokenization
tokenizeBtn.addEventListener('click', () => {
  const patternStr = regexInput.value.trim();
  try {
    // Evaluate pattern – supports /pattern/flags or plain string
    let patt = null;
    if (patternStr.startsWith('/') && patternStr.lastIndexOf('/') > 0) {
      const lastSlash = patternStr.lastIndexOf('/');
      const body = patternStr.slice(1, lastSlash);
      const flags = patternStr.slice(lastSlash + 1);
      patt = new RegExp(body, flags);
    } else {
      patt = new RegExp(patternStr, 'g');
    }
    regexPattern = patt;
  } catch (e) {
    alert('Invalid regex: ' + e.message);
    return;
  }
  // Tokenize each witness
  witnesses.forEach((wit) => {
    wit.tokens = [];
    if (!wit.text) return;
    const matches = Array.from(wit.text.matchAll(regexPattern));
    for (const match of matches) {
      wit.tokens.push(match[0]);
    }
  });
  renderWitnessList();
});

// Alignment
alignBtn.addEventListener('click', () => {
  if (witnesses.length < 2) {
    alert('Please import and tokenize at least two witnesses before aligning.');
    return;
  }
  // Determine max token length
  const maxLen = Math.max(...witnesses.map(w => w.tokens.length));
  alignment = [];
  for (let idx = 0; idx < maxLen; idx++) {
    const row = [];
    for (const w of witnesses) {
      row.push(w.tokens[idx] || '');
    }
    alignment.push(row);
  }
  renderAlignmentTable();
});

// Render witness list
function renderWitnessList() {
  witnessList.innerHTML = '';
  witnesses.forEach((wit) => {
    const card = document.createElement('div');
    card.className = 'witness-card';
    const title = document.createElement('h4');
    title.textContent = wit.name;
    card.appendChild(title);
    const meta = document.createElement('div');
    meta.className = 'metadata';
    meta.textContent = `Tokens: ${wit.tokens.length}`;
    card.appendChild(meta);
    const preview = document.createElement('pre');
    preview.textContent = wit.tokens.slice(0, 20).join(' ');
    card.appendChild(preview);
    witnessList.appendChild(card);
  });
}

// Render alignment table
function renderAlignmentTable() {
  alignmentTable.innerHTML = '';
  if (alignment.length === 0) return;
  const table = document.createElement('table');
  // Header row
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  const firstTh = document.createElement('th');
  firstTh.textContent = 'Token#';
  headerRow.appendChild(firstTh);
  for (const w of witnesses) {
    const th = document.createElement('th');
    th.textContent = w.name;
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  alignment.forEach((row, idx) => {
    const tr = document.createElement('tr');
    const indexTd = document.createElement('td');
    indexTd.textContent = idx;
    tr.appendChild(indexTd);
    // Determine base token (first witness)
    const baseToken = row[0];
    row.forEach((token, wIndex) => {
      const td = document.createElement('td');
      td.textContent = token;
      // variant class if not equal to base token
      if (wIndex > 0 && token !== baseToken) {
        td.classList.add('variant');
      }
      // attach dataset for identification
      td.dataset.wid = witnesses[wIndex].id;
      td.dataset.idx = idx;
      // click handler
      td.addEventListener('click', onCellClick);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  alignmentTable.appendChild(table);
}

// Cell click handler
function onCellClick(evt) {
  const td = evt.currentTarget;
  // Clear previous selection
  const prev = alignmentTable.querySelector('td.selected');
  if (prev) prev.classList.remove('selected');
  td.classList.add('selected');
  const witnessId = td.dataset.wid;
  const tokenIndex = parseInt(td.dataset.idx, 10);
  selectedCell = { witnessId, tokenIndex };
  showAnnotationEditor(witnessId, tokenIndex);
}

// Show annotation editor
function showAnnotationEditor(witnessId, tokenIndex) {
  annoTokenIdEl.textContent = `${witnessId} [${tokenIndex}]`;
  // Populate list
  const annos = (annotations[witnessId] && annotations[witnessId][tokenIndex]) || [];
  annoListEl.innerHTML = '';
  annos.forEach((anno, i) => {
    const li = document.createElement('li');
    li.textContent = `${anno.key}: ${anno.value}`;
    const removeBtn = document.createElement('button');
    removeBtn.textContent = '×';
    removeBtn.title = 'Remove';
    removeBtn.addEventListener('click', () => {
      annos.splice(i, 1);
      showAnnotationEditor(witnessId, tokenIndex);
    });
    li.appendChild(removeBtn);
    annoListEl.appendChild(li);
  });
  annotationEditor.classList.remove('hidden');
}

// Add annotation
addAnnoBtn.addEventListener('click', () => {
  const key = annoKeyInput.value.trim();
  const value = annoValueInput.value.trim();
  if (!selectedCell || !key || !value) return;
  if (!annotations[selectedCell.witnessId]) {
    annotations[selectedCell.witnessId] = {};
  }
  if (!annotations[selectedCell.witnessId][selectedCell.tokenIndex]) {
    annotations[selectedCell.witnessId][selectedCell.tokenIndex] = [];
  }
  annotations[selectedCell.witnessId][selectedCell.tokenIndex].push({ key, value });
  annoKeyInput.value = '';
  annoValueInput.value = '';
  showAnnotationEditor(selectedCell.witnessId, selectedCell.tokenIndex);
});

// Close annotation editor
closeAnnoBtn.addEventListener('click', () => {
  annotationEditor.classList.add('hidden');
});

// Export TEI
exportTeiBtn.addEventListener('click', () => {
  if (!alignment.length) {
    alert('Please align witnesses before exporting.');
    return;
  }
  const tei = generateTei();
  downloadFile(tei, 'edition.xml', 'application/xml');
});

// Export JSON
exportJsonBtn.addEventListener('click', () => {
  if (!alignment.length) {
    alert('Please align witnesses before exporting.');
    return;
  }
  const data = generateJson();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  downloadFile(blob, 'edition.json', 'application/json');
});

// Generate minimal TEI string
function generateTei() {
  let tei = '<?xml version="1.0" encoding="UTF-8"?>\n';
  tei += '<TEI>\n  <teiHeader>\n    <fileDesc>\n      <titleStmt><title>Untitled Edition</title></titleStmt>\n      <publicationStmt><p>Generated by OpenITI EPE JS Prototype</p></publicationStmt>\n      <sourceDesc><p>Multiple witnesses</p></sourceDesc>\n    </fileDesc>\n  </teiHeader>\n  <text>\n    <body>\n';
  // Witness sections
  witnesses.forEach(w => {
    tei += `      <div type="witness" xml:id="${w.id}">\n        <p>`;
    const tokens = w.tokens.map(t => escapeXml(t)).join(' ');
    tei += tokens;
    tei += '</p>\n      </div>\n';
  });
  // Variant apparatus
  tei += '      <div type="apparatus">\n';
  alignment.forEach((row, idx) => {
    // Determine base token and whether variants exist
    const base = row[0];
    const variants = [];
    row.forEach((tok, wIndex) => {
      if (wIndex === 0) return;
      if (tok !== base) {
        variants.push({ witnessId: witnesses[wIndex].id, token: tok });
      }
    });
    if (variants.length > 0) {
      tei += `        <app n="${idx}">\n          <lem wit="#${witnesses[0].id}">${escapeXml(base)}</lem>\n`;
      variants.forEach(v => {
        tei += `          <rdg wit="#${v.witnessId}">${escapeXml(v.token)}</rdg>\n`;
      });
      tei += '        </app>\n';
    }
  });
  tei += '      </div>\n';
  tei += '    </body>\n  </text>\n</TEI>\n';
  return tei;
}

// Generate JSON object
function generateJson() {
  const data = {
    witnesses: witnesses.map(w => ({ id: w.id, name: w.name, tokens: w.tokens })),
    alignment: alignment.map((row, idx) => {
      const base = row[0];
      const variants = [];
      row.forEach((tok, wIndex) => {
        if (tok !== base) {
          variants.push({ witnessId: witnesses[wIndex].id, token: tok });
        }
      });
      return { index: idx, base: { witnessId: witnesses[0].id, token: base }, variants };
    }),
    annotations
  };
  return data;
}

// Helper: download file
function downloadFile(content, filename, mime) {
  let blob;
  if (content instanceof Blob) {
    blob = content;
  } else {
    blob = new Blob([content], { type: mime });
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
}

// Helper: escape XML special characters
function escapeXml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Load samples at start
loadSampleWitnesses();