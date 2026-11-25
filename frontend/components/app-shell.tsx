"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import Topbar from "@/components/topbar"

const PUBLIC_ROUTES = ["/login", "/inscription"]

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Tableau de bord",
    icon: (
      <path d="M3.75 3.75h6.5v6.5h-6.5v-6.5Zm10 0h6.5v6.5h-6.5v-6.5Zm-10 10h6.5v6.5h-6.5v-6.5Zm10 0h6.5v6.5h-6.5v-6.5Z" />
    ),
  },
  {
    href: "/documents",
    label: "Documents",
    icon: (
      <path d="M14 2.75H6.5A1.75 1.75 0 0 0 4.75 4.5v15A1.75 1.75 0 0 0 6.5 21.25h11A1.75 1.75 0 0 0 19.25 19.5V8.25L14 2.75Zm0 0v5.5h5.25M8.25 12.5h7.5M8.25 16h5" />
    ),
  },
  {
    href: "/generation",
    label: "Génération",
    icon: (
      <>
        <path d="M12 3.75v3m0 10.5v3m-5.25-8.25h-3m19.5 0h-3M6.7 6.7l2.1 2.1m6.4 6.4 2.1 2.1m0-10.6-2.1 2.1M8.8 15.2l-2.1 2.1" />
        <path d="M12 15.25a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" />
      </>
    ),
  },
  {
    href: "/planning",
    label: "Planification",
    icon: (
      <path d="M6.75 3v3m10.5-3v3M3.75 9.75h16.5M5.25 5.25h13.5A1.5 1.5 0 0 1 20.25 6.75v12A1.5 1.5 0 0 1 18.75 20.25H5.25A1.5 1.5 0 0 1 3.75 18.75v-12A1.5 1.5 0 0 1 5.25 5.25Z" />
    ),
  },
  {
    href: "/suivi",
    label: "Suivi",
    icon: (
      <path d="m4 6 1.5 1.5L8 5M4 12l1.5 1.5L8 11M4 18l1.5 1.5L8 17M11 6h9M11 12h9M11 18h9" />
    ),
  },
  {
    href: "/chat",
    label: "Assistant IA",
    icon: (
      <path d="M20.25 11.5a8.25 8.25 0 0 1-12.19 7.23L3.75 19.75l1.1-4.14A8.25 8.25 0 1 1 20.25 11.5Z" />
    ),
    ai: true,
  },
  {
    href: "/automations",
    label: "Studio Automations",
    icon: (
      <>
        <path d="M12 5v14M8 12h12M8 12H12"/>
        <path d="M12 5v14a2 2 0 002 2h2a2 2 0 002-2h-2m-2-4h2m-2-4h2m-6-6h2m6 6H10m4 0h6m3-3a2 2 0 11-4 0 2 2 0 014 0z"/>
      </>
    ),
    ai: true,
  },
  {
    href: "/marketplace",
    label: "Marketplace",
    icon: (
      <>
        <path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/>
        <circle cx="3" cy="3" r="1"/>
        <path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/>
        <path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/>
      </>
    ),
  },
  {
    href: "/knowledge",
    label: "Knowledge Hub",
    icon: (
      <>
        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        <circle cx="10" cy="10" r="7"/>
        <path d="M17 7L17 3"/>
        <path d="M3 3v18"/>
        <path d="M21 3v18M3 3h18"/>
      </>
    ),
  },
  {
    href: "/activities",
    label: "Activity Center",
    icon: (
      <path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/>
    ),
  },
  {
    href: "/reports",
    label: "Rapports",
    icon: (
      <>
        <path d="M12 7v5m0 0l2-2m2 2l-2-2m-6-6h2m6-6H10m5 10v5m0 0l2-2m0 2l2 2m-6 6h2m-6-6H10"/>
      </>
    ),
  },
  {
    href: "/connect",
    label: "Connect",
    icon: (
      <path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/>
    ),
    ai: true,
  },
  {
    href: "/settings",
    label: "Paramètres",
    icon: (
      <>
        <path d="M12 15.25a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" />
        <path d="M19.5 12c0-.46-.04-.9-.12-.12-1.8-1.4-1.94-3.36-2.13.86a7.6 7.6 0 0 0-2.32-1.34L14.4 3h-3.88l-.39 2.42a7.6 7.6 0 0 0-2.32 1.34l-2.13-.86-1.94 3.36 1.8 1.4a7.9 7.9 0 0 0 0 2.68l-1.8 1.4 1.94 3.36 2.13-.86c.69.56 1.47 1.01 2.32 1.34L10.52 21h3.88l.39-2.42a7.6 7.6 0 0 0 2.32-1.34l-2.13-.86 1.94 3.36 1.8 1.4c.08-.44.12-.88.12-1.34Z" />
      </>
    ),
  },
]

