# Architektur‑Entscheidungsprotokoll (ADR) – Phase 1

**Datum:** 8. August 2025  
**Status:** Entwurf; Entscheidungen werden laufend ergänzt

Dieses Dokument fasst die Architekturentscheidungen zusammen, die während der ersten Planungsphase für die EPE/RE‑Plattform getroffen wurden. Jede ADR beschreibt den Kontext, die getroffene Entscheidung, die Alternativen und die Konsequenzen.

## ADR 001: Wahl des Web‑Frameworks

**Kontext:**
Die EPE muss eine komplexe Benutzeroberfläche mit Formularen, Import‑Workflows, Echtzeit‑Interaktionen und Rollenverwaltung bieten. Gleichzeitig soll der Entwicklungsaufwand effizient sein und eine große Entwicklergemeinschaft existieren.

**Entscheidung:**
Es wird **Django** als Backend‑Framework gewählt, kombiniert mit einem modernen **React**‑Frontend. Django bietet ein mächtiges ORM, ein integriertes Authentifizierungssystem und gute Internationalisierungs‑Unterstützung. React ermöglicht reaktive UI‑Komponenten, State‑Management und Virtual DOM.

**Alternativen:**
1. **Flask + Vue.js** – schlankeres Backend, aber mehr Eigenarbeit bei Auth und Admin; kleinere Gemeinschaft.  
2. **Node.js + Express + React** – einheitliche JavaScript‑Landschaft, jedoch fehlen serverseitig robuste ORMs.  
3. **Ruby on Rails + Hotwire** – starkes Framework, aber Teamkenntnisse liegen primär in Python.

**Konsequenzen:**
Die Wahl bringt eine höhere Produktivität dank vorhandener Django‑Admin‑Oberfläche und vieler Pakete. Allerdings müssen zwei verschiedene Sprachen (Python & JavaScript/TypeScript) gepflegt werden. Build‑Prozess erfordert eine CI/CD‑Integration für beide Stacks.

## ADR 002: Duale Datenhaltung (JSON & TEI)

**Kontext:**
Forschungsergebnisse müssen sowohl in einem performanten Format für Web‑Anzeige und Suche vorliegen als auch im TEI‑XML‑Format, um Interoperabilität mit anderen Editionsprojekten zu gewährleisten.

**Entscheidung:**
Die Plattform speichert Daten parallel in einem **nativ optimierten JSON‑Format** und einem **TEI XML**. JSON ermöglicht schnelle Client‑seitige Verarbeitung und segmentiertes Laden; TEI bietet ein standardisiertes, austauschbares Austauschformat.

**Alternativen:**
1. Nur TEI – würde die Performance der RE erheblich beeinträchtigen und client‑seitiges Parsing erschweren.  
2. Nur proprietäres JSON – erschwert langfristige Archivierung und Austausch mit anderen Projekten.  
3. TEI in einer Datenbank ablegen und daraus HTML generieren – komplex, fehleranfällig und ineffizient bei großen Zeugenmengen.

**Konsequenzen:**
Es entsteht ein Mehraufwand für die Implementierung und Pflege der Round‑Trip‑Fähigkeit zwischen JSON und TEI. Die klare Trennung ermöglicht aber Leistungsoptimierung und standardkonforme Exporte. Zur Sicherung der Konsistenz müssen GUIDs und Mapping‑Tabellen konsequent gepflegt werden.

## ADR 003: Client‑seitige Volltextsuche mit SQLite/FTS5

**Kontext:**
Die RE soll offline oder serverlos funktionieren können. Gleichzeitig sollen komplexe Volltextanfragen (auch bei 250k+ Wörtern) in weniger als 10 ms beantwortet werden. Eine serverseitige Suche würde Netzwerk‑Latenz und Betriebskosten erhöhen.

**Entscheidung:**
Für die RE wird ein kompaktes **SQLite**‑Index mit **FTS5** als Bundle bereitgestellt. Der Browser kann die Datenbank über `sql.js` oder `wa-sqlite` laden und Suchanfragen lokal ausführen. SQLite‑Dateien können zusammen mit den JSON‑Chunks versioniert werden.

**Alternativen:**
1. Nutzung eines serverseitigen Suchdienstes (Elasticsearch, Solr) – ist performant, erfordert aber laufenden Serverbetrieb.  
2. Nutzung von JavaScript‑Suchbibliotheken (Lunr.js, FlexSearch) – leichtgewichtig, aber weniger effizient bei sehr großen Datenmengen und bietet keine persistente Speicherung.  
3. Progressive Web App mit Service Worker und IndexDB – komplex und unsicher im Hinblick auf Kompatibilität und Performance, insbesondere bei großen Datenmengen.

**Konsequenzen:**
Das Einbinden einer SQLite‑Datei erhöht die initiale Downloadgröße, bringt jedoch enorme Performancevorteile. Bei Updates müssen neue DB‑Dateien verteilt werden. Die Browser‑Kompatibilität ist zu testen (WebAssembly‑Unterstützung). Datenschutzrechtlich müssen die Dateien lokal gespeichert werden dürfen.

## ADR 004: IIIF 3.0 als Standard für Bildauslieferung

**Kontext:**
Zeugenbilder müssen mit beliebiger Auflösung und Ausschnitten angezeigt werden können. Dabei sollen existierende IIIF‑Viewer (z. B. Mirador) eingesetzt werden können, und ein Fallback für Server ohne IIIF‑Unterstützung ist nötig.

