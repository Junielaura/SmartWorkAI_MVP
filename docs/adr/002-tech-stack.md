# ADR-002: Technology Stack Selection

**Status**: Accepted  
**Date**: 2026-11-17  
**Decision**: 
- **Frontend**: Next.js 14+ with App Router, React 18, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+ with FastAPI, SQLModel for ORM, Pydantic for validation
- **Database**: PostgreSQL with SQLAlchemy/Alembic migrations
- **Vector Store**: ChromaDB as MVP, encapsulated behind a service interface for future PostgreSQL pgvector or Pinecone migration
- **AI/LLM**: Ollama with configurable model (DeepSeek Codellama as default), accessed via local HTTP API
- **Embeddings**: `nomic-embed-text` via Ollama or transformers, configurable through environment variables
- **PDF Processing**: PyMuPDF with Tesseract OCR for scanned pages
- **Document Formats**: python-docx (DOCX), openpyxl/Pandas (XLSX), pandas (CSV)
- **Charts**: Plotly for interactive visualizations, exported as PNG/SVG/PDF
- **Background Tasks**: Celery + Redis + Celery Beat
- **Authentication**: JWT tokens with refresh tokens, password hashing via bcrypt
- **Testing**: pytest with pytest-asyncio, httpx for API tests, coverage threshold 80%

**Context**: These technologies were chosen based on the prompt requirements, existing ecosystem maturity, and the need for a balance between capability and development speed for an MVP.

**Consequences**:
- ✅ Next.js App Router gives excellent SEO and performance out of the box
- ✅ FastAPI provides automatic OpenAPI docs and high performance
- ✅ ChromaDB requires no external service in development
- ✅ Ollama keeps LLM inference local and controllable
- ⚠️ Node.js 18+ required for Next.js 14 features
- ⚠️ PostgreSQL knowledge assumed for migrations
- ⚠️ Ollama must be running for AI features in production

**Related**: `docs/architecture.md`, `docs/requirements-traceability.md`