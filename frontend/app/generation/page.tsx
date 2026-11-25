"use client"

import { useCallback, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ApiError, apiDownload, apiFetch, clearToken, getToken } from "@/lib/api"

type DocumentSummary = { id: number; filename: string; format: string; status: string }
type GeneratedFile = {
  id: number; filename: string; format: string; model_version: string; status: string;
  created_at: string | null; validated_at: string | null; document_id: number | null
}
type GenerationKind = "summary" | "docx" | "xlsx"

const KIND_OPTIONS: { value: GenerationKind; label: string; hint: string; ai?: boolean }[] = [
  { value: "summary", label: "Rapport de synthèse (DOCX)", hint: "Résumé structuré du document sélectionné.", ai: true },
  { value: "docx", label: "Rapport complet (DOCX)", hint: "Livrable professionnel mis en forme.", ai: true },
  { value: "xlsx", label: "Tableur de données (XLSX)", hint: "Extrait les tableaux et données structurées." },
]

const STATUS_LABELS: Record<string, string> = { draft: "Brouillon", validated: "Validé", approved: "Approuvé", published: "Publié", error: "Erreur" }

function formatDate(value: string | null): string {
  if (!value) return "—"
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" })
}

function statusClass(status: string): string {
  switch (status) {
    case "validated": case "approved": case "published": return "sw-badge sw-badge-success"
    case "error": return "sw-badge sw-badge-danger"
    default: return "sw-badge sw-badge-warning"
  }
}

