# LexTrace

> **AI-Powered Legal Document Intelligence & Version Control Platform**

LexTrace is an enterprise-grade legal document intelligence system designed for law firms, corporate legal departments, and compliance teams. It provides seamless document ingestion, multi-format text extraction (PDF, DOCX, TXT), immutable version snapshot management, relational SQLite/SQLAlchemy 2.x persistence, RESTful API endpoints, and a modern React Document Vault UI.

---

## Key Features

- **Multi-Format Ingestion & Validation**: Secure file uploads (PDF, DOCX, TXT) with magic-byte header validation and file size verification (up to 25MB).
- **Immutable Document Versioning**: Automatic versioning (`v1.0`, `v2.0`, etc.) with strict status tracking (`current`, `superseded`, `draft`) to maintain complete auditability across document iterations.
- **Text Extraction Engine**: Robust format-specific extraction utilizing `pypdf`, `python-docx`, and fallback UTF-8/Latin-1 encodings.
- **Smart Structural Chunking**: Sequential text chunking with metadata preservation (section names, page numbers, character offsets) ready for downstream vector indexing.
- **FastAPI REST API**: High-performance asynchronous backend providing document management, version history, text retrieval, and health metrics.
- **React Document Vault UI**: Dynamic frontend dashboard featuring document cards, metadata filters, interactive version modals, and raw text previewers.
- **Automated Pytest Suite**: 23+ unit and end-to-end integration tests covering database transactions, file extractions, API contracts, and chunking logic.

---

## System Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │               React + Vite Frontend Vault               │
       │    (Document Cards, Upload Form, Version History Modal) │
       └───────────────────────────┬────────────────────────────┘
                                   │
                           POST /api/documents/upload
                           GET  /api/documents
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                   FastAPI Backend API                  │
       │         (app/routers/documents.py & main.py)           │
       └─────┬─────────────────────┬──────────────────────┬───┘
             │                     │                      │
             ▼                     ▼                      ▼
┌─────────────────────────┐ ┌───────────────┐ ┌──────────────────────┐
│ File Storage & Validation│ │ Text Extractor│ │   SQLAlchemy 2.0 ORM │
│ (Magic bytes, disk path)│ │ (PDF/DOCX/TXT)│ │ (Document & Versions)│
└────────────┬────────────┘ └───────┬───────┘ └──────────┬───────────┘
             │                     │                     │
             ▼                     ▼                     ▼
  uploads/<doc>/<ver>/       Text Chunks         backend/data/
    <filename>               (Indexable)          lextrace.db
```

---

## Repository Structure

```text
LexTrace/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py               # Pydantic environment configuration
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy engine & SessionLocal dependency
│   │   │   ├── models.py               # Document, DocumentVersion & DocumentChunk models
│   │   │   └── init_db.py              # Database schema initialization script
│   │   ├── routers/
│   │   │   ├── documents.py            # Document management REST API routes
│   │   │   ├── health.py               # System health check route
│   │   │   ├── cases.py                # Case tracking routes (legacy/mock)
│   │   │   ├── rag.py                  # RAG search routes (legacy/mock)
│   │   │   └── trace.py                # Trace audit log routes
│   │   ├── services/
│   │   │   ├── document_extractor.py   # Multi-format text extraction logic
│   │   │   └── document_chunker.py     # Document text chunking service
│   │   └── utils/
│   │       └── file_storage.py         # Disk storage & path sanitization
│   ├── data/
│   │   └── lextrace.db                 # SQLite relational database
│   ├── tests/                          # Pytest suite (23 passing tests)
│   ├── main.py                         # FastAPI application entrypoint
│   └── requirements.txt                # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentManager.jsx     # Document upload form & vault grid
│   │   │   ├── CaseTracker.jsx         # Case tracking dashboard component
│   │   │   ├── RagAssistant.jsx        # Semantic query interface
│   │   │   ├── Dashboard.jsx           # Analytics overview
│   │   │   └── TraceAuditLog.jsx       # Audit trail viewer
│   │   ├── api.js                      # Centralized Axios API client
│   │   ├── App.jsx                     # Core application layout
│   │   └── main.jsx                    # React entrypoint
│   └── package.json                    # Frontend dependencies
├── docs/
│   └── MILESTONE_1_WALKTHROUGH.md      # Deep-dive architecture walkthrough
├── package.json                        # Root workspace scripts (concurrently runner)
└── README.md
```

---

## Quick Start Guide

### Prerequisites

- **Python**: `3.10` or higher
- **Node.js**: `18.0` or higher & `npm`

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server
uvicorn main:app --reload --port 8000
```

The API interactive Swagger documentation will be available at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node dependencies
npm install

# Start Vite React development server
npm run dev
```

The React frontend UI will be running at `http://localhost:5173`.

---

### 3. Running Both Servers Concurrently

You can run both backend and frontend servers simultaneously from the root directory:

```bash
# Install root workspace runner
npm install

# Run backend & frontend together
npm run dev
```

---

## Running Automated Tests

The backend includes a comprehensive `pytest` test suite:

```bash
cd backend
pytest -v
```

---

## API Reference Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/documents/upload` | Upload a new legal document or version snapshot |
| `GET` | `/api/documents` | List all documents with version counts and metadata |
| `GET` | `/api/documents/{document_id}` | Fetch document details and complete version history |
| `GET` | `/api/documents/{document_id}/versions/{version_id}/raw` | Retrieve full extracted text for a specific version |
| `DELETE` | `/api/documents/{document_id}` | Delete a document, all versions, and physical files |
| `GET` | `/api/health` | Check backend & database connection status |

---

## Roadmap & Next Steps

- [ ] **Dense Vector Embeddings**: Integration with OpenAI / HuggingFace `sentence-transformers`.
- [ ] **Vector Database**: PostgreSQL + `pgvector` for scalable similarity search.
- [ ] **LLM Grounded RAG Engine**: Retrieval-augmented generation with context citations and confidence scoring.
- [ ] **OCR Support**: Tesseract / AWS Textract fallback for scanned image PDFs.
- [ ] **Authentication & RBAC**: JWT token-based auth with user roles (`Attorney`, `Paralegal`, `Auditor`).

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
