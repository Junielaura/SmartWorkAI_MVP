# Login Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the login page with a professional corporate-dark theme and a password visibility toggle, and fix the 500 error that blocks administrator login.

**Architecture:** Two independent changes: a one-line backend import fix that restores JWT creation, and a self-contained rewrite of the single frontend page. The API contract, token storage, and redirect flow stay unchanged.

**Tech Stack:** FastAPI / Python 3.11 backend in Docker Compose, Next.js 16 / React 19 / Tailwind 4 frontend, pytest for backend tests, Node built-in test runner for a frontend source contract.

## Global Constraints

- Modify only `frontend/app/login/page.tsx` and `backend/app/core/security.py` for production code.
- Add no new npm or pip dependency.
- Keep the endpoint `POST /api/v1/auth/login`, the `localStorage` key `access_token`, and the `/dashboard` redirect unchanged.
- Keep the administrator credentials `admin@smartwork.ai` / `Admin1234!` unchanged.
- No changes to `next.config.ts`, `tailwind.config.js`, or the users table.
- Use French copy in the UI and English copy in source identifiers.

---

### Task 1: Fix administrator login 500 error

**Files:**
- Modify: `backend/app/core/security.py:1`
- Create: `backend/tests/test_auth_token.py`

**Interfaces:**
- Consumes: `app.core.security.create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str`, `app.core.security.verify_token(token: str) -> Optional[dict]`, `app.core.config.settings.SECRET_KEY`, `settings.ALGORITHM`.
- Produces: `create_access_token` keeps the same signature and returns a decodable JWT; the login endpoint returns HTTP 200 with `access_token` for valid credentials.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_auth_token.py` with exactly this content:

```python
from app.core.security import create_access_token, verify_token


def test_create_access_token_returns_decodable_jwt():
    token = create_access_token(subject="admin@smartwork.ai")

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "admin@smartwork.ai"
    assert "exp" in payload
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /home/laura/SmartWorkAI_MVP/backend && python -m pytest tests/test_auth_token.py -v`
Expected: FAIL with `NameError: name 'timezone' is not defined` at `app/core/security.py:49`.

- [ ] **Step 3: Apply the minimal fix**

Change line 1 of `backend/app/core/security.py` from:

```python
from datetime import datetime, timedelta
```

to:

```python
from datetime import datetime, timedelta, timezone
```

No other line changes.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /home/laura/SmartWorkAI_MVP/backend && python -m pytest tests/test_auth_token.py -v`
Expected: PASS with 1 passed.

- [ ] **Step 5: Rebuild and restart the backend container**

Run: `cd /home/laura/SmartWorkAI_MVP && docker compose build backend && docker compose up -d backend`
Expected: image rebuilt and container `smartwork-ai-backend-1` reports `Up` and `healthy`.

- [ ] **Step 6: Verify the real admin login**

Run:

```bash
curl -s -o /tmp/admin-login.json -w '%{http_code}\n' \
  -X POST http://localhost:8100/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@smartwork.ai","password":"Admin1234!"}'
```

Expected: `200`. Then run `python -c "import json;print('access_token' in json.load(open('/tmp/admin-login.json')))"` and expect `True`.

- [ ] **Step 7: Verify the controlled error case**

Run:

```bash
curl -s -X POST http://localhost:8100/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@smartwork.ai","password":"wrong-password"}'
```

Expected: HTTP 401 with body containing `Incorrect email or password`.

- [ ] **Step 8: Commit**

```bash
git add backend/app/core/security.py backend/tests/test_auth_token.py
git commit -m "fix(auth): import timezone for JWT creation"
```

---

### Task 2: Redesign the login page and add the password toggle

**Files:**
- Modify: `frontend/app/login/page.tsx`
- Create: `frontend/tests/login-page.test.mjs`

**Interfaces:**
- Consumes: `next/link`, React `useState`, the rewrite `/api/v1/:path*` defined in `frontend/next.config.ts`.
- Produces: a login page that keeps the same form submission contract and exposes a password visibility toggle driven by local state `showPassword`.

- [ ] **Step 1: Create the failing frontend contract test**

Run `mkdir -p /home/laura/SmartWorkAI_MVP/frontend/tests`, then create `frontend/tests/login-page.test.mjs` with exactly this content:

