# Complete Synthesized Prototype Documentation – EPE & RE (Alpha Phase)

This repository contains a simple prototype for a two-component Scholarly Edition Platform demonstrating basic concepts like data modeling, simple HTTP provisioning of JSON data, and a minimalistic frontend view. The prototype serves as a starting point for further development.

## Repository Structure

* `server.py` – A simple Python HTTP server (based on `http.server`) serving static JSON files from the `data/` directory, simulating part of the RE-API
* `data/sample_witness.json` – Example JSON structure for a witness with few tokens and alignment information
* `index.html` – Minimalistic HTML page that loads example JSON and displays it in browser, serving as simplified Reading Environment prototype
* `epe/parser.py` – Stub file for future ALTO/PAGE parser with placeholder functions demonstrating how ALTO files could be read and converted to internal JSON
* `docs/` – Phase 1 documents (Architecture Dossier, Database Schema, Security Concept, ADR Protocol, Engineering Diary) serving as reference and foundation for further implementation
* `logs/server.log` – API operation logging file
* `data/witnesses.json` – Persistent storage for witnesses
* `data/annotations.json` – Persistent storage for annotations with unique IDs

## Current Capabilities

The prototype now includes:
- Upload and storage of new witnesses (JSON)
- Export of individual witnesses as JSON files
- Comparison of two witnesses with difference highlighting
- Creation, storage, and retrieval of annotations at token level with unique IDs
- Display of existing annotations with visual highlighting of annotated tokens
- Deletion of individual annotations
- Deletion of witnesses with cascade removal of associated annotations
- Display of last 50 log entries for monitoring and debugging
- Comprehensive logging of all API operations

## Usage

1. **Starting the Server**  
   ```bash
   cd prototype
   python server.py
   ```
   Server runs at `http://localhost:8000` serving files from `data/` and the frontend.

2. **Viewing the Reading Prototype**  
   Open `http://localhost:8000/index.html` in browser. The page loads example JSON (`/data/sample_witness.json`) and lists tokens with their coordinates.

3. **Parser Development**  
   The `epe/parser.py` file contains dataclass definition and incomplete `parse_alto()` function for ALTO/PAGE-XML processing preparation, extensible for real imports in EPE.

## API Endpoints

### Witnesses
- `GET /api/witnesses` – List all witnesses
- `POST /api/witnesses` – Import new witness (returns 201 with "Imported witness {id}")
- `DELETE /api/witnesses/<id>` – Delete witness and associated annotations (returns 204 on success, 404 if not found)
- `GET /api/export/<witness_id>` – Export specified witness as JSON file with `Content-Disposition` header for download, filename format: `witness_<id>.json`

### Annotations
- `GET /api/annotations` – Retrieve all annotations
- `GET /api/annotations?witness_id=<id>` – Retrieve annotations for specific witness
- `POST /api/annotations` – Create new annotation with auto-generated unique ID (saves to `data/annotations.json`)
- `DELETE /api/annotations/<id>` – Delete specific annotation by ID (returns 204 on success, 404 if not found, 400 for invalid ID)

### Logging
- `GET /api/logs` – Returns last 50 lines from `logs/server.log` as JSON array

## Data Structures

### Annotation Structure with IDs
Each annotation now contains a unique identifier assigned by the server using a `next_annotation_id` counter:
```json
{
  "id": 3,
  "witness_id": "w1",
  "token_id": "w1t2",
  "annotation": "Beispiel",
  "timestamp": "2025-08-08T21:50:30"
}
```

## Frontend Features

### Witness Management
- Upload new witnesses via file input
- Select and compare two witnesses from dropdown menus
- Visual diff highlighting showing token differences
- Red "Delete Witness" button with `.danger` CSS class and confirmation dialog
- **Export button** in "Compare Witnesses" section – downloads currently selected witness as JSON file

### Annotation System
- Click tokens to create annotations (automatically assigned unique IDs)
- "Load Annotations" button retrieves and displays annotations for selected witness
- Annotated tokens highlighted green with `.annotated` class in alignment table
- Automatic annotation highlighting after witness comparison
- **Individual annotation deletion** – Each annotation in list shows small "×" symbol
  - Click triggers DELETE request with confirmation dialog
  - List automatically refreshes after deletion
  - Highlighting in comparison table updates accordingly

### Log Viewer
- "Server Logs" section with "Load Logs" button
- Displays last 50 log entries in `<pre>` block preserving line breaks
- Shows method, path, status code, and descriptive messages for all API operations

