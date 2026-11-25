"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"

type Citation = {
  document: { id: number; filename: string; format: string }
  chunk: { content_text: string; chunk_metadata?: Record<string, unknown> }
  citation: string
  relevance_score: number
}

type Message = {
  role: "user" | "assistant"
  content: string
  citations?: Citation[]
  fallback?: boolean
}

export default function ChatPage() {
  const router = useRouter()
  const bottomRef = useRef<HTMLDivElement>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState("")
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!localStorage.getItem("access_token")) router.replace("/login")
  }, [router])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  const sendQuestion = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || loading) return
    const accessToken = localStorage.getItem("access_token")
    if (!accessToken) { router.replace("/login"); return }

    setMessages((current) => [...current, { role: "user", content: trimmed }])
    setQuestion("")
    setLoading(true)
    setError(null)

    try {
      const response = await fetch("/api/v1/chat/send", {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, conversation_id: conversationId }),
      })
      if (response.status === 401) { localStorage.removeItem("access_token"); router.replace("/login"); return }
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Erreur ${response.status}`)
      }
      const data = await response.json()
      setConversationId(data.conversation_id)
      setMessages((current) => [...current, { role: "assistant", content: data.answer, citations: data.citations ?? [], fallback: data.fallback }])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de la requête")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100dvh-10rem)] min-h-[500px]">
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-ai">Assistant intelligent</p>
          <span className="sw-badge sw-badge-ai !text-[10px]">IA</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-semibold text-text-primary font-[family-name:var(--font-manrope)]">Assistant documentaire</h1>
        <p className="text-text-secondary mt-1 text-sm sm:text-base">Posez une question sur vos documents importés. Les réponses citent leurs sources.</p>
      </div>

      {error && <div className="mb-4 rounded-lg border border-danger/20 bg-danger-soft p-3 text-sm text-danger" role="alert">{error}</div>}

      <div className="flex-1 overflow-y-auto sw-card p-4 sm:p-5 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="h-full min-h-[220px] flex flex-col items-center justify-center text-center px-4">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-ai-soft text-brand-ai">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className="h-7 w-7" aria-hidden="true">
                <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
                <path d="M19 15l.75 2.25L22 18l-2.25.75L19 21l-.75-2.25L16 18l2.25-.75L19 15z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-text-primary">Posez votre première question</p>
            <p className="text-sm text-text-secondary mt-1 max-w-md">
              Exemple : « Quel est le montant total de la facture ? » ou « Résume le compte rendu de réunion. »
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[88%] sm:max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
              message.role === "user"
                ? "bg-brand-secondary text-white rounded-br-md"
                : "bg-surface-muted/60 text-text-primary border border-border rounded-bl-md"
            }`}>
              {message.role === "assistant" && (
                <div className="flex items-center gap-1.5 mb-2 text-brand-ai">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-3.5 w-3.5"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" /></svg>
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Assistant IA</span>
                </div>
              )}
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 border-t border-border/60 pt-2.5 space-y-2">
                  <p className="text-xs font-semibold text-text-secondary">Sources citées</p>
                  {message.citations.map((citation, citationIndex) => (
                    <div key={citationIndex} className="text-xs rounded-lg bg-surface/70 border border-border/50 p-2">
                      <span className="font-medium text-brand-secondary">[{citationIndex + 1}] {citation.citation}</span>
                      <p className="line-clamp-2 text-text-secondary mt-0.5">{citation.chunk.content_text.slice(0, 220)}</p>
                    </div>
                  ))}
                </div>
              )}
              {message.role === "assistant" && message.fallback && (
                <p className="mt-2 text-[11px] text-warning flex items-center gap-1">
                  <span className="inline-block h-1.5 w-1.5 rounded-full bg-warning" aria-hidden="true" />
                  Mode extractif : modèle IA indisponible, passages sources affichés.
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-ai-soft border border-brand-ai/15 rounded-2xl rounded-bl-md px-4 py-3 text-sm text-brand-ai flex items-center gap-2">
              <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" /><path d="M22 12a10 10 0 00-10-10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" /></svg>
              Recherche dans vos documents…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendQuestion} className="mt-4 flex gap-3">
        <label htmlFor="chat-input" className="sr-only">Votre question</label>
        <input
          id="chat-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Posez une question sur vos documents…"
          className="sw-input flex-1"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()} className="sw-btn-ai shrink-0 !px-5">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" aria-hidden="true"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z" /></svg>
          <span className="hidden sm:inline">Envoyer</span>
        </button>
      </form>
    </div>
  )
}
