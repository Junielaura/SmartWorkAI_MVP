"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { swCard, swInput, swSelect, swBtnAI, swBtnPrimary, swBadge } from "@/components/ui"

type ModelCategory = "report" | "template" | "analysis" | "meeting"
type ModelVersion = "1.0.0" | "2.0.0" | "3.0.0"
type Model = {
  id: string
  name: string
  category: ModelCategory
  version: ModelVersion
  description: string
  author: string
  download_count: number
  price: number | null
  is_free: boolean
  tags: string[]
}

const CATEGORIES = [
  { value: "report", label: "Rapports" },
  { value: "template", label: "Modèles" },
  { value: "analysis", label: "Analyses" },
  { value: "meeting", label: "Comptes rendus" },
]

const PRICE_DISPLAY: Record<number | null, string> = {
  null: "Gratuit",
  0: "Gratuit",
}

export default function MarketplacePage() {
  const router = useRouter()
  const [models, setModels] = useState<Model[]>([])
  const [categoryFilter, setCategoryFilter] = useState<ModelCategory | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/marketplace/", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur chargement marketplace")
      return res.json()
    }).then(setModels).catch((e) => { setError(e.message); setModels([]) })
  }, [categoryFilter, searchQuery])

  const handleSearch = () => {
    setLoading(true)
    try {
      let url = "/api/v1/marketplace/search?query=" + encodeURIComponent(searchQuery)
      if (categoryFilter) {
        url += "&category=" + categoryFilter
      }
      fetch(url, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur recherche marketplace")
        return res.json()
      }).then(setModels).catch((e) => { setError(e.message); setModels([]) })
    } finally { setLoading(false) }
  }

  const handleUseModel = async (modelId: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch(`/api/v1/marketplace/${modelId}/use`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec utilisation modèle")
    }
  }

  const handleDownload = async (modelId: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      const response = await fetch(`/api/v1/marketplace/${modelId}/download`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      // Trigger download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `modele-${modelId}.${getFileExtension(models.find(m => m.id === modelId)?.name ?? "docx")}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec téléchargement")
    }
  }

  const getFileExtension = (filename: string): string => {
    return filename.split(".").pop()?.toLowerCase() ?? "docx"
  }

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-sidebar flex-shrink-0 border-r border-border">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Marketplace</h2>
            <p className="text-text-secondary text-sm">Modèles IA et ressources partagées</p>
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
            <a href="/automations" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M12 5v14M8 12h12M8 12H12"/><path d="M12 5v14a2 2 0 002 2h2a2 2 0 002-2h-2m-2-4h2m-2-4h2m-6-6h2m6 6H10m4 0h6m3-3a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
              Studio Automations
            </a>
            <a href="/knowledge" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/><circle cx="10" cy="10" r="7"/><path d="M17 7L17 3"/><path d="M3 3v18"/><path d="M21 3v18M3 3h18"/></svg>
              Knowledge Hub
            </a>
            <a href="/marketplace" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-brand-secondary text-white">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
              Marketplace
            </a>
            <a href="/activities" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
              Activity Center
            </a>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            
            {/* Filtres */}
            <div className="mb-6 rounded-lg border border-border p-4 bg-surface">
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Catégorie</label>
                  <swSelect
                    value={categoryFilter}
                    onValueChange={(value) => setCategoryFilter(value as ModelCategory | null)}
                  >
                    <option value={null}>Toutes catégories</option>
                    {CATEGORIES.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </swSelect>
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Recherche</label>
                  <swInput
                    placeholder="Rechercher un modèle..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="sw-input"
                  />
                </div>
              </div>
            </div>

            {/* Erreur */}
            {error && (
              <div className="mb-4 bg-danger-soft text-danger rounded-md p-3">
                {error}
              </div>
            )}

            {/* Liste des modèles */}
            <swCard>
              <div className="flex items-baseline justify-between mb-3">
                <h3 className="text-lg font-semibold text-text-primary">
                  Modèles ({models.length})
                </h3>
                <swBadge
                  variant="secondary"
                  className="text-xs"
                >
                  {models.length} modèles
                </swBadge>
              </div>

              {loading ? (
                <div className="py-8 text-center text-text-secondary">
                  Chargement en cours…
                </div>
              ) : models.length === 0 ? (
                <div className="py-8 text-center text-text-secondary">
                  <p>Aucun modèle trouvé.</p>
                  {categoryFilter && <p className="text-text-secondary">Essayez de changer la catégorie.</p>}
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {models.map((model) => (
                    <div
                      key={model.id}
                      className="group rounded-lg border border-border p-4 hover:bg-surface-muted/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-text-primary line-clamp-2">
                          {model.name}
                        </h4>
                        <swBadge
                          variant={model.is_free ? "success" : "secondary"}
                          className="text-xs"
                        >
                          {PRICE_DISPLAY[model.price]}
                        </swBadge>
                      </div>
                      
                      <p className="text-sm text-text-secondary line-clamp-2 mb-3">
                        {model.description}
                      </p>
                      
                      <div className="flex flex-col sm:flex-row gap-2">
                        <p className="text-xs text-text-secondary">
                          {model.version} · {model.author}
                        </p>
                        <p className="text-xs text-text-secondary">
                          {model.download_count} téléchargements
                        </p>
                      </div>
                      
                      <div className="mt-3 pt-3 border-t border-border">
                        <p className="text-xs text-text-secondary mb-1">Mots-clés</p>
                        <div className="flex flex-wrap gap-1">
                          {model.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center gap-1 text-xs rounded bg-border px-2 py-0.5"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="mt-3 pt-3 flex gap-2">
                        <swBtnPrimary
                          onClick={() => handleUseModel(model.id)}
                          disabled={model.is_free ? false : false}
                        >
                          {model.is_free ? "Utiliser" : "Acheter"}
                        </swBtnPrimary>
                        <swBtnAI
                          onClick={() => handleDownload(model.id)}
                          disabled={model.is_free ? false : false}
                          variant="outline"
                        >
                          Télécharger
                        </swBtnAI>
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