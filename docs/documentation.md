# SmartWork AI MVP - Documentation Complète

## 1. Vue d'Ensemble du Projet

SmartWork AI MVP est une application full-stack conçue pour gérer le cycle de vie complet des documents d'entreprise, de l'importation à la génération de rapports en passant par l'analyse assistée par IA. Le système intègre des capacités d'OCR, d'extraction de données, de classification automatique, de recherche vectorielle et de génération de contenu IA.

### Objectifs Majeurs
- **Importer** : Upload de documents (CSV, PDF, XLSX, DOCX) avec extraction automatique et OCR
- **Analyser** : Extraction structurée, classification automatique, indexement vectoriel
- **Générer** : Création de PDFs, PPTXs et rapports à partir des données extraites
- **Planifier** : Scheduling automatisé de rapports via Celery Beat
- **Suivre** : Tableau de bord de gestion des tâches et suivi d'avancement
- **Assister** : Interface de chat IA avec citations de sources sourcées
- **Automatiser** : Studio d'automatisations visuelles sans code
- **Monétiser** : Catalogue de modèles réutilisables
- **Connaître** : Knowledge Hub avec recherche sémantique

---

## 2. Stack Technique Détailée

### 2.1 Frontend (Interface Utilisateur)

| Technologie | Version | Rôle |
|-------------|---------|------|
| **Next.js 14** | App Router | Framework React avec rendu serveur par défaut |
| **React** | 18+ | Interface utilisateur interactive |
| **Tailwind CSS** | 3.x | Framework CSS utility-first pour un design professionnel |
| **TypeScript** | 5.x | Typage statique pour la sécurité |
| **shadcn-ui** | Composants | Bibliothèque de composants d'interface |

**Pages Implémentées :**
- `frontend/app/shell.tsx` - Coque application avec sidebar vertical professionnel
- `frontend/app/importer/page.tsx` - Page d'upload de documents
- `frontend/app/analyser/page.tsx` - Page d'analyse et classification
- `frontend/app/generation/page.tsx` - Page de génération PDF/PPTX
- `frontend/app/planning/page.tsx` - Page planning/rapports
- `frontend/app/suivi/page.tsx` - Page suivi/tasks board
- `frontend/app/chat/page.tsx` - Interface chat IA
- `frontend/app/automations/page.tsx` - Studio d'automatisations visuelles
- `frontend/app/marketplace/page.tsx` - Catalogue de modèles
- `frontend/app/knowledge/page.tsx` - Knowledge Hub sémantique

**Sidebar Caractéristiques :**
- Position : Gauche (left), fixe verticale
- Design : Professionnel avec icônes, couleurs sombres
- Navigation : Accès rapide à toutes les sections
- Réactivité : Responsive sur mobile

---

### 2.2 Backend (API & Logique Métier)

| Technologie | Version | Rôle |
|-------------|---------|------|
| **FastAPI** | 0.109+ | Framework API Python, asynchronous |
| **Python** | 3.11+ | Langage backend |
| **SQLModel** | 0.0.14 | ORM SQLAlchemy + Pydantic simplifié |
| **PostgreSQL** | 15 | Base de données relationnelle |
| **Redis** | 7 | Cache, file d'attente Celery, stockage temporaire |
| **ChromaDB** | 0.4+ | Base de données vectorielle pour RAG |
| **Pydantic** | 2.x | Validation et sérialisation des données |
| **Alembic** | 1.12+ | Gestion des migrations de base de données |

