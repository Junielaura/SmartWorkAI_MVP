# PROMPT — APPLICATION DE LA CHARTE GRAPHIQUE OFFICIELLE DE SMARTWORK AI

## 1. RÔLE ET MISSION

Agis comme un Senior UI/UX Designer, Senior Frontend Engineer et Expert Design System spécialisé dans les applications SaaS professionnelles, les plateformes d'intelligence artificielle et les interfaces de Business Intelligence.

Ta mission consiste à analyser l'application existante **SmartWork AI**, puis à appliquer une identité visuelle moderne, cohérente, élégante et professionnelle sur l'ensemble de l'application.

Tu dois respecter strictement la palette de couleurs définie dans ce document.

**IMPORTANT :** Il ne s'agit pas de créer une nouvelle application ou de reconstruire inutilement l'interface. Il faut améliorer le design de l'application existante tout en préservant son architecture, ses fonctionnalités, ses routes, ses composants métier et ses intégrations.

---

## 2. IDENTITÉ VISUELLE OFFICIELLE

Le positionnement visuel de SmartWork AI est :

**Intelligence artificielle + Productivité professionnelle + Analyse décisionnelle + Automatisation.**

L'application doit inspirer :

- La confiance et la fiabilité.
- L'innovation technologique.
- L'intelligence et la précision.
- La simplicité d'utilisation.
- Le professionnalisme d'une solution SaaS Enterprise.

Le design doit être minimaliste, moderne, épuré et haut de gamme.

### 2.1. Palette de couleurs obligatoire

Utilise exclusivement cette palette comme base de l'identité visuelle.

| Nom               | Code HEX | Utilisation                                |
| ----------------- | -------- | ------------------------------------------ |
| Bleu profond      | #142B4A  | Sidebar, navigation, identité principale   |
| Bleu électrique   | #3478F6  | Boutons principaux, liens, actions actives |
| Turquoise         | #19B6A4  | Succès, validation, automatisation         |
| Violet IA         | #8067E8  | Assistant IA, génération intelligente      |
| Gris bleuté clair | #F4F7FB  | Arrière-plan principal                     |
| Blanc             | #FFFFFF  | Cartes, formulaires, panneaux              |

### 2.2. Couleurs fonctionnelles

Pour les états et notifications, utilise :

- Succès : vert, avec une déclinaison harmonisée autour du turquoise.
- Avertissement : orange.
- Erreur : rouge.
- Information : bleu.
- Fonctionnalité IA : violet.

Les couleurs fonctionnelles doivent rester discrètes et accessibles. Elles ne doivent pas concurrencer les couleurs principales de la marque.

### 2.3. Règle fondamentale

Ne mélange pas toutes les couleurs dans les mêmes composants.

Respecte cette hiérarchie :

1. Le bleu profond représente l'identité de SmartWork AI.
2. Le bleu électrique représente les actions principales.
3. Le turquoise représente la réussite et les processus automatisés.
4. Le violet représente les fonctionnalités liées à l'intelligence artificielle.
5. Le gris bleuté constitue le fond de l'environnement de travail.
6. Le blanc permet de mettre en valeur les contenus.

Le violet doit particulièrement permettre à l'utilisateur d'identifier les fonctions intelligentes.

---

## 3. DESIGN SYSTEM GLOBAL

Avant de modifier les composants, crée un système centralisé de design tokens.

Si le projet utilise Tailwind CSS, configure les couleurs dans sa configuration ou dans le système de variables CSS compatible avec sa version.

Crée des variables globales similaires à celles-ci :

```css
:root {
  /* Brand */
  --color-brand-primary: #142B4A;
  --color-brand-secondary: #3478F6;
  --color-brand-accent: #19B6A4;
  --color-brand-ai: #8067E8;

  /* Backgrounds */
  --color-background: #F4F7FB;
  --color-surface: #FFFFFF;
  --color-surface-muted: #EDF2F8;

  /* Text */
  --color-text-primary: #142B4A;
  --color-text-secondary: #64748B;
  --color-text-muted: #94A3B8;

  /* Borders */
  --color-border: #E2E8F0;

  /* Functional states */
  --color-success: #19B6A4;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
  --color-info: #3478F6;

  /* AI */
  --color-ai-primary: #8067E8;
  --color-ai-soft: #F0ECFF;
}
```

Adapte ces variables à la structure réelle du projet.

