"use client"

import { usePathname } from "next/navigation"
import ThemeToggle from "@/components/theme-toggle"

const TITLES: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": { title: "Tableau de bord", subtitle: "Vue d'ensemble de votre activité" },
  "/documents": { title: "Documents", subtitle: "Gestion documentaire et extraction" },
  "/generation": { title: "Génération", subtitle: "Production de livrables professionnels" },
  "/planning": { title: "Planification", subtitle: "Rapports périodiques et automatisation" },
  "/suivi": { title: "Suivi", subtitle: "Tâches, workflows et avancement" },
  "/chat": { title: "Assistant IA", subtitle: "Dialogue intelligent sur vos documents" },
  "/settings": { title: "Paramètres", subtitle: "Compte et préférences" },
}

export default function Topbar({ onMenuClick }: { onMenuClick?: () => void }) {
  const pathname = usePathname()
  const entry =
    Object.entries(TITLES).find(([href]) => pathname === href || pathname.startsWith(`${href}/`))?.[1] ??
    { title: "SmartWork AI", subtitle: "Espace de travail" }

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-surface/95 backdrop-blur supports-[backdrop-filter]:bg-surface/90">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface text-text-secondary hover:bg-surface-muted lg:hidden"
          aria-label="Ouvrir la navigation"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" className="h-5 w-5" aria-hidden="true">
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>

        <div className="min-w-0 flex-1">
          <nav aria-label="Fil d'Ariane" className="hidden sm:block text-[11px] text-text-muted mb-0.5">
            <span>SmartWork AI</span>
            <span className="mx-1.5">/</span>
            <span className="text-text-secondary">{entry.title}</span>
          </nav>
          <p className="truncate text-sm font-semibold text-text-primary sm:text-base font-[family-name:var(--font-manrope)]">
            {entry.title}
          </p>
          <p className="hidden truncate text-xs text-text-secondary md:block">{entry.subtitle}</p>
        </div>

        <div className="hidden md:block w-full max-w-xs lg:max-w-sm">
          <label htmlFor="global-search" className="sr-only">Recherche globale</label>
          <div className="relative">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              id="global-search"
              type="search"
              placeholder="Rechercher..."
              className="sw-input !py-2 !pl-9 !pr-3 !text-sm"
              readOnly
              aria-readonly="true"
              title="Recherche disponible prochainement"
            />
          </div>
        </div>

        <button
          type="button"
          className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface text-text-secondary transition-colors hover:bg-surface-muted hover:text-text-primary"
          aria-label="Notifications, aucune nouvelle notification"
          title="Notifications"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px]" aria-hidden="true">
            <path d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.17V11a6 6 0 1 0-12 0v3.17a2 2 0 0 1-.6 1.43L4 17h5m6 0a3 3 0 0 1-6 0" />
          </svg>
        </button>

        <ThemeToggle />

        <div className="hidden sm:flex h-9 w-9 items-center justify-center rounded-full bg-brand-secondary/12 text-brand-secondary text-xs font-semibold border border-brand-secondary/20" aria-label="Profil utilisateur" title="Profil">
          SW
        </div>
      </div>
    </header>
  )
}
