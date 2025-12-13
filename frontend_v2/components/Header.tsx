'use client'

import { usePathname } from 'next/navigation'
import { FileText, X } from 'lucide-react'
import { useStore } from '@/lib/store'
import Link from 'next/link'

const pageTitles: Record<string, string> = {
  '/': 'Home',
  '/upload': 'Upload Document',
  '/chat': 'Chat',
  '/quiz': 'Quiz',
  '/competitive-quiz': 'Competitive Quiz',
  '/summary': 'Summary',
  '/flashcards': 'Flashcards',
}

// App name
const APP_NAME = 'Learnify'

export default function Header() {
  const pathname = usePathname()
  const { documentId, filename, clearDocument, clearMessages } = useStore()

  return (
    <header className="h-14 border-b border-border bg-card px-6 flex items-center justify-between">
      <h1 className="font-semibold">{pageTitles[pathname] || APP_NAME}</h1>
      
      {documentId && (
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-light text-accent text-sm">
            <FileText className="w-3.5 h-3.5" />
            <span className="max-w-[200px] truncate font-medium">{filename || 'Document'}</span>
          </div>
          <button
            onClick={() => { clearDocument(); clearMessages() }}
            className="p-1.5 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            title="Clear document"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      {!documentId && pathname !== '/upload' && pathname !== '/' && (
        <Link 
          href="/upload" 
          className="text-sm text-accent hover:underline"
        >
          Upload a document to get started →
        </Link>
      )}
    </header>
  )
}

