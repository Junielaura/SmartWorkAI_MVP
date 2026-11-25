# SmartWorkAI_MVP

SmartWork AI is a complete MVP platform for document processing, analysis, and report generation. It enables users to import documents, extract and structure content, query documents with AI-sourced answers, generate deliverables (DOCX, PDF, XLSX), and produce periodic reports with visualizations.

## Architecture

The application follows a **modular monolith** architecture:

- **Frontend**: Next.js 14+ App Router, React, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI with SQLModel/SQLAlchemy
- **Database**: PostgreSQL (relational data) + ChromaDB (vector embeddings)
- **Cache & Background**: Redis + Celery + Celery Beat
- **AI/LLM**: Ollama with configurable model
- **Storage**: Local filesystem in development, S3-compatible abstraction for production
- **PDF Processing**: PyMuPDF with OCR via Tesseract
- **Office Docs**: python-docx, openpyxl, python-pptx
- **Data Processing**: Pandas

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- Or: Python 3.11+, Node.js 20+, PostgreSQL, Redis, Ollama

### Using Docker Compose (recommended)

```bash
docker compose up -d
```

This starts all services:
- **frontend**: http://localhost:3100
- **backend API**: http://localhost:8100
- **API docs**: http://localhost:8100/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **ChromaDB**: localhost:8000
- **Ollama**: localhost:11434

### Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # adjust as needed
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm install
cp .env.example .env  # adjust as needed
npm run dev  # http://localhost:3000
```

## Project Structure

```
smartwork-ai/
├── frontend/              # Next.js 14+ App Router + React + Tailwind
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── lib/
│   └── tests/
├── backend/               # FastAPI + SQLModel + Alembic
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── workers/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── compose.yaml           # Docker Compose development config
├── compose.override.yaml  # Override dev settings
├── compose.prod.yaml      # Production Docker Compose
├── Makefile               # Common commands
├── docs/
│   ├── architecture.md
│   ├── erd-diagram.md
│   ├── requirements-traceability.md
│   ├── user-guide.md
│   ├── adr/
│   └── gap-analysis.md
├── .env.example           # Environment variables template
├── .gitignore
└── README.md
```

## API Documentation

Once the backend is running, visit: **http://localhost:8100/docs**

The auto-generated OpenAPI docs include all endpoints for:
- Authentication (register, login, logout)
- Document management (upload, list, status, delete)
- RAG querying (ask questions, get sourced answers)
- Generation (DOCX, PDF, XLSX reports)
- Visualization (KPIs, dashboards)
- Reporting (schedules, execution)
- Tasks and notifications

## Environment Variables

See `.env.example` for the complete list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | postgres://smartwork:smartwork@db:5432/smartwork | PostgreSQL connection |
| `REDIS_URL` | redis://redis:6379/0 | Redis connection |
| `CHROMA_HOST` | chroma | Vector store host |
| `CHROMA_PORT` | 8000 | Vector store port |
| `OLLAMA_HOST` | http://host.docker.internal:11434 | LLM service |
| `OLLAMA_MODEL` | mistral | Default LLM model |
| `SECRET_KEY` | _(required)_ | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token TTL |
| `NEXT_PUBLIC_API_URL` | http://localhost:8100 | Frontend API URL |

## Available Scripts

### Backend (`backend/`)

- `uvicorn app.main:app` - Start development server
- `alembic upgrade head` - Run migrations
- `alembic revision --autogenerate -m "message"` - Create migration
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage

### Frontend (`frontend/`)

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

### Root

- `make up` - Start Docker Compose
- `make down` - Stop Docker Compose
- `make logs` - View service logs
- `make test` - Run all tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.