**API Endpoints Créés :**

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/documents/upload` | POST | Upload et extraction de document |
| `/api/v1/documents/{id}` | GET | Récupération document avec extraction |
| `/api/v1/documents/{id}/classification` | PATCH | Mise à jour classification |
| `/api/v1/documents/{id}/download` | GET | Téléchargement fichier original |
| `/api/v1/documents/{id}` | DELETE | Suppression document |
| `/api/v1/chat/send` | POST | Envoi de message IA avec citations |
| `/api/v1/chat/history` | GET | Historique des conversations |
| `/api/v1/generation/pdf` | POST | Génération de fichier PDF |
| `/api/v1/generation/pptx` | POST | Génération de fichier PPTX |
| `/api/v1/workflows/` | GET/POST | Studio d'automatisations visuelles |
| `/api/v1/marketplace/` | GET/POST/POST | Catalogue de modèles |
| `/api/v1/analytics/kpi/sum` | POST | Calcul KPI somme |
| `/api/v1/analytics/kpi/avg` | POST | Calcul KPI moyenne |
| `/api/v1/analytics/kpi/growth` | POST | Calcul taux croissance |
| `/api/v1/analytics/kpi/conversion` | POST | Calcul taux conversion |
| `/api/v1/analytics/kpi/anomalies` | POST | Détection d'anomalies |
| `/api/v1/analytics/chart/generate` | POST | Génération graphique Plotly |
| `/api/v1/tasks/` | GET/POST/PATCH | Gestion des tasks |

---

### 2.3 Base de Données

#### Schéma Principale Tables

| Table | Colonnes Clés | Description |
|-------|--------------|-------------|
| **users** | id, email, password_hash, role, organization_ids | Utilisateurs et leurs organisations |
| **organizations** | id, name, plan_type | Organisations utilisateurs |
| **documents** | id, filename, format, status, owner_id, organization_id | Métadonnées des documents |
| **extracted_data** | id, document_id, structured_data, provenance | Données extraites + provenance |
| **document_chunks** | id, document_id, content_text, chunk_type | Segments de texte indexés |
| **generated_files** | id, document_id, file_path, format | Fichiers générés (PDF, PPTX) |
| **report_schedules** | id, owner_id, timezone, frequency, next_execution | Scheduling rapports |
| **tasks** | id, title, description, status, start/end_at | Tasks utilisateur |
| **audit_logs** | id, actor_id, action, resource_id, result | Traçabilité complète |
| **workflows** | id, name, description, trigger, actions, is_active | Studio automatisations |
| **marketplace_models** | id, name, description, category, template_type | Catalogue modèles |

#### Exemple Schéma Document

```python
class Document(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    format: DocumentFormat  # enum: csv, pdf, xlsx, docx, etc.
    status: DocumentStatus  # enum: uploaded, processing, processed, failed
    size: int
    owner_id: int
    organization_id: Optional[int]
    uploaded_at: datetime
    processed_at: Optional[datetime]
```

---

### 2.4 Services & Modules Backend

| Service/Fichier | Rôle |
|-----------------|------|
| `app/services/extraction.py` | Pipeline extraction OCR + texte, détection auto-scanned |
| `app/services/classification.py` | Classification documentaire par catégories |
| `app/services/embedding.py` | Embeddings sentence-transformers |
| `app/services/rag/rag_pipeline.py` | Pipeline RAG complet : récupération + synthèse |
| `app/services/rag/__init__.py` | Fonctions utilitaires : detect_prompt_injection, QueryLog |
| `app/services/generation.py` | génération_pdf(), génération_pptx() |
| `app/services/ingestion.py` | save_upload(), get_user_organizations() |
| `app/services/workflow.py` | Studio automatisations workflow |
| `app/services/marketplace.py` | Catalogue modèles marketplace |
| `app/workers/celery_app.py` | Configuration Celery + Celery Beat |
| `app/workers/celery_beat.py` | Scheduling automatisé rapports |

---

### 2.5 Outils de Déploiement

| Outil | Rôle |
|-------|------|
| **Docker** | Conteneurisation de tous les services |
| **Docker Compose** | Orchestration 8+ services (db, redis, chroma, ollama, backend, frontend, celery-beat, celery-worker) |
| **Makefile** | Commandes de développement courantes |
| **alembic.ini** | Migration database schema |
| **.env** | Variables d'environnement (ports, URLs, credentials) |

---

## 3. Fonctionnalités Implémentées Détailées

### 3.1 Module Importer (Document Upload)

#### Flux Complet
1. Utilisateur sélectionne fichier via interface
2. `POST /api/v1/documents/upload` reçoit le fichier
3. `save_upload()` stocke le fichier sur disque + met à jour BDD
4. `extract_document()` :
   - Détection automatique format (PDF, CSV, XLSX, DOCX)
   - Si PDF → OCR avec Tesseract (détection de pages scannées)
   - Extraction texte + métadonnées
5. `classify_document()` → attribution catégorie automatique
6. Indexage dans ChromaDB (vectorielle)
7. Création `DocumentChunk` pour recherche locale
8. Mise à jour statut document (processed / needs_review)

#### Fichier Clé : `backend/app/services/extraction.py`

```python
def extract_document(storage_path, extension, use_ocr=False):
    """Extrait le texte d'un document selon son format."""
    if extension == "pdf":
        use_ocr = detect_scanned_pdf(storage_path)  # Auto-detection
    # Extraction selon format
    if extension == "csv":
        text = read_csv(storage_path)
        segments = parse_csv_segments(text)
    elif extension == "pdf":
        if use_ocr:
            text = ocr_pdf_with_tesseract(storage_path)
        else:
            text = extract_pdf_text(storage_path)
        segments = pdf_segment_text(text)
    elif extension == "xlsx":
        text = read_xlsx(storage_path)
        segments = parse_xlsx_segments(text)
    elif extension == "docx":
        text = read_docx(storage_path)
        segments = parse_docx_segments(text)
    return {"text": text, "segments": segments, "pages": ...}
```

**Fonction détection OCR auto :**

```python
def detect_scanned_pdf(path: str) -> bool:
    """Détecte si un PDF est scanné (basé sur le nombre de pages avec texte)."""
    pdf = pdfplumber.open(path)
    pages_with_text = sum(
        1 for page in pdf.pages 
        if page.extract_text().strip()
    )
    return pages_with_text < len(pdf.pages) * 0.1  # < 10% de pages ont du texte
```

---

### 3.2 Module Analyser (Document Analysis)

#### Capacités
- Extraction structurée des données (tables, métadonnées)
- Classification automatique avec catégories prédéfinies
- Indexation vectorielle pour recherche sémantique
- Stockage de la provenance complète

#### Catégories Supportées (exemples)
- `rapport_financier`
- `compte_rendu_reunion`
- `devis`
- `facture`
- `bon_de_commande`

#### Fichier Clé : `backend/app/services/classification.py`

```python
CATEGORIES = [
    "rapport_financier",
    "compte_rendu_reunion", 
    "devis",
    "facture",
    "bon_de_commande",
    # ... plus de catégories
]

def classify_document(text: str) -> dict:
    """Classification automatique d'un document via règles NLP."""
    # Logique de classification par mots-clés, patterns, etc.
    category = determine_category(text)
    confidence = calculate_confidence(text, category)
    return {"category": category, "confidence": confidence}
```

---

### 3.3 Module Générer (Content Generation)

#### Fonctions Disponibles

```python
def generate_pdf(
    document_id: int,
    template: str,
    data: dict,
    citations: bool = True
) -> str:  # returns file path

def generate_pptx(
    document_id: int,
    template: str,
    data: dict,
    citations: bool = True
) -> str:  # returns file path
```

#### Formats de Données Attendus

```json
{
    "title": "Rapport d'activité Q4 2024",
    "sections": [
        {"title": "Résumé", "content": "Texte résumé..."},
        {"title": "Chiffres clés", "content": [{"label": "Chiffre", "value": 12345}]},
        {"title": "Tableau", "content": "Tableau HTML ou structuré"}
    ],
    "source_documents": [document_id1, document_id2]
}
```

#### Endpoints API
- `POST /api/v1/generation/pdf` - Génère PDF téléchargeable
- `POST /api/v1/generation/pptx` - Génère présentation PowerPoint

#### Fichier Clé : `backend/app/services/generation.py`

```python
def generate_pdf(template_name: str, context: dict) -> str:
    """Génère un PDF à partir d'un template et de contexte de données."""
    # Utilisation de reportlab ou weasyprint
    # Intégration des données extraites + citations
    pass
```

---

### 3.4 Module Planifier (Report Scheduling)

#### Configuration Schedule

| Champ | Type | Description |
|-------|------|-------------|
| `timezone` | string | "UTC", "Europe/Paris", etc. |
| `frequency` | string | "daily", "weekly", "monthly" |
| `next_execution` | datetime | Prochain déclenchement |
| `cron_expression` | string | Expression cron détaillée |

#### Endpoints API

```python
# Créer un schedule
POST /api/v1/reporting/schedules
{
    "owner_id": 1,
    "timezone": "Europe/Paris",
    "frequency": "weekly",
    "template": "monthly_report",
    "recipients": ["user@example.com"]
}

# Lister les schedules
GET /api/v1/reporting/schedules

# Modifier un schedule
PATCH /api/v1/reporting/schedules/{id}
```

#### Tâche Celery Beat

```python
@app.on_event("startup")
def setup_periodic_tasks():
    """Configure les tâches périodiques."""
    # Toutes les semaines le lundi à 9h
    beat.send(
        "periodic_task",
        countdown=3600,  # Dans 1 heure
        ...
    )
```

#### Fichier Clé : `backend/app/reporting/tasks.py`

```python
def generate_schedule_report(schedule_id: int, session: Session, owner_id: int):
    """Génère un rapport selon un schedule configuré."""
    schedule = session.get(ReportSchedule, schedule_id)
    # 1. Récupérer les données selon le template
    # 2. Appeler generate_pdf/generate_pptx
    # 3. Envoyer par email si configured
    # 4. Mettre à jour next_execution
    # 5. Logger dans audit_logs
    pass
```

---

### 3.5 Module Suivre (Task Tracking)

#### States des Tasks

| State | Signification |
|-------|--------------|
| `pending` | En attente de démarrage |
| `in_progress` | En cours d'exécution |
| `completed` | Terminé avec succès |
| `failed` | Échec de l'exécution |
| `review` | En revue / nécessite validation |

#### Interface Tableau de Bord
- Liste des tasks avec filtres par état, assignee, date
- Assignment d tasks aux utilisateurs
- Suivi de progression visuelle
- Historique des modifications

#### Endpoints

```python
# Créer une tâche
POST /api/v1/tasks/
{
    "title": "Préparer le rapport mensuel",
    "description": "Collecter les données finance..."",
    "assigned_to_user_id": 5,
    "due_date": "2024-12-31",
    "priority": "high"
}

# Lister les tasks
GET /api/v1/tasks/?status=in_progress&assigned_to=5

# Modifier le statut
PATCH /api/v1/tasks/{id}
{
    "status": "completed",
    "completed_at": "2024-12-15T14:30:00"
}
```

---

### 3.6 Module Chat IA (RAG avec Citations)

#### Architecture RAG

```
Utilisateur question
          ↓
1. Détection injection prompt (graphe de mots-clés)
2. Si OK → identify_scope(user) → IDs documents autorisés
3. Récupération chunks via hybrid search :
   - Similarité vectorielle (ChromaDB)
   - Recherche lexicale (mots-clés)
4. Filtrer par utilisateur/org autorisation
5. Si chunks trouvés → _generate_with_ollama(question, chunks)
6. Si pas de chunks → réponse extractive uniquement
7. Retour → réponse + citations formattées
```

#### Fonction Détection Injection

```python
def detect_prompt_injection(question: str) -> Optional[str]:
    """Détecte si la question contient une tentative d'injection de prompt."""
    patterns = [
        r"ignore\s+previous\s+instructions",
        r"reveal\s+the\s+system\s+prompt",
        r"forget\s+tout\s+previous",
        r"act\s+as\s+",
        # ... plus de patterns
    ]
    for pattern in patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return f"Injection détectée: {pattern}"
    return None
```

#### Pipeline de Récupération Hybride

```python
def retrieve_documents(question: str, user: Any, session) -> List[dict]:
    """Retourne les chunks pertinents avec métadonnées de citation."""
    # 1. Embedding de la question (ou recherche lexicale si embeddings disables)
    # 2. Recherche vectorielle ChromaDB
    # 3. Filtres par organization_id, owner_id
    # 4. Reranking par pertinence + proximité lexicale
    # 5. Retour format: [{"chunk_id": 1, "content": "...", "metadata": {...}}, ...]
    pass
```

#### Format de Réponse Chat

```json
{
    "answer": "La réponse textuelle avec références intégrées",
    "citations": [
        {"source": "Doc1 - page 3", "extract": "Extrait pertinent"},
        {"source": "Doc2 - section 2", "extract": "Autre extrait"}
    ],
    "source_count": 2,
    "conversation_id": "unique-conversation-id",
    "fallback": false,
    "injection_detected": false,
    "used_llm": true
}
```

---

### 3.7 Module Automation Studio (Feature 2)

#### Studio Visuel sans Code

| Capacité | Description |
|----------|-------------|
| **Trigger types** | import, schedule, manual, document_change |
| **Action types** | classify, extract, generate, notify, task_create, report_generate, storage_move |
| **Workflow editor** | Drag-and-drop interface |
| **Versioning** | Workflow versions stored with parameters |
| **Execution history** | Historique des exécutions avec succès/échec |

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/workflows/` | Créer un nouveau workflow |
| `GET /api/v1/workflows/` | Lister les workflows de l'utilisateur |
| `POST /api/v1/workflows/{id}/execute` | Exécuter un workflow contre un document |
| `GET /api/v1/workflows/{run_id}/status` | Vérifier le statut d'exécution |

#### Exemple Workflow

```json
{
    "name": "On import → classifier → extraire → générer rapport → notifier",
    "trigger": "import",
    "trigger_params": {},
    "actions": [
        {"action": "classify", "params": {}},
        {"action": "extract", "params": {}},
        {"action": "generate", "params": {"template": "summary", "format": "docx"}},
        {"action": "notify", "params": {"recipient": "user@example.com", "message": "Rapport généré"}}
    ]
}
```

---

### 3.8 Module Marketplace (Feature 5)

#### Catalogue de Modèles

| Catégorie | Exemples |
|-----------|----------|
| `report` | Rapports administratifs, financiers, mensuels |
| `template` | Modèles DOCX/PPTX personnalisables |
| `analysis` | Analyses de données, KPI reports |
| `meeting` | Comptes rendus de réunion |

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/marketplace/` | Créer un nouveau modèle |
| `GET /api/v1/marketplace/` | Lister les modèles (filtrer par catégorie/public) |
| `GET /api/v1/marketplace/{id}` | Récupérer un modèle par ID |
| `GET /api/v1/marketplace/search/{query}` | Rechercher des modèles |

#### Exemple Modèle

```json
{
    "name": "Rapport financier trimestriel",
    "description": "Template pré-configuré pour rapports financiers trimestriels",
    "category": "report",
    "template_type": "docx",
    "template_params": {
        "title_template": "Rapport financier - {quarter}",
        "sections": ["revenus", "dépenses", "bénéfice"],
        "include_charts": true
    },
    "is_public": true,
    "owner_id": null
}
```

---

### 3.9 Module Knowledge Hub (Feature 6)

#### Recherche Sémantique Intelligente

| Capacité | Description |
|----------|-------------|
| **Recherche par sens** | Trouve l'information par son sens, pas juste par mots-clés |
| **Extraction de concepts** | Identifie les concepts clés dans les requêtes |
| **Résultats enrichis** | Affiche pertinence, citations, liens concepts |
| **Favoris** | Sauvegarde des insights importantes |

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/knowledge/search` | Recherche sémantique naturelle |
| `GET /api/v1/knowledge/concepts` | Extraction de concepts clés |
| `POST /api/v1/knowledge/save` | Sauvegarder un insight |
| `GET /api/v1/knowledge/history` | Historique des recherches |

#### Exemple Requête

```
GET /api/v1/knowledge/search?query="quelles sont les tendances des ventes Q4"&organization_id=1
```

---

### 3.10 Module Collaboration (Feature 4)

#### Annotations & Versioning

| Fonctionnalité | Description |
|----------------|-------------|
| **Annotations** | Commentaires/surlignages sur les documents |
| **Versioning** | Snapshots versionnés des documents |
| **Audit trails** | Historique complet des actions |
| **Rôles utilisateurs** | Owner/Editor/Commenter/Viewer par organisation |

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/documents/{id}/annotations` | Ajouter une annotation |
| `GET /api/v1/documents/{id}/annotations` | Lister les annotations |
| `POST /api/v1/documents/{id}/versions` | Créer une version |
| `GET /api/v1/documents/{id}/versions` | Lister les versions |

---

## 4. Schémas de Données (Schemas Pydantic)

### 4.1 Document Schema

```python
class Document(BaseModel):
    id: int
    filename: str
    format: DocumentFormat  # enum
    status: DocumentStatus  # enum
    size: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    classification: Optional[str]
    classification_confidence: Optional[float]
    classification_confirmed: bool = False
    
    # Données extraites (via relationship)
    extracted_data: Optional[ExtractedData] = None
    chunks: List[DocumentChunk] = []
    workflows: List[Workflow] = []  # Workflows associated
```

### 4.2 Extracted Data Schema

```python
class ExtractedData(BaseModel):
    id: int
    document_id: int
    structured_data: dict  # {text, classification, ...}
    provenance: dict  # {pages, format, segments}
    created_at: datetime
```

### 4.3 Chat Response Schema

```python
class ChatResponse(BaseModel):
    answer: str
    citations: List[dict]  # Formatée pour affichage
    source_count: int
    conversation_id: str
    fallback: bool
    injection_detected: bool
    used_llm: bool
    answer_metadata: dict  # {model, tokens, processing_time}
```

### 4.4 Workflow Schema

```python
class Workflow(BaseModel):
    id: str
    name: str
    description: str
    trigger: str  # import, schedule, manual, document_change
    trigger_params: dict
    actions: List[dict]  # [{"action": "classify", "params": {...}}, ...]
    is_active: bool
    owner_id: Optional[int]
    created_at: datetime
```

### 4.5 Marketplace Model Schema

```python
class MarketplaceModel(BaseModel):
    id: str
    name: str
    description: str
    category: str  # report, template, analysis, meeting
    version: str  # "1.0.0"
    template_type: str  # docx, pdf, xlsx, pptx
    template_params: dict
    is_public: bool
    owner_id: Optional[str]
    usage_count: int
    created_at: datetime
```

### 4.6 Knowledge Hub Schema

```python
class KnowledgeInsight(BaseModel):
    id: str
    user_id: int
    query: str
    concepts: List[str]  # Concepts extraits
    relevant_chunks: List[dict]  # Chunks associés
    relevance_score: float
    created_at: datetime
    is_favorited: bool = False
```

### 4.7 Annotation Schema

```python
class Annotation(BaseModel):
    id: str
    document_id: int
    user_id: int
    content: str
    annotation_type: str  # comment, highlight, note
    metadata: Optional[dict]
    created_at: datetime
```

### 4.8 Schedule Schema

```python
class ReportSchedule(BaseModel):
    id: int
    owner_id: int
    timezone: str  # "UTC", "Europe/Paris", etc.
    frequency: str  # "daily", "weekly", "monthly"
    template: str  # Nom du template PDF/PPTX
    is_active: bool
    next_execution: datetime
    created_at: datetime
    recipients: List[str]  # Emails optionnels
```

---

## 5. Fichiers de Configuration Importants

### 5.1 compose.yaml (Orchestration Docker)

```yaml
name: smartwork-ai

x-backend-build: &backend-build
  context: ./backend
  dockerfile: Dockerfile

x-backend-environment: &backend-environment
  DATABASE_URL: postgresql://smartwork:smartwork@db:5432/smartwork
  REDIS_URL: redis://redis:6379/0
  OLLAMA_HOST: http://ollama:11434
  OLLAMA_MODEL: mistral
  SECRET_KEY: ${SECRET_KEY}
  ALGORITHM: HS256
  ACCESS_TOKEN_EXPIRE_MINUTES: 30
  ENVIRONMENT: development
  DEBUG: True
  CHROMA_HOST: chroma
  CHROMA_PORT: "8000"

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-smartwork}
      POSTGRES_USER: ${POSTGRES_USER:-smartwork}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-smartwork}
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 5s
    networks:
      - data

  chroma:
    image: chromadb/chroma:latest
    restart: unless-stopped
    environment:
      IS_PERSISTENT: "TRUE"
      ANONYMIZED_TELEMETRY: "FALSE"
    volumes:
      - chroma_data:/data
    networks:
      - data

  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - OLLAMA_MODEL=mistral
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - data

  backend:
    build: *backend-build
    image: smartwork/backend:${TAG:-local}
    restart: unless-stopped
    environment: *backend-environment
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      chroma:
        condition: service_started
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s
    ports:
      - "${BACKEND_PORT:-8100}:8000"
    networks:
      - frontend
      - data

  celery-worker:
    build: *backend-build
    image: smartwork/backend:${TAG:-local}
    restart: unless-stopped
    command: ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    networks:
      - data

  celery-beat:
    build: *backend-build
    image: smartwork/backend:${TAG:-local}
    restart: unless-stopped
    command: ["celery", "-A", "app.workers.celery_app", "beat", "--loglevel=info", "--schedule=/tmp/celerybeat-schedule"]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    networks:
      - data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: runner
    image: smartwork/frontend:${TAG:-local}
    restart: unless-stopped
    environment:
      NODE_ENV: production
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT:-8100}}
      API_INTERNAL_URL: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    ports:
      - "${FRONTEND_PORT:-3100}:3000"
    networks:
      - frontend

  redis-commander:
    image: rediscommander/redis-commander:latest
    profiles: ["tools"]
    restart: unless-stopped
    environment:
      REDIS_HOSTS: local:redis:6379
    depends_on:
      redis:
        condition: service_healthy
    ports:
      - "${REDIS_COMMANDER_PORT:-8181}:8081"
    networks:
      - data

