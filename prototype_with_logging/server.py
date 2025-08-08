#!/usr/bin/env python3
"""
Ein sehr einfacher HTTP‑Server für die Bereitstellung statischer Dateien.

Dieser Server dient lediglich Demonstrationszwecken für den Prototyp der Reading
Environment. Er stellt Dateien aus dem aktuellen Arbeitsverzeichnis bereit,
einschließlich der Beispiel‑JSON‑Datei und der HTML‑Datei.

Starten Sie den Server mit:
    python server.py

Anschließend sind die Daten unter http://localhost:8000 erreichbar.
"""

import http.server
import os
import socketserver
import json
import datetime

PORT = 8000

# Globale Zeugenliste, wird beim Start eingelesen.
witnesses = []
# Liste von Annotationen
annotations = []


def load_witnesses():
    """Lädt die Daten aus der JSON-Datei in die globale Liste."""
    global witnesses
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'witnesses.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            witnesses = json.load(f)
    except FileNotFoundError:
        witnesses = []


def load_annotations():
    """Lädt Annotationen aus JSON-Datei."""
    global annotations
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'annotations.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
    except FileNotFoundError:
        annotations = []


def save_annotations():
    """Speichert Annotationen in JSON-Datei."""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'annotations.json')
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)


def save_witnesses():
    """Speichert die globale Liste in die JSON-Datei."""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'witnesses.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(witnesses, f, ensure_ascii=False, indent=2)


def write_log(method: str, path: str, status: int, message: str = '') -> None:
    """Schreibt einen kompakten Logeintrag in logs/server.log."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'server.log')
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    line = f"{timestamp} {method} {path} {status} {message}\n"
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(line)


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP-Handler mit CORS und einfachen API-Endpunkten."""

    def end_headers(self) -> None:
        # CORS-Header hinzufügen
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):  # type: ignore[override]
        self.send_response(204)
        self.end_headers()

    def do_GET(self):  # type: ignore[override]
        parsed_path = self.path.split('?')[0]
        if parsed_path.startswith('/api/'):
            self.handle_api_get(parsed_path)
        else:
            # Statische Dateien ausliefern
            super().do_GET()

    def do_POST(self):  # type: ignore[override]
        parsed_path = self.path
        if parsed_path == '/api/witnesses':
            self.handle_api_post_witness()
        elif parsed_path == '/api/annotations':
            self.handle_api_post_annotation()
        else:
            self.send_error(404, 'Not Found')

    def handle_api_get(self, path):
        if path == '/api/witnesses':
            # Liste der Zeugen (nur id + label)
            meta = [{"id": w["id"], "label": w["label"]} for w in witnesses]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(meta, ensure_ascii=False).encode('utf-8'))
            write_log(self.command, self.path, 200)
            return
        if path.startswith('/api/witnesses/'):
            witness_id = path.split('/')[-1]
            w = next((wit for wit in witnesses if wit['id'] == witness_id), None)
            if not w:
                self.send_error(404, 'Witness not found')
                write_log(self.command, self.path, 404, 'Witness not found')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(w, ensure_ascii=False).encode('utf-8'))
            write_log(self.command, self.path, 200)
            return
        if path == '/api/alignments':
            # Parameter aus Querystring lesen
            # self.path enthält '?', path ist ohne Query
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            base_id = qs.get('base', [None])[0]
            witness_id = qs.get('witness', [None])[0]
            if not base_id or not witness_id:
                self.send_error(400, 'Missing base or witness id')
                write_log(self.command, self.path, 400, 'Missing base or witness id')
                return
            base = next((wit for wit in witnesses if wit['id'] == base_id), None)
            other = next((wit for wit in witnesses if wit['id'] == witness_id), None)
            if not base or not other:
                self.send_error(404, 'Witness not found')
                write_log(self.command, self.path, 404, 'Witness not found')
                return
            alignments = []
            # Einfaches Alignment: Positionen matchen
            base_tokens = base['sections'][0]['tokens']
            other_tokens = other['sections'][0]['tokens']
            max_len = max(len(base_tokens), len(other_tokens))
            for idx in range(max_len):
                base_tok = base_tokens[idx] if idx < len(base_tokens) else None
                other_tok = other_tokens[idx] if idx < len(other_tokens) else None
                alignments.append({
                    'position': idx + 1,
                    'base': base_tok or {'id': None, 'text': '[—]'},
                    'witness': other_tok or {'id': None, 'text': '[—]'}
                })
            resp = {'alignments': alignments}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            write_log(self.command, self.path, 200)
            return
        # unbekannter API Pfad
        self.send_error(404, 'API endpoint not found')
        write_log(self.command, self.path, 404, 'Endpoint not found')

    def handle_api_post_witness(self):
        # JSON-Daten aus dem Request-Body lesen
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            write_log(self.command, self.path, 400, 'Invalid JSON')
            return
        # Minimalvalidierung: muss id und label enthalten und mindestens einen Abschnitt
        if not isinstance(data, dict) or 'id' not in data or 'label' not in data:
            self.send_error(400, 'Missing required fields')
            write_log(self.command, self.path, 400, 'Missing required fields')
            return
        # Prüfen, ob ID bereits existiert
        if any(w['id'] == data['id'] for w in witnesses):
            self.send_error(400, 'Witness ID already exists')
            write_log(self.command, self.path, 400, 'Witness ID exists')
            return
        witnesses.append(data)
        save_witnesses()
        self.send_response(201)
        self.end_headers()
        write_log(self.command, self.path, 201, f"Imported witness {data['id']}")

    def handle_api_post_annotation(self):
        # JSON-Daten aus dem Request-Body lesen
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            write_log(self.command, self.path, 400, 'Invalid JSON')
            return
        # Erwartet: witness_id, token_id, annotation
        if not all(key in data for key in ('witness_id', 'token_id', 'annotation')):
            self.send_error(400, 'Missing fields')
            write_log(self.command, self.path, 400, 'Missing fields')
            return
        # Annotation hinzufügen
        ann = {
            'witness_id': data['witness_id'],
            'token_id': data['token_id'],
            'annotation': data['annotation'],
            'timestamp': datetime.datetime.now().isoformat(timespec='seconds')
        }
        annotations.append(ann)
        save_annotations()
        self.send_response(201)
        self.end_headers()
        write_log(self.command, self.path, 201, f"Annotation added to {data['token_id']}")


def run_server():
    # Wechsel in das Verzeichnis, in dem sich server.py befindet
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Zeugen aus Datei laden
    load_witnesses()
    load_annotations()
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"Server läuft unter http://localhost:{PORT}")
        print("Stoppen mit CTRL+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()


if __name__ == "__main__":
    run_server()