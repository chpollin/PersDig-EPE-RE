# Architecture Dossier – Edition Production Environment (EPE) & Reading Environment (RE)

**Datum:** 8. August 2025  
**Version:** Phase 1 – Planung und Design

## 1 Einleitung

Dieses Dokument beschreibt die übergeordnete Architektur der zweikomponentigen Plattform, bestehend aus dem **Edition Production Environment (EPE)** und der **Reading Environment (RE)**. Ziel ist es, eine skalierbare und robuste Infrastruktur aufzubauen, die bis zu 60 Zeugen (Witnesses) mit einer Textlänge von bis zu 250 000 Wörtern und etwa 15 Millionen Alignment‑Punkten verarbeiten kann. Das System muss pixelgenaue Token‑Koordinaten, gemischten LTR/RTL‑Text sowie eine duale Datenhaltung in **JSON** und **TEI XML** unterstützen.  
Der Zeitrahmen für die Umsetzung der Alpha‑Version endet am **31. Mai 2026**.

## 2 Hoch‑Level‑Architektur

### 2.1 Systemübersicht

Die Architektur gliedert sich in zwei Web‑Applikationen:

1. **Edition Production Environment (EPE)** – eine interaktive Produktionsumgebung für den Import, die Normalisierung, die Tokenisierung, das Alignment, die Annotation und die Anreicherung der Zeugen. Die EPE bietet reichhaltige UI‑Werkzeuge zur manuellen Korrektur und Verwaltung sowie Exporte in unterschiedliche Formate.
2. **Reading Environment (RE)** – ein Endnutzer‑Frontend zum Durchsuchen und Vergleichen der edierten Texte. Die RE arbeitet primär mit statischen, vorverarbeiteten JSON‑Chunks und optionalen SQLite‑Indices und bindet Bilder via IIIF. Sie stellt Deep‑Links bis hinunter zum Token bereit und unterstützt komplexe Suchanfragen.

### 2.2 Komponentenmodell

#### EPE (Backend und Frontend)

- **Importmodule**:  
  – Laden von **METS**‑Paketen (Metadaten, ALTO 4.3/PAGE‑XML und Bilder).  
  – Konnektor für die **eScriptorium‑API** (Token‑authentifiziert, throttled mit max. 10 Requests/s).  
  – Parser zur Normalisierung der eScriptorium‑Modifikationen (z. B. Leerzeichen statt Komma in Koordinaten).  
  – Fallback‑Import für weitere Formate nach Bedarf.
- **Daten‑Normalisierung**: Aufbereitung der ALTO/PAGE‑XML (Korrektur von Koordinaten, Validierung gegen Standard), Umwandlung in ein internes JSON‑Schema.  
- **Tokenisierung**: SQE‑konformer Regex‑Tokenizer mit vollständiger bidi‑Unterstützung; Transformation von Baselines in Token‑Koordinaten mittels proportionaler Segmentierung und Validierung.  
- **Kollations‑Engine**: Integration von **CollateX** und **LERA** für Token‑basiertes Alignment vieler Zeugen; optionale Fuzzy‑Matches für fragmentarische Geniza‑Zeugen.  
- **Annotations‑Subsystem**: Verwaltung verschiedener Annotationsebenen (linguistisch, strukturell, intertextuell, codikologisch, Named Entities, Textreuse), jeweils mit Provenienzinformationen (Autor, Zeitstempel).  
- **Enrichment**: Ergänzung um Übersetzungen und Kommentare auf Ebene von Abschnitten, Zeilen oder Tokens.
- **Exportmodule**: Bereitstellung von TEI XML (inline und stand‑off), JSON‑Chunks, statischem RE‑Build, Plain‑Text, CSV und HTML‑Reports. Jeder Export bietet eine Vorschau im Browser.
- **EPE‑UI**: Eine reaktive Anwendung (bevorzugt Django mit React‑Frontend) mit drei Panels (Zeugenliste, Alignment‑Workspace und Exportpanel), Zoom‑ und Navigationskontrollen, Drag‑&‑Drop‑Funktionen für Alignment‑Korrektur, Toolbar für verschiedene Arbeitsphasen und einen Layer‑Rollen‑Dialog zur Zuordnung diplomatischer versus normalisierter Transkriptionen.

