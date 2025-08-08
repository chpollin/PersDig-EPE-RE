# Prototyp – EPE & RE (Alpha‑Phase)

Dieses Repository enthält einen einfachen Prototyp für die zweikomponentige Scholarly‑Edition‑Plattform. Der Prototyp soll als Ausgangspunkt für die weitere Entwicklung dienen und demonstriert Grundkonzepte wie Datenmodellierung, eine einfache HTTP‑Bereitstellung von JSON‑Daten und eine minimalistische Frontend‑Ansicht.

## Inhalt

* `server.py` – Ein einfacher Python‑HTTP‑Server (basierend auf `http.server`), der statische JSON‑Dateien aus dem Verzeichnis `data/` bereitstellt. Dies simuliert einen Teil der RE‑API.
* `data/sample_witness.json` – Beispielhafte JSON‑Struktur für einen Zeugen mit wenigen Tokens und Alignment‑Informationen.
* `index.html` – Eine minimalistische HTML‑Seite, die das Beispiel‑JSON lädt und im Browser darstellt. Dient als vereinfachter Prototyp der Reading Environment.
* `epe/parser.py` – Eine Stub‑Datei für einen zukünftigen ALTO/PAGE‑Parser. Sie enthält Platzhalterfunktionen, die demonstrieren, wie ALTO‑Dateien eingelesen und in das interne JSON umgewandelt werden könnten.
* `docs/` – Enthält die Dokumente aus Phase 1 (Architektur‑Dossier, Datenbankschema, Sicherheitskonzept, ADR‑Protokoll und Engineering Diary). Diese dienen als Referenz und Grundlage für die weitere Implementierung.

## Benutzung

1. **Starten des Servers**  
   Wechseln Sie in das Verzeichnis `prototype` und starten Sie den Server:

   ```bash
   cd prototype
   python server.py
   ```

   Der Server läuft dann unter `http://localhost:8000` und stellt Dateien aus `data/` und das Frontend bereit.

2. **Ansehen der Reading‑Prototype**  
   Öffnen Sie im Browser `http://localhost:8000/index.html`.  
   Die Seite lädt das Beispiel‑JSON (`/data/sample_witness.json`) und listet die Tokens und ihre Koordinaten auf.

3. **Parser entwickeln**  
   Im Verzeichnis `epe/` finden Sie `parser.py`. Diese Datei enthält eine Dataclass‑Definition und eine unvollständige Funktion `parse_alto()`, die die Verarbeitung von ALTO/PAGE‑XML vorbereiten soll. Der Parser kann in der EPE später erweitert werden, um echte Imports zu unterstützen.

## Hinweise

Dieser Prototyp dient lediglich der Illustration der Architektur und der Datenflüsse. Er erfüllt weder die Performance‑Vorgaben noch die Sicherheitsanforderungen der finalen Plattform. Viele Funktionen (Tokenisierung, Alignment, Annotationen, i18n/A11Y, UI‑Interaktion) sind hier nicht umgesetzt und müssen in späteren Phasen entwickelt werden.