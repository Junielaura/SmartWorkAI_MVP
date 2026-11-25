"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { swCard, swInput, swSelect, swBtnAI, swBtnPrimary, swBadge } from "@/components/ui"

type WorkflowTrigger = "import" | "schedule" | "manual" | "document_change"
type WorkflowAction = 
  | "classify"
  | "extract" 
  | "generate"
  | "notify"
  | "task_create"
  | "report_generate"
  | "storage_move"

const TRIGGER_OPTIONS = [
  { value: "import" as WorkflowTrigger, label: "À l'import d'un document" },
  { value: "schedule" as WorkflowTrigger, label: "Sur échéance planifiée" },
  { value: "manual" as WorkflowTrigger, label: "Manuel (bouton)" },
  { value: "document_change" as WorkflowTrigger, label: "Au changement de document" },
]

const ACTION_OPTIONS = [
  { value: "classify", label: "Classifier le document" },
  { value: "extract", label: "Extraire les données" },
  { value: "generate", label: "Générer un rapport" },
  { value: "notify", label: "Envoyer une notification" },
  { value: "task_create", label: "Créer une task" },
  { value: "report_generate", label: "Générer un rapport programmé" },
  { value: "storage_move", label: "Déplacer le stockage" },
]

export default function AutomationsPage() {
  const router = useRouter()
  const [workflows, setWorkflows] = useState<Array<{id: string, name: string, description: string, trigger: string, is_active: boolean, created_at: string}>>([])
  const [newWorkflow, setNewWorkflow] = useState<{name: string, description: string, trigger: WorkflowTrigger, trigger_params: Record<string, unknown>, actions: Array<{action: WorkflowAction, params: Record<string, unknown>}>}>
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/workflows/", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur chargement workflows")
      return res.json()
    }).then(setWorkflows).catch((e) => { setError(e.message); setWorkflows([]) })
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const accessToken = localStorage.getItem("access_token")
      const response = await fetch("/api/v1/workflows/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newWorkflow),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      setWorkflows(prev => [...prev, {
        id: Date.now().toString(),
        name: newWorkflow.name,
        description: newWorkflow.description,
        trigger: newWorkflow.trigger,
        is_active: true,
        created_at: new Date().toISOString(),
      }])
      setNewWorkflow({
        name: "",
        description: "",
        trigger: "import",
        trigger_params: {},
        actions: [],
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec création workflow")
    } finally { setLoading(false) }
  }

  const handleDelete = async (id: string) => {
    setLoading(true)
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch(`/api/v1/workflows/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      setWorkflows(prev => prev.filter(w => w.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur suppression workflow")
    } finally { setLoading(false) }
  }

  const handleExecute = async (workflowId: string, documentId: string) => {
    setLoading(true)
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch(`/api/v1/workflows/${workflowId}/execute`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ document_id: Number(documentId) }),
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur exécution workflow")
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-sidebar flex-shrink-0 border-r border-border">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Studio d'Automatisations</h2>
            <p className="text-text-secondary text-sm">Créez des workflows visuels sans code</p>
          </div>
          <nav className="space-y-2">
            <a href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7v-10a1 1 0 011-1h3m-4-4l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7l-2-2m2 2v-10a1 1 0 011-1h3m4-4v6m4-6v6m-6-4h6m-6-4H10"/><path d="M12 3v2m0 9v2m0-6v2m6.364-1.636l-.707-.707L12 10.793 19.293 3.901l-.707.707L12 15.207z"/></svg>
              Tableau de bord
            </a>
            <a href="/documents" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M18 20h-8"/><path d="M14 2v4a2 2 0 002 2h4a2 2 0 002-2v-4"/><path d="M7 22H4a2 2 0 01-2-2V10"/></svg>
              Documents
            </a>
            <a href="/chat" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 16a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6z"/><path d="M21 19a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6zM2 3a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V3zM7 22H4a2 2 0 01-2-2v-6.943"/><path d="M3 16h6m5-5a2 2 0 110 4h.01"/><path d="M7 22H4a2 2 0 01-2-2V10"/></svg>
              Chat IA
            </a>
            <a href="/automations" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-brand-secondary text-white">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M12 5v14M8 12h12M8 12H12"/><path d="M12 5v14a2 2 0 002 2h2a2 2 0 002-2h-2m-2-4h2m-2-4h2m-6-6h2m6 6H10m4 0h6m3-3a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
              Studio Automations
            </a>
            <a href="/marketplace" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
              Marketplace
            </a>
            <a href="/knowledge" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/><circle cx="10" cy="10" r="7"/><path d="M17 7L17 3"/><path d="M3 3v18"/><path d="M21 3v18M3 3h18"/></svg>
              Knowledge Hub
            </a>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-2xl mx-auto">
            
            {/* Création de workflow */}
            <swCard>
              <h3 className="text-lg font-semibold text-text-primary mb-4">Nouveau workflow</h3>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Nom du workflow</label>
                  <input 
                    value={newWorkflow.name} 
                    onChange={(e) => setNewWorkflow(prev => ({ ...prev, name: e.target.value }))} 
                    className="sw-input" 
                    placeholder="Ex: On import → classifier → extraire"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Description</label>
                  <textarea 
                    value={newWorkflow.description} 
                    onChange={(e) => setNewWorkflow(prev => ({ ...prev, description: e.target.value }))} 
                    className="sw-input h-24" 
                    placeholder="Description détaillée du workflow..."
                  ></textarea>
                </div>
                
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Trigger</label>
                  <swSelect 
                    value={newWorkflow.trigger} 
                    onValueChange={(value) => setNewWorkflow(prev => ({ ...prev, trigger: value as WorkflowTrigger }))}
                  >
                    {TRIGGER_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </swSelect>
                </div>
                
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Paramètres du trigger</label>
                  <swInput 
                    value={JSON.stringify(newWorkflow.trigger_params)} 
                    onChange={(e) => setNewWorkflow(prev => ({ ...prev, trigger_params: JSON.parse(e.target.value) }))} 
                    className="sw-input" 
                    placeholder='{"jours": 7, "heure": "09:00"}'
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-text-secondary mb-2">Actions</label>
                  <p className="text-xs text-text-secondary mb-1">Sélectionnez les actions à exécuter</p>
                  <div className="space-y-2">
                    {ACTION_OPTIONS.map(opt => (
                      <div key={opt.value} className="flex items-center gap-2 border rounded-md p-2 sw-input-sm">
                        <swSelect 
                          value={opt.value} 
                          onValueChange={(value) => {/* Gérer selection */}}
                        >
                          <option value="">{opt.label}</option>
                        </swSelect>
                        <input 
                          type="text" 
                          placeholder="params" 
                          className="sw-input flex-1 w-32 sm:w-40 text-xs"
                          disabled
                        />
                      </div>
                    ))}
                  </div>
                </div>
                
                <button type="submit" disabled={loading} className="sw-btn-primary w-full">
                  {loading ? "Création en cours…" : "Créer le workflow"}
                </button>
              </form>
            </swCard>

            {/* Liste des workflows existants */}
            <swCard className="mt-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Workflows existants</h3>
              {error ? (
                <div className="bg-danger-soft text-danger p-3 rounded-md mb-4">
                  {error}
                </div>
              ) : workflows.length === 0 ? (
                <p className="text-text-secondary text-center py-8">
                  Aucun workflow créé. Créez votre premier workflow ci-dessus.
                </p>
              ) : (
                <div className="space-y-3">
                  {workflows.map((w) => (
                    <div key={w.id} className="flex items-center justify-between p-3 rounded-md border border-border hover:bg-surface-muted/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-text-primary">{w.name}</span>
                        <span className="text-xs text-text-secondary">{w.trigger}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={w.is_active ? "sw-badge sw-badge-success" : "sw-badge sw-badge-warning"}>
                          {w.is_active ? "Actif" : "Inactif"}
                        </span>
                        <button 
                          onClick={() => handleExecute(w.id, "0")}
                          className="text-sm text-brand-secondary hover:underline"
                        >
                          Exécuter
                        </button>
                        <button 
                          onClick={() => handleDelete(w.id)}
                          className="text-sm text-danger hover:underline"
                        >
                          Supprimer
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </swCard>
          </div>
        </div>
      </div>
    </div>
  )
}