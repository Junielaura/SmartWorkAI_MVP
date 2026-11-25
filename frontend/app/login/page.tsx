"use client"

import { useState } from "react"
import Link from "next/link"

function EyeIcon({ visible }: { visible: boolean }) {
  return visible ? (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 2.25 12s3.75 6.75 9.75 6.75c1.653 0 3.184-.48 4.478-1.277M6.228 6.228A10.45 10.45 0 0 1 12 5.25c6 0 9.75 6.75 9.75 6.75a10.45 10.45 0 0 1-2.022 2.728M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="m3 3 18 18" />
    </svg>
  ) : (
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
    <div className="flex min-h-screen items-center justify-center bg-[#F4F7FB] px-4 py-12">
      <div className="w-full max-w-[440px] rounded-2xl bg-white p-8 shadow-card border border-[#E2E8F0]">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#3478F6] text-white shadow-lg shadow-[#3478F6]/25">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6" aria-hidden="true">
              <path d="M14 2.75H6.5A1.75 1.75 0 0 0 4.75 4.5v15A1.75 1.75 0 0 0 6.5 21.25h11A1.75 1.75 0 0 0 19.25 19.5V8.25L14 2.75Zm0 0v5.5h5.25" />
            </svg>
          </div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#3478F6] mb-2">SmartWork AI</p>
          <h1 className="text-2xl font-semibold text-[#142B4A] font-[family-name:var(--font-manrope)]">Connexion</h1>
          <p className="mt-2 text-sm text-[#64748B]">Accédez à votre espace documentaire intelligent</p>
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
            <label htmlFor="email" className="block text-sm font-medium text-[#142B4A] mb-1.5">Adresse email</label>
            <input
              id="email"
              name="email"
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
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2.5 pr-11 text-sm text-[#142B4A] placeholder:text-[#94A3B8] focus:border-[#3478F6] focus:outline-none focus:ring-3 focus:ring-[#3478F6]/15 transition"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword((c) => !c)}
                aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                aria-pressed={showPassword}
                className="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-lg text-[#94A3B8] transition hover:text-[#3478F6]"
              >
                <EyeIcon visible={showPassword} />
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center rounded-lg bg-[#3478F6] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#2a66d6] disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[#64748B]">
          Pas encore de compte ?{" "}
          <Link href="/inscription" className="font-medium text-[#3478F6] hover:underline">
            Créer un compte
          </Link>
        </p>
      </div>
    </div>
  )
}
