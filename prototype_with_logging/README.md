# Prototyp – EPE & RE (Alpha‑Phase)

Dieses Repository enthält einen einfachen Prototyp für die zweikomponentige Scholarly‑Edition‑Plattform. Der Prototyp soll als Ausgangspunkt für die weitere Entwicklung dienen und demonstriert Grundkonzepte wie Datenmodellierung, eine einfache HTTP‑Bereitstellung von JSON‑Daten und eine minimalistische Frontend‑Ansicht.

## Inhalt

* `server.py` – Ein erweiterter Python‑HTTP‑Server (basierend auf `http.server`) mit einer kleinen REST‑API. Er stellt nicht mehr nur statische Dateien bereit, sondern ermöglicht:
  * Import neuer Zeugen (`POST /api/witnesses`),
  * Abrufen von Zeugenlisten und einzelnen Zeugen (`GET /api/witnesses`, `GET /api/witnesses/<id>`),
  * Vergleich von Zeugen und Abschnitten (`GET /api/alignments?base=<id>&witness=<id>[&base_section=<sid>&witness_section=<sid>]`),
  * Anlegen, Bearbeiten und Löschen von Annotationen (`POST /api/annotations`, `PUT /api/annotations/<id>`, `DELETE /api/annotations/<id>`),
  * Umbenennen (Patch) und Löschen von Zeugen (`PATCH /api/witnesses/<id>`, `DELETE /api/witnesses/<id>`),
  * Export einzelner Zeugen als JSON (`GET /api/export/<id>`),
  * Auslesen und Download des Server‑Logs (`GET /api/logs`, `GET /api/logs/export`).
  Alle Endpunkte schreiben in eine Logdatei `logs/server.log`.

* `index.html` – Eine interaktive HTML‑Seite, die die oben genannten API‑Funktionen nutzt. Sie erlaubt das Hochladen von Zeugen, den Vergleich von zwei Zeugen einschließlich Section‑Auswahl, das Hinzufügen und Bearbeiten von Annotationen (inkl. Hervorhebung im Alignment), einfache Volltextsuche mit Markierung der Treffer, das Exportieren von Zeugen und das Umbenennen oder Löschen eines Zeugen. Logs können angezeigt und heruntergeladen werden.

* `style.css` und `script.js` – Enthalten das Styling und die JavaScript‑Logik für die Frontend‑Interaktionen.

* `data/` – JSON‑Dateien, in denen importierte Zeugen (`witnesses.json`) und Annotationen (`annotations.json`) gespeichert werden. `sample_witness.json` ist ein Beispielzeu­gen zum Experimentieren.

* `epe/parser.py` – Eine Stub‑Datei für einen zukünftigen ALTO/PAGE‑Parser. Sie enthält Platzhalterfunktionen, die demonstrieren, wie ALTO‑Dateien eingelesen und in das interne JSON umgewandelt werden könnten.

* `docs/` – Enthält die Dokumente aus den ersten Projektphasen (Architektur‑Dossier, Datenbankschema, Sicherheitskonzept, ADR‑Protokoll und Engineering Diary) sowie weitere Meilensteinberichte.

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

Obwohl dieser Prototyp bereits zahlreiche Kernfunktionen (Import, Export, Vergleich, Annotationen, Abschnitte, Suchen, Umbenennen/Löschen, Logging) demonstriert, ist er nicht für den produktiven Einsatz ausgelegt. Die Umsetzung basiert auf dem Python‑Modul `http.server` und speichert Daten in JSON‑Dateien – dies entspricht nicht den Performance‑ und Sicherheitsanforderungen der finalen Plattform. Funktionen wie fortgeschrittene Tokenisierung, fuzzy Alignment, komplexe Annotationsmodelle, i18n/A11Y oder eine echte Datenbank müssen in späteren Phasen noch implementiert oder optimiert werden.