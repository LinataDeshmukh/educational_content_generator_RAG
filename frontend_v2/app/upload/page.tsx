'use client'

import { useState, useEffect, useCallback } from 'react'
import { Upload, FileText, Loader2, Check, Trash2 } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface Doc { document_id: string; filename: string; vector_count: number }

export default function UploadPage() {
  const router = useRouter()
  const { documentId, filename, setDocument, clearDocument, clearMessages } = useStore()
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [existingDocs, setExistingDocs] = useState<Doc[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient.listDocuments()
      .then((res) => setExistingDocs(res.documents || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const dropped = Array.from(e.dataTransfer.files).filter((f) => f.type === 'application/pdf')
    if (dropped.length) { setFiles(dropped); setError(null) }
    else setError('Only PDF files are accepted')
  }, [])

  const handleUpload = async () => {
    if (!files.length) return
    setUploading(true)
    setError(null)
    try {
      const res = await apiClient.uploadPdf(files)
      setDocument(res.document_id, res.filename)
      clearMessages()
      setFiles([])
      router.push('/chat')
    } catch (e: any) {
      setError(e.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const selectDoc = (doc: Doc) => {
    setDocument(doc.document_id, doc.filename)
    clearMessages()
    router.push('/chat')
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      {/* Current Document */}
      {documentId && (
        <div className="mb-8 p-4 rounded-xl bg-accent-light border border-accent/20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Check className="w-5 h-5 text-accent" />
            <div>
              <p className="font-medium">{filename}</p>
              <p className="text-xs text-muted-foreground font-mono">{documentId}</p>
            </div>
          </div>
          <button
            onClick={() => { clearDocument(); clearMessages() }}
            className="p-2 rounded-lg hover:bg-accent/10 text-accent"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className={`relative p-12 rounded-2xl border-2 border-dashed transition-all ${
          files.length ? 'border-accent bg-accent-light/30' : 'border-border hover:border-accent/50 hover:bg-muted/50'
        }`}
      >
        <input
          type="file"
          accept=".pdf"
          multiple
          onChange={(e) => { setFiles(Array.from(e.target.files || [])); setError(null) }}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="text-center">
          <Upload className="w-10 h-10 mx-auto mb-4 text-muted-foreground" />
          <p className="font-semibold mb-1">
            {files.length ? `${files.length} file(s) selected` : 'Drop PDF files here'}
          </p>
          <p className="text-sm text-muted-foreground">
            {files.length ? files.map((f) => f.name).join(', ') : 'or click to browse • max 300 pages'}
          </p>
        </div>
      </div>

      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full mt-4 py-3 rounded-xl bg-accent text-white font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {uploading ? <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</> : 'Upload & Start Learning'}
        </button>
      )}

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {/* Existing Documents */}
      {existingDocs.length > 0 && (
        <div className="mt-10">
          <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-4">
            Or continue with existing document
          </h2>
          <div className="space-y-2">
            {existingDocs.map((doc) => (
              <button
                key={doc.document_id}
                onClick={() => selectDoc(doc)}
                className="w-full flex items-center gap-4 p-4 rounded-xl border border-border bg-card hover:border-accent/30 hover:bg-muted/50 text-left transition-all"
              >
                <FileText className="w-5 h-5 text-accent" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{doc.filename}</p>
                  <p className="text-xs text-muted-foreground">{doc.vector_count} chunks indexed</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="mt-8 flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading documents...
        </div>
      )}
    </div>
  )
}
