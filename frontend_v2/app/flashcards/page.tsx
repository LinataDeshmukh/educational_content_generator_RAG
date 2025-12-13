'use client'

import { useState } from 'react'
import { Loader2, ChevronLeft, ChevronRight, RotateCcw, Download, RotateCw } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

export default function FlashcardsPage() {
  const { documentId, flashcards, currentIndex, showAnswer, setFlashcards, setCurrentIndex, setShowAnswer, clearFlashcards } = useStore()
  const [numCards, setNumCards] = useState(20)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
      const res = await apiClient.generateFlashcards(numCards, documentId)
      setFlashcards(res.flashcards)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  const cards = flashcards?.flashcards || []
  const card = cards[currentIndex]

  if (!flashcards) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-3">Number of cards: {numCards}</label>
            <input type="range" min={10} max={100} value={numCards} onChange={e => setNumCards(+e.target.value)} className="w-full accent-accent" />
          </div>
          <button onClick={generate} disabled={loading} className="w-full py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Flashcards'}
          </button>
          {error && <p className="text-sm text-error">{error}</p>}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto py-8">
      {/* Progress */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <span className="text-muted-foreground">{flashcards.flashcard_set_title || 'Flashcards'}</span>
        <span className="font-medium">{currentIndex + 1} / {cards.length}</span>
      </div>
      <div className="h-1 rounded-full bg-muted mb-6 overflow-hidden">
        <div className="h-full bg-accent transition-all" style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }} />
      </div>

      {/* Card */}
      <div
        onClick={() => setShowAnswer(!showAnswer)}
        className={`min-h-[280px] p-8 rounded-2xl border-2 cursor-pointer flex flex-col items-center justify-center text-center transition-all ${
          showAnswer ? 'border-accent bg-accent-light' : 'border-border bg-card hover:border-accent/30'
        }`}
      >
        <p className="text-xs text-muted-foreground uppercase tracking-wide mb-4">
          {showAnswer ? 'Answer' : 'Question'}
        </p>
        <p className={`${showAnswer ? 'text-base' : 'text-lg font-medium'}`}>
          {showAnswer ? card?.back : card?.front}
        </p>
        {showAnswer && card?.category && (
          <span className="mt-6 px-3 py-1 rounded-full bg-accent/10 text-accent text-xs">{card.category}</span>
        )}
        <p className="mt-8 text-xs text-muted-foreground flex items-center gap-1">
          <RotateCw className="w-3 h-3" /> Click to flip
        </p>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6">
        <button onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))} disabled={currentIndex === 0}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border hover:bg-muted disabled:opacity-30 text-sm">
          <ChevronLeft className="w-4 h-4" /> Previous
        </button>
        <button onClick={() => setCurrentIndex(Math.min(cards.length - 1, currentIndex + 1))} disabled={currentIndex === cards.length - 1}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border hover:bg-muted disabled:opacity-30 text-sm">
          Next <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mt-8">
        <button onClick={clearFlashcards} className="flex-1 py-3 rounded-xl border border-border hover:bg-muted font-medium flex items-center justify-center gap-2 text-sm">
          <RotateCcw className="w-4 h-4" /> New Set
        </button>
        <button onClick={() => { const b = new Blob([JSON.stringify(flashcards, null, 2)]); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'flashcards.json'; a.click() }}
          className="px-4 py-3 rounded-xl border border-border hover:bg-muted">
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