function NavIcon({ children, active, ai }: { children: React.ReactNode; active: boolean; ai?: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`h-[18px] w-[18px] shrink-0 transition-colors ${
        active ? "text-white" : ai ? "text-brand-ai" : "text-sidebar-muted group-hover:text-white"
      }`}
      aria-hidden="true"
    >
      {children}
    </svg>
  )
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  const isPublicRoute = PUBLIC_ROUTES.includes(pathname)
  const [session, setSession] = useState<{ checked: boolean; loggedIn: boolean }>({ checked: false, loggedIn: false })

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token && !isPublicRoute) {
      router.replace("/login")
    }
    const frame = requestAnimationFrame(() => {
      setSession({ checked: true, loggedIn: !!token })
      setMobileOpen(false)
    })
    return () => cancelAnimationFrame(frame)
  }, [router, isPublicRoute, pathname])

  const { checked: ready, loggedIn } = session

  if (!ready) return null

  if (isPublicRoute) {
    return <main className="min-h-screen bg-background">{children}</main>
  }

  if (!loggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <div className="sw-card p-8 text-center max-w-sm w-full">
          <p className="text-text-secondary mb-4">Session requise pour accéder à cet espace.</p>
          <Link href="/login" className="sw-btn-primary w-full">Se connecter</Link>
        </div>
      </div>
    )
  }

  const sidebarContent = (
    <>
      <div className="px-5 py-5 border-b border-white/10">
        <Link href="/dashboard" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-secondary text-white shadow-lg shadow-brand-secondary/30">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5" aria-hidden="true">
              <path d="M14 2.75H6.5A1.75 1.75 0 0 0 4.75 4.5v15A1.75 1.75 0 0 0 6.5 21.25h11A1.75 1.75 0 0 0 19.25 19.5V8.25L14 2.75Zm0 0v5.5h5.25" />
              <path d="M8.25 13h7.5M8.25 16.5h5" />
            </svg>
          </span>
          <span className="flex flex-col leading-tight">
            <span className="text-sm font-semibold tracking-tight text-white font-[family-name:var(--font-manrope)]">SmartWork AI</span>
            <span className="text-[11px] font-medium uppercase tracking-wider text-sidebar-muted">Espace de travail</span>
          </span>
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-5" aria-label="Navigation principale">
        <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-sidebar-muted">Navigation</p>
        <ul className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`)
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    active
                      ? "bg-sidebar-active text-white"
                      : "text-sidebar-text/85 hover:bg-sidebar-hover hover:text-white"
                  }`}
                >
                  {active && <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r bg-brand-secondary" aria-hidden="true" />}
                  <NavIcon active={active} ai={item.ai}>{item.icon}</NavIcon>
                  <span className="flex-1">{item.label}</span>
                  {item.ai && (
                    <span className="rounded-full bg-brand-ai/20 px-1.5 py-0.5 text-[10px] font-semibold text-brand-ai">IA</span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t border-white/10 p-3">
        <button
          onClick={() => {
            localStorage.removeItem("access_token")
            router.replace("/login")
          }}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-text/85 transition-colors hover:bg-sidebar-hover hover:text-white"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px] shrink-0 text-sidebar-muted" aria-hidden="true">
            <path d="M15.75 8.25 19.5 12l-3.75 3.75M19.5 12h-9M12 3.75H6.5A2.75 2.75 0 0 0 3.75 6.5v11A2.75 2.75 0 0 0 6.5 20.25H12" />
          </svg>
          Déconnexion
        </button>
      </div>
    </>
  )

  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <aside className="hidden lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-64 lg:shrink-0 lg:flex-col bg-sidebar text-sidebar-text border-r border-white/5">
          {sidebarContent}
        </aside>

        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-overlay backdrop-blur-[1px]"
              aria-label="Fermer la navigation"
              onClick={() => setMobileOpen(false)}
            />
            <aside className="absolute left-0 top-0 flex h-full w-72 max-w-[85vw] flex-col bg-sidebar text-sidebar-text shadow-elevated">
              <div className="absolute right-3 top-3">
                <button
                  type="button"
                  onClick={() => setMobileOpen(false)}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-sidebar-muted hover:bg-sidebar-hover hover:text-white"
                  aria-label="Fermer"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" className="h-4 w-4"><path d="M6 6l12 12M18 6 6 18" /></svg>
                </button>
              </div>
              {sidebarContent}
            </aside>
          </div>
        )}

        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar onMenuClick={() => setMobileOpen(true)} />
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <div className="mx-auto w-full max-w-7xl">{children}</div>
          </main>
        </div>
      </div>
    </div>
  )
}