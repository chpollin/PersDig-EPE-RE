# Sicherheits- und Robustheitskonzept – EPE & RE

**Datum:** 8. August 2025  
**Version:** Phase 1 – Planung

Dieses Dokument beschreibt die Sicherheitsmaßnahmen und Robustheitsstrategien für die Edition Production Environment (EPE) und die Reading Environment (RE). Ziel ist es, die Integrität, Verfügbarkeit und Vertraulichkeit der Daten sowie die Stabilität des Systems unter hoher Last zu gewährleisten.

## 1 Bedrohungsmodell und Schutzziele

Die Plattform verarbeitet wissenschaftlich wertvolle Texte, teilweise mit personenbeziehbaren Daten (z. B. Editoren, Annotationen). Angriffe können daher auf Verfügbarkeit (DoS), unautorisierte Datenzugriffe, Datenmanipulation oder Diebstahl abzielen. Da Endnutzer weltweit darauf zugreifen, müssen internationale Datenschutzanforderungen (insbesondere die DSGVO) eingehalten werden.

**Schutzziele:**

1. **Vertraulichkeit** – Schutz sensibler Nutzerdaten und API‑Schlüssel.
2. **Integrität** – Sicherstellung der Unveränderbarkeit wissenschaftlicher Daten durch Authentifizierung und Prüfmechanismen.
3. **Verfügbarkeit** – Aufrechterhaltung des Betriebs auch unter Lastspitzen und im Fehlerfall.
4. **Nachvollziehbarkeit** – Protokollierung relevanter Ereignisse und Änderungen.
5. **Datenschutz** – Minimierung personenbezogener Daten und Einhaltung gesetzlicher Vorschriften.

## 2 Authentifizierung und Autorisierung

- **Benutzerverwaltung**: Jeder Benutzer verfügt über individuelle Zugangsdaten (Username/Passwort) oder Single‑Sign‑On (SSO). Passwörter werden mit modernen Hash‑Algorithmen (bcrypt/Argon2) gespeichert.  
- **Token‑basierte Authentifizierung**: Für API‑Zugriffe (eScriptorium, optional RE‑REST) werden JWT oder OAuth2‑Tokens verwendet. Tokens enthalten Ablaufzeiten und rollenbasierte Claims.  
- **Rollenbasierte Autorisierung**: Rollen (Administrator, Editor, Viewer) werden im System definiert. Permissions sind feingranular (z. B. Import durchführen, Annotationen bearbeiten, Exporte herunterladen).  
- **CSRF‑Schutz**: Alle state‑verändernden Web‑Requests werden durch CSRF‑Tokens abgesichert.

## 3 Rate‑Limiting und API‑Schutz

- **eScriptorium‑Connector**: Begrenzung auf 10 Requests pro Sekunde; bei Überschreitung wird der Import gepuffert.  
- **Medienserver (IIIF‑Fallback)**: Limitierung auf 100 Requests pro Minute pro IP.  
- **Externer API‑Zugriff (optional)**: Falls die EPE eine REST‑API bereitstellt, gilt ein globales Rate‑Limit und Throttling pro Benutzer.  
- **Brute‑Force‑Schutz**: Login‑Versuche sind rate‑limitiert; nach fünf Fehlversuchen wird der Account zeitweise blockiert.

## 4 Datenübertragung und Verschlüsselung

- **TLS/HTTPS**: Alle Daten werden verschlüsselt übertragen (TLS 1.3). Interne Kommunikation (z. B. zwischen Anwendung und Datenbank) erfolgt über verschlüsselte Verbindungen oder lokale Unix‑Sockets.  
- **Encryption at Rest**: Datenbanken (MySQL/PostgreSQL, SQLite) und Objekt‑Storage (S3) werden verschlüsselt; Schlüsselverwaltung über ein zentrales Geheimnissystem (z. B. HashiCorp Vault).  
- **API‑Schlüssel**: Zugangsdaten zu externen Diensten (eScriptorium, CollateX, LERA) werden verschlüsselt gespeichert und nur zur Laufzeit entschlüsselt.

## 5 CORS, Content Security und Datenschutz

