"use client"

import { useState } from "react"
import Link from "next/link"

export default function RegistrationPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [orgName, setOrgName] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const response = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, organization_name: orgName }),
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        setError(err.detail || "Inscription impossible. Vérifiez les informations.")
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
    <div className="flex min-h-screen items-center justify-center bg-[#F4F7FB] px-4 py-12">
      <div className="w-full max-w-[440px] rounded-2xl bg-white p-8 shadow-card border border-[#E2E8F0]">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#3478F6] text-white shadow-lg shadow-[#3478F6]/25">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6" aria-hidden="true">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="8.5" cy="7" r="4" /><path d="M20 8v6m3-3h-6" />
            </svg>
          </div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3478F6] mb-2">SmartWork AI</p>
          <h1 className="text-2xl font-semibold text-[#142B4A] font-[family-name:var(--font-manrope)]">Créer un compte</h1>
          <p className="mt-2 text-sm text-[#64748B]">Démarrez avec votre espace de travail intelligent</p>
        </div>

        {error && (
          <div role="alert" className="mb-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-[#142B4A] mb-1.5">Adresse email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2.5 text-sm text-[#142B4A] placeholder:text-[#94A3B8] focus:border-[#3478F6] focus:outline-none focus:ring-3 focus:ring-[#3478F6]/15 transition"
              placeholder="vous@entreprise.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-[#142B4A] mb-1.5">Mot de passe</label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2.5 text-sm text-[#142B4A] placeholder:text-[#94A3B8] focus:border-[#3478F6] focus:outline-none focus:ring-3 focus:ring-[#3478F6]/15 transition"
              placeholder="Créer un mot de passe"
            />
          </div>
          <div>
            <label htmlFor="orgName" className="block text-sm font-medium text-[#142B4A] mb-1.5">Nom de l&apos;organisation</label>
            <input
              id="orgName"
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              required
              className="w-full rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2.5 text-sm text-[#142B4A] placeholder:text-[#94A3B8] focus:border-[#3478F6] focus:outline-none focus:ring-3 focus:ring-[#3478F6]/15 transition"
              placeholder="Votre organisation"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center rounded-lg bg-[#3478F6] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#2a66d6] disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Création du compte…" : "Créer mon compte"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[#64748B]">
          Déjà un compte ?{" "}
          <Link href="/login" className="font-medium text-[#3478F6] hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  )
}
