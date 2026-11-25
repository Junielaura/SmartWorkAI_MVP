"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { ApiError, apiFetch, clearToken, getToken } from "@/lib/api"

type Task = {
  id: number
  title: string
  status: string
  assigned_to_id: number | null
  organization_id: number | null
  due_date: string | null
  comments?: Record<string, unknown>
}

type Column = { key: string; label: string; statuses: string[]; dot: string }

const COLUMNS: Column[] = [
  { key: "to_do", label: "À faire", statuses: ["to_do"], dot: "bg-text-muted" },
  { key: "in_progress", label: "En cours", statuses: ["in_progress", "rejected", "error"], dot: "bg-brand-secondary" },
  { key: "validated", label: "Validé", statuses: ["validated", "approved"], dot: "bg-brand-accent" },
  { key: "completed", label: "Terminé", statuses: ["completed"], dot: "bg-brand-accent" },
]

const STATUS_OPTIONS = [
  { value: "to_do", label: "À faire" },
  { value: "in_progress", label: "En cours" },
  { value: "validated", label: "Validé" },
  { value: "approved", label: "Approuvé" },
  { value: "rejected", label: "Rejeté" },
  { value: "error", label: "Erreur" },
  { value: "completed", label: "Terminé" },
]

const STATUS_LABELS: Record<string, string> = Object.fromEntries(STATUS_OPTIONS.map((o) => [o.value, o.label]))

function formatDate(value: string | null): string {
  if (!value) return "—"
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleDateString("fr-FR", { dateStyle: "medium" })
}

function isOverdue(task: Task): boolean {
  if (!task.due_date) return false
  if (["completed", "validated", "approved"].includes(task.status)) return false
  const date = new Date(task.due_date)
  if (Number.isNaN(date.getTime())) return false
  return date.getTime() < Date.now()
}

