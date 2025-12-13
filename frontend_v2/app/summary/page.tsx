'use client'

import { useState } from 'react'
import { Loader2, Download, RotateCcw } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

export default function SummaryPage() {
  const { documentId } = useStore()
  const [length, setLength] = useState<'short' | 'medium' | 'long'>('medium')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<any>(null)

  if (!documentId) {
    return (
      <div className="max-w-md mx-auto py-20 text-center">
        <p className="text-muted-foreground mb-4">No document loaded</p>
        <Link href="/upload" className="text-accent hover:underline">Upload a PDF →</Link>
      </div>
    )
  }

  const generate = async () => {
    setLoading(true); setError(null)
    try {
      const res = await apiClient.generateSummary(length, documentId)
      setSummary(res.summary)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  if (!summary) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-3">Summary length</label>
            <div className="grid grid-cols-3 gap-3">
              {(['short', 'medium', 'long'] as const).map(l => (
                <button key={l} onClick={() => setLength(l)}
                  className={`p-4 rounded-xl border text-center transition-colors ${length === l ? 'border-accent bg-accent-light' : 'border-border hover:border-accent/30'}`}>
                  <p className="font-medium capitalize">{l}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {l === 'short' && '~200 words'}
                    {l === 'medium' && '~400 words'}
                    {l === 'long' && '~800 words'}
                  </p>
                </button>
              ))}
            </div>
          </div>
          <button onClick={generate} disabled={loading} className="w-full py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Summary'}
          </button>
          {error && <p className="text-sm text-error">{error}</p>}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="p-6 rounded-xl bg-card border border-border mb-6">
        <h2 className="text-lg font-semibold mb-4">{summary.summary_title || 'Summary'}</h2>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{summary.summary}</p>
        {summary.key_topics?.length > 0 && (
          <div className="mt-6 pt-4 border-t border-border">
            <p className="text-xs font-medium text-muted-foreground uppercase mb-2">Key Topics</p>
            <div className="flex flex-wrap gap-2">
              {summary.key_topics.map((t: string, i: number) => (
                <span key={i} className="px-2 py-1 rounded-md bg-accent-light text-accent text-xs">{t}</span>
              ))}
            </div>
          </div>
        )}
        {summary.word_count && <p className="mt-4 text-xs text-muted-foreground">{summary.word_count} words</p>}
      </div>
      <div className="flex gap-3">
        <button onClick={() => setSummary(null)} className="flex-1 py-3 rounded-xl border border-border hover:bg-muted font-medium flex items-center justify-center gap-2">
          <RotateCcw className="w-4 h-4" /> New Summary
        </button>
        <button onClick={() => { const b = new Blob([summary.summary || '']); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'summary.txt'; a.click() }}
          className="px-4 py-3 rounded-xl border border-border hover:bg-muted">
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