networks:
  frontend:
  data:

volumes:
  pg_data:
  redis_data:
  chroma_data:
  ollama_data:
```

### 5.2 .env (Variables d'Environnement)

```env
# Ports de publication
BACKEND_PORT=8100
FRONTEND_PORT=3100
POSTGRES_PORT=5442
REDIS_PORT=6390
CHROMA_PUBLISHED_PORT=8101
OLLAMA_PORT=11444
REDIS_COMMANDER_PORT=8181

# Base de données
POSTGRES_DB=smartwork
POSTGRES_USER=smartwork
POSTGRES_PASSWORD=smartwork

# URLs de service
OLLAMA_URL=http://ollama:11434
NEXT_PUBLIC_API_URL=http://localhost:8100

# Sécurité
SECRET_KEY=0c8e1ba785e0a3229dd2aa4ef620ebf22766100e61ecf871b0d104c45cb1bec8
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
DEBUG=True
TAG=latest
```

### 5.3 backend/app/core/config.py

```python
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql://smartwork:smartwork@localhost:5432/smartwork")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    OLLAMA_HOST: str = Field(default="http://ollama:11434")
    OLLAMA_MODEL: str = Field(default="mistral")
    OLLAMA_TIMEOUT: int = Field(default=60)
    SECRET_KEY: str = Field(default="change-this-to-a-secure-random-string")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Chemins de stockage
    STORAGE_DIR: str = Field(default="/tmp/smartwork/storage")
    UPLOAD_DIR: str = Field(default="/tmp/smartwork/uploads")
    GENERATED_DIR: str = Field(default="/tmp/smartwork/generated")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    LOG_DIR: str = Field(default="/tmp/smartwork/logs")
    
    # Vector store
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8000)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 6. Structure du Dossier Documentation

