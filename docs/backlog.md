# SmartWork AI MVP - Ordered Backlog (Sprint Roadmap)

## Phase 1: Moteur Documentaire (Weeks 1-3)
| # | Task | Module | Priority | Gate |
|---|------|--------|----------|------|
| 1 | Project structure + Docker Compose (frontend, backend, PostgreSQL, Redis, ChromaDB, Ollama) | Infra | Critical | Gate 0 |
| 2 | Base de données : modèles users, organizations, documents (SQLModel + Alembic) | Backend | Critical | Gate 0 |
| 3 | Authentification JWT + gestion des sessions | Backend | Critical | Gate 1 |
| 4 | API d'upload avec validation MIME, extension, taille, intégrité | Backend | Critical | Gate 1 |
| 5 | Stockage sécurisé des fichiers originaux | Backend | Critical | Gate 1 |
| 6 | Extraction PDF (PyMuPDF) : texte, métadonnées, tableaux | Backend | Critical | Gate 2 |
| 7 | Extraction DOCX (python-docx) : paragraphes, titres, tableaux | Backend | Critical | Gate 2 |
| 8 | Extraction XLSX (openpyxl/Pandas) : feuilles, formules, valeurs | Backend | Critical | Gate 2 |
| 9 | Extraction CSV (encodage, séparateur, en-têtes) | Backend | Critical | Gate 2 |
| 10 | OCR Tesseract pour PDF scanné | Backend | High | Gate 2 |
| 11 | Classification assistée (rapport, tableau, compte-rendu, facture) | Backend | High | Gate 2 |
| 12 | Découpage en chunks avec métadonnées de provenance | Backend | Critical | Gate 2 |
| 13 | Service d'embeddings (nomic-embed-text via Ollama/transformers) | Backend | Critical | Gate 2 |
| 14 | Indexation ChromaDB avec métadonnées filtrables | Backend | Critical | Gate 2 |
| 15 | Pipeline RAG : question → périmètre → récupération autorisée → classement → génération → citations → réponse | Backend | Critical | Gate 2 | done |
| 16 | Interface de chat : historique minimal, signalement de réponse | Frontend | Critical | Gate 2 | done |
| 17 | Tests : PDF natif, PDF scanné, DOCX tableau, XLSX multi-feuilles, CSV, invalide, vide, citations, pas de fuite utilisateur | All | Critical | Gate 2 |
| 18 | Gate 2 validation : utilisateur peut importer formats cibles, vérifier extraction, poser questions avec réponses sourcées | — | — | Gate 2 |

## Phase 2: Moteur de Génération (Weeks 4-5)
| # | Task | Module | Priority | Gate | Status |
|---|------|--------|----------|------|--------|
| 19 | Registre de modèles versionnés avec chemins et paramètres | Backend | Critical | Gate 3 | done |
| 20 | Modèle de synthèse/rapport professionnel (DOCX template) | Backend | Critical | Gate 3 | done |
| 21 | Génération DOCX avec python-docx : titres, dates, tableaux, références, en-têtes/pieds, styles | Backend | Critical | Gate 3 | done |
| 22 | Génération PDF : conversion DOCX → PDF ou génération dédiée | Backend | High | Gate 3 | done |
| 23 | Génération XLSX avec openpyxl/Pandas : données structurées, formules | Backend | Critical | Gate 3 | done |
| 24 | Insertion de graphiques Plotly dans DOCX/PDF | Backend | High | Gate 3 | done |
| 25 | Prévisualisation avant génération/download | Frontend | Critical | Gate 3 | done |
| 26 | Historique des fichiers générés avec métadonnées (sources, modèle, auteur, version) | Backend | Critical | Gate 3 | done |
| 27 | Choix de format, modèle et ton (professionnel, académique, administratif, synthétique) | Frontend | Critical | Gate 3 | done |
| 28 | Tests : fichiers ouvrables, contenu non tronqué, tableaux cohérents, métadonnées et sources, droits de téléchargement | All | Critical | Gate 3 | done |
| 29 | Gate 3 validation : génération répétable de livrables valides à partir de données extraites | — | — | Gate 3 | done |

## Phase 3: Moteur de Visualisation (Weeks 6-7)
| # | Task | Module | Priority | Gate | Status |
|---|------|--------|----------|------|--------|
| 30 | Analyse colonnes : types de données, unités, dates, valeurs manquantes | Backend | Critical | Gate 4 | done |
| 31 | Détection doublons et incohérences (sans suppression silencieuse) | Backend | High | Gate 4 | done |
| 32 | Calculs KPI déterministes avec Pandas/SQL (validation, ratio, total) | Backend | Critical | Gate 4 | done |
| 33 | Graphiques Plotly : barres, courbes, secteurs, histogrammes, tableaux | Backend | Critical | Gate 4 | done |
| 34 | Filtres, regroupements, comparaison de périodes | Frontend | Critical | Gate 4 | done |
| 35 | Export PDF/XLSX des résultats de visualisation | Backend | Critical | Gate 4 | - |
| 36 | Affichage provenance et limites (valeurs manquantes, période incomplète, échantillon faible) | Frontend | High | Gate 4 | done |
| 37 | Sauvegarde de dashboard | Backend | High | Gate 4 | done |
| 38 | Tests : jeu de données de référence, calculs attendus, unités, filtres, dates, valeurs nulles, export, isolation données | All | Critical | Gate 4 | done |
| 39 | Gate 4 validation : KPI reproductibles, visuels contrôlables par utilisateur | — | — | Gate 4 | - |

