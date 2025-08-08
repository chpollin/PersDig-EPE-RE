# Engineering Diary – Phase 1 (August–September 2025)

Dieses Tagebuch dokumentiert den Arbeitsfortschritt während der ersten Planungsphase für die digitale Scholarly‑Edition‑Plattform. Die Einträge spiegeln Diskussionen, Entscheidungen, Probleme und Erkenntnisse wider.

## 8 Aug 2025 – Kickoff und Spezifikationsanalyse

Heute fand der Projektkickoff statt. Das Team hat die detaillierte Spezifikation für die zweikomponentige Plattform gelesen und analysiert. Kernpunkte: Skalierung bis 60 Zeugen, 250 k Wörter, 15 Mio Alignments; Dual‑Format (JSON/TEI); pixelgenaue Koordinaten trotz Baselines; strenge Performance‑Vorgaben; vollständige RTL/LTR‑Unterstützung; komplexes Annotationen‑ und Alignment‑System.  

Wir diskutierten zunächst die Aufteilung in EPE und RE sowie die Wahl der zugrunde liegenden Technologien. Da viele Teammitglieder Erfahrung mit Django und React haben, zeichnete sich diese Kombination früh als Favorit ab. Ebenfalls identifiziert wurde die Notwendigkeit eines internen JSON‑Schemas neben TEI. Wir vereinbarten, die Spezifikation in einzelne Meilensteine zu gliedern.

## 9 Aug 2025 – Grobentwurf der Architektur

Basierend auf der Spezifikation wurde ein erstes Architekturdiagramm skizziert (Backend, Frontend, Datenbanken, externen Tools). Wir führten einen Workshop zu den Schnittstellen von eScriptorium, CollateX und LERA durch. Die Erkenntnis: eScriptorium liefert nur ALTO/PAGE‑XML und keine JSON‑Daten; daher muss ein eigener Parser mit Normalisierung der Koordinaten erstellt werden.  

Beim Thema Datenhaltung diskutierten wir, ob TEI als einziges Format ausreichen könnte. Die Performance‑Vorgaben (FTS5, <10 ms Suche) legten jedoch die Notwendigkeit eines performanten JSON‑Formats nahe. Wir entwarfen die Grundstruktur des JSON (Segmente, Alignment‑Matrizen, Annotationsebenen). Außerdem wurde die Verwendung von SQLite/FTS5 in der RE beschlossen.

## 11 Aug 2025 – Datenbankmodellierung

Heute arbeiteten wir das relationale Datenbankschema aus. Es entstanden Tabellen für `Witness`, `Section`, `Token`, `TokenAlignment`, `Annotation`, `User`, `Export` etc. Wir überlegten, wie die Mappings zu TEI‑Elementen aussehen und welche GUIDs erforderlich sind, um Round‑Trip‑Fähigkeit zu gewährleisten.  

Wir untersuchten das SQE‑MySQL‑Schema als Referenz und führten eine Zuordnung der Tabellen durch. Entscheidung: auch wenn wir SQLite/FTS5 für die RE einsetzen, bleibt eine relationale Datenbank (MySQL oder PostgreSQL) im Backend wichtig. Erste Skizzen zur FTS5‑Integration in SQLite wurden erstellt.

## 14 Aug 2025 – Sicherheit und Infrastruktur

Ein weiteres Meeting drehte sich um das Sicherheitskonzept. Wir identifizierten potenzielle Angriffsvektoren (DoS, unautorisierte Zugriffe) und formulierten Schutzziele. Es wurde beschlossen, Token‑basierte Authentifizierung (JWT/OAuth2), TLS, Rate‑Limiting und CORS/CSP‑Policies zu implementieren. Für die Import‑Pipelines soll ein Offline‑Queueing eingerichtet werden, um Netzwerkprobleme abzufangen.  

Wir legten fest, dass der eigene Medienserver auf FastAPI basiert, IIIF 3.0 unterstützt und libvips zum Generieren von Pyramidal‑TIFFs nutzt. CDN‑Caching mit definierten Timeouts (24h für `info.json`, 1h für Manifeste) wurde als Teil des Konzepts aufgenommen.

## 19 Aug 2025 – Architekturentscheidungen (ADR)

In einer Sitzung wurden die ersten Architekturentscheidungen formalisiert und in ADRs dokumentiert: Wahl von Django + React (ADR 001), duale Datenhaltung (ADR 002), Einsatz von SQLite/FTS5 (ADR 003), IIIF 3.0 als Standard (ADR 004), Integration von CollateX/LERA (ADR 005), Layer‑basiertes Transkriptionsmodell (ADR 006) und frühzeitige i18n/A11Y‑Berücksichtigung (ADR 007).  

Diese Dokumentation sollte gewährleisten, dass spätere Teammitglieder die Hintergründe nachvollziehen können. Wir diskutierten Alternativen und hielten die jeweiligen Konsequenzen fest.

## 23 Aug 2025 – Internationalisierung & Accessibility

Es wurde ein Konzept für die Internationalisierung erarbeitet. Wir entschieden uns, alle UI‑Strings auszulagern und sowohl LTR- als auch RTL‑Layouts zu testen. React‑i18next wurde als potentielles Tool in Betracht gezogen. Für die Zugänglichkeit (A11Y) erstellten wir eine Checkliste nach WCAG 2.1 AA, die Fokus‑Indikatoren, Tastatur‑Navigation und Screenreader‑Kompatibilität umfasst.

## 27 Aug 2025 – Planung der Parser

Wir evaluieren bestehende Parser für ALTO/PAGE und stellten fest, dass eScriptorium modifizierte ALTO‑4.3‑Dateien mit Leerzeichen statt Kommas verwendet. Daraus ergab sich die Anforderung, ein eigenes Normalisierungsskript zu schreiben. Die Baseline‑Informationen müssen so interpoliert werden, dass tokenbasierte Bounding‑Boxen entstehen; für RTL‑Sprachen wird eine separate Logik benötigt.  

Außerdem begannen wir, die JSON‑Schemas (Zeuge, Abschnitt, Token, Annotation) in JSON Schema zu definieren, um spätere Validierungen zu ermöglichen.

## 31 Aug 2025 – Abschluss Phase 1

In der letzten Sitzung des Monats haben wir die Arbeit der ersten Phase zusammengetragen und die offenen Fragen identifiziert. Die wichtigsten Deliverables (Architektur‑Dossier, DB‑Schema, Sicherheitskonzept, ADRs) wurden finalisiert. Für Phase 2 planen wir, den eScriptorium‑Connector zu entwickeln, den ALTO/PAGE‑Parser zu implementieren und die Tokenisation‑Pipeline aufzubauen.  

Das Team hat den Umfang des Projekts erneut bewertet und bestätigt, dass die definierten Meilensteine und Zeitziele erreichbar sind, sofern wir die Arbeiten sequenziell, aber mit enger Verzahnung der Teilmodule durchführen.