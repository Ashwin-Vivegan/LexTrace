# LexTrace - Milestone 1 Implementation & Walkthrough Guide

This document is a comprehensive, technical walkthrough of the **LexTrace** project based **ONLY on the codebase currently implemented** in Milestone 1. It serves as an interview preparation guide and architectural reference.

---

## SECTION 1 — CURRENT PROJECT OVERVIEW

LexTrace is an AI-powered legal document intelligence platform. In **Milestone 1**, the system focuses on backend document ingestion, multi-format text extraction, document version management, SQLite relational storage via SQLAlchemy 2.x ORM, REST API endpoints, automated testing, and a React frontend document upload vault.

### Actual Implemented Flow

```text
User Selects File & Fills Metadata (React UI)
  ↓
FormData HTTP Request (POST /api/documents/upload)
  ↓
FastAPI Router (app/routers/documents.py)
  ↓
File Validation & Header Inspection (app/services/document_extractor.py & app/utils/file_storage.py)
  ↓
Physical File Storage (uploads/<document_id>/v<version>/<filename>)
  ↓
Text Extraction Service (PDF via pypdf, DOCX via python-docx, TXT via UTF-8)
  ↓
SQLAlchemy ORM Transaction (app/db/models.py -> Document & DocumentVersion)
  ↓
SQLite Database (backend/data/lextrace.db)
  ↓
JSON Response (document_id, version_id, text_length, status)
  ↓
React UI Display (Document card grid, version list modal, text previewer)
```

### System Status Classification

| Component | Status | Details |
| :--- | :--- | :--- |
| **SQLite Persistence & SQLAlchemy ORM** | **IMPLEMENTED** | Relational `Document` and `DocumentVersion` schemas stored in `backend/data/lextrace.db`. |
| **Document Ingestion (PDF, DOCX, TXT)** | **IMPLEMENTED** | Upload validation, header magic bytes inspection, 25MB limit, and physical disk storage. |
| **Text Extraction Service** | **IMPLEMENTED** | Format-specific extractions via `pypdf`, `python-docx`, and UTF-8/Latin-1 `TXT` reader. |
| **Document Versioning System** | **IMPLEMENTED** | Version tagging (`current`, `superseded`, `draft`), auto-status update on new version upload. |
| **REST API Endpoints** | **IMPLEMENTED** | Upload, list documents, get document details + version history, view raw text, delete document. |
| **Pytest Automated Test Suite** | **IMPLEMENTED** | 11 unit & API integration tests covering connection, models, extractions, API endpoints, and versioning. |
| **React Document Vault UI** | **IMPLEMENTED** | File selector, metadata entry form, document cards, version modal, text viewer, deletion handler. |
| **In-Memory Legacy Demo Endpoints** | **PARTIALLY IMPLEMENTED** | Mock case tracking (`/api/cases`), trace audit logs (`/api/trace`), and basic TF-IDF mock RAG (`/api/rag/ask`) operating on in-memory mock data arrays. |
| **PostgreSQL & pgvector** | **NOT IMPLEMENTED** | Database is currently SQLite; pgvector table structures are not created yet. |
| **Dense Vector Embeddings** | **NOT IMPLEMENTED** | No neural embedding model (e.g. OpenAI / SentenceTransformers) integrated yet. |
| **LLM Grounded QA & RAG** | **NOT IMPLEMENTED** | No LLM API calls (OpenAI/Gemini/Groq); mock RAG endpoint uses template text formatting over TF-IDF scores. |
| **OCR (Optical Character Recognition)** | **NOT IMPLEMENTED** | Scanned PDFs without text streams return a clear extraction error message. |
| **Authentication & RBAC** | **NOT IMPLEMENTED** | Endpoints are unauthenticated; no user roles or JWT tokens. |

---

## SECTION 2 — PROJECT STRUCTURE

