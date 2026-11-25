"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type ReportSchedule = {
  id: string
  frequency: string
  timezone: string
  next_execution: string
  is_active: boolean
  parameters: Record<string, unknown>
  created_at: string
}

type GeneratedReport = {
  id: string
  filename: string
  format: string
  status: string
  created_at: string
  validated_at: string | null
}

export default function ReportsPage() {
  const router = useRouter()
  const [schedules, setSchedules] = useState<ReportSchedule[]>([])
  const [reports, setReports] = useState<GeneratedReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/reporting/schedules", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur chargement des schedules")
      return res.json()
    }).then(setSchedules).catch((e) => { setError(e.message); setSchedules([]) })
    fetch("/api/v1/reporting/history", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur chargement de l'historique")
      return res.json()
    }).then(setReports).catch((e) => { setError(e.message); setReports([]) })
  }, [])

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const accessToken = localStorage.getItem("access_token")
      const response = await fetch("/api/v1/reporting/schedules", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          frequency: "weekly",
          timezone: "Europe/Paris",
          parameters: {},
        }),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      setSchedules(prev => [...prev, {
        id: Date.now().toString(),
        frequency: "weekly",
        timezone: "Europe/Paris",
        next_execution: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        is_active: true,
        parameters: {},
        created_at: new Date().toISOString(),
      }])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec création schedule")
    } finally { setLoading(false) }
  }

  const handleGenerateReport = async (scheduleId: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch(`/api/v1/reporting/schedules/${scheduleId}/generate`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec génération rapport")
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="flex min-h-screen">
        <div className="w-64 bg-gray-800 flex-shrink-0 border-r border-gray-700">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-6">Rapports</h2>
            <p className="text-gray-500 text-sm">Planification et génération de rapports</p>
          </div>
          <nav className="space-y-2">
            <a href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7v-10a1 1 0 011-1h3m-4-4l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7l-2-2m2 2v-10a1 1 0 011-1h3m4-4v6m4-6v6m-6-4h6m-6-4H10"/><path d="M12 3v2m0 9v2m0-6v2m6.364-1.636l-.707-.707L12 10.793 19.293 3.901l-.707.707L12 15.207z"/></svg>
              Tableau de bord
            </a>
            <a href="/marketplace" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
              Marketplace
            </a>
            <a href="/knowledge" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/><circle cx="10" cy="10" r="7"/><path d="M17 7L17 3"/><path d="M3 3v18"/><path d="M21 3v18M3 3h18"/></svg>
              Knowledge Hub
            </a>
            <a href="/activities" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
              Activity Center
            </a>
            <a href="/reports" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-gray-900 text-gray-100">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M12 7v5m0 0l2-2m2 2l-2-2m-6-6h2m6-6H10m5 10v5m0 0l2-2m0 2l2 2m-6 6h2m-6-6H10"/><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              Rapports
            </a>
          </nav>
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4">
                <p className="text-3xl font-semibold text-gray-900" id="activity-count">Chargement…</p>
                <p className="text-gray-500 text-xs">Activités</p>
              </div>
              <div className="p-4">
                <p className="text-3xl font-semibold text-gray-900" id="notification-count">Chargement…</p>
                <p className="text-gray-500 text-xs">Notifications</p>
              </div>
              <div className="p-4">
                <p className="text-3xl font-semibold text-gray-900" id="unread-activity">Chargement…</p>
                <p className="text-gray-500 text-xs">Non lues</p>
              </div>
              <div className="p-4">
                <p className="text-3xl font-semibold text-gray-900" id="total-count">Chargement…</p>
                <p className="text-gray-500 text-xs">Total</p>
              </div>
            </div>

            <div className="p-4 rounded-md border border-gray-700 mb-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-3">Nouveau schedule</h3>
              <form onSubmit={handleCreateSchedule} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-500 mb-2">Fréquence</label>
                  <select className="p-2 border border-gray-600 rounded-md bg-gray-800 text-gray-100">
                    <option value="daily">Quotidien</option>
                    <option value="weekly">Hebdomadaire</option>
                    <option value="monthly">Mensuel</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-500 mb-2">Fuseau horaire</label>
                  <input value="Europe/Paris" readOnly className="w-full p-2 border border-gray-600 rounded-md bg-gray-800 text-gray-100" />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-500 mb-2">Paramètres</label>
                  <input value="{}" readOnly className="w-full p-2 border border-gray-600 rounded-md bg-gray-800 text-gray-100" />
                </div>
                
                <button type="submit" disabled={loading} className="w-full py-2 bg-gray-900 text-gray-100 rounded-md">
                  {loading ? "Création en cours…" : "Créer le schedule"}
                </button>
              </form>
            </div>

            <div className="p-4 rounded-md border border-gray-700 mt-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-3">Rapports générés</h3>
              <p className="text-gray-500 text-xs mb-3">Aucun schedule créé. Créez votre first schedule ci-dessus.</p>
              {loading ? (
                <div className="py-8 text-center text-gray-500">Chargement en cours…</div>
              ) : schedules.length === 0 ? (
                <div className="py-8 text-center text-gray-500">Aucun schedule créé.</div>
              ) : (
                <div className="space-y-3">
                  {schedules.map((s) => (
                    <div key={s.id} className="p-3 rounded-md border border-gray-700 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-gray-900">{s.frequency} ({s.timezone})</span>
                        <span className="text-gray-500 text-xs {s.is_active ? "bg-green-600/20 text-green-400" : "bg-red-600/20 text-red-400"} rounded px-2 py-0.5>
                          {s.is_active ? "Actif" : "Inactif"}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleGenerateReport(s.id)}
                          className="text-sm text-gray-400 hover:underline"
                        >
                          Générer maintenant
                        </button>
                        <button className="text-sm text-gray-400 hover:underline">Supprimer</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}