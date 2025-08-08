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
# Laufende ID für Annotationen
next_annotation_id = 1


def find_witness_by_id(witness_id: str):
    """Hilfsfunktion, um einen Zeugen anhand seiner ID zu finden."""
    return next((wit for wit in witnesses if wit['id'] == witness_id), None)


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
    """Lädt Annotationen aus JSON-Datei und initialisiert den ID-Zähler."""
    global annotations, next_annotation_id
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'annotations.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
    except FileNotFoundError:
        annotations = []
    # Initialisiere den ID-Zähler anhand vorhandener Annotationen
    next_annotation_id = 1
    for ann in annotations:
        if isinstance(ann, dict) and 'id' in ann:
            try:
                next_annotation_id = max(next_annotation_id, int(ann['id']) + 1)
            except Exception:
                pass


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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
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

    def do_DELETE(self):  # type: ignore[override]
        parsed_path = self.path.split('?')[0]
        if parsed_path.startswith('/api/witnesses/'):
            self.handle_api_delete_witness(parsed_path)
            return
        if parsed_path.startswith('/api/annotations/'):
            self.handle_api_delete_annotation(parsed_path)
            return
        self.send_error(404, 'Not Found')
        write_log(self.command, self.path, 404, 'Delete endpoint not found')

    def do_PUT(self):  # type: ignore[override]
        """Behandelt PUT-Anfragen, aktuell für Annotationen."""
        parsed_path = self.path.split('?')[0]
        if parsed_path.startswith('/api/annotations/'):
            self.handle_api_put_annotation(parsed_path)
            return
        self.send_error(404, 'Not Found')
        write_log(self.command, self.path, 404, 'PUT endpoint not found')

    def do_PATCH(self):  # type: ignore[override]
        """Behandelt PATCH-Anfragen, aktuell für Zeugen."""
        parsed_path = self.path.split('?')[0]
        if parsed_path.startswith('/api/witnesses/'):
            self.handle_api_patch_witness(parsed_path)
            return
        self.send_error(404, 'Not Found')
        write_log(self.command, self.path, 404, 'PATCH endpoint not found')

    def handle_api_delete_witness(self, path):
        witness_id = path.split('/')[-1]
        global witnesses, annotations
        idx = next((i for i, w in enumerate(witnesses) if w['id'] == witness_id), None)
        if idx is None:
            self.send_error(404, 'Witness not found')
            write_log(self.command, self.path, 404, 'Witness not found')
            return
        # Remove witness
        removed = witnesses.pop(idx)
        # Remove associated annotations
        annotations = [ann for ann in annotations if ann['witness_id'] != witness_id]
        save_witnesses()
        save_annotations()
        self.send_response(204)
        self.end_headers()
        write_log(self.command, self.path, 204, f"Deleted witness {witness_id}")

    def handle_api_delete_annotation(self, path):
        """Löscht eine Annotation anhand ihrer ID."""
        global annotations
        ann_id_str = path.split('/')[-1]
        try:
            ann_id = int(ann_id_str)
        except ValueError:
            self.send_error(400, 'Invalid annotation id')
            write_log(self.command, self.path, 400, 'Invalid annotation id')
            return
        # Finde Annotation
        idx = next((i for i, a in enumerate(annotations) if a.get('id') == ann_id), None)
        if idx is None:
            self.send_error(404, 'Annotation not found')
            write_log(self.command, self.path, 404, 'Annotation not found')
            return
        annotations.pop(idx)
        save_annotations()
        self.send_response(204)
        self.end_headers()
        write_log(self.command, self.path, 204, f"Deleted annotation {ann_id}")

    def handle_api_put_annotation(self, path):
        """Aktualisiert den Text einer bestehenden Annotation."""
        global annotations
        ann_id_str = path.split('/')[-1]
        try:
            ann_id = int(ann_id_str)
        except ValueError:
            self.send_error(400, 'Invalid annotation id')
            write_log(self.command, self.path, 400, 'Invalid annotation id')
            return
        # JSON-Daten aus dem Request-Body lesen
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            write_log(self.command, self.path, 400, 'Invalid JSON')
            return
        if 'annotation' not in data:
            self.send_error(400, 'Missing annotation field')
            write_log(self.command, self.path, 400, 'Missing annotation field')
            return
        # Finde Annotation
        ann = next((a for a in annotations if a.get('id') == ann_id), None)
        if not ann:
            self.send_error(404, 'Annotation not found')
            write_log(self.command, self.path, 404, 'Annotation not found')
            return
        ann['annotation'] = data['annotation']
        ann['timestamp'] = datetime.datetime.now().isoformat(timespec='seconds')
        save_annotations()
        self.send_response(200)
        self.end_headers()
        write_log(self.command, self.path, 200, f"Updated annotation {ann_id}")

    def handle_api_patch_witness(self, path):
        """Aktualisiert einzelne Felder eines Zeugen, z. B. das Label."""
        witness_id = path.split('/')[-1]
        w = find_witness_by_id(witness_id)
        if not w:
            self.send_error(404, 'Witness not found')
            write_log(self.command, self.path, 404, 'Witness not found')
            return
        # JSON-Daten aus dem Request-Body lesen
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            write_log(self.command, self.path, 400, 'Invalid JSON')
            return
        updated = False
        if 'label' in data and isinstance(data['label'], str):
            w['label'] = data['label']
            updated = True
        if not updated:
            self.send_error(400, 'No updatable fields provided')
            write_log(self.command, self.path, 400, 'No updatable fields provided')
            return
        save_witnesses()
        self.send_response(200)
        self.end_headers()
        write_log(self.command, self.path, 200, f"Updated witness {witness_id}")

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
            base_sec_id = qs.get('base_section', [None])[0]
            witness_sec_id = qs.get('witness_section', [None])[0]
            if not base_id or not witness_id:
                self.send_error(400, 'Missing base or witness id')
                write_log(self.command, self.path, 400, 'Missing base or witness id')
                return
            base = find_witness_by_id(base_id)
            other = find_witness_by_id(witness_id)
            if not base or not other:
                self.send_error(404, 'Witness not found')
                write_log(self.command, self.path, 404, 'Witness not found')
                return
            # Abschnitt ermitteln
            def select_section(wit, sec_id):
                if sec_id:
                    for sec in wit.get('sections', []):
                        if str(sec.get('id')) == sec_id:
                            return sec
                # Fallback: erster Abschnitt oder None
                return wit.get('sections', [None])[0] if wit.get('sections') else None
            base_sec = select_section(base, base_sec_id)
            other_sec = select_section(other, witness_sec_id)
            if not base_sec or not other_sec:
                self.send_error(404, 'Section not found')
                write_log(self.command, self.path, 404, 'Section not found')
                return
            alignments = []
            # Einfaches Alignment: Positionen matchen
            base_tokens = base_sec.get('tokens', [])
            other_tokens = other_sec.get('tokens', [])
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
        if path == '/api/annotations':
            # optional witness_id filter
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            wit_id = qs.get('witness_id', [None])[0]
            if wit_id:
                anns = [ann for ann in annotations if ann['witness_id'] == wit_id]
            else:
                anns = annotations
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(anns, ensure_ascii=False).encode('utf-8'))
            write_log(self.command, self.path, 200)
            return
        if path.startswith('/api/export/'):
            # Exportiert einen Zeugen als JSON-Datei
            witness_id = path.split('/')[-1]
            w = next((wit for wit in witnesses if wit['id'] == witness_id), None)
            if not w:
                self.send_error(404, 'Witness not found')
                write_log(self.command, self.path, 404, 'Witness not found')
                return
            content = json.dumps(w, ensure_ascii=False, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="witness_{witness_id}.json"')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            write_log(self.command, self.path, 200, f'Exported witness {witness_id}')
            return
        if path == '/api/logs':
            # Liefert die letzten 50 Logzeilen
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            log_path = os.path.join(log_dir, 'server.log')
            lines = []
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-50:]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'logs': [l.strip() for l in lines]}, ensure_ascii=False).encode('utf-8'))
            write_log(self.command, self.path, 200)
            return
        if path == '/api/logs/export':
            # Liefert das Log als herunterladbare Datei
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            log_path = os.path.join(log_dir, 'server.log')
            if not os.path.exists(log_path):
                self.send_error(404, 'Log file not found')
                write_log(self.command, self.path, 404, 'Log not found')
                return
            with open(log_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="server.log"')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            write_log(self.command, self.path, 200, 'Exported logs')
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
        global next_annotation_id
        # Annotation mit eindeutiger ID erstellen
        ann_id = next_annotation_id
        next_annotation_id += 1
        ann = {
            'id': ann_id,
            'witness_id': data['witness_id'],
            'token_id': data['token_id'],
            'annotation': data['annotation'],
            'timestamp': datetime.datetime.now().isoformat(timespec='seconds')
        }
        annotations.append(ann)
        save_annotations()
        self.send_response(201)
        self.end_headers()
        write_log(self.command, self.path, 201, f"Annotation {ann_id} added to {data['token_id']}")


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