export default function GenerationPage() {
  const router = useRouter()
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [history, setHistory] = useState<GeneratedFile[]>([])
  const [documentId, setDocumentId] = useState<string>("")
  const [kind, setKind] = useState<GenerationKind>("summary")
  const [tone, setTone] = useState("professional")
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError && err.status === 401) { clearToken(); router.replace("/login"); return }
    setError(err instanceof Error ? err.message : "Une erreur est survenue")
  }, [router])

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [documentsData, historyData] = await Promise.all([
        apiFetch<{ documents: DocumentSummary[] }>("/api/v1/documents"),
        apiFetch<{ files: GeneratedFile[] }>("/api/v1/generation/history"),
      ])
      setDocuments(documentsData.documents ?? [])
      setHistory(historyData.files ?? [])
      setDocumentId((current) => current || (documentsData.documents?.[0] ? String(documentsData.documents[0].id) : ""))
    } catch (err) { handleError(err) }
    finally { setLoading(false) }
  }, [handleError])

  useEffect(() => {
    if (!getToken()) { router.replace("/login"); return }
    const frame = requestAnimationFrame(() => { void loadData() })
    return () => cancelAnimationFrame(frame)
  }, [loadData, router])

  const generate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!documentId || generating) return
    setGenerating(true); setError(null); setSuccess(null)
    try {
      if (kind === "xlsx") {
        await apiFetch(`/api/v1/generation/xlsx?document_id=${documentId}`, { method: "POST" })
      } else if (kind === "docx") {
        await apiFetch(`/api/v1/generation/docx?document_id=${documentId}&tone=${encodeURIComponent(tone)}`, { method: "POST" })
      } else {
        await apiFetch(`/api/v1/generation/summary/${documentId}?tone=${encodeURIComponent(tone)}`, { method: "POST" })
      }
      setSuccess("Livrable généré. Il est disponible dans l'historique ci-dessous.")
      const historyData = await apiFetch<{ files: GeneratedFile[] }>("/api/v1/generation/history")
      setHistory(historyData.files ?? [])
    } catch (err) { handleError(err) }
    finally { setGenerating(false) }
  }

  const download = async (file: GeneratedFile) => {
    setError(null)
    try {
      await apiDownload(`/api/v1/generation/file/${file.id}`, file.filename)
      const historyData = await apiFetch<{ files: GeneratedFile[] }>("/api/v1/generation/history")
      setHistory(historyData.files ?? [])
    } catch (err) { handleError(err) }
  }

  const selectedKind = KIND_OPTIONS.find((o) => o.value === kind)

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Module génération</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Génération de livrables</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Produisez des documents professionnels à partir de vos sources analysées.</p>
      </div>

      {error && <div className="mb-6 rounded-lg border border-danger/20 bg-danger-soft p-4 text-sm text-danger" role="alert">{error}</div>}
      {success && <div className="mb-6 rounded-lg border border-brand-accent/20 bg-success-soft p-4 text-sm text-brand-accent" role="status">{success}</div>}

      <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
        <form onSubmit={generate} className="sw-card p-5 sm:p-6 space-y-5 h-fit">
          <div>
            <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Nouveau livrable</h2>
            <p className="text-sm text-text-secondary mt-1">Choisissez la source et le format de sortie.</p>
          </div>

          <div>
            <label htmlFor="document" className="sw-label">Document source</label>
            <select id="document" value={documentId} onChange={(e) => setDocumentId(e.target.value)} disabled={loading || documents.length === 0} className="sw-input disabled:opacity-60">
              {documents.length === 0 && <option value="">Aucun document disponible</option>}
              {documents.map((d) => <option key={d.id} value={d.id}>{d.filename} ({d.format.toUpperCase()})</option>)}
            </select>
          </div>

          <div>
            <label htmlFor="kind" className="sw-label">
              <span className="inline-flex items-center gap-2">
                Type de livrable
                {selectedKind?.ai && <span className="sw-badge sw-badge-ai !text-[10px] !px-1.5 !py-0">IA</span>}
              </span>
            </label>
            <select id="kind" value={kind} onChange={(e) => setKind(e.target.value as GenerationKind)} className="sw-input">
              {KIND_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <p className="text-xs text-text-secondary mt-1.5">{selectedKind?.hint}</p>
          </div>

          {kind !== "xlsx" && (
            <div>
              <label htmlFor="tone" className="sw-label">Ton</label>
              <select id="tone" value={tone} onChange={(e) => setTone(e.target.value)} className="sw-input">
                <option value="professional">Professionnel</option>
                <option value="concise">Concis</option>
                <option value="detailed">Détaillé</option>
              </select>
            </div>
          )}

          <button type="submit" disabled={!documentId || generating} className={selectedKind?.ai ? "sw-btn-ai w-full" : "sw-btn-primary w-full"}>
            {generating ? "Génération en cours…" : selectedKind?.ai ? "Générer avec l'IA" : "Générer le livrable"}
          </button>
        </form>

        <section className="sw-card overflow-hidden">
          <div className="px-5 py-4 border-b border-border">
            <h2 className="text-base font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Historique des générations</h2>
            <p className="text-sm text-text-secondary mt-0.5">Les fichiers générés sont conservés comme brouillons avant validation.</p>
          </div>

          {loading ? (
            <p className="px-6 py-10 text-sm text-text-secondary">Chargement…</p>
          ) : history.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <p className="text-sm text-text-secondary">Aucun livrable généré pour le moment.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-surface-muted/60 text-left text-xs uppercase tracking-wider text-text-secondary">
                  <tr>
                    <th className="px-5 py-3 font-medium">Fichier</th>
                    <th className="px-5 py-3 font-medium">Format</th>
                    <th className="px-5 py-3 font-medium">Statut</th>
                    <th className="px-5 py-3 font-medium">Créé le</th>
                    <th className="px-5 py-3 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {history.map((file) => (
                    <tr key={file.id} className="hover:bg-surface-muted/30 transition-colors">
                      <td className="px-5 py-3 font-medium text-text-primary max-w-[240px] truncate">{file.filename}</td>
                      <td className="px-5 py-3 text-text-secondary uppercase text-xs">{file.format}</td>
                      <td className="px-5 py-3"><span className={statusClass(file.status)}>{STATUS_LABELS[file.status] ?? file.status}</span></td>
                      <td className="px-5 py-3 text-text-secondary text-xs whitespace-nowrap">{formatDate(file.created_at)}</td>
                      <td className="px-5 py-3 text-right">
                        <button onClick={() => download(file)} className="text-brand-secondary font-medium hover:underline text-sm">Télécharger</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