#### RE (statisches Frontend bzw. optional REST‑Backend)

- **Datenbereitstellung**: Primär statische JSON‑Chunks je Abschnitt, enthalten Alignment‑Matrizen für bis zu 60 Zeugen, Token‑Koordinaten, Annotationen und Vorindizes.  
  – **SQLite** mit **FTS5** wird als optionaler Beipack zum Client ausgeliefert, um Volltextsuche und komplexe Queries lokal in <10 ms zu ermöglichen.  
  – Sekundärer Betriebsmodus erlaubt das Parsen von externen TEI‑Dateien zur Laufzeit, jedoch ohne Token‑Bild‑Alignment und mit reduzierter Performance.
- **Bildintegration**: Nutzung der **IIIF Image API 3.0 Level 2** zur Auslieferung der Bilder. Das Frontend nutzt **Mirador 3.3.0** mit eigenen Plugins (Token‑Navigation, Vergleich mehrerer Zeugen). Fallback über einen eigenen Medienserver mit S3‑Storage, libvips‑basierten Pyramidal‑TIFFs und FastAPI.
- **Benutzerinteraktion**: Auswahl und Vergleich der Zeugen, Wahl eines Basetextes, Anzeige des Kritischen Apparats, Volltext‑ und Struktur‑Navigation, persistente Deep‑Links bis zum Token, Exportfunktionen.

### 2.3 Datenflüsse

1. **Import**: Die EPE nimmt METS/ALTO‑Pakete oder via eScriptorium‑API geladene Seiten entgegen. Nach der Normalisierung werden Metadaten, Bilder und Texte in das interne JSON‑Format überführt.  
2. **Tokenisierung & Koordinatentransformation**: Aus den Baselines der ALTO/PAGE‑XML werden Token‑Koordinaten berechnet und in JSON abgelegt.  
3. **Sektionierung & Alignment**: Zeugen werden manuell bzw. automatisch segmentiert und anschließend auf Token‑Ebene kollationiert. Alignments werden in einer Matrix mit bis zu 15 Millionen Punkten gespeichert.  
4. **Annotation & Enrichment**: Nutzer importieren oder erstellen Annotationen und Anreicherungen, die wiederum in JSON und TEI persistiert werden.  
5. **Export & Veröffentlichung**: Nach Abschluss der Bearbeitung erzeugt die EPE TEI‑ und JSON‑Exporte sowie ein statisches RE‑Build. Diese Daten werden im RE ausgeliefert; optional steht ein REST‑API für dynamische Abfragen zur Verfügung.  
6. **Nutzung in der RE**: Endnutzer laden Abschnitts‑ bzw. Seiten‑bezogene JSON‑Chunks; Bilder werden via IIIF geladen. Die RE stellt Such‑ und Navigationsfunktionen sowie Exporte bereit.

## 3 Datenhaltung und Formate

### 3.1 Internes JSON

Das JSON‑Format ist für Performance und die Integration mit der RE optimiert. Es enthält:

- **Segmentierte Zeugen**: Jedes Segment (z. B. Seite oder Kolumne) wird als eigenes Objekt gespeichert, um progressives Laden zu ermöglichen.
- **Alignment‑Matrizen**: Mehrdimensionale Arrays, die pro Basetoken die korrespondierenden Tokens der einzelnen Zeugen referenzieren (GUIDs).  
- **Token‑Koordinaten**: Pixelgenaue Bounding‑Boxen auf Basis der Zeilen‑Baselines; RTL/LTR‑unabhängig; inklusive Checksumme zur Validierung.  
- **Annotationsebenen**: Stufenförmig organisiert, mit IDs zur Verbindung mit TEI und externen Autoritäten.  
- **Provenienz**: Editor, Zeitstempel und Herkunft jeder Operation/Annotation.

