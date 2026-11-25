"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"

type DocumentSummary = {
  id: number
  filename: string
  format: string
  status: string
  size: number | null
  uploaded_at: string | null
  classification: string | null
  classification_confidence: number | null
  classification_confirmed: boolean
}

type Chunk = {
  id: number
  content_text: string
  chunk_type: string
  index_position: number
  metadata: Record<string, unknown>
}

type DocumentDetail = DocumentSummary & {
  extracted_data: {
    text?: string
    tables?: unknown[]
    metadata?: Record<string, unknown>
  } | null
  provenance: Record<string, unknown> | null
  chunks: Chunk[]
}

const CATEGORIES = [
  "rapport",
  "tableau de données",
  "compte rendu",
  "facture",
  "document administratif",
  "autre",
]

function formatProvenance(metadata: Record<string, unknown>): string {
  const parts: string[] = []
  if (metadata.page) parts.push(`page ${metadata.page}`)
  if (metadata.sheet) parts.push(`feuille ${metadata.sheet}`)
  if (metadata.paragraph !== undefined && metadata.paragraph !== null) parts.push(`paragraphe ${metadata.paragraph}`)
  if (metadata.table !== undefined && metadata.table !== null) parts.push(`tableau ${metadata.table}`)
  return parts.length ? parts.join(", ") : "source"
}

function statusBadge(status: string) {
  const map: Record<string, { label: string; cls: string }> = {
    processed: { label: "Traité", cls: "sw-badge sw-badge-success" },
    completed: { label: "Traité", cls: "sw-badge sw-badge-success" },
    processing: { label: "En traitement", cls: "sw-badge sw-badge-warning" },
    pending: { label: "En attente", cls: "sw-badge sw-badge-warning" },
    uploaded: { label: "Importé", cls: "sw-badge sw-badge-info" },
    error: { label: "Erreur", cls: "sw-badge sw-badge-danger" },
    failed: { label: "Erreur", cls: "sw-badge sw-badge-danger" },
  }
  const m = map[status] ?? { label: status, cls: "sw-badge sw-badge-neutral" }
  return <span className={m.cls}>{m.label}</span>
}

