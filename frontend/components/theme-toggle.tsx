"use client"

import { useSyncExternalStore } from "react"

function subscribe(callback: () => void) {
  const obs = new MutationObserver(callback)
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
  window.addEventListener("storage", callback)
  return () => {
    obs.disconnect()
    window.removeEventListener("storage", callback)
  }
}

function getSnapshot() {
  return document.documentElement.classList.contains("dark")
}

function getServerSnapshot() {
  return false
}

export default function ThemeToggle() {
  const dark = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
  const mounted = useSyncExternalStore(() => () => {}, () => true, () => false)

  const toggle = () => {
    const next = !dark
    document.documentElement.classList.toggle("dark", next)
    try {
      localStorage.setItem("sw-theme", next ? "dark" : "light")
    } catch {
      /* ignore */
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={mounted && dark ? "Activer le mode clair" : "Activer le mode sombre"}
      title={mounted && dark ? "Mode clair" : "Mode sombre"}
      className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface text-text-secondary transition-colors hover:bg-surface-muted hover:text-text-primary"
    >
      {mounted && dark ? (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px]" aria-hidden="true">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2.5v2.5M12 19v2.5M4.22 4.22l1.77 1.77M17.95 17.95l1.83 1.83M2.5 12H5M19 12h2.5M4.22 19.78l1.77-1.77M17.95 6.05l1.83-1.83" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px]" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3c.2 0 .4 0 .6.02A7 7 0 0 0 20.98 12.2c.01.2.02.39.02.59Z" />
        </svg>
      )}
    </button>
  )
}
