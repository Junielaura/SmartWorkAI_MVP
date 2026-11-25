# Rapport d'écart — Cahier des charges SmartWork AI MVP

- **Référence** : `Cahier_des_charges_SmartWork_AI_MVP.docx` (v1.0 — MVP)
- **Code audité** : `backend/` (FastAPI), `frontend/` (Next.js), `compose.yaml`, `backend/alembic/`
- **Date** : 19 novembre 2026
- **Méthode** : lecture du code + exécution réelle de l'API (`http://localhost:8100`) avec un compte admin, lecture des logs Docker, inspection du schéma PostgreSQL.

---

## 1. Résumé exécutif

Le projet contient un **squelette cohérent** des six modules (modèles, services, routes, workers, pages), mais **le parcours critique du cahier des charges n'est pas opérationnel** :

> importer un PDF/DOCX/XLSX/CSV → visualiser l'extraction avec provenance → poser une question et obtenir une réponse sourcée.

Sur les endpoints testés en direct :

| Endpoint | Attendu | Résultat réel |
|---|---|---|
| `POST /api/v1/auth/login` | Connexion | **200 OK** |
| `POST /api/v1/documents/upload` | Document traité | **500** |
| `GET /api/v1/documents/{id}` | Extraction + provenance | **500** |
| `POST /api/v1/chat/send` | Réponse sourcée | **500** |
| `POST /api/v1/tasks/` | Tâche créée | **500** |
| `GET /api/v1/reporting/schedules` | Liste des planifications | **500** |
| `POST /api/v1/reporting/schedules` | Planification créée | **500** |
| `POST /api/v1/analytics/profile/{id}` | Profiling | **500** |
| `GET /api/v1/generation/history` | Historique | 200 (vide) |

**Conclusion** : les exigences marquées « done » dans `docs/requirements-traceability.md` (RAG, génération, rapports, tâches, UI) ne sont pas démontrables. Le MVP est à un stade de **prototype partiellement câblé**, pas de version fonctionnelle.

---

## 2. Écarts par module

Légende : ✅ conforme · 🟠 partiel · ❌ absent · 💥 présent mais cassé à l'exécution.

### Module 1 — Importation et compréhension des documents

| Exigence | État | Preuve / écart |
|---|---|---|
| Dépôt PDF, DOCX, XLSX, CSV | 🟠 | Validation d'extension présente (`ingestion.py:20`), mais l'upload échoue : `get_user_organizations` ouvre `Session()` sans moteur (`ingestion.py:82`) → `UnboundExecutionError`. |
| Détection MIME + validation taille/intégrité | 🟠 | Taille et extension vérifiées ; MIME calculé mais **non rejeté** en cas d'incohérence (`ingestion.py:68-70`). |
| Stockage sécurisé | 💥 | `settings.STORAGE_DIR` / `UPLOAD_DIR` / `GENERATED_DIR` **n'existent pas** dans `config.py` → `AttributeError`. |
| Extraction PDF (texte, tableaux, métadonnées) | 💥 | `extraction.py:47` ne route **jamais** vers `extraction_pdf.extract_pdf` ; il renvoie un texte vide avec la note « PyMuPDF non disponible ». |
| OCR pages scannées | ❌ | Code présent (`extraction_pdf.py:87`) mais jamais appelé, et `pytesseract`/`Pillow` absents de `requirements.txt` et du Dockerfile. |
| Extraction DOCX | 🟠 | Fonctionne isolément, mais ne conserve pas de provenance par paragraphe exploitable. |
| Extraction XLSX | 🟠 | `ws.used_range` n'existe pas sur `openpyxl` (`extraction_xlsx.py:61`) → erreur ; les cellules/lignes ne sont pas conservées avec adresse. |
| Extraction CSV | ✅ | Encodages et délimiteurs gérés. |
| Classification assistée + confirmation utilisateur | 🟠 | Classifieur par mots-clés présent ; **aucun endpoint** pour consulter/corriger la catégorie. |
| Découpage + indexation sémantique | ❌ | Aucun chunk n'est persisté dans `document_chunks` ; aucun embedding ; ChromaDB n'est jamais appelé. |
| Gestion des versions, statuts, erreurs, suppression | ❌ | `DocumentVersion` jamais créée ; pas d'endpoint de suppression ; statut bloqué à `uploaded`. |
| Critère : extraction consultable avec provenance | ❌ | `GET /documents/{id}` échoue (`doc.extracted_data` / `doc.chunks` inexistants sur le modèle). |
| Critère : réponses citant pages/feuilles | ❌ | Voir module 5. |