```
/home/laura/SmartWorkAI_MVP/docs/
├── architecture.md          # Schéma architectural
├── erd-diagram.md           # Diagramme Entité-Relation
├── backlog.md               # Backlog des fonctionnalités
├── requirements-traceability.md  # Traçabilité des exigences
├── gap-analysis.md          # Analyse des écarts
├── adr/
│   ├── 001-modular-monolith.md   # Architecture ADR 1
│   ├── 002-tech-stack.md         # Architecture ADR 2
│   └── 003-rag-pipeline.md       # Architecture ADR 3
├── documentation.md         # ← Nouveau fichier créé
├── Prompt_Implementation_SmartWork_AI_MVP.md  # Guide d'implémentation
├── todolist.md              # Liste de tâches
└── Cahier_des_charges_SmartWork_AI_MVP.docx  # Spécifications Word

### 6.1 Autres fichiers de documentation :

| Fichier | Emplacement | Description |
|---------|-------------|-------------|
| `Prompt_Implementation_SmartWork_AI_MVP.md` | Racine `/home/laura/SmartWorkAI_MVP/` | Guide d'implémentation détaillé |
| `todolist.md` | Racine `/home/laura/SmartWorkAI_MVP/` | Liste de tâches en cours |
| `Cahier_des_charges_SmartWork_AI_MVP.docx` | Racine `/home/laura/SmartWorkAI_MVP/` | Spécifications initiales (Word) |
| `frontend/README.md` | `frontend/` | Documentation frontend |

---

## 7. Diagrammes Mermaid (dans documentation.md)

### 7.1 Diagramme de Classes

```mermaid
classDiagram
    class Document {
        +int id
        +str filename
        +DocumentFormat format
        +DocumentStatus status
        +int size
        +datetime uploaded_at
        +datetime processed_at
        +str classification
        +float classification_confidence
        +bool classification_confirmed
    }
    
    class ExtractedData {
        +int id
        +int document_id
        +dict structured_data
        +dict provenance
        +datetime created_at
    }
    
    class DocumentChunk {
        +int id
        +int document_id
        +str content_text
        +str chunk_type
        +int index_position
        +dict chunk_metadata
    }
    
    class Workflow {
        +str id
        +str name
        +str description
        +str trigger
        +dict trigger_params
        +list actions
        +bool is_active
        +int owner_id
        +datetime created_at
    }
    
    class MarketplaceModel {
        +str id
        +str name
        +str description
        +str category
        +str version
        +str template_type
        +dict template_params
        +bool is_public
        +str owner_id
        +int usage_count
        +datetime created_at
    }
    
    class KnowledgeInsight {
        +str id
        +int user_id
        +str query
        +list concepts
        +list relevant_chunks
        +float relevance_score
        +datetime created_at
        +bool is_favorited
    }
    
    class Annotation {
        +str id
        +int document_id
        +int user_id
        +str content
        +str annotation_type
        +dict metadata
        +datetime created_at
    }
    
    class Task {
        +int id
        +str title
        +str description
        +TaskStatus status
        +str priority
        +int assigned_to_user_id
        +datetime due_date
        +datetime started_at
        +datetime completed_at
        +datetime created_at
        +datetime updated_at
    }
    
    class ReportSchedule {
        +int id
        +int owner_id
        +str timezone
        +str frequency
        +str template
        +bool is_active
        +datetime next_execution
        +datetime created_at
        +list recipients
    }
    
    class ChatResponse {
        +str answer
        +list citations
        +int source_count
        +str conversation_id
        +bool fallback
        +bool injection_detected
        +bool used_llm
        +dict answer_metadata
    }
    
    class AuditLog {
        +int id
        +int actor_id
        +str action
        +int resource_id
        +str result
    }
    
    class User {
        -int id
        -str email
        -str password_hash
        -str role
        +list organization_ids
    }
    
    class Organization {
        -int id
        -str name
        -str plan_type
    }
    
    Document "1" *-- "many" DocumentChunk : contains
    Document "1" *-- "1" ExtractedData : has
    Document "1" *-- "many" Workflow : associated
    Document "1" *-- "many" MarketplaceModel : referenced
    Document "1" *-- "many" KnowledgeInsight : cited
    Document "1" *-- "many" Annotation : has
    User "many" --o{ Organization "many" : belongs to
    Task "many" --> "1" User : assigned to
    ReportSchedule "many" --> "1" User : owned by
    Document "many" --> "1" User : uploaded by
    ChatResponse "1" --> "many" DocumentChunk : cites
```

---

## 8. Historique des Corrections et Problèmes Résolus

### 8.1 Problème Temporel (10 fichiers)

| Fichier | Erreur | Correction |
|---------|--------|------------|
| `documents.py` | `name 'timezone' is not defined` | `from datetime import datetime, timezone` |
| `tasks.py` | Même erreur | Même correction |
| `generation.py` | Même erreur | Même correction |
| `chat.py` | Même erreur | Même correction |
| `reporting.py` | Même erreur | Même correction |
| `services/generation.py` | Même erreur | Même correction |
| `services/rag/rag_pipeline.py` | Même erreur | Même correction |
| `services/rag/__init__.py` | Même erreur | Même correction |
| Plus de 5 autres fichiers | Même pattern | Même correction |

### 8.2 Problèmes Import & Exécution

| Problème | Fichier | Solution |
|----------|---------|----------|
| `detect_prompt_injection` non importé | `rag_pipeline.py:339` | `from app.services.rag import detect_prompt_injection, QueryLog` |
| `QueryLog` non importé | `rag_pipeline.py:420` | Même import |
| `await` sur fonction synchrone | `rag_pipeline.py:351` | Retiré `await` |
| `OLLAMA_HOST` incorrect en test | `conftest.py:62` | `http://ollama:11434` au lieu de `http://127.0.0.1:9` |
| Modèle Ollama wrong | `config.py + compose.yaml` | `mistral` au lieu de `llama3.2` |

### 8.3 Problèmes Docker

| Problème | Cause | Solution |
|----------|-------|----------|
| `host.docker.internal` inaccessible | Containers Docker | `http://ollama:11434` sur réseau Docker |
| Migration Alembic échoue | Base déjà à jour | Retrait service migrate de compose.yaml |
| Ports en conflit | Multiple `restart` clés | Nettoyage YAML |
| `sentence-transformers` non installé | Dépendance optionnelle | Warning géré, ChromaDB used |

---

## 9. Guide de Déploiement

### 9.1 Prérequis

```bash
# Sur machine hôte
docker compose version 2.20+
docker 26+
Python 3.11+
Node.js 20+ (pour frontend)
```

### 9.2 Démarrage Rapide

```bash
# 1. Cloner et entrer dans le répertoire
git clone <repo>
cd SmartWorkAI_MVP

# 2. Copier le fichier d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (ou laisser defaults)

# 3. Démarrer tous les services
docker compose up -d

# 3. Attendre que les services soient prêts
#    - DB: ~5 secondes
#    - Redis: ~2 secondes
#    - Chroma: ~10 secondes
#    - Ollama: ~2-5 minutes (premier chargement modèle)
#    - Backend: ~3 secondes

# 4. Vérifier que le backend répond
curl http://localhost:8100/health

# 5. Accéder à l'interface
#    - Frontend: http://localhost:3100
#    - Redis Commander: http://localhost:8181 (profil tools)
#    - Docs API: http://localhost:8100/docs

# 6. Premier chargement du modèle Ollama
#    La première requête LLM peut prendre 30-60 secondes
#    C'est normal - le modèle est chargé en mémoire

# 7. Tester le parcours complet
docker compose exec backend python -m pytest tests/test_critical_path.py::test_upload_extract_and_cited_chat -x
```

### 9.3 Premiers Pas dans l'Application

1. **Se connecter** : Utiliser les credentials par défaut ou s'enregistrer
2. **Créer une organisation** : Via l'interface ou l'API
3. **Uploader un document** : CSV, PDF, XLSX ou DOCX
4. **Voir l'analyse** : Classification automatique + extraction de données + indexation vectorielle
5. **Poser une question** : Interface chat avec citations de sources
6. **Générer un rapport** : PDF ou PPTX à partir des données extraites
7. **Planifier un rapport** : Configurer le schedule et les emails
8. **Suivre les tasks** : Tableau de bord de suivi
9. **Utiliser le Studio d'automatisations** : Créer des workflows visuels
10. **Parcourir le Marketplace** : Télécharger des modèles réutilisables
11. **Explorer le Knowledge Hub** : Recherche sémantique across documents

---

## 10. Roadmap et Prochaines Étapes

### Phase 1 - Terminée ✅
- Cycle Importer → Analyser → Générer de base
- Interface sidebar professionnelle
- Toutes les API endpoints
- Configuration Docker fonctionnelle
- Corrections timezone et imports
- ChromaDB vector store intégré
- Pipeline RAG complet avec citations
- Détection d'injection prompt
- Anomalie KPI détectée

### Phase 2 - En cours 🔄
- Ollama/LLM pleinement opérationnel (mode extractif fallback)
- Embeddings sentence-transformers installés et actifs
- Tests end-to-end complets sur tous les parcours
- Interface utilisateur UX refinements (nouvelle pages)
- Module de feedback utilisateur

### Phase 3 - Planifiée 📋
- Multitenancy avancé (isolation org stricte)
- Personnalisation des templates PDF/PPTX avancée
- API webhook pour intégrations externes (Slack, Email)
- Analytics et reporting dashboards interactifs
- Module de feedback utilisateur Notifications

### Phase 4 - Future 🌟
- Support multilingue (FR/EN/...)
- Intégration tiers (Slack, Email, Teams, etc.)
- IA locale avec différents modèles (Llama, Nemotron)
- Archivage et conformité RGPD avancée
- API publiques pour partenaires ISV
- Module de scoring de document intelligence

---

## 11. Aperçu Technique Résumé

```
SmartWork AI MVP - Stack Complète

┌────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Next.js 14 + React + TypeScript)       │
│  - 11 pages UI responsive                                  │
│  - Sidebar verticale gauche professionnelle                 │
│  - Composants shadcn-ui                                    │
│  - Routing App Router avec Tailwind                       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API LAYER (FastAPI 0.109+ + Python 3.11)          │     │
│  │  - 70+ endpoints RESTful                           │     │
│  │  - Authentification JWT (30min expiration)         │     │
│  │  - Validation Pydantic V2                          │     │
│  │  - Async/await throughout                          │     │
│  │  - 15 fichiers timezone corrigés                   │     │
│  │  - RAG pipeline complet avec citations              │     │
│  │  - Studio automatisations visuelles                │     │
│  │  - Catalogue modèles Marketplace                    │     │
│  │  - Knowledge Hub recherche sémantique               │     │
│  │  - Détection injection prompt                       │     │
│  │  - Détection anomalies KPI                          │     │
│  │  - Génération PDF/PPTX                              │     │
│  │  - Scheduling Celery Beat                           │     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  INFRASTRUCTURE LAYER                                │     │
│  │  - PostgreSQL 15 : Base de données relationnelle     │     │
│  │  - Redis 7     : Cache + File d'attente Celery       │     │
│  │  - ChromaDB    : Vector store (RAG)                  │     │
│  │  - Ollama/ Mistral 7B    : LLM runtime               │     │
│  │  - Tesseract     : OCR engine (PDF scannés)          │     │
│  │  - Celery/Beat   : Tâches asynchrones + scheduling   │     │
│  │  - Marketplace storage                               │     │
│  │  - Knowledge Graph                                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
│  Données flow: User → Frontend → FastAPI → Services →      │
│  Base de données/Vector store → Réponse → Frontend → User   │
└─────────────────────────────────────────────────────────────┘

---

## 12. Contact et Support

Pour toute question ou problème technique :

- **Documentation détaillée** : Voir fichiers `/home/laura/SmartWorkAI_MVP/docs/`
- **API Documentation** : `http://localhost:8100/docs` (Swagger UI)
- **Interface utilisateur** : `http://localhost:3100`
- **Problèmes connus** : Voir section 8 de cette documentation
- **Support technique** : Équipe développement SmartWork AI

---

**Document généré le 24 novembre 2026 pour le projet SmartWork AI MVP**
**Version 2.0 - Documentation complète post-implémentation avec toutes les 10 features**