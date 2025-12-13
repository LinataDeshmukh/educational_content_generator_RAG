'use client'

import { useEffect } from 'react'
import { useStore } from '@/lib/store'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, sidebarOpen } = useStore()

  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    root.style.setProperty('--sidebar-width', sidebarOpen ? '240px' : '64px')
  }, [theme, sidebarOpen])

  return <>{children}</>
}