export default function SuiviPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [title, setTitle] = useState("")
  const [dueDate, setDueDate] = useState("")
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError && err.status === 401) { clearToken(); router.replace("/login"); return }
    setError(err instanceof Error ? err.message : "Une erreur est survenue")
  }, [router])

  const loadTasks = useCallback(async () => {
    const data = await apiFetch<{ tasks: Task[] }>("/api/v1/tasks")
    setTasks(data.tasks ?? [])
  }, [])

  useEffect(() => {
    if (!getToken()) { router.replace("/login"); return }
    let active = true
    void (async () => {
      setLoading(true)
      try {
        await loadTasks()
      } catch (err) {
        if (active) handleError(err)
      } finally {
        if (active) setLoading(false)
      }
    })()
    return () => { active = false }
  }, [handleError, loadTasks, router])

  const stats = useMemo(() => {
    const inProgress = tasks.filter((t) => ["in_progress", "rejected", "error"].includes(t.status)).length
    const done = tasks.filter((t) => ["validated", "approved", "completed"].includes(t.status)).length
    return { total: tasks.length, inProgress, done, toDo: tasks.filter((t) => t.status === "to_do").length }
  }, [tasks])

  const createTask = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = title.trim()
    if (!trimmed || creating) return
    setCreating(true); setError(null); setSuccess(null)
    try {
      const params = new URLSearchParams({ title: trimmed })
      if (dueDate) params.set("due_date", dueDate)
      await apiFetch(`/api/v1/tasks?${params.toString()}`, { method: "POST" })
      setTitle(""); setDueDate("")
      setSuccess("Tâche créée et assignée.")
      await loadTasks()
    } catch (err) { handleError(err) }
    finally { setCreating(false) }
  }

  const updateStatus = async (task: Task, newStatus: string) => {
    if (newStatus === task.status) return
    setBusyId(task.id); setError(null); setSuccess(null)
    try {
      await apiFetch(`/api/v1/tasks/${task.id}/status?new_status=${encodeURIComponent(newStatus)}`, { method: "PATCH" })
      setSuccess("Statut mis à jour.")
      await loadTasks()
    } catch (err) { handleError(err) }
    finally { setBusyId(null) }
  }

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Module workflows</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Suivi des tâches</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Suivez l&apos;avancement des tâches issues de vos documents.</p>
      </div>

      {error && <div className="mb-6 rounded-lg border border-danger/20 bg-danger-soft p-4 text-sm text-danger" role="alert">{error}</div>}
      {success && <div className="mb-6 rounded-lg border border-brand-accent/20 bg-success-soft p-4 text-sm text-brand-accent" role="status">{success}</div>}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        {[
          { label: "Tâches totales", value: stats.total, tone: "text-text-primary" },
          { label: "À faire", value: stats.toDo, tone: "text-text-secondary" },
          { label: "En cours", value: stats.inProgress, tone: "text-brand-secondary" },
          { label: "Clôturées", value: stats.done, tone: "text-brand-accent" },
        ].map((item) => (
          <div key={item.label} className="sw-card p-5">
            <p className="text-sm text-text-secondary">{item.label}</p>
            <p className={`text-3xl font-semibold mt-1 font-[family-name:var(--font-manrope)] ${item.tone}`}>{item.value}</p>
          </div>
        ))}
      </div>

      <form onSubmit={createTask} className="sw-card p-5 mb-8 flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="title" className="sw-label">Nouvelle tâche</label>
          <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ex. Valider le rapport mensuel" className="sw-input" />
        </div>
        <div className="sm:w-44">
          <label htmlFor="due" className="sw-label">Échéance</label>
          <input id="due" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="sw-input" />
        </div>
        <button type="submit" disabled={!title.trim() || creating} className="sw-btn-primary shrink-0">
          {creating ? "Création…" : "Créer la tâche"}
        </button>
      </form>

      {loading ? (
        <p className="text-sm text-text-secondary">Chargement…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {COLUMNS.map((column) => {
            const columnTasks = tasks.filter((t) => column.statuses.includes(t.status))
            return (
              <section key={column.key} className="rounded-xl border border-border bg-surface-muted/40 p-3 flex flex-col min-h-[180px]">
                <div className="flex items-center justify-between px-1 pb-3">
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${column.dot}`} aria-hidden="true" />
                    <h2 className="text-sm font-semibold text-text-primary font-[family-name:var(--font-manrope)]">{column.label}</h2>
                  </div>
                  <span className="text-xs font-medium text-text-secondary bg-surface rounded-full px-2 py-0.5 border border-border">{columnTasks.length}</span>
                </div>

                <div className="space-y-2.5">
                  {columnTasks.length === 0 && <p className="text-xs text-text-muted px-1 py-4 text-center">Aucune tâche</p>}
                  {columnTasks.map((task) => {
                    const overdue = isOverdue(task)
                    return (
                      <article key={task.id} className="bg-surface rounded-lg border border-border shadow-card p-3">
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium text-text-primary leading-snug">{task.title}</p>
                          {["rejected", "error"].includes(task.status) && (
                            <span className="sw-badge sw-badge-danger !text-[10px] !px-1.5 shrink-0">{STATUS_LABELS[task.status]}</span>
                          )}
                        </div>

                        <p className={`text-xs mt-2 ${overdue ? "text-danger font-medium" : "text-text-secondary"}`}>
                          Échéance : {formatDate(task.due_date)}
                          {overdue ? " · en retard" : ""}
                        </p>

                        <label className="sr-only" htmlFor={`status-${task.id}`}>Statut de {task.title}</label>
                        <select
                          id={`status-${task.id}`}
                          value={task.status}
                          onChange={(e) => updateStatus(task, e.target.value)}
                          disabled={busyId === task.id}
                          className="mt-3 w-full rounded-md border border-border bg-surface px-2 py-1.5 text-xs text-text-primary disabled:opacity-60 focus:border-brand-secondary focus:outline-none"
                        >
                          {STATUS_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                        </select>
                      </article>
                    )
                  })}
                </div>
              </section>
            )
          })}
        </div>
      )}
    </div>
  )
}
