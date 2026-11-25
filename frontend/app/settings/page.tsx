"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ThemeToggle from "@/components/theme-toggle"

function decodeEmail(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    return payload.sub ?? null
  } catch {
    return null
  }
}

export default function SettingsPage() {
  const router = useRouter()
  const [email, setEmail] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) { router.replace("/login"); return }
    const frame = requestAnimationFrame(() => setEmail(decodeEmail(token)))
    return () => cancelAnimationFrame(frame)
  }, [router])

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Configuration</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Paramètres</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Gérez votre compte et vos préférences d&apos;affichage.</p>
      </div>

      <div className="space-y-6 max-w-3xl">
        <section className="sw-card p-5 sm:p-6">
          <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)] mb-4">Compte</h2>
          <div className="space-y-4">
            <div>
              <p className="sw-label mb-1">Adresse email</p>
              <p className="text-sm text-text-primary bg-surface-muted/50 border border-border rounded-lg px-3 py-2.5">{email ?? "—"}</p>
            </div>
          </div>
        </section>

        <section className="sw-card p-5 sm:p-6">
          <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)] mb-1">Apparence</h2>
          <p className="text-sm text-text-secondary mb-4">Choisissez le thème d&apos;affichage de l&apos;interface.</p>
          <div className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface-muted/30 p-4">
            <div>
              <p className="text-sm font-medium text-text-primary">Thème</p>
              <p className="text-xs text-text-secondary">Clair ou sombre, enregistré sur cet appareil.</p>
            </div>
            <ThemeToggle />
          </div>
        </section>

        <section className="sw-card p-5 sm:p-6">
          <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)] mb-1">Session</h2>
          <p className="text-sm text-text-secondary mb-4">Déconnectez-vous de cet appareil.</p>
          <button
            onClick={() => { localStorage.removeItem("access_token"); router.replace("/login") }}
            className="inline-flex items-center justify-center rounded-lg border border-danger/25 bg-surface px-4 py-2.5 text-sm font-medium text-danger hover:bg-danger-soft transition-colors"
          >
            Se déconnecter
          </button>
        </section>
      </div>
    </div>
  )
}
