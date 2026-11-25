# Design Spec — Refonte de la page de connexion et correction du login admin

**Date** : 2026-11-20
**Statut** : Approuvé par l'utilisateur
**Périmètre** : `frontend/app/login/page.tsx`, `backend/app/core/security.py`

## 1. Contexte

La page de connexion actuelle est fonctionnelle mais visuellement minimale : fond gris clair, carte blanche simple, aucun retour d'état pendant la requête, et aucun moyen d'afficher le mot de passe saisi. Par ailleurs, la connexion avec le compte administrateur échoue systématiquement avec une erreur 500, alors que les identifiants `admin@smartwork.ai` / `Admin1234!` sont corrects.

L'investigation a établi la cause de l'erreur 500 : `backend/app/core/security.py:49` appelle `datetime.now(timezone.utc)` mais le module `timezone` n'est pas importé (ligne 1 : `from datetime import datetime, timedelta`). Le mot de passe est vérifié avec succès ; l'exception `NameError` survient lors de la création du JWT.

## 2. Objectifs

1. Offrir une page de connexion professionnelle, cohérente avec l'identité visuelle « Corporate sombre » de l'application.
2. Permettre à l'utilisateur d'afficher ou masquer son mot de passe.
3. Corriger l'erreur 500 qui empêche la connexion de l'administrateur.
4. Conserver le flux d'authentification existant sans changer de contrat d'API.

## 3. Non-objectifs

- Refonte du reste de l'interface ou de la sidebar.
- Migration du stockage du token hors de `localStorage` (traitée dans les perspectives du guide).
- Ajout d'une politique RBAC ou d'une page de réinitialisation de mot de passe.
- Modification du schéma de la table `users` ou des identifiants administrateur.

## 4. Design de l'interface

### 4.1 Structure

Un seul fichier est modifié : `frontend/app/login/page.tsx`. Aucun composant partagé n'est créé et aucune dépendance n'est ajoutée.

- Conteneur racine : `min-h-screen`, fond dégradé `slate-950` vers `blue-950`, halo radial discret en haut à gauche.
- Carte centrale : fond blanc, `rounded-2xl`, ombre douce, largeur maximale d'environ 420 px, paddings généreux.
- En-tête : pastille carrée arrondie portant « SW » en indigo, titre « Connexion à SmartWork AI », sous-titre « Accédez à votre espace documentaire intelligent ».

### 4.2 Champs et contrôles

| Élément | Comportement |
|---|---|
| Email | `type="email"`, `autoComplete="email"`, label associé via `htmlFor`. |
| Mot de passe | `type` bascule entre `password` et `text`, `autoComplete="current-password"`, label associé. |
| Bouton de visibilité | SVG inline (œil / œil barré), positionné à droite du champ, `aria-label` dynamique, `aria-pressed` reflétant l'état, piloté par `showPassword`. |
| Bouton de soumission | Pleine largeur, fond indigo, libellé « Se connecter », désactivé et libellé « Connexion… » pendant la requête. |
| Lien inscription | Conservé sous le bouton, même destination `/inscription`. |

### 4.3 États

- `email`, `password` : valeurs du formulaire.
- `showPassword` : visibilité du mot de passe.
- `error` : message d'erreur ou `null`.
- `loading` : état d'attente, calculé localement pendant la requête.

Le focus conserve un anneau visible sur tous les contrôles. Le bouton de visibilité ne soumet pas le formulaire (`type="button"`).

### 4.4 Erreurs

Le bandeau rouge existant est conservé et retravaillé : icône d'avertissement, message retourné par l'API ou message générique « Erreur de connexion. Réessayez. ». Le message API `Incorrect email or password` est affiché tel quel.

## 5. Flux de données

1. L'utilisateur saisit ses identifiants et active éventuellement le toggle de visibilité.
2. La soumission envoie `POST /api/v1/auth/login` en JSON via le rewrite Next.js défini dans `frontend/next.config.ts` (`/api/v1/:path*` → `API_INTERNAL_URL`).
3. Le backend vérifie le mot de passe puis crée le JWT avec `create_access_token`.
4. Le token est stocké dans `localStorage` sous `access_token`.
5. Le navigateur redirige vers `/dashboard`.

Aucun champ ni paramètre d'API n'est modifié.

## 6. Correction backend

Une ligne est ajoutée à `backend/app/core/security.py` :

```python
from datetime import datetime, timedelta, timezone
```

Aucune autre logique de sécurité n'est touchée. L'image backend doit être reconstruite (`docker compose build backend`) pour que la correction soit effective dans le conteneur, puis le service redémarré (`docker compose up -d backend`).

## 7. Vérification

| Contrôle | Commande / action | Résultat attendu |
|---|---|---|
| Syntaxe du spec | Relecture inline | Aucun `TBD`, aucune contradiction |
| Build frontend | `npm run build` dans `frontend/` | Build réussi |
| Login admin | `curl -X POST http://localhost:8100/api/v1/auth/login -H 'Content-Type: application/json' -d '{"email":"admin@smartwork.ai","password":"Admin1234!"}'` | HTTP 200 avec `access_token` |
| Erreur contrôlée | Même appel avec un mot de passe erroné | HTTP 401 avec `Incorrect email or password` |
| Toggle | Test manuel dans le navigateur | Le mot de passe passe de masqué à visible et inversement |

## 8. Risques et arbitrages

- Le build frontend peut échouer si la configuration Tailwind/Turbopack existante est déjà instable ; aucune modification de cette configuration n'est prévue dans ce spec.
- Le compte admin dépend de la graine de données présente dans PostgreSQL ; aucune réinitialisation de la base n'est effectuée.
- Le stockage du token dans `localStorage` reste une limite de sécurité connue, documentée dans `docs/guide.md`.

## 9. Références

- `frontend/app/login/page.tsx` — page actuelle.
- `backend/app/api/v1/router.py` — endpoints `/auth/register` et `/auth/login`.
- `backend/app/core/security.py` — création et vérification du JWT.
- `frontend/next.config.ts` — rewrite de l'API.
- `docs/gap-analysis.md` — identifiants administrateur de référence.
