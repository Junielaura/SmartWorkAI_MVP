"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type Activity = {
  id: string
  type: "upload" | "generation" | "share" | "collaboration" | "task"
  title: string
  description: string
  created_at: string
  read: boolean
}

type Notification = {
  id: string
  type: "success" | "warning" | "info"
  title: string
  message: string
  created_at: string
  read: boolean
}

export default function ActivitiesPage() {
  const router = useRouter()
  const [activities, setActivities] = useState<Activity[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetch("/api/v1/activities", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur chargement activités")
        return res.json()
      }).then(setActivities).catch((e) => { setError(e.message); setActivities([]) }),
      fetch("/api/v1/notifications", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur chargement notifications")
        return res.json()
      }).then(setNotifications).catch((e) => { setError(e.message); setNotifications([]) }),
    ]).finally(() => setLoading(false))
  }, [])

  const markActivityAsRead = async (id: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch("/api/v1/activities/read", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id }),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur marquage activité lue")
    }
  }

  const markNotificationAsRead = async (id: string) => {
    try {
      const accessToken = localStorage.getItem("access_token")
      await fetch("/api/v1/notifications/read", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id }),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur marquage notification lue")
    }
  }

  useEffect(() => {
    if (error) {
      fetch("/api/v1/activities", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur rechargement activités")
        return res.json()
      }).then(setActivities).catch(() => setActivities([]))
      fetch("/api/v1/notifications", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
      }).then(res => {
        if (!res.ok) throw new Error("Erreur rechargement notifications")
        return res.json()
      }).then(setNotifications).catch(() => setNotifications([]))
    }
  }, [error])

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="flex min-h-screen">
        <div className="w-64 bg-gray-800 flex-shrink-0 border-r border-gray-700">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-6">Centre d'Activité</h2>
            <p className="text-gray-500 text-sm">Notifications et activités récentes</p>
          </div>
          <nav className="space-y-2">
            <a href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7v-10a1 1 0 011-1h3m-4-4l2 2m-2-2v10a1 1 0 01-1 1h-3m-7 7l-2-2m2 2v-10a1 1 0 011-1h3m4-4v6m4-6v6m-6-4h6m-6-4H10"/><path d="M12 3v2m0 9v2m0-6v2m6.364-1.636l-.707-.707L12 10.793 19.293 3.901l-.707.707L12 15.207z"/></svg>
              Tableau de bord
            </a>
            <a href="/documents" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M18 20h-8"/><path d="M14 2v4a2 2 0 002 2h4a2 2 0 002-2v-4"/><path d="M7 22H4a2 2 0 01-2-2V10"/></svg>
              Documents
            </a>
            <a href="/chat" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 16a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6z"/><path d="M21 19a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v6zM2 3a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V3zM7 22H4a2 2 0 01-2-2v-6.943"/><path d="M3 16h6m5-5a2 2 0 110 4h.01"/><path d="M7 22H4a2 2 0 01-2-2V10"/></svg>
              Chat IA
            </a>
            <a href="/automations" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M12 5v14M8 12h12M8 12H12"/><path d="M12 5v14a2 2 0 002 2h2a2 2 0 002-2h-2m-2-4h2m-2-4h2m-6-6h2m6 6H10m4 0h6m3-3a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
              Studio Automations
            </a>
            <a href="/marketplace" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M18 13v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h8a2 2 0 012 2v3m-2-2v2h2V9h2v3z"/><circle cx="3" cy="3" r="1"/><path d="M21 15c0 2-2 3-3 3H6l-3-3m0 0l-2-2m-2-2h10"/><path d="M9 18v2m6 0v2M5 9h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2m0 12h14a2 2 0 012 2v2a2 2 0 01-2 2H5a2 2 0 01-2-2v-2"/></svg>
              Marketplace
            </a>
            <a href="/knowledge" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-700 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/><circle cx="10" cy="10" r="7"/><path d="M17 7L17 3"/><path d="M3 3v18"/><path d="M21 3v18M3 3h18"/></svg>
              Knowledge Hub
            </a>
            <a href="/activities" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-gray-900 text-gray-100">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-5 w-5"><path d="M3 9l9 6l9-6m-3-3l9 6v-12l-9-6l-9 6"/></svg>
              Activity Center
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
              <h3 className="text-lg font-semibold text-gray-100 mb-3">
                Activités récentes
                <span className="text-gray-500 text-xs ml-auto">{activities.length} activités</span>
              </h3>
            </div>

            {loading ? (
              <div className="py-8 text-center text-gray-500">Chargement en cours…</div>
            ) : activities.length === 0 ? (
              <div className="py-8 text-center text-gray-500">Aucune activité récente.</div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {activities.map((activity) => (
                  <div
                    key={activity.id}
                    className="p-3 rounded-md border border-gray-700 flex items-start gap-3"
                    onClick={() => markActivityAsRead(activity.id)}
                  >
                    <div className="w-8 h-8 rounded-md flex-shrink-0 flex items-center justify-center" style={{ background: activity.read ? "#e5e7eb" : "#f3f4f6" }}>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4">
                        <path d="M13 2L3 14h4l10 10L13 2Z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 line-clamp-1 truncate">{activity.title}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.created_at).toLocaleDateString("fr-FR")}
                      </p>
                      {activity.description && (
                        <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">
                          {activity.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="p-4 rounded-md border border-gray-700 mt-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-3">
                Notifications
                <span className="text-gray-500 text-xs ml-auto">{notifications.length} notifications</span>
              </h3>
            </div>

            {loading ? (
              <div className="py-8 text-center text-gray-500">Chargement en cours…</div>
            ) : notifications.length === 0 ? (
              <div className="py-8 text-center text-gray-500">Aucune notification.</div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="p-3 rounded-md border border-gray-700 flex items-start gap-3"
                    onClick={() => markNotificationAsRead(notification.id)}
                  >
                    <div className="w-8 h-8 rounded-md flex-shrink-0 flex items-center justify-center" style={{ background: notification.read ? "#e5e7eb" : "#f3f4f6" }}>
                      {notification.type === "success" ? (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4">
                          <path d="M5 13l4 4L19 7"/>
                        </svg>
                      ) : notification.type === "warning" ? (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4">
                          <path d="M12 9v2m0 0h.01m-6.938 4h13.856c1.538 0 2.462-1.03 2.462-2L21.961 7.5A2.23 2.23 0 0018.734 5H5a2.23 2.23 0 00-2.224 2.263L4.736 11.25c0 .61.092 1.2.288 1.763l1.55 2.5M15.75 4.25l-1.5 2.5M10.5 9.5l3 3m0 0l3 3m-3-3v12"/>
                        </svg>
                      ) : (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" className="h-4 w-4">
                          <path d="M12 9v2m0 0h.01m-6.938 4h13.856c1.538 0 2.462-1.03 2.462-2L21.961 7.5A2.23 2.23 0 0018.734 5H5a2.23 2.23 0 00-2.224 2.263L4.736 11.25c0 .61.092 1.2.288 1.763l1.55 2.5M15.75 4.25l-1.5 2.5M10.5 9.5l3 3m0 0l3 3m-3-3v12"/>
                        </svg>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 line-clamp-1 truncate">{notification.title}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(notification.created_at).toLocaleDateString("fr-FR")}
                      </p>
                      {notification.message && (
                        <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">
                          {notification.message}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}