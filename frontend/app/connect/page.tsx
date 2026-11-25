"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type ConnectionType = "google-drive" | "microsoft-365" | "slack" | "email"
type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error"

const CONNECTION_TYPES = [
  { value: "google-drive", label: "Google Drive" },
  { value: "microsoft-365", label: "Microsoft 365" },
  { value: "slack", label: "Slack" },
  { value: "email", label: "Email" },
]

export default function ConnectPage() {
  const router = useRouter()
  const [status, setStatus] = useState<Record<ConnectionType, ConnectionStatus>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/v1/connect/status", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    }).then(res => {
      if (!res.ok) throw new Error("Erreur chargement statut connect")
      return res.json()
    }).then(setStatus).catch((e) => { setError(e.message); setStatus({}) })
  }, [])

  const handleConnect = async (type: ConnectionType) => {
    setStatus(prev => ({ ...prev, [type]: "connecting" }))
    try {
      const accessToken = localStorage.getItem("access_token")
      const response = await fetch("/api/v1/connect/start", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ type }),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      setStatus(prev => ({ ...prev, [type]: "connected" }))
      setError(null)
    } catch (err) {
      setStatus(prev => ({ ...prev, [type]: "error" }))
      setError(err instanceof Error ? err.message : "Échec connexion")
    }
  }

  const handleDisconnect = async (type: ConnectionType) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch(`/api/v1/connect/${type}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      setStatus(prev => ({ ...prev, [type]: "disconnected" }))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec déconnexion")
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="flex min-h-screen">
        <div className="w-64 bg-gray-800 flex-shrink-0 border-r border-gray-700">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-6">Connect</h2>
            <p className="text-gray-500 text-sm">Intégrations et connexions</p>
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
            <a href="/reports" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M12 7v5m0 0l2-2m2 2l-2-2m-6-6h2m6-6H10m5 10v5m0 0l2-2m0 2l2 2m-6 6h2m-6-6H10"/><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              Rapports
            </a>
            <a href="/connect" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-gray-900 text-gray-100">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
              Connect
            </a>
          </nav>
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {CONNECTION_TYPES.map((type) => (
                <div key={type.value} className="p-4">
                  <h4 className="font-medium text-gray-900">{type.label}</h4>
                  <p className="text-gray-500 text-xs">{status[type.value] ?? "Non connecté"}</p>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-md border border-gray-700 mb-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Connecter un service</h3>
              {Object.values(status).every(s => s === "disconnected") ? (
                <p className="text-gray-500 text-sm mb-4">Aucune connexion configurée. Ajoutez vos services préférés ci-dessus.</p>) : (
                <p className="text-gray-500 text-sm mb-4">Services connectés ci-dessus.</p>)}
              <div className="grid grid-cols-2 gap-2">
                {CONNECTION_TYPES.map((type) => (
                  <div key={type.value} className="p-3 rounded-md border border-gray-700">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-gray-900">{type.label}</span>
                      <span className="text-gray-500 text-xs">{status[type.value] ?? "disconnected"}</span>
                    </div>
                    {status[type.value] === "disconnected" && (
                      <button
                        onClick={() => handleConnect(type)}
                        className="w-full py-2 bg-gray-900 text-gray-100 rounded-md text-sm mt-2"
                      >
                        Connecter
                      </button>
                    )}
                    {status[type.value] === "connected" && (
                      <button
                        onClick={() => handleDisconnect(type)}
                        className="w-full py-2 bg-gray-900 text-gray-100 rounded-md text-sm mt-2"
                      >
                        Déconnecter
                      </button>
                    )}
                    {status[type.value] === "error" && (
                      <button
                        onClick={() => handleConnect(type)}
                        className="w-full py-2 bg-gray-900 text-gray-100 rounded-md text-sm mt-2"
                      >
                        Réessayer
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-md border border-gray-700">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Services supportés</h3>
              <p className="text-gray-500 text-sm mb-4">Connectez vos services pour automatiser les workflows et partager du contenu.</p>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="inline-flex items-center gap-2 text-xs text-gray-500 rounded bg-gray-800 px-2 py-1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4"><path d="M21 16a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6z"/><path d="M21 19a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6zM2 3a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V3z"/></svg>
                    Google Drive
                  </span>
                </div>
                <div>
                  <span className="inline-flex items-center gap-2 text-xs text-gray-500 rounded bg-gray-800 px-2 py-1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
                    Microsoft 365
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-4">
                <div>
                  <span className="inline-flex items-center gap-2 text-xs text-gray-500 rounded bg-gray-800 px-2 py-1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
                    Slack
                  </span>
                </div>
                <div>
                  <span className="inline-flex items-center gap-2 text-xs text-gray-500 rounded bg-gray-800 px-2 py-1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4"><path d="M21 16a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6z"/><path d="M21 19a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6zM2 3a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V3z"/></svg>
                    Email
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}