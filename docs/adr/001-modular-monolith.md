# ADR-001: Modular Monolith Architecture

**Status**: Accepted  
**Date**: 2026-11-17  
**Decision**: The SmartWork AI MVP will be implemented as a modular monolith rather than microservices. All components (frontend, backend, database, caching, AI pipeline) reside in a single deployable unit with clear internal module boundaries.

**Context**: A microservices architecture would introduce unnecessary complexity for an MVP, requiring infrastructure (service discovery, inter-service communication, distributed tracing) that delays value delivery. The modular monolith allows shared domain models, in-process calls, and simpler deployment while maintaining clean boundaries for future evolution.

**Consequences**:
- ✅ Simpler deployment (single Docker Compose stack)
- ✅ Faster development (no inter-service RPC overhead)
- ✅ Easier debugging (single log context)
- ⚠️ Must enforce module boundaries to prevent circular dependencies
- ⚠️ Scaling requires scaling the entire monolith (acceptable for MVP)

**Related**: `docs/architecture.md`, `compose.yaml`