import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  // Theme
  theme: 'light' | 'dark'
  toggleTheme: () => void
  
  // Sidebar
  sidebarOpen: boolean
  toggleSidebar: () => void
  
  // Document
  documentId: string | null
  filename: string | null
  setDocument: (id: string, filename?: string) => void
  clearDocument: () => void
  
  // Chat
  messages: Array<{ role: 'user' | 'assistant'; content: string; sources?: any[] }>
  addMessage: (msg: any) => void
  clearMessages: () => void
  
  // Quiz
  quiz: any | null
  answers: Record<string, any>
  showResults: boolean
  setQuiz: (quiz: any) => void
  setAnswer: (key: string, val: any) => void
  setShowResults: (show: boolean) => void
  clearQuiz: () => void
  
  // Flashcards
  flashcards: any | null
  currentIndex: number
  showAnswer: boolean
  setFlashcards: (fc: any) => void
  setCurrentIndex: (i: number) => void
  setShowAnswer: (show: boolean) => void
  clearFlashcards: () => void
  
  // Competitive Quiz
  quizId: string | null
  sessionId: string | null
  questionBank: any[] | null
  currentQuestion: any | null
  currentDifficulty: string | null
  answerHistory: any[]
  stats: any | null
  answerResult: any | null
  waitingForNext: boolean
  setQuizBank: (id: string, bank: any[]) => void
  setSession: (sid: string, q: any, d: string) => void
  setCurrentQuestion: (q: any, d: string) => void
  addToHistory: (a: any) => void
  setStats: (s: any) => void
  setAnswerResult: (r: any) => void
  setWaitingForNext: (w: boolean) => void
  clearSession: () => void
  clearAll: () => void
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'light',
      toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
      
      sidebarOpen: true,
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      
      documentId: null,
      filename: null,
      setDocument: (id, filename) => set({ documentId: id, filename: filename || null }),
      clearDocument: () => set({ documentId: null, filename: null }),
      
      messages: [],
      addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
      clearMessages: () => set({ messages: [] }),
      
      quiz: null,
      answers: {},
      showResults: false,
      setQuiz: (quiz) => set({ quiz, answers: {}, showResults: false }),
      setAnswer: (key, val) => set((s) => ({ answers: { ...s.answers, [key]: val } })),
      setShowResults: (show) => set({ showResults: show }),
      clearQuiz: () => set({ quiz: null, answers: {}, showResults: false }),
      
      flashcards: null,
      currentIndex: 0,
      showAnswer: false,
      setFlashcards: (fc) => set({ flashcards: fc, currentIndex: 0, showAnswer: false }),
      setCurrentIndex: (i) => set({ currentIndex: i, showAnswer: false }),
      setShowAnswer: (show) => set({ showAnswer: show }),
      clearFlashcards: () => set({ flashcards: null, currentIndex: 0, showAnswer: false }),
      
      quizId: null,
      sessionId: null,
      questionBank: null,
      currentQuestion: null,
      currentDifficulty: null,
      answerHistory: [],
      stats: null,
      answerResult: null,
      waitingForNext: false,
      setQuizBank: (id, bank) => set({ quizId: id, questionBank: bank }),
      setSession: (sid, q, d) => set({ sessionId: sid, currentQuestion: q, currentDifficulty: d, answerHistory: [], stats: null, answerResult: null, waitingForNext: false }),
      setCurrentQuestion: (q, d) => set({ currentQuestion: q, currentDifficulty: d }),
      addToHistory: (a) => set((s) => ({ answerHistory: [...s.answerHistory, a] })),
      setStats: (s) => set({ stats: s }),
      setAnswerResult: (r) => set({ answerResult: r }),
      setWaitingForNext: (w) => set({ waitingForNext: w }),
      clearSession: () => set({ sessionId: null, currentQuestion: null, currentDifficulty: null, answerHistory: [], stats: null, answerResult: null, waitingForNext: false }),
      clearAll: () => set({ quizId: null, sessionId: null, questionBank: null, currentQuestion: null, currentDifficulty: null, answerHistory: [], stats: null, answerResult: null, waitingForNext: false }),
    }),
    {
      name: 'learnify-storage',
      partialize: (s) => ({ theme: s.theme, sidebarOpen: s.sidebarOpen, documentId: s.documentId, filename: s.filename, quizId: s.quizId, questionBank: s.questionBank }),
    }
  )
)