### 3.2 TEI XML

Die TEI‑Daten werden sowohl inline als auch stand‑off gespeichert. Wichtigste Elemente sind `<listWit>`, `<app>`, `<lem>`, `<rdg>`, `<rdgGrp>`, `<subst>`, `<witStart/>`, `<lacunaStart/>` sowie stand‑off‑Markierungen bei überlappenden Varianten. Über eindeutige GUIDs und XPath‑Mappen lässt sich eine verlustfreie Round‑Trip‑Konvertierung zwischen TEI und dem internen JSON gewährleisten.

### 3.3 Datenbanken

- **SQLite** mit **FTS5** wird in der RE verwendet, um Volltextsuche und schnelle Abfragen im Browser zu unterstützen. Die Datenbank enthält Textinhalte und Indexstrukturen für die Zeugen.  
- **MySQL (SQE‑Schema)** oder PostgreSQL wird serverseitig für persistente Speicherung in der EPE genutzt. Das Schema umfasst Tabellen für Zeugen, Tokens, Alignments, Annotationen, Benutzer und Rollen. Die genauen Tabellen und Beziehungen werden im separaten Schema‑Dokument definiert.

## 4 Datenlebenszyklus

1. **Eingabe**: Upload/Import von METS‑Paketen oder API‑Calls an eScriptorium.  
2. **Normalisierung**: Parsen der ALTO/PAGE‑XML; Korrektur von eScriptorium‑Modifikationen; Validierung.  
3. **Tokenisierung & Abschnittsbildung**: Aufteilung in Tokens (Regex‑Tokenizer) und manuelle/automatische Segmentierung in Abschnitte.  
4. **Alignment**: Berechnung der Token‑Äquivalenzen zwischen Zeugen; Speicherung der Alignment‑Matrizen.  
5. **Annotation/Enrichment**: Hinzufügen von Metadaten und Kommentaren; Anbindung an externe Ressourcen.  
6. **Export**: Erstellung von TEI‑, JSON‑, SQLite‑ und optional CSV/HTML‑Exporte; Veröffentlichung für das RE.  
7. **Archivierung**: Persistente Speicherung der Daten, Versionierung und Wiederherstellung bei Bedarf.

## 5 Sicherheits‑ und Robustheitskonzept

- **Authentifizierung und Autorisierung**: Token‑basierte Authentifizierung für API‑Zugriffe (eScriptorium, interner REST‑API). Benutzerrollen in der EPE (Administrator, Editor, Betrachter) steuern den Zugriff.  
- **Rate‑Limiting**: eScriptorium‑Requests sind auf 10 req/s begrenzt; der eigene Medienserver beschränkt Anfragen auf 100 req/min.  
- **CORS & CSRF**: Cross‑Origin‑Requests werden kontrolliert zugelassen; CSRF‑Tokens schützen interaktive Formulare.  
- **Transportverschlüsselung**: Alle Dienste sind über HTTPS/TLS erreichbar.  
- **Fehlerresilienz**: Offline‑Queue für fehlgeschlagene Exporte; Crash‑Recovery für lange Importprozesse; Export‑Retry‑Mechanismen.  
- **CDN‑Caching**: `info.json` der IIIF‑Manifeste wird 24 h lang gecached, Manifeste selbst 1 h; das reduziert Last und verbessert die Verfügbarkeit.  
- **Logging und Monitoring**: Zentralisiertes Log‑Management (z. B. ELK‑Stack) und Health‑Checks; Benachrichtigungen bei Ausfällen oder Überlastung.  
- **Datenschutz**: Berücksichtigung der DSGVO; Speicherung von personenbezogenen Daten wird minimiert; Pseudonymisierung von Benutzerinformationen.

