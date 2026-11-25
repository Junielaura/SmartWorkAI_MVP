# SmartWork AI MVP - Requirements Traceability Matrix

| ID | Requirement | Module | Priority | Dependencies | Files Concerned | Tests | Status |
|----|-------------|--------|----------|--------------|-----------------|-------|--------|
| REQ-01 | Compte/utilisateur avec authentification | Module 6 | Critical | — | backend/app/models/user.py, backend/app/auth.py, frontend/app/login.page | Unit tests for auth, integration test login/logout | pending |
| REQ-02 | Importation de documents (PDF, DOCX, XLSX, CSV) | Module 1 | Critical | REQ-01 | backend/app/services/ingestion.py, backend/app/services/extraction.py, frontend/app/documents/page.tsx | `tests/test_critical_path.py`, `tests/test_extraction.py` (upload CSV/DOCX/XLSX/PDF, extension invalide) | done |
| REQ-03 | Extraction du texte, tableaux et métadonnées par format | Module 1 | Critical | REQ-02 | backend/app/services/extraction.py, extraction_pdf.py, extraction_docx.py, extraction_xlsx.py | `tests/test_extraction.py` (PDF page, DOCX paragraphe/table, XLSX feuille, CSV) | done (OCR non validé) |
| REQ-04 | Classification assistée des documents | Module 1 | High | REQ-03 | backend/app/services/classification.py, frontend/app/documents/page.tsx | `tests/test_extraction.py`, `tests/test_critical_path.py` (facture, correction utilisateur) | done |
| REQ-05 | Découpage en chunks et indexation vectorielle | Module 1 | Critical | REQ-04 | backend/app/services/embedding.py, compose.yaml (service chroma) | Chunks with metadata, stable IDs, filterable metadata, reindexation | pending |
| REQ-06 | Assistant RAG avec réponses sourcées | Module 1/5 | Critical | REQ-05 | backend/app/services/rag/rag_pipeline.py, backend/app/api/v1/chat.py, frontend/app/chat/page.tsx | `tests/test_critical_path.py` (citations PDF/feuille, isolation, injection) | partial (retrieval lexical, LLM Ollama optionnel) |
| REQ-07 | Génération de documents (DOCX, PDF, XLSX) | Module 2 | Critical | REQ-03 | backend/app/services/generation.py, frontend/app/generation.component | Rapport synthétique modifiable, conformité modèle, données numériques non estimées, fichier lisible et régénérable | done |
| REQ-08 | Génération de visualisations (Plotly) | Module 3 | High | REQ-03 | backend/app/analytics/visualization.py, frontend/app/dashboard.component | KPI attendus, filtres, dates, valeurs nulles, export PDF/XLSX, isolation données | done |
| REQ-09 | Rapports périodiques (quotidien/hebdomadaire) | Module 4 | High | REQ-01, REQ-07 | backend/app/workers/celery_app.py, backend/app/reporting/tasks.py, backend/app/schemas/report_schedule.py, backend/api/v1/reporting.py, compose.yaml | Déclenchement simulé, fuseau horaire, idempotence, échec/reprise, validation, permissions, historique | done |
| REQ-10 | Assistant conversationnel avec mémoire limitée | Module 5 | High | REQ-06 | backend/app/services/chat.py, frontend/app/chat.interface | Contexte utilisateur limité, droits appliqués, réponse absente/ambiguë, signalement, journalisation des requêtes | done |
| REQ-11 | Gestion des tâches et historique | Module 6 | Medium | REQ-01 | backend/app/models/task.py, backend/app/api/v1/tasks.py, backend/app/services/notifications.py, backend/app/models/audit_log.py | Tâche avec responsable/statut/historique, actions sensibles journalisées, utilisateurs voient seulement autorisés | done |
| REQ-12 | Sécurité et contrôle d'accès par organisation | Module 1-6 | Critical | REQ-01 | backend/app/core/security.py, backend/app/api/v1/tasks.py | Séparation organisations, accès refusé sans permission, injection de prompt, fichiers malformés | done |
| REQ-13 | Traçabilité complète (provenance, versions, validations) | Module 1-6 | Critical | REQ-01, REQ-03 | backend/app/models/audit_log.py, backend/app/models/document_version.py | Migrations base vide/base existante, audit logs complets | done |
| REQ-14 | Interface utilisateur responsive (Next.js + Tailwind) | Frontend | Critical | REQ-01, REQ-02, REQ-06 | frontend/app/, frontend/components/ | `tsc --noEmit`, pages /documents et /chat | partial (upload + chat ; génération/rapports absents) |
| REQ-15 | Architecture modulaire et maintenable | Infrastructure | Critical | — | backend/app/, infra/, docs/adr/ | Lint, formatage, typage, analyse dépendances, tests unitaires/integration/E2E | pending |

**Legend:**
- **Critical**: Essential for MVP delivery
- **High**: Important for MVP, may be deferred if time-boxed
- **Medium**: Useful but not essential for initial MVP