- **CORS‑Regeln**: Die Medienserver und APIs sind nur für definierte Origins freigeschaltet. Preflight‑Anfragen werden validiert.  
- **Content Security Policy (CSP)**: Strenge CSP‑Header schützen vor Cross‑Site‑Scripting (XSS).  
- **Cookie‑Sicherheit**: Cookies sind mit `Secure` und `HttpOnly` versehen; SameSite‑Regeln verhindern Session‑Hijacking.  
- **Datensparsamkeit**: Speicherung personenbezogener Daten wird minimiert; Editoren können Pseudonyme verwenden. Logs werden nach einer definierbaren Aufbewahrungsfrist anonymisiert oder gelöscht.  
- **Rechtskonformität**: Einwilligungen (Opt‑In) für Tracking und Analyse; Datenschutzerklärung gemäß DSGVO.

## 6 Fehlerresilienz und Wiederherstellung

- **Transaktionssicherheit**: Alle import- und exportrelevanten Operationen werden in Datenbanktransaktionen ausgeführt.  
- **Offline‑Queues**: Bei Netzwerkausfall werden Import- oder Exportvorgänge lokal gepuffert und bei Wiederherstellung der Verbindung automatisch erneut versucht.  
- **Automatisches Wiederaufsetzen**: Client‑seitig werden unterbrochene Benutzer‑Sessions (EPE) wiederhergestellt; server‑seitig gibt es Retry‑Mechanismen.  
- **Redundanz**: Backups der Datenbank und des Objekt‑Storage werden regelmäßig angelegt. Vorhalten von warm‑Standby‑Instanzen ermöglicht schnelle Wiederherstellung.

## 7 Logging, Monitoring und Audit

- **Zentrales Logging**: Alle Anwendungen schreiben Logs in ein zentrales System (z. B. ELK‑Stack). Sensible Daten werden gehashed oder ausgeblendet.  
- **Monitoring**: Kennzahlen wie CPU‑Nutzung, Speicherauslastung, Request‑Raten, Antwortzeiten und Fehlerquoten werden überwacht. Dashboards warnen bei Überschreiten von Schwellenwerten.  
- **Audit‑Trail**: Alle Änderungen an wissenschaftlichen Daten (z. B. Token‑Korrekturen, Annotationen) werden mit Benutzer, Zeitstempel und Änderungsdetails versioniert.  
- **Alarme**: Automatische Benachrichtigung bei sicherheitsrelevanten Ereignissen (z. B. ungewöhnliche Login‑Versuche, DoS‑Muster, Integritätsverletzungen).

## 8 Content Delivery und Caching

- **CDN**: IIIF‑`info.json` wird 24 Stunden, Manifeste werden 1 Stunde gecached; statische Assets des RE (HTML/JS/CSS) werden versioniert und langfristig im CDN gespeichert.  
- **Cache‑Invalidierung**: Inhalte werden über eindeutige Versionsnummern oder Hashes adressiert; nach einem Release werden alte Caches invalidiert.  
- **Edge‑Rate‑Limiting**: CDN übernimmt erste Schicht der Ratenbegrenzung; dadurch wird der Ursprungsserver entlastet.

## 9 Zugriff auf externe Dienste

- **eScriptorium**: Nutzung nur über HTTPS und authentifizierte Sessions; Importrate wird strikt eingehalten.  
- **CollateX/LERA**: Lokale Container‑Deployments minimieren Latenz; Alternativzugriff über gesicherte REST‑Endpoints.  
- **TEI‑CAT**: Wird primär offline eingesetzt; Uploads werden auf Viren geprüft, bevor sie verarbeitet werden.  
- **VIAF/GeoNames**: Abfragen über HTTPS; Ergebnis wird gecached, um unnötige Anfragen zu vermeiden.

## 10 Überprüfung und Penetrationstests

Vor der Alpha‑Freigabe werden Sicherheits‑Scans (z. B. OWASP ZAP) und Penetrationstests durchgeführt. Schwachstellen werden priorisiert behoben. Ein regelmäßiger Security‑Audit (mindestens halbjährlich) stellt die fortlaufende Einhaltung der Sicherheitsanforderungen sicher.

## 11 Fazit

Durch dieses Sicherheits- und Robustheitskonzept wird gewährleistet, dass die Plattform gegen die meisten gängigen Angriffsszenarien abgesichert ist, die Datensicherheit gewahrt bleibt und die Performance unter hoher Last stabil bleibt. Die Kombination aus Rate‑Limiting, Verschlüsselung, CORS/CSP‑Regeln, robustem Fehlerhandling und kontinuierlichem Monitoring bildet ein solides Fundament für die Entwicklung und den Betrieb der EPE‑ und RE‑Infrastruktur.