**Interdiction :** ne multiplie pas les couleurs HEX directement dans chaque composant. Les couleurs doivent être réutilisées depuis le système centralisé.

---

## 4. APPLICATION DU DESIGN À L'ENSEMBLE DE L'INTERFACE

### 4.1. Sidebar et navigation principale

La sidebar doit utiliser le bleu profond `#142B4A`.

Elle doit contenir :

- Le logo SmartWork AI.
- Le nom de la plateforme.
- Les menus de navigation.
- Les icônes associées aux fonctionnalités.
- Les informations du profil utilisateur.
- Le bouton de déconnexion.

Règles de design :

- Texte blanc ou gris très clair.
- Icônes discrètes et élégantes.
- Élément actif avec un fond bleu légèrement plus clair.
- Indicateur actif bleu électrique `#3478F6`.
- Transitions douces au survol.
- Séparation visuelle claire entre les groupes de menus.

Ne surcharge pas la sidebar avec des couleurs différentes.

### 4.2. Barre supérieure (Topbar)

Utilise un fond blanc.

Elle doit présenter :

- Le titre de la page.
- Le fil d'Ariane si nécessaire.
- La recherche globale.
- Les notifications.
- Le profil utilisateur.
- Le sélecteur de thème clair/sombre.

Ajoute une bordure inférieure légère.

### 4.3. Zone de travail principale

Le fond général doit être `#F4F7FB`.

Les pages doivent disposer :

- D'un espacement régulier.
- D'une hiérarchie typographique claire.
- D'une largeur de contenu maîtrisée.
- D'une disposition responsive.
- De sections visuellement bien séparées.

Évite les fonds trop colorés et les dégradés excessifs.

### 4.4. Cartes et panneaux

Les cartes doivent utiliser :

- Fond blanc.
- Bordure légère `#E2E8F0`.
- Coins arrondis cohérents.
- Ombres très discrètes.
- Espacement intérieur confortable.

Les cartes doivent être homogènes dans toutes les pages.

### 4.5. Boutons

**Bouton principal :**

- Fond `#3478F6`.
- Texte blanc.
- Hover légèrement plus sombre.
- Focus visible.
- Coins arrondis modérés.

**Bouton secondaire :**

- Fond blanc.
- Texte bleu profond.
- Bordure gris clair.

**Bouton de validation :**

- Turquoise.

**Bouton associé à une fonctionnalité IA :**

- Violet `#8067E8`.
- Texte blanc.
- Icône IA éventuellement intégrée.

Ne rends pas tous les boutons colorés. Les actions principales doivent être visuellement prioritaires.

### 4.6. Formulaires et champs de saisie

Applique un design uniforme :

- Fond blanc.
- Bordure gris clair.
- Texte bleu profond.
- Placeholder gris.
- Focus avec bordure bleue.
- Message d'erreur rouge.
- Message de validation turquoise.

Les champs doivent rester lisibles et suffisamment espacés.

---

## 5. APPLICATION AUX SIX MODULES DE SMARTWORK AI

Il est essentiel de conserver une identité commune tout en différenciant les fonctionnalités.

### MODULE 1 — Gestion documentaire et compréhension des documents

Fonctionnalités :

- Importation de documents.
- Liste des documents.
- Prévisualisation.
- Extraction de texte.
- OCR.
- Classification.
- Segmentation.
- Indexation vectorielle.
- Historique et versions.

Design :

- Bleu profond pour les titres.
- Bleu électrique pour les actions d'importation.
- Turquoise pour les traitements terminés.
- Orange pour les traitements en attente.
- Rouge pour les erreurs.
- Violet pour les fonctions d'analyse IA.

Les zones de dépôt doivent être modernes, avec une icône de document et un état visuel clair.

### MODULE 2 — Génération documentaire

Fonctionnalités :

- Génération Word.
- Génération PDF.
- Génération Excel.
- Génération PowerPoint.
- Gestion des modèles.
- Prévisualisation.
- Téléchargement.
- Historique.

Design :

- Bleu électrique pour les actions de création et de téléchargement.
- Violet pour la génération assistée par IA.
- Blanc pour les zones de prévisualisation.
- Turquoise pour les générations réussies.

La prévisualisation doit donner l'impression d'un véritable espace de travail documentaire.

### MODULE 3 — Tableaux de bord et visualisations

Fonctionnalités :

- KPI.
- Graphiques.
- Filtres.
- Analyse des données.
- Comparaisons.
- Exports.

