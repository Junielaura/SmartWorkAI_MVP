"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type DashboardOverview = {
  task_statistics: {
    total: number
    by_status: Record<string, number>
    recent: { id: number; title: string; status: string }[]
  }
  document_statistics: {
    total: number
    by_status: Record<string, number>
  }
}

function decodeEmail(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    return payload.sub ?? null
  } catch {
    return null
  }
}

const STATUS_META: Record<string, { label: string; cls: string }> = {
  to_do: { label: "À faire", cls: "sw-badge sw-badge-neutral" },
  in_progress: { label: "En cours", cls: "sw-badge sw-badge-info" },
  validated: { label: "Validé", cls: "sw-badge sw-badge-success" },
  approved: { label: "Approuvé", cls: "sw-badge sw-badge-success" },
  completed: { label: "Terminé", cls: "sw-badge sw-badge-success" },
  rejected: { label: "Rejeté", cls: "sw-badge sw-badge-danger" },
  error: { label: "Erreur", cls: "sw-badge sw-badge-danger" },
}

export default function DashboardPage() {
  const router = useRouter()
  const [email, setEmail] = useState<string | null>(null)
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.replace("/login")
      return
    }
    const frame = requestAnimationFrame(() => setEmail(decodeEmail(token)))

    fetch("/api/v1/tasks/dashboard/overview", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        if (response.status === 401) {
          localStorage.removeItem("access_token")
          router.replace("/login")
          return null
        }
        if (!response.ok) throw new Error(`Erreur ${response.status}`)
        return response.json()
      })
      .then((data) => {
        if (data) setOverview(data)
      })
      .catch((err) => setError(err.message))
    return () => cancelAnimationFrame(frame)
  }, [router])

  const kpis = [
    {
      label: "Tâches totales",
      value: overview?.task_statistics.total ?? "—",
      tone: "text-brand-secondary",
      bg: "bg-info-soft",
      icon: <path d="M9 11l2 2 4-4m5 2a9 9 0 11-18 0 9 9 0 0118 0z" />,
    },
    {
      label: "Tâches en cours",
      value: overview?.task_statistics.by_status.in_progress ?? "—",
      tone: "text-warning",
      bg: "bg-warning-soft",
      icon: <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />,
    },
    {
      label: "Documents",
      value: overview?.document_statistics.total ?? "—",
      tone: "text-brand-primary dark:text-brand-secondary",
      bg: "bg-surface-muted",
      icon: <path d="M14 2.75H6.5A1.75 1.75 0 0 0 4.75 4.5v15A1.75 1.75 0 0 0 6.5 21.25h11A1.75 1.75 0 0 0 19.25 19.5V8.25L14 2.75Zm0 0v5.5h5.25" />,
    },
    {
      label: "Documents traités",
      value: overview?.document_statistics.by_status.processed ?? "—",
      tone: "text-brand-accent",
      bg: "bg-success-soft",
      icon: <path d="M5 13l4 4L19 7" />,
    },
    {
      label: "Activités récentes",
      value: overview?.activity_statistics?.total ?? "—",
      tone: "text-brand-warning",
      bg: "bg-warning-soft",
      icon: <path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6" />,
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Vue d&apos;ensemble</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Tableau de bord</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">
          {email ? `Connecté en tant que ${email}` : "Bienvenue sur SmartWork AI"}
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-danger/20 bg-danger-soft p-4 text-sm text-danger" role="alert">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="sw-card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm text-text-secondary">{kpi.label}</p>
                <p className={`text-3xl font-semibold mt-2 font-[family-name:var(--font-manrope)] ${kpi.tone}`}>
                  {kpi.value}
                </p>
              </div>
              <span className={`inline-flex h-10 w-10 items-center justify-center rounded-lg ${kpi.bg} ${kpi.tone}`}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5" aria-hidden="true">{kpi.icon}</svg>
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="sw-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Tâches récentes</h2>
            <p className="text-sm text-text-secondary">Dernières tâches accessibles dans votre espace</p>
          </div>
          <span className="sw-badge sw-badge-info">{overview?.task_statistics.recent.length ?? 0}</span>
        </div>
        {overview && overview.task_statistics.recent.length > 0 ? (
          <ul className="divide-y divide-border">
            {overview.task_statistics.recent.map((task) => {
              const meta = STATUS_META[task.status] ?? { label: task.status, cls: "sw-badge sw-badge-neutral" }
              return (
                <li key={task.id} className="px-5 py-3.5 flex items-center justify-between gap-3">
                  <span className="text-sm text-text-primary font-medium truncate">{task.title}</span>
                  <span className={meta.cls}>{meta.label}</span>
                </li>
              )
            })}
          </ul>
        ) : (
          <div className="px-5 py-10 text-center">
            <p className="text-sm text-text-secondary">Aucune tâche pour le moment.</p>
          </div>
        )}
      </div>
    </div>
  )
}
