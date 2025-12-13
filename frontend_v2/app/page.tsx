'use client'

import { Upload, MessageCircle, FileQuestion, Trophy, FileText, Layers, ArrowRight, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useStore } from '@/lib/store'

const features = [
  { icon: MessageCircle, title: 'Chat', desc: 'Ask questions about your material', href: '/chat', color: 'bg-blue-500' },
  { icon: FileQuestion, title: 'Quiz', desc: 'Test your knowledge', href: '/quiz', color: 'bg-purple-500' },
  { icon: Trophy, title: 'Competitive', desc: 'Adaptive difficulty quiz', href: '/competitive-quiz', color: 'bg-amber-500' },
  { icon: FileText, title: 'Summary', desc: 'Get key insights', href: '/summary', color: 'bg-emerald-500' },
  { icon: Layers, title: 'Flashcards', desc: 'Study with cards', href: '/flashcards', color: 'bg-rose-500' },
]

export default function Home() {
  const { documentId, filename } = useStore()

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Hero */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-light text-accent text-sm font-medium mb-4">
          <BookOpen className="w-4 h-4" />
          Learnify
        </div>
        <h1 className="text-4xl font-bold tracking-tight mb-3">
          Transform Documents into
          <br />
          <span className="text-accent">Learning Experiences</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto">
          Upload your educational PDFs and interact with them through chat, quizzes, summaries, and flashcards.
        </p>
      </div>

      {/* Document Status or Upload CTA */}
      {documentId ? (
        <div className="mb-10 p-6 rounded-2xl bg-card border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Current Document</p>
              <p className="text-xl font-semibold">{filename || 'Document loaded'}</p>
            </div>
            <Link 
              href="/chat" 
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-accent text-white font-medium hover:opacity-90 transition-opacity"
            >
              Start Learning <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      ) : (
        <Link href="/upload">
          <div className="mb-10 p-8 rounded-2xl border-2 border-dashed border-border hover:border-accent hover:bg-accent-light/30 transition-all cursor-pointer text-center">
            <Upload className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
            <p className="font-semibold mb-1">Upload a PDF to get started</p>
            <p className="text-sm text-muted-foreground">Drag and drop or click to browse</p>
          </div>
        </Link>
      )}

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((f) => {
          const isDisabled = !documentId
          return (
            <Link key={f.href} href={isDisabled ? '#' : f.href} onClick={(e) => isDisabled && e.preventDefault()}>
              <div className={`p-5 rounded-xl border border-border bg-card hover:shadow-md transition-all ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-accent/30'}`}>
                <div className={`w-10 h-10 rounded-lg ${f.color} flex items-center justify-center mb-3`}>
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold mb-1">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            </Link>
          )
        })}
      </div>

      {/* How it works */}
      <div className="mt-16 pt-8 border-t border-border">
        <h2 className="text-lg font-semibold mb-6">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { step: '1', title: 'Upload', desc: 'Add your PDF documents (up to 300 pages)' },
            { step: '2', title: 'Process', desc: 'AI indexes and understands your content' },
            { step: '3', title: 'Learn', desc: 'Chat, quiz, summarize, or create flashcards' },
          ].map((s) => (
            <div key={s.step} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-semibold flex-shrink-0">
                {s.step}
              </div>
              <div>
                <h3 className="font-medium mb-1">{s.title}</h3>
                <p className="text-sm text-muted-foreground">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