Design :

- Bleu électrique pour les séries principales.
- Turquoise pour les séries secondaires.
- Violet pour les indicateurs issus d'analyses IA.
- Orange et rouge pour les alertes.

Les graphiques doivent être lisibles et sobres.

Ne choisis pas les couleurs uniquement pour leur esthétique : elles doivent permettre de distinguer correctement les catégories de données.

### MODULE 4 — Rapports périodiques

Fonctionnalités :

- Rapports quotidiens.
- Rapports hebdomadaires.
- Programmation.
- Historique.
- Validation humaine.
- Notifications.

Design :

- Bleu profond pour les titres.
- Bleu électrique pour les programmations.
- Turquoise pour les rapports validés.
- Orange pour les rapports en attente.
- Rouge pour les échecs.

Les statuts doivent être présentés avec des badges sobres.

### MODULE 5 — Assistant conversationnel IA

Ce module doit avoir une identité visuelle légèrement distincte.

Le violet `#8067E8` doit devenir sa couleur d'identification.

Applique-le à :

- L'icône de l'assistant.
- L'indicateur de réponse IA.
- Les suggestions de questions.
- Les actions intelligentes.
- Les zones de génération.
- Les éléments de conversation associés à l'IA.

Conserve néanmoins le fond blanc ou gris clair pour assurer le confort de lecture.

Les messages de l'utilisateur et ceux de l'assistant doivent être facilement différenciables.

Les sources documentaires citées doivent être visuellement identifiables.

### MODULE 6 — Gestion des tâches et workflows

Fonctionnalités :

- Création de tâches.
- Affectation.
- Échéances.
- Suivi.
- Commentaires.
- Notifications.
- Historique.

Design :

- Bleu pour les tâches actives.
- Turquoise pour les tâches terminées.
- Orange pour les tâches en attente.
- Rouge pour les tâches en retard.
- Violet pour les actions automatisées par IA.

Utilise une représentation claire des statuts et des échéances.

---

## 6. TYPOGRAPHIE

Utilise :

- Inter : police principale de toute l'application.
- Manrope : police secondaire pour les titres importants et certains éléments de marque.

Hiérarchie recommandée :

- H1 : 28 à 32 px.
- H2 : 22 à 26 px.
- H3 : 18 à 20 px.
- Texte courant : 14 à 16 px.
- Texte secondaire : 12 à 14 px.

Utilise des graisses typographiques cohérentes.

Ne multiplie pas les styles de texte inutilement.

---

## 7. MODE CLAIR ET MODE SOMBRE

Implémente un véritable système de thèmes.

### Mode clair

- Background : `#F4F7FB`
- Surface : `#FFFFFF`
- Texte principal : `#142B4A`
- Texte secondaire : `#64748B`
- Primary : `#3478F6`
- Accent : `#19B6A4`
- AI : `#8067E8`
- Border : `#E2E8F0`

### Mode sombre

- Background : `#111827`
- Surface : `#1E293B`
- Surface secondaire : `#273449`
- Texte principal : `#F8FAFC`
- Texte secondaire : `#CBD5E1`
- Primary : `#75A5FF`
- Accent : `#36CDBA`
- AI : `#A996FF`
- Border : `#334155`

Le mode sombre doit préserver les contrastes, les états fonctionnels et la lisibilité des graphiques.

Le changement de thème doit être disponible depuis la topbar ou les paramètres utilisateur.

Si le projet possède déjà un mécanisme de thème, améliore-le au lieu d'en créer un second.

---

## 8. RESPONSIVE DESIGN

L'interface doit être entièrement adaptée à :

- Ordinateurs de bureau.
- Ordinateurs portables.
- Tablettes.
- Smartphones.

Sur mobile :

- La sidebar devient une navigation latérale rétractable.
- Les cartes passent en une seule colonne si nécessaire.
- Les tableaux deviennent adaptatifs.
- Les formulaires occupent correctement la largeur disponible.
- Les graphiques restent lisibles.
- Les boutons restent accessibles.

Ne te contente pas de réduire les dimensions : adapte réellement les dispositions.

---

## 9. ACCESSIBILITÉ ET QUALITÉ VISUELLE

Respecte les bonnes pratiques WCAG 2.2 AA lorsque cela est applicable.

Vérifie notamment :