### Module 2 — Génération de documents

| Exigence | État | Preuve / écart |
|---|---|---|
| DOCX | 🟠 | Générateur présent (`generation.py`), jamais validé de bout en bout faute d'extraction. |
| PDF | 🟠 | Conversion via `libreoffice`, **non installé** dans `backend/Dockerfile` → échec garanti. |
| XLSX | 🟠 | Générateur présent, alimenté par des données structurées qui ne sont jamais produites. |
| PPTX | ❌ | Aucun code, `python-pptx` absent des dépendances. |
| Bibliothèque de modèles (rapport, synthèse, note, présentation, suivi) | ❌ | Un seul template DOCX codé en dur. |
| Titres, sommaire, en-têtes/pieds, numérotation | 🟠 | Titres et tableaux seulement ; pas de sommaire, en-têtes, pieds, numérotation. |
| Prévisualisation / édition / régénération | ❌ | Aucune UI ni endpoint de prévisualisation. |
| Traçabilité (sources, modèle, paramètres, auteur) | 🟠 | Champs `generation_params` renseignés, mais permissions de téléchargement erronées (`generation.py:246` compare `document_id` à des IDs d'organisation). |
| Critère : données numériques issues du moteur de calcul | ❌ | La génération recopie du texte extrait ; aucun lien avec les KPI Pandas. |

### Module 3 — Tableaux de bord et visuels

| Exigence | État | Preuve / écart |
|---|---|---|
| Détection colonnes/types/unités/dates/manquants/doublons | 🟠 | `DataProfiling` existe (`kpi_calculator.py:49`) mais n'est jamais alimenté par de vraies données structurées. |
| Proposition d'indicateurs (définition, formule, unité, période) | 🟠 | `KPIResult` porte ces champs ; aucune proposition automatique. |
| Calculs déterministes Pandas/SQL | 🟠 | SUM/AVG/count/growth/conversion codés ; endpoints en **500** car `doc.chunks` n'existe pas (`dashboard.py:45`). |
| Choix de graphiques adaptés | 🟠 | `generate_chart` gère bar/line/pie/histogram/scatter, mais aucun choix automatique. |
| Filtres, regroupements, comparaison de périodes | 🟠 | Filtres simples ; pas de regroupement ni comparaison de périodes. |
| Export PDF/XLSX des résultats | ❌ | Aucun endpoint d'export de dashboard. |
| Enregistrer / réactualiser un dashboard | ❌ | Tables `dashboards` absente du schéma et du code. |
| Critères : définition + provenance, données vérifiables, limites visibles | ❌ | Non démontrable (endpoints cassés, pas d'UI). |

### Module 4 — Rapports périodiques

| Exigence | État | Preuve / écart |
|---|---|---|
| Fréquence, fuseau, période, sources, modèle | 🟠 | Schéma Pydantic présent ; `ReportSchedule` n'a **ni** `organization_id` **ni** `owner_id`, utilisés par l'API (`reporting.py:92`) → 500. |
| Collecte / fraîcheur / complétude | 🟠 | Fonctions présentes mais logique approximative ; `_create_report_draft(report, session)` appelée avec des signatures incompatibles (`reporting.py` vs `tasks.py:307`). |
| Comparaison période précédente + KPI | ❌ | Absent. |
| Brouillon → validation → publication/rejet | 🟠 | Endpoints validate/publish existent ; `report.parameters` n'existe pas sur le modèle → 500 à l'exécution. |
| Notifications responsables + historique | ❌ | `Notification` importé depuis `app.models` **n'existe pas** ; email non implémenté (simulation). |
| Échecs, relances, anti-doublons | 🟠 | Idempotence Redis présente ; workers utilisent une session fermée (`tasks.py:71-80`), génération pointant sur `document_id=report.id`. |
| Critère : sources datées + validation humaine + historique | ❌ | Non démontrable. |

### Module 5 — Assistant conversationnel

| Exigence | État | Preuve / écart |
|---|---|---|
| Questions corpus autorisé + citations | 💥 | `POST /chat/send` → **500** (`asyncio` non importé, `chat.py:33`). |
| Périmètre par droits | 🟠 | Requête d'autorisation correcte dans l'intention, mais `user.get(...)` sur un objet SQLModel (`rag_pipeline.py:100`) → `AttributeError` si on atteint ce code. |
| Synthèse, points clés, comparaison, explication KPI | ❌ | Aucun appel LLM ; le « RAG » fait un matching de mots-clés et recopie des extraits (`rag_pipeline.py:112-170`). |
| Actions contrôlées (générer rapport/tableau) | ❌ | Absent du chat. |
| Mémoire de conversation limitée | 🟠 | `Conversation.context_summary` mis à jour avec la dernière question/réponse ; pas d'historique de messages exploité. |
| Réponse explicite si information absente | ✅ | Message prévu (`rag_pipeline.py:242-248`). |
| Journalisation + signalement | 🟠 | Log fichier (`QueryLog`) et endpoint `/chat/report` ; le signalement n'est pas persisté dans une table dédiée. |
| Critères : références vérifiables, pas d'invention, droits appliqués | ❌ | Pas de génération LLM, donc pas de réponse sourcée au sens du cahier des charges. |

### Module 6 — Tâches, workflows et suivi

| Exigence | État | Preuve / écart |
|---|---|---|
| Historique documents/analyses/rapports/exports | 🟠 | Historique de génération présent ; pas de vue unifiée. |
| Statuts et cycle de vie | 🟠 | Statuts définis ; création de tâche **500** (`notify_task_assigned.delay` sur une fonction simple, `tasks.py:86`). |
| Affectation, échéances, commentaires | 🟠 | Champs présents ; `due_date` reçu en `str` n'est jamais converti en datetime. |
| Notifications in-app/email | ❌ | Notifications poussées dans Redis, jamais lues par le frontend ; table `notifications` absente. |
| Workflows déclenchés | ❌ | Table `workflows` absente, aucune logique de déclenchement. |
| Tableau de suivi + audit | 🟠 | `/tasks/dashboard/overview` répond ; audit partiellement écrit, avec FK `audit_logs.resource_id → documents.id` incorrecte pour les tâches (`alembic/...:114`). |
| Critères : responsable/statut/historique, actions journalisées, isolation | 🟠 | Isolation partielle ; journalisation incomplète (pas de `commit` sur certaines entrées, FK incohérente). |

---

## 3. Écarts transverses

### 3.1 Base de données

Tables du cahier des charges **absentes** du schéma et des modèles :

- `dashboards` (définitions, KPI, filtres, propriétaire)
- `workflows` (déclencheurs, étapes, règles)
- `notifications` (destinataire, contenu, statut de lecture)
- `document_versions` existe mais n'est jamais alimentée
- `extracted_data` et `document_chunks` existent mais ne sont jamais alimentées par l'upload

Le modèle `ReportSchedule` ne contient pas `organization_id`/`owner_id` alors que l'API les utilise ; `Report` n'a pas de champ `parameters`. Ces décalages provoquent des `AttributeError` en production.

### 3.2 Sécurité et gouvernance

- Rôles `Administrateur / Collaborateur / Validateur / Lecteur` : **non implémentés** (simple chaîne `role` non contrôlée).
- Contrôle d'accès : filtrage par organisation présent sur plusieurs endpoints, mais plusieurs vérifications sont erronées (ex. téléchargement de fichiers générés).
- Pas d'antivirus, pas de chiffrement au repos, pas de politique de rétention/suppression.
- Injection de prompt : détection par regex présente ; pas de protection structurelle côté LLM (pas de LLM du tout).
- CORS : `CORS_ORIGINS = []` par défaut, sans variable d'environnement associée.

### 3.3 Exigences non fonctionnelles

| Exigence | État | Écart |
|---|---|---|
| Performance / traitements longs | 🟠 | Celery configuré ; workers instables (session fermée, mauvaises signatures). |
| Traçabilité | ❌ | Provenance non persistée ; versions jamais créées ; audit partiel. |
| Maintenabilité | 🟠 | Architecture modulaire lisible ; aucun test, pas de lint/typage configuré, matrice de traçabilité inexacte. |
| Fiabilité | ❌ | Nombreux 500 sur les parcours nominaux. |
| Accessibilité / ergonomie | 🟠 | UI Tailwind responsive mais très incomplète. |

### 3.4 Frontend

Pages existantes : `/login`, `/inscription`, `/dashboard`, `/documents` (liste seule), `/settings`.
**Absents** : upload, aperçu d'extraction, chat, génération, dashboards, planification de rapports, gestion des tâches. La page `/` est encore le template par défaut de Next.js.

### 3.5 Tests et qualité

- Aucun fichier de test (`pytest` est dans les dépendances mais `tests/` n'existe pas).
- Aucun lint/formatage/typage configuré (pas de `ruff`, `mypy`, `eslint` exécuté en CI).
- Aucune CI.
- Les critères « Tests unitaires et E2E » et « Gate 7 » du cahier des charges ne sont pas satisfaits.

### 3.6 Documentation

`docs/requirements-traceability.md` et `docs/backlog.md` marquent « done » des exigences non fonctionnelles (REQ-06, 07, 08, 09, 10, 11, 12, 13, tâches 15-16, 19-29, 30-38, 40-51, 52-58) sans preuve de test. La matrice doit être considérée comme **non fiable** jusqu'à correction.

---

## 4. Plan de remédiation priorisé

### P0 — Parcours critique (bloquant pour le MVP)

1. **Configuration & stockage** : ajouter `STORAGE_DIR`, `UPLOAD_DIR`, `GENERATED_DIR`, `OLLAMA_MODEL`, `CHROMA_*` ; créer les répertoires au démarrage.
2. **Upload** : session DB correcte, nom de fichier unique, `DocumentVersion`, audit, statuts d'erreur.
3. **Extraction** : router PDF (et OCR optionnel), corriger XLSX, produire des segments avec provenance (page/feuille/paragraphe).
4. **Persistance** : écrire `ExtractedData` et `DocumentChunk` ; exposer `GET /documents/{id}` avec texte, tableaux, chunks et classification ; ajouter `PATCH /documents/{id}/classification`.
5. **RAG** : périmètre par organisation, retrieval sur `document_chunks`, citations page/feuille, synthèse LLM optionnelle (Ollama) avec repli extractif, réponse « information absente ».
6. **Chat** : endpoint fonctionnel, mémoire courte, journalisation, signalement.
7. **UI** : upload + aperçu d'extraction + page de chat avec citations.

### P1 — Modules 2 à 6

8. Génération : PDF (installer LibreOffice ou générateur dédié), PPTX, modèles, prévisualisation, permissions.
9. Dashboards : persistance `dashboards`, export PDF/XLSX, choix de graphiques.
10. Rapports : corriger le schéma `ReportSchedule`/`Report`, notifications, workers Celery, historique.
11. Tâches : corriger `.delay`, FK d'audit, dates, notifications in-app, table `workflows`.
12. Rôles et permissions : appliquer réellement les 4 rôles.

### P2 — Qualité

13. Tests unitaires, intégration et E2E sur les parcours critiques.
14. CI (lint, typage, tests), migrations vérifiées sur base vide et existante.
15. Mise à jour honnête de la matrice de traçabilité avec preuves.

---

## 5. Preuves d'exécution (reproductibles)

```bash
# Connexion
TOKEN=$(curl -s -X POST http://localhost:8100/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@smartwork.ai","password":"Admin1234!"}' \
  | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# Upload (500)
curl -i -X POST http://localhost:8100/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" -F "file=@test.csv"

# Chat (500)
curl -i -X POST "http://localhost:8100/api/v1/chat/send?message=test" \
  -H "Authorization: Bearer $TOKEN"

# Planifications (500)
curl -i http://localhost:8100/api/v1/reporting/schedules \
  -H "Authorization: Bearer $TOKEN"
```

Erreurs observées dans les logs backend :

```
sqlalchemy.exc.UnboundExecutionError: Could not locate a bind configured on mapper Mapper[User(users)] ...
NameError: name 'asyncio' is not defined            # chat.py:33
AttributeError: organization_id                     # reporting.py:92
AttributeError: 'function' object has no attribute 'delay'  # tasks.py:86
sqlalchemy.exc.NoResultFound                        # documents/{id}
NameError: name 'datetime' is not defined
```

---

## 6. Ce qui peut être conservé

- Authentification JWT, création d'organisation, modèle de données de base.
- Structure modulaire (services, routes, workers) et Docker Compose.
- Extracteurs DOCX/XLSX/CSV et générateurs DOCX/XLSX (à fiabiliser).
- Calculs KPI Pandas et génération de figures Plotly (à brancher sur des données réelles).
- Configuration Celery/Redis et idempotence Redis.
- UI Tailwind de base (login, inscription, dashboard, liste documents).

Ces briques constituent une base saine pour reconstruire le parcours critique sans repartir de zéro.

---

## 7. Remédiation P0 — statut après corrections

Le parcours critique a été réparé et vérifié. Les éléments ci-dessous sont désormais fonctionnels.

### 7.1 Corrections apportées

| Élément | Correction |
|---|---|
| Configuration | Ajout de `STORAGE_DIR`, `UPLOAD_DIR`, `GENERATED_DIR`, `LOG_DIR`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `CHROMA_*` et création des répertoires au démarrage (`core/config.py`, `main.py`). |
| Upload | Session DB correcte, nom de fichier unique, validation MIME/taille/extension, `DocumentVersion`, statuts `processing`/`processed`/`needs_review`/`failed`, audit (`services/ingestion.py`, `api/v1/documents.py`). |
| Extraction PDF | Routage effectif vers PyMuPDF, provenance par page, OCR Tesseract activé si le PDF n'a pas de texte (`services/extraction.py`, `extraction_pdf.py`). |
| Extraction DOCX | Paragraphes numérotés et tableaux indexés (`extraction_docx.py`). |
| Extraction XLSX/CSV | Feuilles, en-têtes, lignes et plage conservés ; correction de `used_range` (`extraction_xlsx.py`). |
| Persistance | Écriture de `extracted_data` et `document_chunks` avec métadonnées de provenance (`documents.py`). |
| Consultation | `GET /documents/{id}` retourne texte, tableaux, chunks et provenance ; `PATCH /documents/{id}/classification` permet la correction ; ajout de `GET /documents/{id}/download` et `DELETE /documents/{id}`. |
| RAG | Périmètre par organisation, retrieval sur `document_chunks`, scoring par tokens (accents/stopwords), citations page/feuille/paragraphe, réponse « information absente », détection d'injection, synthèse Ollama optionnelle avec repli extractif (`services/rag/rag_pipeline.py`). |
| Chat | Endpoint `POST /chat/send` fonctionnel (body JSON), mémoire courte (10 messages), historique, signalement (`api/v1/chat.py`). |
| Frontend | Page Documents avec import, aperçu d'extraction, provenance et correction de classification ; page `/chat` avec réponses et citations ; lien « Assistant » dans la navigation. |
| Tests | 10 tests pytest couvrant extraction PDF/DOCX/XLSX/CSV, upload, chat sourcé, absence de fuite inter-organisations, injection de prompt et correction de classification. |

### 7.2 Vérifications exécutées

```text
docker compose run --rm --no-deps backend pytest -q
=> 10 passed

Upload CSV    -> 201, status=processed, chunk_count=1, table détectée
Upload DOCX   -> 201, classification=rapport, chunks=2, table=1
Upload XLSX   -> 201, chunks=1, feuille=Ventes
Upload PDF    -> 201, classification=facture, chunks=1, page=1
Chat PDF      -> citations ["facture.pdf, page 1"]
Chat XLSX     -> citations ["ventes.xlsx, feuille Ventes"]
Chat DOCX     -> citations ["rapport.docx, paragraphe 0", "rapport.docx, tableau 0"]
Frontend      -> /documents, /chat, /dashboard répondent 200 ; `tsc --noEmit` OK
```

### 7.3 Limites restantes du P0

- **LLM local** : la synthèse Ollama est implémentée mais le service Ollama de l'hôte n'écoute que sur `127.0.0.1` et n'est pas joignable depuis le conteneur (`host.docker.internal` → connexion refusée). Le chat fonctionne en mode extractif. Pour activer la synthèse : exposer Ollama sur `0.0.0.0:11434` ou lancer le profil `ai` du compose après avoir téléchargé un modèle.
- **Embeddings/ChromaDB** : non branchés ; le retrieval est lexical. L'indexation vectorielle reste au backlog P1.
- **OCR** : le code et les paquets sont ajoutés, mais l'image Docker doit être reconstruite pour installer `tesseract-ocr` (le build a échoué pour timeout réseau lors de l'audit).
- **PDF scanné** : dépend de Tesseract ; non validé dans cet environnement.
- **Génération PDF/PPTX, dashboards persistés, rapports et tâches** : toujours aux statuts décrits en sections 2 et 4 (P1).
- **Lint frontend** : `tsc` passe ; `eslint` conserve 5 erreurs préexistantes dans `dashboard`, `settings`, `app-shell` et `inscription`, indépendantes du parcours critique.
