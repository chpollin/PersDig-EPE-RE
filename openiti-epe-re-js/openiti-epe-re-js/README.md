# OpenITI EPE‑RE JS Prototype

This repository contains a self‑contained, browser‑only prototype for an **Edition Production
Environment (EPE)** and **Reading Environment (RE)** built entirely with **HTML**,
**CSS**, and **JavaScript**.  The goal of this project is to demonstrate how key
features from the Roshan Initiative’s RFP can be realised without any server side
components or build tools.

## How to run

To explore the prototype simply open the HTML files directly in your web browser:

* **Edition Production Environment** – open `epe/index.html`.  From here you can
  import witness files, tokenize them, align multiple witnesses and export
  the results as TEI or JSON.
* **Reading Environment** – open `re/index.html`.  It consumes the JSON
  export produced by the EPE and presents a lightweight reading interface
  where you can browse variants and annotations.

Everything runs client‑side; there is no backend and no dependencies.  Modern
browsers supporting ES6 modules are required.

## Folder structure

```
openiti-epe-re-js/
├── README.md               – this file
├── epe/                    – Edition Production Environment
│   ├── index.html          – main EPE UI
│   ├── style.css           – styles for the EPE
│   ├── script.js           – EPE logic in vanilla JS
│   └── sample/             – a few tiny example witnesses used by default
│       ├── witness1.txt
│       └── witness2.txt
└── re/                     – Reading Environment
    ├── index.html          – main RE UI
    ├── style.css           – styles for the RE
    └── script.js           – RE logic in vanilla JS
```

## Limitations

This prototype is intentionally simple.  It does **not** implement the full
functionality described in the RFP: there is no authentication, IIIF
viewer, passim/KITAB integration, or true multi‑witness collation logic.
Instead, it focuses on demonstrating the following core concepts:

* uploading plain‑text witnesses (via file input) and tokenizing them using a
  user supplied regular expression;
* displaying a list of witnesses with basic metadata;
* aligning tokens naïvely by index across witnesses;
* annotating individual tokens with key–value pairs;
* exporting the edition as a simplistic TEI document and as a JSON blob;
* reading a JSON export in a separate RE that supports witness selection
  and variant highlighting.

Feel free to build upon this foundation.  The code is written to be
accessible and hackable so that more advanced features (multi‑token alignment,
sectioning, image integration, etc.) can be added incrementally.