```text
c:\Users\Admin\Desktop\Lextrace project\
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py               # Application settings (Pydantic Settings)
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py             # SQLAlchemy engine, SessionLocal, get_db dependency
│   │   │   ├── models.py               # Document & DocumentVersion ORM models
│   │   │   └── init_db.py              # Schema creation script (Base.metadata.create_all)
│   │   ├── schemas/
│   │   │   ├── __init__.py             # Schema registry exports
│   │   │   ├── document.py             # Document API Pydantic V2 schemas
│   │   │   └── legacy.py               # Legacy mock endpoint schemas
│   │   ├── services/
│   │   │   ├── document_extractor.py   # Format-specific text extraction logic
│   │   │   ├── storage.py              # Legacy in-memory mock datastore
│   │   │   └── rag_engine.py           # Legacy TF-IDF mock search engine
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── file_storage.py         # File saving, path sanitization, directory cleanup
│   │   └── routers/
│   │       ├── documents.py            # Main Document Management REST API routes
│   │       ├── cases.py                # Legacy case tracking routes (mock)
│   │       ├── health.py               # Health check route
│   │       ├── rag.py                  # Legacy mock RAG search routes
│   │       └── trace.py                # Legacy trace audit log routes
│   ├── data/
│   │   └── lextrace.db                 # SQLite database file
│   ├── uploads/                        # Physical uploaded document storage directory
│   ├── tests/
│   │   ├── conftest.py                 # Pytest fixtures (in-memory DB & TestClient)
│   │   ├── test_database.py            # Database connection & ORM model tests
│   │   ├── test_documents_api.py       # End-to-end API lifecycle tests
│   │   └── test_extraction.py          # Document text extraction unit tests
│   ├── main.py                         # FastAPI application entrypoint & startup lifespan
│   └── requirements.txt                # Python package dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentManager.jsx     # Document upload form, list grid, version viewer
│   │   │   ├── CaseTracker.jsx         # Case tracker UI component
│   │   │   ├── Dashboard.jsx           # Overview dashboard component
│   │   │   ├── Header.jsx              # Application header
│   │   │   ├── RagAssistant.jsx        # Search/RAG query UI component
│   │   │   ├── Sidebar.jsx             # Navigation sidebar
│   │   │   └── TraceAuditLog.jsx       # Trace log audit table
│   │   ├── App.jsx                     # Main React App container & tab navigation
│   │   ├── api.js                      # API client functions (fetch wrappers)
│   │   └── main.jsx                    # React Vite DOM entrypoint
│   ├── index.html                      # HTML root template
│   └── package.json                    # Node.js dependencies
└── docs/
    └── MILESTONE_1_WALKTHROUGH.md     # Current documentation artifact
```

### Important Files & Interactions

1. **`backend/app/core/config.py`**
   - **Purpose**: Defines application configuration using `pydantic-settings`.
   - **What it does**: Sets `DATABASE_URL` (`sqlite:///./data/lextrace.db`), `UPLOAD_DIR` (`./uploads`), `MAX_UPLOAD_SIZE_BYTES` (25MB), and `ALLOWED_EXTENSIONS` (`.pdf`, `.docx`, `.txt`). Automatically creates `./data` and `./uploads` directories on load.
   - **Interactions**: Imported by `database.py`, `file_storage.py`, and `documents.py`.

2. **`backend/app/db/database.py`**
   - **Purpose**: Configures SQLAlchemy ORM engine and session factory.
   - **What it does**: Creates `engine` (with `check_same_thread=False` for SQLite), `SessionLocal` factory, `Base` declarative class, and `get_db()` generator function for FastAPI dependency injection.
   - **Interactions**: Used by `models.py`, `init_db.py`, `documents.py` router, and `conftest.py`.

3. **`backend/app/db/models.py`**
   - **Purpose**: Defines database tables using SQLAlchemy ORM.
   - **What it does**: Contains `Document` model (logical document record) and `DocumentVersion` model (snapshot of file version). Establishes a 1-to-N cascading relationship.
   - **Interactions**: Used by `documents.py` router, `init_db.py`, and test files.

