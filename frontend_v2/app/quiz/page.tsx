'use client'

import { useState } from 'react'
import { Loader2, Check, X, Download, RotateCcw } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

export default function QuizPage() {
  const { documentId, quiz, answers, showResults, setQuiz, setAnswer, setShowResults, clearQuiz } = useStore()
  const [numQ, setNumQ] = useState(10)
  const [types, setTypes] = useState(['multiple_choice', 'short_answer'])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [evals, setEvals] = useState<Record<string, any>>({})

  if (!documentId) {
    return (
      <div className="max-w-md mx-auto py-20 text-center">
        <p className="text-muted-foreground mb-4">No document loaded</p>
        <Link href="/upload" className="text-accent hover:underline">Upload a PDF →</Link>
      </div>
    )
  }

  const generate = async () => {
    if (!types.length) { setError('Select at least one type'); return }
    setLoading(true); setError(null)
    try {
      const res = await apiClient.generateQuiz(numQ, types, documentId)
      setQuiz(res.quiz)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  const submit = async () => {
    setShowResults(true)
    for (let i = 0; i < (quiz?.questions?.length || 0); i++) {
      const q = quiz.questions[i]
      if (q.question_type === 'short_answer' && answers[`q_${i+1}`]?.trim()) {
        try {
          const r = await apiClient.evaluateAnswer(answers[`q_${i+1}`], q.correct_answer, q.question)
          setEvals(p => ({ ...p, [`q_${i+1}`]: r }))
        } catch { setEvals(p => ({ ...p, [`q_${i+1}`]: { is_correct: false } })) }
      }
    }
  }

  const calculateStats = () => {
    const questions = quiz?.questions || []
    const mcQuestions = questions.filter((q: any) => q.question_type === 'multiple_choice')
    const saQuestions = questions.filter((q: any) => q.question_type === 'short_answer')
    
    // MC stats
    let mcAnswered = 0, mcCorrect = 0
    mcQuestions.forEach((q: any, idx: number) => {
      const i = questions.indexOf(q)
      const k = `q_${i+1}`
      if (answers[k] !== undefined) {
        mcAnswered++
        const userOpt = q.options?.[answers[k]]
        const correctOpt = q.correct_answer
        if (userOpt?.[0] === correctOpt?.[0]) mcCorrect++
      }
    })
    
    // SA stats
    let saAnswered = 0, saCorrect = 0
    saQuestions.forEach((q: any, idx: number) => {
      const i = questions.indexOf(q)
      const k = `q_${i+1}`
      if (answers[k]?.trim()) {
        saAnswered++
        if (evals[k]?.is_correct) saCorrect++
      }
    })
    
    const totalQuestions = questions.length
    const totalAnswered = mcAnswered + saAnswered
    const totalCorrect = mcCorrect + saCorrect
    const mcTotal = mcQuestions.length
    const saTotal = saQuestions.length
    
    return {
      overall: {
        total: totalQuestions,
        answered: totalAnswered,
        correct: totalCorrect,
        percentage: totalQuestions ? Math.round((totalCorrect / totalQuestions) * 100) : 0,
        completionRate: totalQuestions ? Math.round((totalAnswered / totalQuestions) * 100) : 0,
        accuracyRate: totalAnswered ? Math.round((totalCorrect / totalAnswered) * 100) : 0,
      },
      mc: {
        total: mcTotal,
        answered: mcAnswered,
        correct: mcCorrect,
        incorrect: mcAnswered - mcCorrect,
        unanswered: mcTotal - mcAnswered,
        percentage: mcTotal ? Math.round((mcCorrect / mcTotal) * 100) : 0,
        accuracyRate: mcAnswered ? Math.round((mcCorrect / mcAnswered) * 100) : 0,
      },
      sa: {
        total: saTotal,
        answered: saAnswered,
        correct: saCorrect,
        incorrect: saAnswered - saCorrect,
        unanswered: saTotal - saAnswered,
        percentage: saTotal ? Math.round((saCorrect / saTotal) * 100) : 0,
        accuracyRate: saAnswered ? Math.round((saCorrect / saAnswered) * 100) : 0,
      },
      answerHistory: questions.map((q: any, i: number) => {
        const k = `q_${i+1}`
        let isCorrect = false
        if (q.question_type === 'multiple_choice') {
          const userOpt = q.options?.[answers[k]]
          isCorrect = userOpt?.[0] === q.correct_answer?.[0]
        } else {
          isCorrect = evals[k]?.is_correct || false
        }
        return {
          questionNum: i + 1,
          type: q.question_type,
          isCorrect,
          answered: q.question_type === 'multiple_choice' 
            ? answers[k] !== undefined 
            : !!answers[k]?.trim(),
        }
      }),
    }
  }
  
  const score = () => {
    const stats = calculateStats()
    return {
      correct: stats.overall.correct,
      total: stats.overall.total,
      pct: stats.overall.percentage,
    }
  }

  if (!quiz) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-3">Number of questions: {numQ}</label>
            <input type="range" min={5} max={50} value={numQ} onChange={e => setNumQ(+e.target.value)} className="w-full accent-accent" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-3">Question types</label>
            <div className="flex gap-4">
              {[['multiple_choice', 'Multiple Choice'], ['short_answer', 'Short Answer']].map(([k, l]) => (
                <label key={k} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={types.includes(k)} onChange={e => setTypes(e.target.checked ? [...types, k] : types.filter(t => t !== k))} className="rounded accent-accent" />
                  {l}
                </label>
              ))}
            </div>
          </div>
          <button onClick={generate} disabled={loading} className="w-full py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Quiz'}
          </button>
          {error && <p className="text-sm text-error">{error}</p>}
        </div>
      </div>
    )
  }

  const s = showResults ? score() : null
  const stats = showResults ? calculateStats() : null

  return (
    <div className="max-w-2xl mx-auto py-8">
      {showResults && s && stats && (
        <div className="mb-8 space-y-6">
          {/* Overall Score Card */}
          <div className="p-6 rounded-xl bg-card border border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">📊 Performance Summary</h2>
              <span className="text-4xl">{s.pct >= 70 ? '🎉' : s.pct >= 50 ? '📚' : '💪'}</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div>
                <p className="text-2xl font-bold">{s.pct}%</p>
                <p className="text-xs text-muted-foreground">Overall Score</p>
                <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full transition-all" style={{ width: `${s.pct}%` }} />
                </div>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.overall.correct}/{stats.overall.total}</p>
                <p className="text-xs text-muted-foreground">Correct Answers</p>
                <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-success rounded-full transition-all" style={{ width: `${stats.overall.total ? (stats.overall.correct / stats.overall.total * 100) : 0}%` }} />
                </div>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.overall.completionRate}%</p>
                <p className="text-xs text-muted-foreground">Completion Rate</p>
                <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-accent/50 rounded-full transition-all" style={{ width: `${stats.overall.completionRate}%` }} />
                </div>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.overall.accuracyRate}%</p>
                <p className="text-xs text-muted-foreground">Accuracy Rate</p>
                <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-success rounded-full transition-all" style={{ width: `${stats.overall.accuracyRate}%` }} />
                </div>
              </div>
            </div>

            {/* Visual Chart: Overall Performance */}
            <div className="mt-6">
              <h4 className="text-sm font-medium mb-3">Performance Breakdown</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground w-24">Correct</span>
                  <div className="flex-1 h-6 bg-muted rounded-lg overflow-hidden flex">
                    <div className="bg-success flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.overall.total ? (stats.overall.correct / stats.overall.total * 100) : 0}%` }}>
                      {stats.overall.correct > 0 && stats.overall.correct}
                    </div>
                    <div className="bg-error flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.overall.total ? ((stats.overall.answered - stats.overall.correct) / stats.overall.total * 100) : 0}%` }}>
                      {stats.overall.answered - stats.overall.correct > 0 && (stats.overall.answered - stats.overall.correct)}
                    </div>
                    <div className="bg-muted-foreground/20 flex items-center justify-center text-xs text-muted-foreground" style={{ width: `${stats.overall.total ? ((stats.overall.total - stats.overall.answered) / stats.overall.total * 100) : 0}%` }}>
                      {stats.overall.total - stats.overall.answered > 0 && (stats.overall.total - stats.overall.answered)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-success" />
                    <span>Correct ({stats.overall.correct})</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-error" />
                    <span>Incorrect ({stats.overall.answered - stats.overall.correct})</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-muted-foreground/20" />
                    <span>Unanswered ({stats.overall.total - stats.overall.answered})</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Breakdown by Question Type */}
          <div className="p-6 rounded-xl bg-card border border-border">
            <h3 className="text-lg font-semibold mb-4">Question Type Breakdown</h3>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Multiple Choice Stats */}
              {stats.mc.total > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Multiple Choice</h4>
                    <span className="text-sm text-muted-foreground">{stats.mc.percentage}%</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total:</span>
                      <span>{stats.mc.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Answered:</span>
                      <span>{stats.mc.answered}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-success">Correct:</span>
                      <span className="text-success">{stats.mc.correct}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-error">Incorrect:</span>
                      <span className="text-error">{stats.mc.incorrect}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Unanswered:</span>
                      <span>{stats.mc.unanswered}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-border">
                      <span className="text-muted-foreground">Accuracy:</span>
                      <span className="font-medium">{stats.mc.accuracyRate}%</span>
                    </div>
                  </div>
                  
                  {/* Visual Chart for MC */}
                  <div className="mt-4">
                    <div className="h-8 bg-muted rounded-lg overflow-hidden flex">
                      <div className="bg-success flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.mc.total ? (stats.mc.correct / stats.mc.total * 100) : 0}%` }}>
                        {stats.mc.correct > 0 && stats.mc.correct}
                      </div>
                      <div className="bg-error flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.mc.total ? (stats.mc.incorrect / stats.mc.total * 100) : 0}%` }}>
                        {stats.mc.incorrect > 0 && stats.mc.incorrect}
                      </div>
                      <div className="bg-muted-foreground/20 flex items-center justify-center text-xs text-muted-foreground" style={{ width: `${stats.mc.total ? (stats.mc.unanswered / stats.mc.total * 100) : 0}%` }}>
                        {stats.mc.unanswered > 0 && stats.mc.unanswered}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Short Answer Stats */}
              {stats.sa.total > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Short Answer</h4>
                    <span className="text-sm text-muted-foreground">{stats.sa.percentage}%</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total:</span>
                      <span>{stats.sa.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Answered:</span>
                      <span>{stats.sa.answered}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-success">Correct:</span>
                      <span className="text-success">{stats.sa.correct}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-error">Incorrect:</span>
                      <span className="text-error">{stats.sa.incorrect}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Unanswered:</span>
                      <span>{stats.sa.unanswered}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-border">
                      <span className="text-muted-foreground">Accuracy:</span>
                      <span className="font-medium">{stats.sa.accuracyRate}%</span>
                    </div>
                  </div>
                  
                  {/* Visual Chart for SA */}
                  <div className="mt-4">
                    <div className="h-8 bg-muted rounded-lg overflow-hidden flex">
                      <div className="bg-success flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.sa.total ? (stats.sa.correct / stats.sa.total * 100) : 0}%` }}>
                        {stats.sa.correct > 0 && stats.sa.correct}
                      </div>
                      <div className="bg-error flex items-center justify-center text-xs text-white font-medium" style={{ width: `${stats.sa.total ? (stats.sa.incorrect / stats.sa.total * 100) : 0}%` }}>
                        {stats.sa.incorrect > 0 && stats.sa.incorrect}
                      </div>
                      <div className="bg-muted-foreground/20 flex items-center justify-center text-xs text-muted-foreground" style={{ width: `${stats.sa.total ? (stats.sa.unanswered / stats.sa.total * 100) : 0}%` }}>
                        {stats.sa.unanswered > 0 && stats.sa.unanswered}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Answer History */}
          <div className="p-6 rounded-xl bg-card border border-border">
            <h3 className="text-lg font-semibold mb-4">📝 Answer History</h3>
            
            {/* Visual Grid */}
            <div className="mb-4">
              <div className="grid grid-cols-10 gap-2 mb-3">
                {stats.answerHistory.map((item: any) => (
                  <div
                    key={item.questionNum}
                    className={`aspect-square rounded-lg flex items-center justify-center text-xs font-medium ${
                      !item.answered
                        ? 'bg-muted-foreground/20 text-muted-foreground'
                        : item.isCorrect
                        ? 'bg-success text-white'
                        : 'bg-error text-white'
                    }`}
                    title={`Q${item.questionNum}: ${item.answered ? (item.isCorrect ? 'Correct' : 'Incorrect') : 'Not answered'}`}
                  >
                    {item.questionNum}
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 rounded-lg bg-success" />
                  <span>Correct</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 rounded-lg bg-error" />
                  <span>Incorrect</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 rounded-lg bg-muted-foreground/20" />
                  <span>Not answered</span>
                </div>
              </div>
            </div>

            {/* Detailed List */}
            <div className="space-y-2 mt-4 pt-4 border-t border-border">
              {stats.answerHistory.map((item: any) => (
                <div key={item.questionNum} className="flex items-center justify-between p-2 rounded-lg bg-muted/50 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Q{item.questionNum}</span>
                    <span className="text-xs text-muted-foreground">
                      ({item.type === 'multiple_choice' ? 'MC' : 'SA'})
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.answered ? (
                      item.isCorrect ? (
                        <span className="text-success flex items-center gap-1">
                          <Check className="w-4 h-4" /> Correct
                        </span>
                      ) : (
                        <span className="text-error flex items-center gap-1">
                          <X className="w-4 h-4" /> Incorrect
                        </span>
                      )
                    ) : (
                      <span className="text-muted-foreground">Not answered</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {quiz.questions?.map((q: any, i: number) => {
          const k = `q_${i+1}`
          const isCorrect = q.question_type === 'multiple_choice' 
            ? q.options?.[answers[k]]?.[0] === q.correct_answer?.[0]
            : evals[k]?.is_correct
          return (
            <div key={i} className="p-5 rounded-xl bg-card border border-border">
              <div className="flex gap-3 mb-4">
                <span className="text-sm font-medium text-muted-foreground">{i+1}.</span>
                <p className="text-sm font-medium flex-1">{q.question}</p>
                {showResults && answers[k] !== undefined && (
                  <span className={isCorrect ? 'text-success' : 'text-error'}>
                    {isCorrect ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
                  </span>
                )}
              </div>
              {q.question_type === 'multiple_choice' ? (
                <div className="space-y-2 ml-6">
                  {q.options?.map((opt: string, j: number) => {
                    const sel = answers[k] === j
                    const correct = opt[0] === q.correct_answer?.[0]
                    let cls = 'border-border hover:border-accent/30'
                    if (showResults) {
                      if (correct) cls = 'border-success bg-success/5'
                      else if (sel) cls = 'border-error bg-error/5'
                    } else if (sel) cls = 'border-accent bg-accent-light'
                    return (
                      <button key={j} onClick={() => !showResults && setAnswer(k, j)} disabled={showResults}
                        className={`w-full p-3 rounded-lg border text-left text-sm transition-colors ${cls}`}>
                        {opt}
                      </button>
                    )
                  })}
                </div>
              ) : (
                <div className="ml-6">
                  <textarea value={answers[k] || ''} onChange={e => !showResults && setAnswer(k, e.target.value)} disabled={showResults}
                    placeholder="Your answer..." rows={2}
                    className="w-full p-3 rounded-lg bg-muted border border-border text-sm resize-none focus:outline-none focus:border-accent" />
                  {showResults && <p className="mt-2 text-xs text-muted-foreground"><strong>Answer:</strong> {q.correct_answer}</p>}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="mt-6 flex gap-3">
        {!showResults ? (
          <button onClick={submit} className="flex-1 py-3 rounded-xl bg-accent text-white font-medium">Submit</button>
        ) : (
          <>
            <button onClick={() => { clearQuiz(); setEvals({}) }} className="flex-1 py-3 rounded-xl border border-border hover:bg-muted font-medium flex items-center justify-center gap-2">
              <RotateCcw className="w-4 h-4" /> New Quiz
            </button>
            <button onClick={() => { const b = new Blob([JSON.stringify(quiz, null, 2)]); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'quiz.json'; a.click() }}
              className="px-4 py-3 rounded-xl border border-border hover:bg-muted">
              <Download className="w-4 h-4" />
            </button>
          </>
        )}
      </div>
    </div>
  )
}
