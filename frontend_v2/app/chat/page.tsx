'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Trash2, User, Bot } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

export default function ChatPage() {
  const { documentId, filename, messages, addMessage, clearMessages } = useStore()
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!documentId) {
    return (
      <div className="max-w-md mx-auto py-20 text-center">
        <p className="text-muted-foreground mb-4">No document loaded</p>
        <Link href="/upload" className="text-accent hover:underline">Upload a PDF →</Link>
      </div>
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    
    const q = input.trim()
    setInput('')
    addMessage({ role: 'user', content: q })
    setLoading(true)

    try {
      const response = await apiClient.chat(q, documentId, filename || undefined)
      addMessage({ 
        role: 'assistant', 
        content: response.answer,
        sources: response.sources,
      })
      setLoading(false)
    } catch (e: any) {
      console.error('Chat error:', e)
      addMessage({ role: 'assistant', content: `Error: ${e.message || 'Failed to get response'}` })
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-10rem)] flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && !loading && (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <Bot className="w-12 h-12 text-muted-foreground/30 mb-4" />
            <p className="text-muted-foreground mb-2">Ask anything about your document</p>
            <p className="text-sm text-muted-foreground/60">{filename}</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === 'user' ? 'bg-accent text-white' : 'bg-muted'
            }`}>
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div className={`inline-block px-4 py-3 rounded-2xl text-sm ${
                msg.role === 'user' 
                  ? 'bg-accent text-white rounded-br-md' 
                  : 'bg-card border border-border rounded-bl-md'
              }`}>
                <p className="whitespace-pre-wrap text-left">{msg.content}</p>
              </div>
              {msg.sources?.length > 0 && (
                <details className="mt-2 text-xs text-left">
                  <summary className="text-muted-foreground cursor-pointer hover:text-foreground">
                    {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}
                  </summary>
                  <div className="mt-2 space-y-2 p-3 rounded-lg bg-muted">
                    {msg.sources.slice(0, 3).map((s: any, j: number) => (
                      <div key={j} className="text-muted-foreground">
                        <p className="line-clamp-2">{s.text}</p>
                        {s.metadata?.page_number && <p className="text-xs opacity-60">Page {s.metadata.page_number}</p>}
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
            </div>
          </div>
        )}
        
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <form onSubmit={handleSubmit} className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="w-full px-4 py-3 pr-12 rounded-xl bg-card border border-border focus:border-accent focus:outline-none text-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-accent text-white disabled:opacity-30"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            disabled={loading}
            className="p-3 rounded-xl border border-border hover:bg-muted text-muted-foreground hover:text-foreground disabled:opacity-50"
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}