4. **`backend/app/services/document_extractor.py`**
   - **Purpose**: Extracts plain text from uploaded document files.
   - **What it does**: Inspects magic bytes to block spoofed extensions. Uses `pypdf` for PDFs, `python-docx` for DOCXs (paragraphs + tables), and UTF-8/Latin-1 for TXT files. Raises `ExtractionError` on zero-byte or image-only PDFs.
   - **Interactions**: Called by `documents.py` upload route handler.

5. **`backend/app/utils/file_storage.py`**
   - **Purpose**: Manages file storage operations on disk.
   - **What it does**: Sanitizes filenames, constructs folder hierarchy `uploads/<document_id>/v<version>/<filename>`, streams uploaded files, enforces size limits, and deletes files when documents are deleted.
   - **Interactions**: Called by `documents.py` upload and delete routes.

6. **`backend/app/routers/documents.py`**
   - **Purpose**: FastAPI APIRouter handling document management REST endpoints.
   - **What it does**: Implements `POST /upload`, `GET /`, `GET /{document_id}`, `GET /{document_id}/versions/{version_id}/text`, and `DELETE /{document_id}`.
   - **Interactions**: Receives HTTP requests from frontend `api.js`, interacts with DB models, `DocumentExtractor`, and `file_storage`.

7. **`backend/main.py`**
   - **Purpose**: Application entrypoint and server runner.
   - **What it does**: Instantiates `FastAPI()`, adds CORS middleware (`allow_origins=["*"]`), registers lifespan context manager calling `init_db()`, and mounts API routers under `/api`.
   - **Interactions**: Imported by uvicorn and pytest test suite.

8. **`frontend/src/api.js`**
   - **Purpose**: Frontend API integration module.
   - **What it does**: Contains async JavaScript functions (`uploadDocument`, `fetchDocuments`, `fetchDocumentDetail`, `fetchExtractedText`, `deleteDocument`) wrapping `fetch()` calls to `http://localhost:5000/api`.
   - **Interactions**: Imported by `App.jsx` and `DocumentManager.jsx`.

9. **`frontend/src/components/DocumentManager.jsx`**
   - **Purpose**: Primary React UI view for document operations.
   - **What it does**: Renders file upload form, metadata inputs, document grid cards, version modal, text preview box, and deletion prompt.
   - **Interactions**: Receives document array and upload handler from `App.jsx`, calls `api.js` functions.

---

## SECTION 3 — BACKEND WALKTHROUGH

### Execution Flow Step-by-Step

#### Startup Flow
1. **Command Launched**: `uvicorn main:app --port 5000` or `python main.py`.
2. **Settings Loaded**: `app/core/config.py` evaluates settings and ensures `./data` and `./uploads` exist.
3. **Engine Creation**: `app/db/database.py` initializes the SQLAlchemy SQLite engine (`sqlite:///./data/lextrace.db`).
4. **App Lifespan Triggered**: `main.py` enters `lifespan(app)` context manager and calls `init_db()`.
5. **Tables Created**: `app/db/init_db.py` executes `Base.metadata.create_all(bind=engine)`, creating `documents` and `document_versions` tables if missing.
6. **Routers Registered**: `main.py` mounts `/api/documents`, `/api/health`, `/api/cases`, `/api/trace`, `/api/rag`.

#### Document Upload Execution Flow
7. **HTTP Request Arrives**: `POST /api/documents/upload` carrying `multipart/form-data`.
8. **Dependency Injection**: FastAPI invokes `get_db()` (`app/db/database.py`), yielding a SQLAlchemy `Session`.
9. **Extension Check**: `upload_document()` (`app/routers/documents.py`) verifies extension is in `{'.pdf', '.docx', '.txt'}`.
10. **Metadata Validation**: Pydantic model `DocumentMetadataInput` (`app/schemas/document.py`) validates fields (e.g., `document_type` in `{'contract', 'case_precedent', 'regulation', 'other'}`).
11. **Document Record Lookup/Creation**:
    - If `existing_document_id` provided: fetches existing `Document` from DB.
    - If new: generates a unique `document_id` (`DOC-101-XXXX`) and inserts `Document` into DB.
