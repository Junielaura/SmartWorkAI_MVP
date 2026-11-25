# SmartWork AI MVP - Architecture

## 1. Global Architecture

The application follows a **modular monolith** architecture with a clear separation between:

- **Frontend**: Next.js 14+ App Router, React, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI with SQLModel/SQLAlchemy
- **Database**: PostgreSQL (relational data) + ChromaDB (vector embeddings)
- **Cache & Background**: Redis + Celery + Celery Beat
- **AI/LLM**: Ollama with configurable model (DeepSeek, Llama, etc.)
- **Storage**: Local filesystem in development, S3-compatible abstraction for production

### 1.1 Component Diagram

```mermaid
graph TD
    subgraph Frontend
        F1[Next.js App Router]
        F2[React Components]
        F3[Tailwind CSS]
        F4[API Routes / Server Actions]
    end

    subgraph Backend
        B1[FastAPI Main]
        B2[API Routes / Endpoints]
        B3[Services: Ingestion/Extraction]
        B4[Services: Classification]
        B5[Services: Embedding/ChromaDB]
        B6[Services: RAG]
        B7[Services: Generation]
        B8[Services: Analytics/Visualization]
        B9[Services: Reporting/Celery]
        B10[Repositories]
        B11[Models/SQLModel]
        B12[Auth & Permissions]
    end

    subgraph Infra
        I1[PostgreSQL]
        I2[Redis]
        I3[ChromaDB]
        I4[Ollama / LLM]
        I5[Celery Workers]
    end

    subgraph Storage
        S1[Local Filesystem / S3 Abstraction]
    end

    %% Connections
    F1 <-->|HTTP, WS| B1
    B1 <-->|SQL, queries| I1
    B1 <-->|Cache, tasks| I2
    B1 <-->|Vector store, embeddings| I3
    B1 <-->|Generate, embed| I4
    B1 <|||S1| File storage
    B5 <|||I3| ChromaDB operations
    B9 <|||I2| Celery Beat
    B9 <|||I5| Celery Workers