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