**Entscheidung:**
Die Plattform nutzt **IIIF Image API 3.0 Level 2** als primären Standard für die Bildauslieferung. Für Zeugen ohne eigenen IIIF‑Server wird ein eigener Medienserver bereitgestellt (FastAPI, libvips/Sharp), der IIIF‑konforme Endpunkte anbietet. Mirador 3.3.0 wird als Viewer eingebunden.

**Alternativen:**
1. Speicherung der Bilder als statische WebP/AVIF und Skalierung im Browser – ineffizient bei hohen Auflösungen und ohne Standard‑Viewer.  
2. Nutzung proprietärer Bilderdienste – lock‑in Effekt und fehlende Kontrolle über Rate‑Limiting oder Datenschutz.  
3. Verzichten auf Zoom‑ und ROI‑Funktionen – schränkt Benutzererlebnis ein.

**Konsequenzen:**
Die Entscheidung erleichtert die Integration mit bestehenden IIIF‑Ökosystemen und Werkzeugen. Der Medienserver muss Rate‑Limiting (100 req/min), CORS und CDN‑Caching implementieren. Implementierungsaufwand entsteht durch das Aufsetzen des eigenen IIIF‑Fallbacks, aber langfristig wird so die Interoperabilität gewährleistet.

## ADR 005: Integration externer Alignment‑Tools

**Kontext:**
Kollation von bis zu 60 Zeugen ist mit einer Eigenimplementierung kaum effizient zu bewältigen. Externe Tools wie CollateX und LERA bieten ausgereifte Algorithmen, müssen aber in die Pipeline integriert werden.

**Entscheidung:**
Es werden sowohl **CollateX** (für Needleman‑Wunsch/Dekker‑Algorithmen) als auch **LERA** (für Geniza‑ähnliche Fälle) integriert. Die Anfragen an die REST‑APIs werden containerisiert im eigenen Cluster ausgeführt. Fuzzy‑Matching wird optional aktiviert und kann manuell nachjustiert werden.

**Alternativen:**
1. Eigenentwicklung eines Alignment‑Algorithmus – sehr aufwändig, schwer zu testen und zu validieren.  
2. Verwendung nur eines Tools – würde die Flexibilität (z. B. für fragmentarische Texte) einschränken.  
3. Nutzung kommerzieller Tools – Lizenzkosten, eingeschränkte Anpassbarkeit.

**Konsequenzen:**
Die Entscheidung erfordert das Management zweier externer Tools (Version, Konfiguration, Monitoring). Dafür steht ein bewährtes Algorithmenspektrum zur Verfügung. Bei steigender Last müssen die Container entsprechend skaliert werden, was DevOps‑Aufwand bedeutet.

## ADR 006: Rolle‑basiertes Layer‑Modell für Transkriptionen

**Kontext:**
Jeder Zeuge kann mehrere Transkriptionslayer haben (diplomatisch, normalisiert, interpretiert). Diese Layer müssen im Kollationsprozess unterschiedlich behandelt werden und im RE selektierbar sein.

**Entscheidung:**
Ein Rollen‑Dialog wird in der EPE implementiert, der jeder Transkriptionsquelle pro Zeuge eine Rolle (diplomatisch, normalisiert, …) zuweist. Nur die diplomatische Transkription dient als Basis für die Kollation; andere Layer können später in der RE eingeblendet werden. Layer‑Informationen werden in Metadaten (`layer_roles`) gespeichert.

**Alternativen:**
1. Alle Layer gleich behandeln – erschwert die Analyse, da normalisierte Texte oft abweichen.  
2. Nur diplomatische Transkription speichern – verhindert Verfügbarkeit normalisierter Varianten.  
3. Layer in separaten Projekten verwalten – erhöht Komplexität und Inkonsistenzgefahr.

**Konsequenzen:**
Der Layer‑Dialog erhöht den Entwicklungsaufwand, sorgt aber für klare Strukturen in Kollation und Export. Die TEI‑Exporte müssen diese Rollen korrekt in `<app>` und `<rdg>` abbilden. Das RE erhält Schalter, um zwischen Layern umzuschalten.

## ADR 007: i18n/A11Y‑Unterstützung in fünf Sprachen

**Kontext:**
Die Zielgruppe ist international; die Nutzeroberfläche muss neben Englisch auch Persisch, Arabisch, Türkisch und Urdu unterstützen. Zudem sollen WCAG 2.1 AA‑Kriterien erfüllt werden.

**Entscheidung:**
Von Anfang an wird ein Internationalisierungssystem implementiert (z. B. Django i18n + React‑i18next). Alle Strings werden externalisiert, Right‑to‑Left‑Layouts müssen korrekt gerendert werden. A11Y‑Tests (z. B. mit Axe) werden in die CI integriert. Fokus‑Indikatoren werden auf 2 px festgelegt und alle Funktionen sind mit Tastatur bedienbar.

**Alternativen:**
1. i18n/A11Y erst später einbauen – führt zu Refactoring‑Aufwand und möglicherweise zu unzugänglichen Komponenten.  
2. Nur englische Oberfläche – schließt einen Teil der Zielgruppe aus.  
3. Externe Übersetzungsplugins – unflexibel und möglicherweise nicht konform mit WCAG.

**Konsequenzen:**
Es entsteht Mehraufwand für Lokalisierung und Testen, sorgt aber für breitere Zugänglichkeit und bessere Benutzererfahrung. Ressourcen für Übersetzungen müssen eingeplant werden.

## Zusammenfassung

Die obigen Entscheidungen bilden die Grundlage für die Architektur und Implementierung der EPE‑/RE‑Plattform. Alle ADRs können in späteren Phasen erweitert oder angepasst werden, benötigen jedoch eine formale Freigabe, falls sie die non‑negotiables der ursprünglichen Spezifikation betreffen.