export default function DocumentsPage() {
  const router = useRouter()
  const fileInput = useRef<HTMLInputElement>(null)
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [detail, setDetail] = useState<DocumentDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [category, setCategory] = useState("")
  const [savingCategory, setSavingCategory] = useState(false)

  const token = () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null)

  const handleUnauthorized = (response: Response): boolean => {
    if (response.status === 401) {
      localStorage.removeItem("access_token")
      router.replace("/login")
      return true
    }
    return false
  }

  const loadDocuments = async () => {
    const accessToken = token()
    if (!accessToken) { router.replace("/login"); return }
    const response = await fetch("/api/v1/documents", { headers: { Authorization: `Bearer ${accessToken}` } })
    if (handleUnauthorized(response)) return
    if (!response.ok) throw new Error(`Erreur ${response.status}`)
    const data = await response.json()
    setDocuments(data.documents ?? [])
  }

  const openDocument = async (id: number) => {
    const accessToken = token()
    if (!accessToken) return
    const response = await fetch(`/api/v1/documents/${id}`, { headers: { Authorization: `Bearer ${accessToken}` } })
    if (handleUnauthorized(response)) return
    if (!response.ok) { setError(`Impossible de charger le document (${response.status})`); return }
    const data: DocumentDetail = await response.json()
    setDetail(data)
    setCategory(data.classification ?? "")
  }

  useEffect(() => {
    let active = true
    const load = async () => {
      try { await loadDocuments() }
      catch (err) { if (active) setError(err instanceof Error ? err.message : "Échec du chargement") }
      finally { if (active) setLoading(false) }
    }
    void load()
    return () => { active = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router])

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const file = fileInput.current?.files?.[0]
    if (!file) { setError("Sélectionnez un fichier PDF, DOCX, XLSX ou CSV."); return }
    const accessToken = token()
    if (!accessToken) return
    setUploading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append("file", file)
      const response = await fetch("/api/v1/documents/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
        body: formData,
      })
      if (handleUnauthorized(response)) return
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      const created = await response.json()
      if (fileInput.current) fileInput.current.value = ""
      await loadDocuments()
      await openDocument(created.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de l'import")
    } finally {
      setUploading(false)
    }
  }

  const saveCategory = async () => {
    if (!detail || !category) return
    const accessToken = token()
    if (!accessToken) return
    setSavingCategory(true)
    setError(null)
    try {
      const response = await fetch(`/api/v1/documents/${detail.id}/classification`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({ category }),
      })
      if (handleUnauthorized(response)) return
      if (!response.ok) throw new Error(`Erreur ${response.status}`)
      await openDocument(detail.id)
      await loadDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de la mise à jour")
    } finally {
      setSavingCategory(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-secondary mb-2">Module documentaire</p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Documents</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Importez, analysez et classez vos documents avec traçabilité.</p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-danger/20 bg-danger-soft p-4 text-sm text-danger" role="alert">{error}</div>
      )}

      <form onSubmit={handleUpload} className="sw-card p-5 sm:p-6 mb-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label htmlFor="document" className="sw-label">Importer un document</label>
            <p className="text-xs text-text-secondary mb-2">PDF, DOCX, XLSX ou CSV — 50 Mo max. Extraction et indexation automatiques.</p>
            <input
              id="document"
              ref={fileInput}
              type="file"
              accept=".pdf,.docx,.xlsx,.csv"
              className="block w-full text-sm text-text-secondary file:mr-4 file:rounded-lg file:border-0 file:bg-brand-secondary file:px-4 file:py-2.5 file:text-sm file:font-medium file:text-white hover:file:brightness-95 file:transition-colors"
            />
          </div>
          <button type="submit" disabled={uploading} className="sw-btn-primary shrink-0">
            {uploading ? "Traitement…" : "Importer et extraire"}
          </button>
        </div>
      </form>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="sw-card overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Bibliothèque</h2>
            <span className="sw-badge sw-badge-neutral">{documents.length}</span>
          </div>
          {loading ? (
            <p className="p-6 text-sm text-text-secondary">Chargement…</p>
          ) : documents.length === 0 ? (
            <div className="p-10 text-center">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-surface-muted text-text-muted">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="h-6 w-6"><path d="M14 2.75H6.5A1.75 1.75 0 0 0 4.75 4.5v15A1.75 1.75 0 0 0 6.5 21.25h11A1.75 1.75 0 0 0 19.25 19.5V8.25L14 2.75Zm0 0v5.5h5.25" /></svg>
              </div>
              <p className="text-sm text-text-secondary">Aucun document pour le moment.</p>
              <p className="text-xs text-text-muted mt-1">Importez un fichier pour lancer l&apos;extraction.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-surface-muted/60 text-text-secondary text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-4 py-3 font-medium">Nom</th>
                    <th className="px-4 py-3 font-medium">Format</th>
                    <th className="px-4 py-3 font-medium">Statut</th>
                    <th className="px-4 py-3 font-medium">Classement</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {documents.map((document) => (
                    <tr
                      key={document.id}
                      onClick={() => openDocument(document.id)}
                      className={`cursor-pointer transition-colors hover:bg-surface-muted/50 ${detail?.id === document.id ? "bg-info-soft/40" : ""}`}
                    >
                      <td className="px-4 py-3 text-text-primary font-medium max-w-[220px] truncate">{document.filename}</td>
                      <td className="px-4 py-3 text-text-secondary uppercase text-xs">{document.format}</td>
                      <td className="px-4 py-3">{statusBadge(document.status)}</td>
                      <td className="px-4 py-3 text-text-secondary text-xs">{document.classification ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="sw-card p-5 sm:p-6">
          {!detail ? (
            <div className="py-12 text-center">
              <p className="text-sm text-text-secondary">Sélectionnez un document pour consulter son extraction et ses sources.</p>
            </div>
          ) : (
            <div className="space-y-5">
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="text-base font-semibold text-text-primary truncate font-[family-name:var(--font-manrope)]">{detail.filename}</h2>
                    <p className="text-xs text-text-secondary mt-1">
                      {detail.format.toUpperCase()} · {detail.chunks.length} segment(s)
                    </p>
                  </div>
                  {statusBadge(detail.status)}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-surface-muted/30 p-4">
                <div className="flex flex-col sm:flex-row gap-3 sm:items-end">
                  <div className="flex-1">
                    <label htmlFor="category" className="sw-label">
                      <span className="inline-flex items-center gap-1.5">
                        Classification
                        <span className="sw-badge sw-badge-ai !text-[10px] !px-1.5 !py-0">IA</span>
                      </span>
                    </label>
                    <select id="category" value={category} onChange={(e) => setCategory(e.target.value)} className="sw-input">
                      <option value="">— Sélectionner —</option>
                      {CATEGORIES.map((item) => <option key={item} value={item}>{item}</option>)}
                    </select>
                  </div>
                  <button onClick={saveCategory} disabled={savingCategory || !category} className="sw-btn-secondary shrink-0">
                    {savingCategory ? "Enregistrement…" : "Confirmer"}
                  </button>
                </div>
                {detail.classification_confirmed && (
                  <p className="text-xs text-brand-accent mt-2 flex items-center gap-1">
                    <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.7-9.3a1 1 0 00-1.4-1.4L9 10.58 7.7 9.3a1 1 0 00-1.4 1.4l2 2a1 1 0 001.4 0l4-4z" clipRule="evenodd" /></svg>
                    Classification confirmée par l&apos;utilisateur.
                  </p>
                )}
              </div>

              <div>
                <h3 className="text-sm font-semibold text-text-primary mb-2">Texte extrait</h3>
                <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-lg bg-surface-muted/50 border border-border p-3 text-xs text-text-secondary font-sans">
                  {detail.extracted_data?.text || "Aucun texte extrait."}
                </pre>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-text-primary mb-2">Segments et provenance</h3>
                <ul className="space-y-2 max-h-56 overflow-auto">
                  {detail.chunks.map((chunk) => (
                    <li key={chunk.id} className="border border-border rounded-lg p-3 bg-surface">
                      <p className="text-xs font-medium text-brand-secondary mb-1">
                        {formatProvenance(chunk.metadata)} · {chunk.chunk_type}
                      </p>
                      <p className="text-xs text-text-secondary line-clamp-3">{chunk.content_text.slice(0, 300)}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