12. **Version ID Check**: Generates `version_id` (`DOC-101-XXXX-V1_0`) and confirms no duplicate version exists.
13. **File Streaming to Disk**: `save_uploaded_file()` (`app/utils/file_storage.py`) streams file to `uploads/DOC-101-XXXX/v1.0/filename.pdf` while validating max 25MB size.
14. **Text Extraction**: `DocumentExtractor.extract_text()` (`app/services/document_extractor.py`) validates header magic bytes (`%PDF-`, `PK\x03\x04`) and extracts plain text.
15. **Status Update**: If new version status is `'current'`, existing versions for the document are updated to `'superseded'`.
16. **Version Record Insertion**: `DocumentVersion` object created and added to session.
17. **DB Commit**: `db.commit()` persists transaction.
18. **JSON Response Returned**: `DocumentUploadResponse` payload returned to client.

---

## SECTION 4 — DATABASE WALKTHROUGH

### Current SQLite Implementation

- **Database File Location**: `backend/data/lextrace.db`
- **Configuration**: Configured via `DATABASE_URL = "sqlite:///./data/lextrace.db"`.
- **SQLAlchemy Version**: 2.x using `declarative_base()` and `sessionmaker()`.

### Database Schema & Tables

```mermaid
erdiagram
    documents ||--o{ document_versions : "has many (1-to-N)"
    documents {
        int id PK
        string document_id UK
        string document_name
        string document_type
        string jurisdiction
        string practice_area
        string client_reference
        datetime created_at
        datetime updated_at
    }
    document_versions {
        int id PK
        string version_id UK
        string document_id FK
        string version_number
        string file_name
        string file_path
        string file_type
        int file_size
        text extracted_text
        string effective_date
        string status
        datetime created_at
    }
```

#### Table 1: `documents`
- **Purpose**: Represents logical document entities (e.g., "Master Services Agreement").
- **Columns**:
  - `id` (Integer, Primary Key, Autoincrement)
  - `document_id` (String(50), Unique, Indexed, Non-nullable): Business identifier (e.g. `DOC-101-A1F2`).
  - `document_name` (String(255), Non-nullable): Human readable document title.
  - `document_type` (String(50), Non-nullable): Categorization (`contract`, `case_precedent`, `regulation`, `other`).
  - `jurisdiction` (String(100), Nullable): Legal jurisdiction (e.g. "England and Wales").
  - `practice_area` (String(100), Nullable): Practice domain (e.g. "Intellectual Property").
  - `client_reference` (String(100), Nullable): Client tracking code (e.g. "REF-9921").
  - `created_at` / `updated_at` (DateTime): Timestamp tracking.
- **Relationship**: `versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")`.

#### Table 2: `document_versions`
- **Purpose**: Stores immutable snapshots of document revisions and extracted text.
- **Columns**:
  - `id` (Integer, Primary Key, Autoincrement)
  - `version_id` (String(100), Unique, Indexed, Non-nullable): Version key (e.g. `DOC-101-A1F2-V1_0`).
  - `document_id` (String(50), Foreign Key `documents.document_id` with `ON DELETE CASCADE`): Relational link.
  - `version_number` (String(20), Non-nullable): Version tag (e.g. `"1.0"`, `"2.0"`).
  - `file_name` (String(255), Non-nullable): Original uploaded filename.
  - `file_path` (String(500), Non-nullable): Relative disk location.
  - `file_type` (String(20), Non-nullable): Format (`pdf`, `docx`, `txt`).
  - `file_size` (Integer, Non-nullable): Byte size.
  - `extracted_text` (Text, Nullable): Plain text extracted from document body.
  - `effective_date` (String(50), Nullable): Effective date string.
  - `status` (String(20), Non-nullable): Version state (`current`, `superseded`, `draft`).
  - `created_at` (DateTime): Creation timestamp.
- **Relationship**: `document = relationship("Document", back_populates="versions")`.