## 6 Interoperabilität und externe Dienste

- **eScriptorium‑API**: Hauptquelle für Bilder und vorab erkannte Zeilen‑Baselines. Da eScriptorium keinen JSON‑Export bietet, wird ein eigener Parser für die ALTO/PAGE‑Outputs implementiert.  
- **CollateX/LERA**: Verwendung der REST‑Schnittstellen für das Multi‑Witness‑Alignment. Beide Tools werden containerisiert und mit definierten Normalisierungsoptionen eingebunden.  
- **TEI‑CAT**: Dient zur Validierung des TEI‑Exports; erzeugt Fehlerberichte und optional LaTeX‑Exports.  
- **IIIF/Mirador**: Bilder werden via IIIF 3.0 ausgeliefert; Mirador dient als Viewer im RE und in der EPE‑Vorschau.  
- **Weitere Integrationen**: Passim/KITAB für Textreuse‑Annotationen; VIAF/GeoNames für Named Entities; EVT 2 als Referenz für Viewer‑Funktionalitäten.

## 7 Performanzziele und Skalierbarkeit

- **Ladezeiten**: Erste 10–20 Zeugen innerhalb von 30 s (Import/Rendering), weitere Zeugen asynchron.  
- **Interaktionslatenz**: <2 s für UI‑Aktionen (z. B. Alignments verschieben, Annotationen setzen).  
- **Seitenauslieferung**: <500 ms für das Laden von Abschnitten in der RE.  
- **Token‑Extraktion**: <100 ms beim Navigieren von Zeilen/Seiten.  
- **Maximallast**: Test mit 200 Zeugen × 300 Seiten (~15 Mio Wörter); Browser darf nicht abstürzen.

## 8 Werkzeuge und Frameworks

| Komponente | bevorzugte Technologie | Begründung |
|-----------|-----------------------|------------|
| Backend (EPE) | **Django** (Python) | Ausgereiftes Framework mit ORM, Auth, Admin‑Interface; gute Internationalisierung; große Community |
| Frontend | **React** (JavaScript/TypeScript) | Reaktive UI, State‑Management (Redux/Zustand), gute Einbindung in Django via DRF oder GraphQL |
| Datenbank | **PostgreSQL** oder **MySQL** | Persistente Speicherung, relationale Integrität, Unterstützung für JSON‑Felder; Anlehnung an das SQE‑MySQL‑Schema |
| Client‑seitiger Index | **SQLite + FTS5** | Volltextsuche im Browser in <10 ms; einfache Verteilung als Datei |
| Image‑Server | **IIIF 3.0** + eigener FastAPI‑Server | Standardisierte Bildauslieferung; Fallback mit libvips/Sharp, CORS & Rate‑Limiting |
| Alignment | **CollateX**, **LERA** | Etablierte Tools für Token‑Alignment großer Zeugenmengen; REST‑Schnittstellen |
| TEI‑Validierung | **TEI‑CAT** | Validierung, Fehleranalyse und weitere Exporte |

## 9 Zusammenfassung

Die Architektur der zweikomponentigen Plattform ist so ausgelegt, dass sie hohe Datenmengen und komplexe Vergleiche zwischen vielen Zeugen verarbeiten kann. Durch die Trennung von Produktions‑ und Leseumgebung, die Nutzung dualer Datenformate (JSON & TEI) sowie den Einsatz von Standard‑Frameworks (Django, React, SQLite/FTS5, IIIF) wird ein flexibles und robustes System geschaffen. Die konsequente Einbindung externer Spezialwerkzeuge (CollateX, LERA, TEI‑CAT) und ein durchdachtes Sicherheits‑ und Performance‑Konzept bilden die Grundlage für die erfolgreiche Realisierung der Alpha‑Version bis Mai 2026.