## CSS Classes and Styling

- `.danger` – Destructive actions (light red background, red text, red border)
- `.annotated` – Highlighted tokens with annotations (green background)
- `.ann-delete` – Small delete buttons for annotations (subtle but visible design with red background, small format for clear deletion warning)

## Logging System

Comprehensive logging captures all API operations with format:
```
2025-08-08T21:35:10 POST /api/witnesses 201 Imported witness w3
2025-08-08T21:36:30 DELETE /api/witnesses/w3 204 Deleted witness w3
2025-08-08T21:45:12 GET /api/export/w3 200 Exported witness w3
2025-08-08T21:47:18 DELETE /api/annotations/5 204 Deleted annotation 5
```

All API handlers pass status codes and messages to `write_log()` function, creating meaningful audit trail for:
- Witness imports and exports
- Annotation creation and deletion
- Witness deletion operations
- Error conditions (with appropriate status codes)

## Development Milestones

### Milestone 1: Delete Witnesses and Verify Logging
Implemented complete deletion functionality improving data hygiene and enabling test data cleanup. Deletion removes witness and all associated annotations, with changes persisted to JSON files and logged for verification.

### Extension Step 2: Annotations & Logging (August 8, 2025)
Added annotation management and log monitoring based on rationale that:
- **Annotations** are central to edition processes; editors need immediate feedback and ability to review notes
- **Transparency/Debugging** through frontend log access enables quick error response during development
- **Iterative approach** creates solid foundation without additional dependencies

### Milestone 3: Export and Delete Annotations
Following successful witness deletion implementation, the prototype was extended toward productive features. Two logical steps were witness export capability and individual annotation management (deletion). Both extensions serve data hygiene and facilitate workflows:
- Witnesses can be backed up or further processed
- Erroneous annotations can be conveniently removed
- Export functionality enables secure processing or backup of witnesses
- Individual annotation deletion with unique IDs enables precise data management

## Technical Architecture

### Data Flow
1. **Import**: POST request creates witness → logged
2. **Export**: GET request downloads witness as JSON file → logged
3. **Display**: GET requests fetch witness data for comparison
4. **Annotate**: POST creates annotation with unique ID, GET retrieves for display
5. **Delete Witness**: DELETE removes witness and all associated annotations → logged
6. **Delete Annotation**: DELETE removes specific annotation by ID → logged
7. **Monitor**: GET retrieves logs for verification

### Design Patterns
- RESTful API design with proper status codes
- JSON file-based persistence with ID management
- Event-driven frontend updates with automatic refresh
- Defensive programming (confirmation dialogs)
- Comprehensive audit logging
- Separation of concerns (server/client)
- Unique identifier management for annotations

## Limitations and Future Development

This prototype merely illustrates architecture and data flows, not meeting performance or security requirements of final platform. Missing features requiring future development include:

### Immediate Next Steps (from structured report)
- **Parsing**: Complete ALTO/PAGE parser implementation
- **Tokenization**: Advanced tokenization algorithms
- **Alignment**: Integration of external alignment tools
- **Search**: Full-text search capabilities
- **Database**: Migration from JSON files to proper database
- **IIIF**: Integration for image serving
- **Security**: Authentication, authorization, encryption
- **Performance**: Optimization for large datasets
- **Testing**: Comprehensive test suite
- **UI**: Reactive frontend architecture
- **i18n/A11Y**: Internationalization and accessibility

### Foundational Elements Established
These implementations form the basis for:
- Integration of external alignment tools
- Complete ALTO/PAGE parser implementation
- Introduction of reactive frontend architecture
- Detailed annotation types and role management
- Advanced scholarly edition workflows
- Data migration and backup strategies

## Result Summary

With these three milestones, the prototype provides:
- Complete CRUD operations for witnesses (Create, Read, Update via annotations, Delete)
- Full annotation lifecycle management with unique identifiers
- Export/import capabilities for data portability
- Transparent operation logging for all actions
- User-friendly interface with safety features
- Clean REST API implementation

The user interface remains clear and organized while the server-side has been extended with cleanly implemented endpoints. Logging continues to enable transparent tracking of all actions, providing a solid foundation for the scholarly edition platform's further development.

## Notes

The prototype demonstrates core concepts while maintaining awareness of limitations. It provides essential functions for data management, user interaction, and system monitoring, establishing key workflows, data structures, and interaction patterns necessary for the complete EPE (Edition Production Environment) and RE (Reading Environment) system.