---

## SECTION 5 — DOCUMENT UPLOAD WALKTHROUGH

### Concrete Example Flow: Uploading `"Asterion Cloud Services Agreement.pdf"`

1. **Frontend Selection**: User selects `"Asterion Cloud Services Agreement.pdf"` in `DocumentManager.jsx` file input and fills metadata fields (`document_name="Asterion Cloud Services Agreement"`, `document_type="contract"`, `version_number="1.0"`, `status_str="current"`).
2. **Form Submission**: User clicks "Process & Upload File". `handleSubmit()` constructs JavaScript `FormData` object.
3. **HTTP Request**: `uploadDocument(formData)` in `frontend/src/api.js` issues `POST http://localhost:5000/api/documents/upload` carrying `multipart/form-data`.
4. **FastAPI Endpoint**: Request hits `upload_document()` in `backend/app/routers/documents.py`.
5. **Validation**:
   - `file.filename` extension `.pdf` checked against `ALLOWED_EXTENSIONS`.
   - `DocumentMetadataInput` schema validates `document_type` and `status_str`.
6. **File Storage**:
   - `generate_document_id()` creates `DOC-101-B4E9`.
   - `save_uploaded_file()` in `app/utils/file_storage.py` streams file bytes to disk at `uploads/DOC-101-B4E9/v1.0/Asterion_Cloud_Services_Agreement.pdf` and verifies file size <= 25MB.
7. **Text Extraction**: `DocumentExtractor.extract_text()` in `app/services/document_extractor.py`:
   - Checks file header for `%PDF` magic bytes.
   - Parses PDF pages with `pypdf.PdfReader`.
   - Returns concatenated text string (`"SECTION 1: SERVICES..."`).
8. **Database Insertion**:
   - Creates `Document(document_id="DOC-101-B4E9", ...)` record.
   - Creates `DocumentVersion(version_id="DOC-101-B4E9-V1_0", extracted_text=..., status="current")` record.
   - `db.commit()` persists records to `backend/data/lextrace.db`.
9. **Response Returned**: HTTP 201 JSON payload returned:
   ```json
   {
     "document_id": "DOC-101-B4E9",
     "version_id": "DOC-101-B4E9-V1_0",
     "document_name": "Asterion Cloud Services Agreement",
     "document_type": "contract",
     "version_number": "1.0",
     "status": "current",
     "file_type": "pdf",
     "file_size": 124500,
     "text_length": 8420,
     "message": "Document uploaded and processed successfully"
   }
   ```
10. **Frontend Display**: `DocumentManager.jsx` displays green success banner and re-fetches document list from `GET /api/documents` to update grid cards.

---

## SECTION 6 — DOCUMENT EXTRACTION

### Extraction Implementation Details

Extraction is handled by `DocumentExtractor` in `backend/app/services/document_extractor.py`.

#### 1. Header Validation
Before parsing, `validate_file_header()` reads the first 16 bytes of the file:
- **PDF**: Must begin with `b"%PDF"`.
- **DOCX**: Must begin with `b"PK\x03\x04"` (ZIP archive header).
- If header fails or file is 0 bytes, raises `ExtractionError`.

#### 2. Format Extractor Engines
- **PDF (`pypdf`)**:
  - `pypdf.PdfReader(file_path)` iterates over pages and calls `page.extract_text()`.
  - Joins non-empty page strings with double newlines `\n\n`.
  - **Scanned PDF Handling**: If concatenated text length is 0, raises `ExtractionError("PDF file contains no extractable text. It may be scanned or image-only...")`.
- **DOCX (`python-docx`)**:
  - `docx.Document(file_path)` extracts paragraph text `p.text` and table cell text `cell.text`.
  - Table rows are joined with cell separators ` | ` under `--- Document Tables ---`.
- **TXT**:
  - Opens file with `utf-8` encoding. On `UnicodeDecodeError`, falls back to `latin-1`.