- Les contrastes texte/fond.
- Les états de focus.
- La navigation au clavier.
- Les labels des formulaires.
- Les messages d'erreur.
- Les états de chargement.
- Les états vides.
- Les états de succès.

Ne transmets jamais une information uniquement par la couleur. Ajoute un libellé ou une icône lorsque cela est nécessaire.

---

## 10. MÉTHODOLOGIE D'EXÉCUTION OBLIGATOIRE

Ne commence pas par modifier tous les fichiers simultanément.

### ÉTAPE 1 — AUDIT DE L'APPLICATION

Analyse :

- La structure du frontend.
- Le framework et sa version.
- La configuration Tailwind ou CSS.
- Les composants partagés.
- Le système de navigation.
- Les pages existantes.
- Les bibliothèques d'icônes.
- Le système de graphiques.
- Le système de thèmes.

Identifie les incohérences visuelles et les composants à réutiliser.

Présente un bref diagnostic avant les modifications.

### ÉTAPE 2 — MISE EN PLACE DU DESIGN SYSTEM

- Centralise les couleurs.
- Configure les variables CSS.
- Configure les polices.
- Harmonise les bordures, espacements et rayons.
- Prépare les thèmes clair et sombre.
- Crée ou améliore les composants UI réutilisables.

### ÉTAPE 3 — REFONTE DES COMPOSANTS COMMUNS

Commence par :

1. Sidebar.
2. Topbar.
3. Layout principal.
4. Boutons.
5. Cartes.
6. Formulaires.
7. Modales.
8. Badges et alertes.
9. Tableaux.
10. États de chargement et états vides.

### ÉTAPE 4 — APPLICATION AUX SIX MODULES

Applique ensuite le design system à chaque module.

Ne laisse aucune page avec l'ancien thème si elle fait partie de l'application.

Vérifie que les couleurs spécifiques des modules respectent la hiérarchie définie dans ce prompt.

### ÉTAPE 5 — VÉRIFICATION

Effectue :

- Une vérification visuelle de toutes les pages.
- Une vérification responsive.
- Une vérification des thèmes.
- Une vérification des contrastes.
- Une vérification des interactions.
- Une vérification des graphiques et tableaux.
- Une vérification des composants partagés.

Lance les tests et commandes de vérification adaptés au projet.

Corrige les régressions avant de terminer.

---

## 11. CONTRAINTES À RESPECTER ABSOLUMENT

1. Ne supprime aucune fonctionnalité existante.
2. Ne modifie pas inutilement le backend.
3. Ne modifie pas les contrats API.
4. Ne casse pas les routes.
5. Ne supprime aucune donnée.
6. Ne remplace pas les vrais composants fonctionnels par des maquettes statiques.
7. Ne crée pas de pages fictives pour donner l'impression que le travail est terminé.
8. Ne duplique pas les composants existants.
9. Ne multiplie pas les couleurs arbitrairement.
10. N'ajoute pas de dépendances sans justification.
11. Ne modifie pas les mécanismes d'authentification ou les autorisations.
12. Préserve la compatibilité avec la stack existante.

Le résultat doit être un véritable design system appliqué à l'application, pas seulement une modification de quelques couleurs CSS.

---

## 12. LIVRABLES ATTENDUS

À la fin, fournis :

1. Le diagnostic initial de l'interface.
2. La liste des fichiers créés et modifiés.
3. Le design system centralisé.
4. Les variables de couleurs.
5. Les composants UI harmonisés.
6. Les six modules adaptés.
7. Le mode clair et le mode sombre.
8. Les vérifications responsive.
9. Les tests exécutés et leurs résultats réels.
10. Les éventuels problèmes restants.

Pour chaque étape, indique les modifications effectuées et les critères de validation.

Ne prétends jamais qu'un test a réussi s'il n'a pas été exécuté.

## 13. INSTRUCTION DE DÉMARRAGE

Commence par l'ÉTAPE 1 : AUDIT DE L'APPLICATION EXISTANTE.

Ne modifie aucun fichier avant d'avoir identifié la structure réelle du projet et les composants concernés.

Présente ton diagnostic, ta stratégie de modification et les fichiers qui seront concernés.

Attends ma validation avant d'entreprendre une refonte globale.

**OBJECTIF FINAL :** faire de SmartWork AI une application SaaS professionnelle, moderne, élégante, cohérente et immédiatement identifiable grâce à sa palette bleu profond, bleu électrique, turquoise et violet IA.cfc-housing-portal
