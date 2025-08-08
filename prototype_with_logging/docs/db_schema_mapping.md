# Datenbankschema und Mappings – EPE & RE

**Datum:** 8. August 2025  
**Version:** Phase 1 – Planung

Dieses Dokument beschreibt die Datenmodellierung für die Edition Production Environment (EPE) und die Reading Environment (RE). Es legt die Tabellenstrukturen, ihre Beziehungen sowie die Zuordnung zu den beiden Zielformaten (internes JSON und TEI XML) fest. Darüber hinaus werden Hinweise für die Integration in relationale Datenbanken wie MySQL/PostgreSQL (Server‑Seite) und SQLite/FTS5 (Client‑Seite) gegeben.

## 1 Kernobjekte und Relationen

Die wichtigsten Entitäten des Systems sind:

### 1.1 Witness (Zeuge)

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Interne eindeutige ID |
| `siglum` | VARCHAR | Kurzkennung (z. B. „MS 001“) |
| `label` | TEXT | Vollständige Bezeichnung (z. B. „MS 001 – folio 42r“) |
| `folio` | VARCHAR | Blatt- oder Seitenangabe |
| `total_tokens` | INTEGER | Anzahl der Tokens im Zeugen |
| `metadata` | JSON | Zusätzliche Metadaten (Herkunft, Datierung, Sprache etc.) |
| `layer_roles` | JSON | Zuordnung der Transkriptionslayer (diplomatisch, normalisiert, …) |

### 1.2 BaseText (Basetext)

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Identifikator für den Basetext |
| `title` | VARCHAR | Titel oder Bezeichnung |
| `language` | VARCHAR | Sprache des Basetextes |
| `description` | TEXT | Beschreibung |
| `created_at` | DATETIME | Erstellungsdatum |
| `updated_at` | DATETIME | Letzte Aktualisierung |

### 1.3 Section (Abschnitt/Sektion)

Ein Zeuge wird in Abschnitte unterteilt, um progressives Laden zu ermöglichen.

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Abschnitts-ID |
| `witness_id` | Foreign Key → Witness | Verweis auf den zugehörigen Zeugen |
| `order_no` | INTEGER | Sequenznummer im Zeugen |
| `type` | VARCHAR | Art des Abschnitts (z. B. „Seite“, „Spalte“, „Kolumne“) |
| `start_token_id` | Foreign Key → Token | Erster Token im Abschnitt |
| `end_token_id` | Foreign Key → Token | Letzter Token im Abschnitt |
| `metadata` | JSON | Abschnittsspezifische Metadaten (z. B. Überschrift) |

### 1.4 Token

Tokens repräsentieren die kleinste semantische Einheit (Wort oder Zeichen). Sie werden in der EPE generiert und enthalten Koordinateninformationen.

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Eindeutige Token-ID |
| `witness_id` | Foreign Key → Witness | Zugehöriger Zeuge |
| `position` | INTEGER | Fortlaufende Position im Zeugen |
| `section_id` | Foreign Key → Section | Abschnitt, zu dem der Token gehört |
| `text` | VARCHAR | Das Token selbst |
| `start_offset` | INTEGER | Zeichenposition im Ursprungsstring |
| `end_offset` | INTEGER | Endposition im Ursprungsstring |
| `bbox` | JSON | Bounding‑Box im Bild (`{x, y, width, height}`) |
| `baseline` | JSON | Alternativ zu `bbox`: Baseline‑Koordinaten (für unvollständige Boxen) |
| `checksum` | VARCHAR | Prüfwert zur Validierung der Koordinaten |

### 1.5 TokenAlignment

Die Alignments verknüpfen Tokens aus verschiedenen Zeugen mit dem Basetext.

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Alignment‑ID |
| `base_token_id` | Foreign Key → Token | Token des Basetextes |
| `witness_token_id` | Foreign Key → Token | Token im Zeugen |
| `alignment_type` | VARCHAR | Typ (exakt, lacuna, fuzzy, emendation) |
| `score` | FLOAT | Ähnlichkeitswert (optional) |
| `group_id` | UUID | Gruppiert zusammengehörige Alignments (z. B. überlappende Varianten) |

### 1.6 Annotation

Annotationen sind vielfältig und können sich auf Tokens, Abschnitte, Seiten oder externe Ressourcen beziehen.

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Annotation‑ID |
| `target_type` | ENUM | Zieltyp (Token, Section, Witness, BaseText, External) |
| `target_id` | VARCHAR | ID des annotierten Objekts (z. B. Token-ID) |
| `annotation_type` | VARCHAR | Kategorie (POS, Morph, Lemma, strukturell, intertextuell, Codikologie, NER, Textreuse etc.) |
| `data` | JSON | Strukturiertes Annotationsdatenobjekt |
| `author` | VARCHAR | Urheber der Annotation |
| `timestamp` | DATETIME | Erstellungs-/Änderungszeitpunkt |
| `provenance` | JSON | Herkunftsinformation (z. B. importiert vs. manuell) |

### 1.7 User & Role

Für die EPE ist ein Berechtigungssystem notwendig.

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Benutzer-ID |
| `username` | VARCHAR | Login‑Name |
| `password_hash` | VARCHAR | Gesichertes Passwort |
| `email` | VARCHAR | E-Mail |
| `role` | ENUM | Rolle (Administrator, Editor, Viewer) |
| `created_at` | DATETIME | Erstellungsdatum |
| `updated_at` | DATETIME | Letzte Aktualisierung |

### 1.8 Export & Versioning