## Phase 4: Rapports Quotidiens et Hebdomadaires (Weeks 8-9)
| # | Task | Module | Priority | Gate | Status |
|---|------|--------|----------|------|--------|
| 40 | Configuration Celery + Redis + Celery Beat | Infra | Critical | Gate 5 | done |
| 41 | Tâches idempotentes : même échéance → pas de doublons | Backend | Critical | Gate 5 | done |
| 42 | Choix sources, période, fréquence, fuseau horaire, modèle, destinataires | Frontend | Critical | Gate 5 | done |
| 43 | Contrôle fraîcheur et complétude des sources avant génération | Backend | Critical | Gate 5 | done |
| 44 | Génération brouillon rapport (status draft/pending_review) | Backend | Critical | Gate 5 | done |
| 45 | Statuts : brouillon, à valider, approuvé, rejeté, publié, échec | Backend | Critical | Gate 5 | done |
| 46 | Validation humaine obligatoire avant diffusion externe/sensible | Backend | Critical | Gate 5 | done |
| 47 | Notifications in-app ; email si service configuré | Backend | High | Gate 5 | done |
| 48 | Historique : logs, erreurs, tentatives, relances contrôlées | Backend | Critical | Gate 5 | done |
| 49 | Page gestion des planifications et exécutions | Frontend | Critical | Gate 5 | done |
| 50 | Tests : déclenchement simulé, fuseau horaire, idempotence, échec/reprise, validation, permissions, historique | All | Critical | Gate 5 | done |
| 51 | Gate 5 validation : rapport quotidien/hebdomadaire généré selon planning, traçable, bloqué jusqu'à validation | — | — | Gate 5 | done |

## Phase 5: Module 6 - Tâches et Suivi (Weeks 10-11)
| # | Task | Module | Priority | Gate | Status |
|---|------|--------|----------|------|--------|
| 52 | Tableau de bord documents et traitements | Frontend | High | Gate 6 | done |
| 53 | Liste tâches avec responsable, échéance, statut, commentaires | Frontend | Critical | Gate 6 | done |
| 54 | Historique analyses, rapports, fichiers | Frontend | Medium | Gate 6 | done |
| 55 | Notifications et journal d'audit des actions sensibles | Backend | Critical | Gate 6 | done |
| 56 | Vérification autorisations sur chaque endpoint et action | Backend | Critical | Gate 6 | done |
| 57 | Tests : chaque traitement et livrable retrouvable, statut compréhensible | All | Critical | Gate 6 | done |
| 58 | Gate 6 validation : chaque traitement et livrable retrouvable, statut compréhensible | — | — | Gate 6 | done |

## Phase 6: Qualité, Sécurité et Recette (Weeks 12-13)
| # | Task | Module | Priority | Gate |
|---|------|--------|----------|------|
| 59 | Tests unitaires des services et calculs | All | Critical | Gate 7 |
| 60 | Tests d'intégration API/base/vector store/LLM mocké | All | Critical | Gate 7 |
| 61 | Tests end-to-end des parcours critiques | All | Critical | Gate 7 |
| 62 | Tests permissions, séparation espaces, injection de prompt, fichiers malformés, accès exports | All | Critical | Gate 7 |
| 63 | Tests non-régression après chaque correction | All | Critical | Gate 7 |
| 64 | Migrations base vide et base existante | Infra | Critical | Gate 7 |
| 65 | Lint, formatage, typage, analyse dépendances | All | Critical | Gate 7 |
| 66 | Performances sur documents de taille représentative | All | High | Gate 7 |
| 67 | Limites connues, procédure sauvegarde/restauration, guide utilisateur | Docs | Critical | Gate 7 |
| 68 | Matrice de traçabilité : chaque exigence done/deferred/blocked avec justification et preuve de test | Docs | Critical | Gate 7 |
| 69 | Gate 7 validation : matrice traçabilité → done, aucun done sans test | — | — | Gate 7 |

## Post-MVP / Backlog Continued
| # | Task | Module | Priority |
|---|------|--------|----------|
| 70 | Connecteurs avancés (email, CRM, ERP, cloud storage) | — | Deferred |
| 71 | Multi-organisation avancé (facturation, quotas, admin délégué) | — | Deferred |
| 72 | Workflows visuels complexes et déclencheurs conditionnels | — | Deferred |
| 73 | Comparaison intelligente à grande échelle | — | Deferred |
| 74 | Personnalisation complète des chartes graphiques | — | Deferred |
| 75 | Application mobile native et hors ligne | — | Deferred |

**Legend**: Critical = essential for MVP | High = important but may be deferred | Medium = nice-to-have | Gate = exit criteria that must be passed before proceeding