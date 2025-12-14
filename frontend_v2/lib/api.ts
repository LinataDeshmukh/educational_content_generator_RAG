const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      let errorMessage = `Request failed: ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch {
        // Use default error message
      }
      throw new Error(errorMessage)
    }

    return response.json()
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health')
  }

  async uploadPdf(files: File[]): Promise<{
    document_id: string
    filename: string
    page_count: number
    chunks_created: number
  }> {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))

    const response = await fetch(`${this.baseUrl}/upload/`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      let errorMessage = `Upload failed: ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch {
        // Use default error message
      }
      throw new Error(errorMessage)
    }

    return response.json()
  }

  async listDocuments(): Promise<{
    documents: Array<{
      document_id: string
      filename: string
      vector_count: number
    }>
  }> {
    return this.request('/documents/list')
  }

  async chat(
    question: string,
    documentId: string,
    filename?: string
  ): Promise<{
    answer: string
    sources: Array<{ text: string; metadata?: { page_number?: number } }>
    from_document: boolean
    message?: string
    filename?: string
  }> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        question,
        document_id: documentId,
        filename,
      }),
    })
  }


  async generateQuiz(
    numQuestions: number,
    questionTypes: string[],
    documentId: string
  ): Promise<{ quiz: any }> {
    return this.request('/quiz/', {
      method: 'POST',
      body: JSON.stringify({
        num_questions: numQuestions,
        question_types: questionTypes,
        document_id: documentId,
      }),
    })
  }

  async evaluateAnswer(
    userAnswer: string,
    correctAnswer: string,
    question: string
  ): Promise<{ is_correct: boolean; feedback: string }> {
    return this.request('/quiz/evaluate-answer', {
      method: 'POST',
      body: JSON.stringify({
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        question,
      }),
    })
  }

  async generateSummary(
    length: 'short' | 'medium' | 'long',
    documentId: string
  ): Promise<{ summary: any }> {
    return this.request('/summary/', {
      method: 'POST',
      body: JSON.stringify({
        length,
        document_id: documentId,
      }),
    })
  }

  async generateFlashcards(
    numFlashcards: number,
    documentId: string
  ): Promise<{ flashcards: any }> {
    return this.request('/flashcards/', {
      method: 'POST',
      body: JSON.stringify({
        num_flashcards: numFlashcards,
        document_id: documentId,
      }),
    })
  }

  async generateCompetitiveQuizBank(
    numQuestions: number,
    documentId?: string,
    topic?: string
  ): Promise<{ quiz_id: string; question_bank: any[] }> {
    return this.request('/competitive-quiz/generate-bank', {
      method: 'POST',
      body: JSON.stringify({
        num_questions: numQuestions,
        document_id: documentId,
        topic,
      }),
    })
  }

  async startCompetitiveQuiz(
    quizId: string,
    numQuestions: number
  ): Promise<{
    session_id: string
    question: any
    current_difficulty: string
  }> {
    return this.request('/competitive-quiz/start', {
      method: 'POST',
      body: JSON.stringify({
        quiz_id: quizId,
        num_questions: numQuestions,
      }),
    })
  }

  async submitCompetitiveAnswer(
    sessionId: string,
    questionId: string,
    answer: string
  ): Promise<{
    is_correct: boolean
    correct_answer: string
    explanation: string
    reward: number
    stats: any
    is_complete: boolean
    next_question?: any
    next_difficulty?: string
  }> {
    return this.request('/competitive-quiz/answer', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        answer,
      }),
    })
  }
}

export const apiClient = new APIClient()