| Feld | Typ | Beschreibung |
|------|----|---------------|
| `id` | Primary Key | Export-ID |
| `witness_id` | Foreign Key → Witness | Bezug auf den Zeugen |
| `format` | ENUM | Exportformat (TEI-inline, TEI-standoff, JSON, CSV, HTML) |
| `created_at` | DATETIME | Exportzeitpunkt |
| `file_path` | VARCHAR | Speicherort der exportierten Datei |
| `hash` | VARCHAR | Prüfsumme |

## 2 Integrationen mit TEI und JSON

Die oben genannten Tabellen bilden die Grundlage für einen relationalen Ansatz. Zur Abbildung in **JSON** und **TEI** gelten folgende Mappings:

### 2.1 Witness

Im internen JSON wird ein Zeuge durch ein Objekt mit Feldern wie `id`, `siglum`, `label`, `sections` usw. repräsentiert. In TEI erscheint der Zeuge in der `<listWit>` als `<witness xml:id="w$id" n="siglum">label</witness>`.

### 2.2 Section

Abschnitte werden im JSON als `sections`-Array mit start- und endToken referenziert. In TEI können Abschnitte (z. B. Seiten) mittels `<pb n="42r"/>` oder `<cb n="1"/>` markiert werden. Zusätzliche Strukturelemente (Kapitel, Absätze) werden via `<div>` abgebildet.

### 2.3 Token

Im JSON sind Tokens Objekte mit Text, Koordinaten (`bbox` oder `baseline`) und Verweisen auf Alignments. Im TEI können Tokens inline als `<w xml:id="tok123">Wort</w>` auftreten; bei stand‑off‑Markup werden sie über eine Range in der TEI‑Datei referenziert, während die Koordinaten im Stand‑off‑Segment (`<spanGrp type="imageCoords">`) abgelegt werden.

### 2.4 TokenAlignment

Im JSON sind Alignments Matrixstrukturen, die pro Basetoken ein Array mit Zeugen‑Token‑IDs enthalten. In TEI erfolgt die Darstellung im Kritischen Apparat über `<app>`, `<lem>` und `<rdg>`‑Elemente; die Zuordnung wird über `@wit` und `@from`/`@to` abgebildet. Über `group_id` lassen sich `<rdgGrp>` anlegen (z. B. für orthographische vs. substantielle Varianten).

### 2.5 Annotation

Im JSON wird das `data`‑Feld pro Annotation als Objekt mit frei definierbaren Attributen gespeichert. In TEI werden Annotationen je nach Typ an unterschiedlichen Stellen verankert: grammatikalische Annotationen an `<w>` via `@ana`, strukturelle an `<div>` oder `<note>`, Named Entities über `<name>` oder `<placeName>` mit `@ref`‑Attributen. Stand‑off‑Annotationen kommen zum Einsatz, wenn sich Annotationsbereiche überlappen.

## 3 SQLite FTS5‑Schema (RE)

Für die RE wird ein kompaktes SQLite‑Schema mit Volltextsuche verwendet. Dies kann wie folgt aussehen:

```sql
-- Tabelle, die den Volltext und Metainformationen enthält
CREATE VIRTUAL TABLE doc_tokens USING fts5(
  token_id UNINDEXED,
  witness_id UNINDEXED,
  section_id UNINDEXED,
  text,
  tokenize = 'unicode61 remove_diacritics 1'
);

-- Tabelle zur schnellen Zuordnung der Koordinaten und Alignments
CREATE TABLE token_lookup (
  token_id INTEGER PRIMARY KEY,
  witness_id INTEGER,
  section_id INTEGER,
  position INTEGER,
  bbox TEXT,
  alignment_ids TEXT -- kommaseparierte Alignment-IDs
);

-- Tabelle für Metadaten zu Zeugen und Abschnitten
CREATE TABLE metadata (
  key TEXT PRIMARY KEY,
  value TEXT
);
```

Die `fts5`-Tabelle `doc_tokens` enthält nur den Text der Tokens und kann damit sehr schnell durchsucht werden. Die `token_lookup`-Tabelle ermöglicht die Zuordnung zu Koordinaten, Alignments und weiteren Metadaten.

## 4 Integration mit bestehenden Schemas (SQE‑MySQL)

Das **SQE‑MySQL**‑Schema des Schweizer Qurʾān Edition Project dient als Referenz. Die wichtigsten Übereinstimmungen sind:

- **Witness** entspricht `manuscript` und `folio` in SQE.  
- **Token** entspricht `transcription_character` oder `transcription_token`.  
- **Alignment** entspricht dort den Tabellen für `collated_token` und `lemma_reading`.  
- **Annotation** lässt sich auf `annotation` bzw. `app` und `note` abbilden.

Zur Sicherung der Round‑Trip‑Fähigkeit sind zusätzliche Felder wie GUIDs (`uuid`) erforderlich, die sowohl in MySQL als auch im internen JSON und in der TEI auftauchen. Für die Migration zwischen den Systemen sollten eindeutige IDs persistent gehalten und in Mapping‑Tabellen gespeichert werden.

## 5 Zusammenfassung

Dieses Datenbankschema unterstützt die Anforderungen an Skalierbarkeit, Performance und Interoperabilität der Plattform. Durch die klare Trennung der Entitäten (Zeugen, Abschnitte, Tokens, Alignments, Annotationen) und die flexible Zuordnung zu JSON und TEI ist eine verlustfreie Konvertierung möglich. Die Integration mit SQLite FTS5 ermöglicht schnelle Volltextsuche client‑seitig, während das relationale Backend die persistente Speicherung und Transaktionssicherheit gewährleistet. Für spätere Anpassungen (z. B. Erweiterung der Annotationstypen, Einführung weiterer Rollen) ist das Schema modular aufgebaut.