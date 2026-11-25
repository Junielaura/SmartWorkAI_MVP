# ADR-003: RAG Pipeline Approach - Explicit over Framework

**Status**: Accepted  
**Date**: 2026-11-17  
**Decision**: The RAG (Retrieval-Augmented Generation) pipeline will be implemented explicitly without the LangChain framework. The pipeline consists of these stages: question → scope identification → authorized retrieval → context ranking/truncation → generation with citations → answer.

**Context**: While LangChain simplifies some RAG patterns, it adds abstraction layers and dependencies that are unnecessary for the MVP. An explicit pipeline gives full control over:
- Permission filtering at the retrieval stage
- Context window management
- Citation formatting and provenance tracking
- Prompt injection protection
- Deterministic behavior for KPI calculations

**Pipeline Details**:
1. **Question preprocessing**: Parse intent, identify user organization scope
2. **Authorized retrieval**: Query ChromaDB with organization filter, apply permission checks
3. **Context ranking**: Re-rank by relevance score, limit by token budget
4. **Context truncation**: Keep only most relevant passages, preserve page/leaf references
5. **Generation**: Construct prompt with system instructions, retrieved context, and user question
6. ** citation injection**: Embed precise source references (document, page, sheet, paragraph) in the response
7. **Answer validation**: Verify claims against context before returning

**Consequences**:
- ✅ Full control over permission filtering and security
- ✅ No framework lock-in, easy to switch vector store or LLM provider
- ✅ Transparent behavior, easier debugging
- ✅ Fine-grained context management for token budget
- ⚠️ More manual implementation (∼200 lines vs ∼50 with LangChain)
- ⚠️ Must re-implement common patterns (prompt templates, document transformers)

**Related**: `docs/architecture.md`, `docs/requirements-traceability.md` (REQ-06)