"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { swCard, swInput, swBtnAI, swBadge } from "@/components/ui"

type Concept = { label: string; relevance: number }
type Insight = {
  id: string
  query: string
  concepts: Concept[]
  created_at: string
  is_favorited: boolean
}

export default function KnowledgeHubPage() {
  const router = useRouter()
  const [insights, setInsights] = useState<Insight[]>([])
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/knowledge/search?query=" + encodeURIComponent(query), {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur recherche knowledge")
      return res.json()
    }).then(setInsights).catch((e) => { setError(e.message); setInsights([]) })
  }, [query])

  const handleSearch = () => {
    setLoading(true)
    try {
      fetch("/api/v1/knowledge/search?query=" + encodeURIComponent(query), {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur recherche knowledge")
        return res.json()
      }).then(setInsights).catch((e) => { setError(e.message); setInsights([]) })
    } finally { setLoading(false) }
  }

  const handleSaveInsight = async (insightId: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch("/api/v1/knowledge/save", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ insightId }),
      })
      setInsights(prev => prev.map(insight =>
        insight.id === insightId
          ? { ...insight, is_favorited: true }
          : insight
      ))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec sauvegarde insight")
    }
  }

  const handleDeleteInsight = async (insightId: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch("/api/v1/knowledge/delete", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ insightId }),
      })
      setInsights(prev => prev.filter(insight => insight.id !== insightId))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec suppression insight")
    }
  }

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-sidebar flex-shrink-0 border-r border-border">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">Hub de Connaissances</h2>
            <p className="text-text-secondary text-sm">Recherche sémantique et gestion d'insights</p>
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
            <a href="/marketplace" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
              Marketplace
            </a>
            <a href="/knowledge" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-brand-secondary text-white">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/><circle cx="10" cy="10" r="7"/><path d="M17 7L17 3"/><path d="M3 3v18"/><path d="M21 3v18M3 3h18"/></svg>
              Knowledge Hub
            </a>
            <a href="/activities" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-text-secondary hover:bg-surface-muted/50 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
              Activity Center
            </a>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            
            {/* Barre de recherche */}
            <div className="mb-6 rounded-lg border border-border p-4 bg-surface muted">
              <div className="flex gap-3">
                <swInput
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Rechercher des idées, concepts, insights..."
                  className="flex-1"
                />
                <swBtnAI
                  onClick={handleSearch}
                  disabled={!query.trim() || loading}
                >
                  {loading ? "Recherche en cours…" : "Rechercher"}
                </swBtnAI>
              </div>
            </div>

            {/* Erreur */}
            {error && (
              <div className="mb-4 bg-danger-soft text-danger rounded-md p-3">
                {error}
              </div>
            )}

            {/* Liste des insights */}
            <swCard>
              <div className="flex items-baseline justify-between mb-3">
                <h3 className="text-lg font-semibold text-text-primary">
                  Mes Insights ({insights.length})
                </h3>
                <swBadge
                  variant="secondary"
                  className="text-xs"
                >
                  {insights.length} insights
                </swBadge>
              </div>

              {loading ? (
                <div className="py-8 text-center text-text-secondary">
                  Recherche en cours…
                </div>
              ) : insights.length === 0 ? (
                <div className="py-8 text-center text-text-secondary">
                  Aucun insight trouvé. Essayez une requête différente.
                </div>
              ) : (
                <div className="space-y-3">
                  {insights.map((insight) => (
                    <div
                      key={insight.id}
                      className="p-3 rounded-md border border-border hover:bg-surface-muted/50 transition-colors cursor-pointer"
                      onClick={() => handleSaveInsight(insight.id)}
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0" style={{ background: "#e5e7eb" }}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4">
                            <path d="M13 2L3 14h4l10 10L13 2Z"/>
                          </svg>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary line-clamp-2">{insight.query}</p>
                          <p className="text-xs text-text-secondary">
                            {new Date(insight.created_at).toLocaleDateString("fr-FR")}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {insight.concepts.map((concept) => (
                          <span
                            key={concept.label}
                            className="inline-flex items-center gap-1 text-xs text-text-secondary rounded-bg"
                            style={{ background: "#f3f4f6", color: "#6b7280" }}
                          >
                            {concept.label}
                          </span>
                        ))}
                      </div>
                      {insight.is_favorited ? (
                        <button
                          onClick={() => handleDeleteInsight(insight.id)}
                          className="ml-auto text-xs text-danger hover:underline"
                        >
                          Retirer
                        </button>
                      ) : (
                        <button
                          onClick={() => handleSaveInsight(insight.id)}
                          className="ml-auto text-xs text-brand-primary hover:underline"
                        >
                          Épingler
                        </button>
                      )}
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