```js
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { test } from "node:test"

const source = readFileSync(new URL("../app/login/page.tsx", import.meta.url), "utf8")

test("password field exposes a visibility toggle", () => {
  assert.match(source, /showPassword/)
  assert.match(source, /type=\{showPassword \? "text" : "password"\}/)
  assert.match(source, /aria-pressed=\{showPassword\}/)
  assert.match(source, /Afficher le mot de passe/)
})

test("login page uses corporate dark theme and loading state", () => {
  assert.match(source, /from-slate-950/)
  assert.match(source, /via-blue-950/)
  assert.match(source, /loading \? "Connexion…" : "Se connecter"/)
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /home/laura/SmartWorkAI_MVP/frontend && node --test tests/login-page.test.mjs`
Expected: FAIL with `AssertionError` on the first `assert.match` because `showPassword` is absent.

- [ ] **Step 3: Replace the login page**

Replace the entire content of `frontend/app/login/page.tsx` with:

```tsx
"use client"

import { useState } from "react"
import Link from "next/link"

function EyeIcon({ visible }: { visible: boolean }) {
  if (visible) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 2.25 12s3.75 6.75 9.75 6.75c1.653 0 3.184-.48 4.478-1.277M6.228 6.228A10.45 10.45 0 0 1 12 5.25c6 0 9.75 6.75 9.75 6.75a10.45 10.45 0 0 1-2.022 2.728M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="m3 3 18 18" />
      </svg>
    )
  }

  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12s3.75-6.75 9.75-6.75 9.75 6.75 9.75 6.75-3.75 6.75-9.75 6.75S2.25 12 2.25 12Z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    </svg>
  )
}

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        setError(err.detail || "Erreur de connexion. Réessayez.")
        return
      }
      const data = await response.json()
      localStorage.setItem("access_token", data.access_token)
      window.location.href = "/dashboard"
    } catch {
      setError("Erreur de connexion. Réessayez.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 px-4 py-12">
      <div className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />

      <div className="relative w-full max-w-[420px] rounded-2xl bg-white p-8 shadow-2xl shadow-slate-950/40 ring-1 ring-white/10">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-base font-bold tracking-tight text-white shadow-lg shadow-indigo-600/30">
            SW
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">Connexion à SmartWork AI</h1>
          <p className="mt-2 text-sm text-slate-500">Accédez à votre espace documentaire intelligent</p>
        </div>

        {error && (
          <div role="alert" className="mb-6 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-7-4a1 1 0 1 0-2 0v4a1 1 0 0 0 2 0V6Zm-1 8a1.25 1.25 0 1 0 0 2.5A1.25 1.25 0 0 0 10 14Z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700">
              Adresse email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Mot de passe
            </label>
            <div className="relative mt-2">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-300 px-4 py-3 pr-12 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30"
              />
              <button
                type="button"
                onClick={() => setShowPassword((current) => !current)}
                aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                aria-pressed={showPassword}
                className="absolute inset-y-0 right-0 flex w-12 items-center justify-center rounded-r-lg text-slate-500 transition hover:text-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
              >
                <EyeIcon visible={showPassword} />
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Pas encore de compte ?{" "}
          <Link href="/inscription" className="font-medium text-indigo-600 hover:text-indigo-700 hover:underline">
            Créer un compte
          </Link>
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Run the frontend contract test**

Run: `cd /home/laura/SmartWorkAI_MVP/frontend && node --test tests/login-page.test.mjs`
Expected: PASS with 2 tests passed.

- [ ] **Step 5: Build the frontend**

Run: `cd /home/laura/SmartWorkAI_MVP/frontend && npm run build`
Expected: `Compiled successfully` and no TypeScript errors.

- [ ] **Step 6: Verify manually in the browser**

Run: `docker compose up -d frontend` from `/home/laura/SmartWorkAI_MVP`, then open `http://localhost:3100/login`.
Expected: dark gradient background, centered white card, eye button toggles the password between masked and visible, admin credentials reach `/dashboard`.

- [ ] **Step 7: Commit**

```bash
git add frontend/app/login/page.tsx frontend/tests/login-page.test.mjs
git commit -m "feat(login): redesign page and add password visibility toggle"
```

---

## Self-Review Notes

- Spec section 1 (context and root cause) is covered by Task 1 steps 1–4.
- Spec section 2 (objectives) is covered by Task 1 (objective 3) and Task 2 (objectives 1, 2, 4).
- Spec section 4.1–4.4 (layout, controls, states, errors) is covered by Task 2 step 3.
- Spec section 5 (data flow) is preserved unchanged and verified by Task 1 step 6 and Task 2 step 6.
- Spec section 6 (backend fix) is covered by Task 1 step 3.
- Spec section 7 (verification) is covered by Task 1 steps 2, 4, 6, 7 and Task 2 steps 2, 4, 5, 6.
- No placeholder remains; names `showPassword`, `loading`, `EyeIcon`, `create_access_token` are consistent across all tasks.