#### 3. Storage & Error Propagation
- Extracted text is returned as a single `str` and stored in SQLite `document_versions.extracted_text`.
- If extraction raises `ExtractionError`, the uploaded physical file is cleaned up (deleted from disk) and FastAPI returns `HTTP 400 Bad Request` with the error detail.

---

## SECTION 7 — METADATA

### Supported Metadata Fields

| Field Name | Source | Validation | Storage Column | Status |
| :--- | :--- | :--- | :--- | :--- |
| `document_name` | Form field | Pydantic (1-255 chars) | `documents.document_name` | Required |
| `document_type` | Form field | Pydantic (`contract`, `case_precedent`, `regulation`, `other`) | `documents.document_type` | Required (default `"other"`) |
| `version_number` | Form field | Pydantic (max 20 chars) | `document_versions.version_number` | Required (default `"1.0"`) |
| `status` / `status_str` | Form field | Pydantic (`current`, `superseded`, `draft`) | `document_versions.status` | Required (default `"current"`) |
| `jurisdiction` | Form field | Pydantic (max 100 chars) | `documents.jurisdiction` | Optional |
| `practice_area` | Form field | Pydantic (max 100 chars) | `documents.practice_area` | Optional |
| `client_reference` | Form field | Pydantic (max 100 chars) | `documents.client_reference` | Optional |
| `effective_date` | Form field | Pydantic (max 50 chars) | `document_versions.effective_date` | Optional |
| `existing_document_id` | Form field | DB lookup | Linked to target `Document` | Optional |

### Document Version Handling
When uploading a new file version with `existing_document_id` specified:
- The system attaches the new `DocumentVersion` to the target `Document`.
- If the new version status is `"current"`, all existing versions for that `document_id` with status `"current"` are automatically updated in SQLite to `"superseded"`.

---

## SECTION 8 — API WALKTHROUGH

### Implemented REST API Endpoints

#### 1. Document Upload
- **Method**: `POST`
- **Path**: `/api/documents/upload`
- **Purpose**: Uploads legal document file and metadata, extracts text, stores file on disk, creates database records.
- **Request**: `multipart/form-data` (`file`, `document_name`, `document_type`, `version_number`, etc.)
- **Response**: `201 Created` JSON (`document_id`, `version_id`, `text_length`, `status`, `message`).
- **Implementation**: `upload_document()` in `backend/app/routers/documents.py`.

#### 2. List Documents
- **Method**: `GET`
- **Path**: `/api/documents`
- **Purpose**: Returns document list with metadata and current version status (excludes full text).
- **Request**: None
- **Response**: `200 OK` JSON Array of document summaries.
- **Implementation**: `list_documents()` in `backend/app/routers/documents.py`.

#### 3. Document Details
- **Method**: `GET`
- **Path**: `/api/documents/{document_id}`
- **Purpose**: Returns single document metadata and list of all associated versions.
- **Request**: Path parameter `document_id`
- **Response**: `200 OK` JSON (`document_id`, `document_name`, `versions: [...]`).
- **Implementation**: `get_document_detail()` in `backend/app/routers/documents.py`.

#### 4. Extracted Text Retrieval
- **Method**: `GET`
- **Path**: `/api/documents/{document_id}/versions/{version_id}/text`
- **Purpose**: Returns full raw extracted text for a specific document version.
- **Request**: Path parameters `document_id`, `version_id`
- **Response**: `200 OK` JSON (`document_id`, `version_id`, `text`).
- **Implementation**: `get_extracted_text()` in `backend/app/routers/documents.py`.

#### 5. Delete Document
- **Method**: `DELETE`
- **Path**: `/api/documents/{document_id}`
- **Purpose**: Deletes document, cascading version DB records, and directory tree from disk.
- **Request**: Path parameter `document_id`
- **Response**: `200 OK` JSON (`success: true`, `message`).
- **Implementation**: `delete_document()` in `backend/app/routers/documents.py`.

#### 6. System Health Check
- **Method**: `GET`
- **Path**: `/api/health`
- **Purpose**: Returns server operational health status.
- **Request**: None
- **Response**: `200 OK` JSON (`status: "healthy"`).
- **Implementation**: `health_check()` in `backend/app/routers/health.py`.

