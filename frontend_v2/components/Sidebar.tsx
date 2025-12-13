'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, Upload, MessageCircle, FileQuestion, Trophy, FileText, Layers,
  Sun, Moon, PanelLeftClose, PanelLeft, BookOpen
} from 'lucide-react'
import { useStore } from '@/lib/store'
import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'

const navItems = [
  { icon: Home, label: 'Home', href: '/', requiresDoc: false },
  { icon: Upload, label: 'Upload', href: '/upload', requiresDoc: false },
  { icon: MessageCircle, label: 'Chat', href: '/chat', requiresDoc: true },
  { icon: FileQuestion, label: 'Quiz', href: '/quiz', requiresDoc: true },
  { icon: Trophy, label: 'Competitive', href: '/competitive-quiz', requiresDoc: true },
  { icon: FileText, label: 'Summary', href: '/summary', requiresDoc: true },
  { icon: Layers, label: 'Flashcards', href: '/flashcards', requiresDoc: true },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { documentId, theme, toggleTheme, sidebarOpen, toggleSidebar } = useStore()
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)

  useEffect(() => {
    const check = async () => {
      try {
        await apiClient.healthCheck()
        setBackendOnline(true)
      } catch {
        setBackendOnline(false)
      }
    }
    check()
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside 
      className={`fixed left-0 top-0 h-screen bg-card border-r border-border flex flex-col transition-all duration-200 z-50 ${
        sidebarOpen ? 'w-60' : 'w-16'
      }`}
    >
      {/* Logo */}
      <div className={`h-14 border-b border-border flex items-center ${sidebarOpen ? 'justify-between px-4' : 'justify-center'}`}>
        {sidebarOpen && (
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
              <BookOpen className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold">Learnify</span>
          </Link>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
        >
          {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            const isDisabled = item.requiresDoc && !documentId

            // Determine styles
            let className = `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              sidebarOpen ? '' : 'justify-center'
            } `

            if (isActive) {
              className += 'bg-accent text-white'
            } else if (isDisabled) {
              className += 'opacity-30 cursor-not-allowed text-muted-foreground'
            } else {
              className += 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }

            return (
              <li key={item.href}>
                <Link
                  href={isDisabled ? '#' : item.href}
                  onClick={(e) => isDisabled && e.preventDefault()}
                  className={className}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <item.icon className="w-4 h-4 flex-shrink-0" />
                  {sidebarOpen && <span>{item.label}</span>}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-border space-y-1">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors ${
            sidebarOpen ? '' : 'justify-center'
          }`}
          title={!sidebarOpen ? (theme === 'dark' ? 'Light mode' : 'Dark mode') : undefined}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {sidebarOpen && <span>{theme === 'dark' ? 'Light mode' : 'Dark mode'}</span>}
        </button>

        {/* Backend Status */}
        <div 
          className={`flex items-center gap-3 px-3 py-2.5 text-sm text-muted-foreground ${
            sidebarOpen ? '' : 'justify-center'
          }`}
          title={backendOnline === null ? 'Checking backend...' : backendOnline ? 'Backend online' : 'Backend offline'}
        >
          <div 
            className={`w-2 h-2 rounded-full flex-shrink-0 ${
              backendOnline === null ? 'bg-muted-foreground' : backendOnline ? 'bg-success' : 'bg-error'
            }`}
          />
          {sidebarOpen && <span className="text-xs">{backendOnline ? 'Online' : backendOnline === null ? 'Checking...' : 'Offline'}</span>}
        </div>
      </div>
    </aside>
  )
}
