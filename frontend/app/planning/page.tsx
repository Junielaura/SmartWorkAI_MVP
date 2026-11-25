"use client"

import { useCallback, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ApiError, apiFetch, clearToken, getToken } from "@/lib/api"

type ReportSchedule = {
  id: number; frequency: string; timezone: string; next_execution: string | null;
  parameters: { recipients?: string[]; document_id?: number | string; [key: string]: unknown };
  is_active: boolean; organization_id?: number
}
type DocumentSummary = { id: number; filename: string; format: string }

const FREQUENCIES = [
  { value: "daily", label: "Quotidienne" },
  { value: "weekly", label: "Hebdomadaire" },
  { value: "monthly", label: "Mensuelle" },
]

function frequencyLabel(value: string): string {
  return FREQUENCIES.find((i) => i.value === value)?.label ?? value
}
function formatDate(value: string | null): string {
  if (!value) return "—"
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" })
}

export default function PlanningPage() {
  const router = useRouter()
  const [schedules, setSchedules] = useState<ReportSchedule[]>([])
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [frequency, setFrequency] = useState("weekly")
  const [timezone, setTimezone] = useState("Europe/Paris")
  const [recipients, setRecipients] = useState("")
  const [documentId, setDocumentId] = useState("")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError && err.status === 401) { clearToken(); router.replace("/login"); return }
    setError(err instanceof Error ? err.message : "Une erreur est survenue")
  }, [router])

  const loadSchedules = useCallback(async () => {
    const [scheduleData, documentData] = await Promise.all([
      apiFetch<{ schedules: ReportSchedule[] }>("/api/v1/reporting/schedules"),
      apiFetch<{ documents: DocumentSummary[] }>("/api/v1/documents"),
    ])
    setSchedules(scheduleData.schedules ?? [])
    setDocuments(documentData.documents ?? [])
    setDocumentId((cur) => cur || (documentData.documents?.[0] ? String(documentData.documents[0].id) : ""))
  }, [])

  useEffect(() => {
    if (!getToken()) { router.replace("/login"); return }
    let active = true
    void (async () => {
      setLoading(true)
      try {
        await loadSchedules()
      } catch (e) {
        if (active) handleError(e)
      } finally {
        if (active) setLoading(false)
      }
    })()
    return () => { active = false }
  }, [handleError, loadSchedules, router])

  const createSchedule = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (saving) return
    setSaving(true); setError(null); setSuccess(null)
    try {
      const recipientList = recipients.split(",").map((i) => i.trim()).filter(Boolean)
      await apiFetch("/api/v1/reporting/schedules", {
        method: "POST",
        body: JSON.stringify({ frequency, timezone, parameters: { document_id: Number(documentId), recipients: recipientList }, is_active: true }),
      })
      setRecipients("")
      setSuccess("Planification créée avec succès.")
      await loadSchedules()
    } catch (err) { handleError(err) }
    finally { setSaving(false) }
  }

  const toggleActive = async (schedule: ReportSchedule) => {
    setBusyId(schedule.id); setError(null)
    try {
      await apiFetch(`/api/v1/reporting/schedules/${schedule.id}`, { method: "PUT", body: JSON.stringify({ is_active: !schedule.is_active }) })
      await loadSchedules()
    } catch (err) { handleError(err) }
    finally { setBusyId(null) }
  }

  const triggerNow = async (schedule: ReportSchedule) => {
    setBusyId(schedule.id); setError(null); setSuccess(null)
    try {
      const result = await apiFetch<{ report_id: number; filename: string }>(`/api/v1/reporting/schedules/${schedule.id}/generate?force=true`, { method: "POST" })
      setSuccess(`Brouillon généré (rapport #${result.report_id}). Retrouvez-le dans l'historique des générations.`)
    } catch (err) { handleError(err) }
    finally { setBusyId(null) }
  }

  const removeSchedule = async (schedule: ReportSchedule) => {
    if (!window.confirm("Supprimer cette planification ?")) return
    setBusyId(schedule.id); setError(null); setSuccess(null)
    try {
      await apiFetch(`/api/v1/reporting/schedules/${schedule.id}`, { method: "DELETE" })
      setSuccess("Planification supprimée.")
      await loadSchedules()
    } catch (err) { handleError(err) }
    finally { setBusyId(null) }
  }

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Module rapports</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Planification</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Programmez la production récurrente de rapports et déclenchez-les à la demande.</p>
      </div>

      {error && <div className="mb-6 rounded-lg border border-danger/20 bg-danger-soft p-4 text-sm text-danger" role="alert">{error}</div>}
      {success && <div className="mb-6 rounded-lg border border-brand-accent/20 bg-success-soft p-4 text-sm text-brand-accent" role="status">{success}</div>}

      <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
        <form onSubmit={createSchedule} className="sw-card p-5 sm:p-6 space-y-5 h-fit">
          <div>
            <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Nouvelle planification</h2>
            <p className="text-sm text-text-secondary mt-1">Un brouillon est créé à chaque exécution avant validation.</p>
          </div>

          <div>
            <label htmlFor="frequency" className="sw-label">Fréquence</label>
            <select id="frequency" value={frequency} onChange={(e) => setFrequency(e.target.value)} className="sw-input">
              {FREQUENCIES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </div>

          <div>
            <label htmlFor="timezone" className="sw-label">Fuseau horaire</label>
            <input id="timezone" value={timezone} onChange={(e) => setTimezone(e.target.value)} placeholder="Europe/Paris" className="sw-input" />
          </div>

          <div>
            <label htmlFor="documentId" className="sw-label">Document source</label>
            <select id="documentId" value={documentId} onChange={(e) => setDocumentId(e.target.value)} disabled={documents.length === 0} className="sw-input disabled:opacity-60">
              {documents.length === 0 && <option value="">Aucun document disponible</option>}
              {documents.map((d) => <option key={d.id} value={d.id}>{d.filename} ({d.format.toUpperCase()})</option>)}
            </select>
          </div>

          <div>
            <label htmlFor="recipients" className="sw-label">Destinataires <span className="text-text-muted font-normal">(optionnel)</span></label>
            <input id="recipients" value={recipients} onChange={(e) => setRecipients(e.target.value)} placeholder="alice@exemple.fr, bob@exemple.fr" className="sw-input" />
            <p className="text-xs text-text-muted mt-1.5">Emails séparés par des virgules.</p>
          </div>

          <button type="submit" disabled={saving || !documentId} className="sw-btn-primary w-full">
            {saving ? "Enregistrement…" : "Programmer le rapport"}
          </button>
        </form>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Planifications</h2>
            <span className="sw-badge sw-badge-neutral">{schedules.length}</span>
          </div>

          {loading ? (
            <p className="text-sm text-text-secondary">Chargement…</p>
          ) : schedules.length === 0 ? (
            <div className="sw-card p-10 text-center border-dashed">
              <p className="text-sm text-text-secondary">Aucune planification. Créez-en une pour automatiser vos rapports.</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {schedules.map((schedule) => (
                <li key={schedule.id} className="sw-card p-5">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-semibold text-text-primary font-[family-name:var(--font-manrope)]">
                          Rapport {frequencyLabel(schedule.frequency).toLowerCase()}
                        </span>
                        <span className={schedule.is_active ? "sw-badge sw-badge-success" : "sw-badge sw-badge-warning"}>
                          {schedule.is_active ? "Active" : "En pause"}
                        </span>
                      </div>
                      <p className="text-sm text-text-secondary mt-1">Fuseau : {schedule.timezone} · Prochaine exécution : {formatDate(schedule.next_execution)}</p>
                      {schedule.parameters?.document_id && (
                        <p className="text-sm text-text-secondary mt-0.5">
                          Source : {documents.find((d) => String(d.id) === String(schedule.parameters.document_id))?.filename ?? `document #${schedule.parameters.document_id}`}
                        </p>
                      )}
                      {schedule.parameters?.recipients && schedule.parameters.recipients.length > 0 && (
                        <p className="text-sm text-text-secondary mt-0.5">Destinataires : {schedule.parameters.recipients.join(", ")}</p>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-2 shrink-0">
                      <button onClick={() => triggerNow(schedule)} disabled={busyId === schedule.id} className="sw-btn-primary !px-3 !py-1.5 !text-xs">
                        {busyId === schedule.id ? "…" : "Générer"}
                      </button>
                      <button onClick={() => toggleActive(schedule)} disabled={busyId === schedule.id} className="sw-btn-secondary !px-3 !py-1.5 !text-xs">
                        {schedule.is_active ? "Pause" : "Activer"}
                      </button>
                      <button onClick={() => removeSchedule(schedule)} disabled={busyId === schedule.id} className="inline-flex items-center justify-center rounded-lg border border-danger/25 bg-surface px-3 py-1.5 text-xs font-medium text-danger hover:bg-danger-soft disabled:opacity-60 transition-colors">
                        Supprimer
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