---

## SECTION 9 — FRONTEND WALKTHROUGH

### Current React Frontend Architecture

The frontend is built with React and Vite in `frontend/src/`.

#### Components & Data Flow

```text
App.jsx (Main Container & Active Tab State)
  ├── Header.jsx (API Status Indicator & Search Input)
  ├── Sidebar.jsx (Navigation Tabs: rag, dashboard, cases, trace, documents)
  └── DocumentManager.jsx (Document Vault Tab)
        ├── File Upload Modal Form (Multipart submission via api.js)
        ├── Document Cards Grid (Rendered from backend API data)
        └── Versions & Text Inspection Modal (Fetches detail & version text via api.js)
```

#### State & API Communication
- **Initial Load**: `App.jsx` triggers `useEffect()` calling `fetchDocuments()` in `api.js`.
- **API Helper (`api.js`)**: Wraps `fetch('http://localhost:5000/api/documents...')`. `uploadDocument(formData)` sends `FormData` without explicit `Content-Type` header to allow browser boundary calculation.
- **Error Handling**: `DocumentManager.jsx` displays inline red error banners on HTTP 400/500 failures (e.g. unsupported extension or extraction failure).
- **Success Handling**: On success, displays green alert box with document ID, version ID, text length, and re-fetches document list.

---

## SECTION 10 — COMPLETE REQUEST FLOW

### Actual System Architecture Flow Diagram

```text
+-----------------------------------------------------------------------+
|                            REACT FRONTEND                             |
|  DocumentManager.jsx -> api.js uploadDocument(formData)               |
+-----------------------------------------------------------------------+
                                   |
                       POST /api/documents/upload
                                   |
+-----------------------------------------------------------------------+
|                           FASTAPI BACKEND                             |
|  main.py -> app/routers/documents.py (upload_document)                |
+-----------------------------------------------------------------------+
          |                        |                        |
          v                        v                        v
+-------------------+    +-------------------+    +---------------------+
| Pydantic Schema   |    | File Storage Util |    | Document Extractor  |
| DocumentMetadata  |    | file_storage.py   |    | document_extractor  |
| Input Validation  |    | Saves file to disk|    | Parses PDF/DOCX/TXT |
+-------------------+    +-------------------+    +---------------------+
                                   |                        |
                                   +-----------+------------+
                                               |
                                               v
                                 +---------------------------+
                                 | SQLAlchemy ORM Session    |
                                 | Document & DocumentVersion|
                                 +---------------------------+
                                               |
                                               v
                                 +---------------------------+
                                 | SQLite Database           |
                                 | backend/data/lextrace.db  |
                                 +---------------------------+
```


## SECTION 11 — SECURITY REVIEW

| Security Metric | Status Level | Findings & Analysis |
| :--- | :--- | :--- |
| **Filename Sanitization** | **GOOD** | `sanitize_filename()` strips path separators and non-alphanumeric characters, mitigating path traversal. |
| **Header Magic Bytes Check** | **GOOD** | Inspects PDF `%PDF` and DOCX ZIP headers to prevent extension spoofing. |
| **File Size Limits** | **GOOD** | Enforces 25 MB max limit during stream writing to prevent denial-of-service disk filling. |
| **SQL Injection** | **GOOD** | Uses SQLAlchemy ORM parameterized queries; raw SQL execution is avoided. |
| **CORS Configuration** | **MEDIUM** | `CORSMiddleware` currently configured with `allow_origins=["*"]`. Should be restricted to specific frontend domain in production. |
| **Error Message Exposure** | **LOW** | Detailed error tracebacks returned in HTTP 400/500 responses during debug mode. |
| **Authentication & Authorization** | **CRITICAL** | Currently unauthenticated; no user roles, JWT validation, or access controls implemented. |
| **Rate Limiting** | **MEDIUM** | No API rate limiting implemented on upload endpoints. |

---

## SECTION 12 — CURRENT LIMITATIONS

### Genuinely NOT Implemented Yet

- **No PostgreSQL / pgvector**: Database is currently local SQLite.
- **No Dense Vector Embeddings**: No embedding models integrated.
- **No Real LLM Integration**: No OpenAI, Gemini, or Groq API calls.
- **No Optical Character Recognition (OCR)**: Image-only scanned PDFs fail text extraction.
- **No User Authentication**: No login, JWT tokens, or session management.
- **No Role-Based Access Control (RBAC)**: All endpoints are public and unrestricted.
- **No Background Task Queue**: File upload and text extraction run synchronously within the HTTP request thread.

---

## SECTION 13 — MILESTONE STATUS

| Feature | Status | Implementation Evidence Location |
| :--- | :--- | :--- |
| **SQLite Database Persistence** | **IMPLEMENTED** | `backend/app/db/database.py`, `backend/data/lextrace.db` |
| **SQLAlchemy 2.x ORM Models** | **IMPLEMENTED** | `backend/app/app/db/models.py` (`Document`, `DocumentVersion`) |
| **PDF Text Extraction** | **IMPLEMENTED** | `backend/app/services/document_extractor.py::extract_pdf()` |
| **DOCX Text Extraction** | **IMPLEMENTED** | `backend/app/services/document_extractor.py::extract_docx()` |
| **TXT Text Extraction** | **IMPLEMENTED** | `backend/app/services/document_extractor.py::extract_txt()` |
| **File Storage & Path Protection** | **IMPLEMENTED** | `backend/app/utils/file_storage.py` (`uploads/` directory) |
| **Document Versioning** | **IMPLEMENTED** | `backend/app/routers/documents.py`, `backend/app/db/models.py` |
| **Document Management REST APIs** | **IMPLEMENTED** | `backend/app/routers/documents.py` (Upload, List, Detail, Text, Delete) |
| **Pytest Automated Test Suite** | **IMPLEMENTED** | `backend/tests/` (11 passing test cases) |
| **React Document Vault UI** | **IMPLEMENTED** | `frontend/src/components/DocumentManager.jsx`, `frontend/src/api.js` |
| **Dense Vector Embeddings** | **NOT IMPLEMENTED** | No neural embedding integration |
| **PostgreSQL & pgvector** | **NOT IMPLEMENTED** | Database remains SQLite |
| **RAG LLM Synthesis** | **NOT IMPLEMENTED** | No LLM API integration |
| **OCR for Scanned PDFs** | **NOT IMPLEMENTED** | Scanned PDFs return extraction error |

---

## SECTION 13 — HOW TO RUN THE CURRENT SYSTEM

### 1. Start the Backend Server
```bash
cd backend
python main.py
```
*Server starts on `http://localhost:5000`.*

### 2. Access Swagger API Documentation
Open browser at:
`http://localhost:5000/docs`

### 3. Run Automated Tests
```bash
cd backend
python -m pytest -v
```

### 4. Start the React Frontend
```bash
cd frontend
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## SECTION 14 — SUMMARY OF IMPLEMENTATION

- **Implemented**: SQLite DB, SQLAlchemy 2.x ORM (`Document` & `DocumentVersion`), File Storage under `uploads/`, Header signature checks, Text extraction (PDF via `pypdf`, DOCX via `python-docx`, TXT), Versioning status updates (`current`/`superseded`), REST APIs (Upload, List, Detail, Version Text, Delete), Pytest suite (11 tests), and React upload vault UI.
- **Partially Implemented**: In-memory demo endpoints (`/api/cases`, `/api/trace`, mock TF-IDF `/api/rag/ask`) using temporary data arrays in `storage.py`.
- **Not Implemented**: PostgreSQL, pgvector, Dense Embeddings, LLM API calls, OCR, Authentication, RBAC.
- **Security Audit Summary**: Filename sanitization, size limits, and magic byte header checks are GOOD. Unauthenticated routes are CRITICAL for future production milestones.
