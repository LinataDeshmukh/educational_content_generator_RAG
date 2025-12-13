'use client'

import { useState } from 'react'
import { Loader2, Check, X, Lightbulb, ChevronRight, RotateCcw, FileText, Target } from 'lucide-react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

const diffColors: Record<string, string> = { low: 'bg-emerald-500', medium: 'bg-amber-500', hard: 'bg-rose-500' }

export default function CompetitiveQuizPage() {
  const { documentId, quizId, sessionId, questionBank, currentQuestion, currentDifficulty, answerHistory, stats, answerResult, waitingForNext,
    setQuizBank, setSession, setCurrentQuestion, addToHistory, setStats, setAnswerResult, setWaitingForNext, clearSession, clearAll } = useStore()
  const [source, setSource] = useState<'document' | 'topic'>('document')
  const [topic, setTopic] = useState('')
  const [numQ, setNumQ] = useState(10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [hint, setHint] = useState(false)

  if (!documentId) {
    return (
      <div className="max-w-md mx-auto py-20 text-center">
        <p className="text-muted-foreground mb-4">No document loaded</p>
        <Link href="/upload" className="text-accent hover:underline">Upload a PDF →</Link>
      </div>
    )
  }

  const generateBank = async () => {
    if (source === 'topic' && !topic.trim()) { setError('Enter a topic'); return }
    setLoading(true); setError(null)
    try {
      const res = await apiClient.generateCompetitiveQuizBank(30, source === 'document' ? documentId : undefined, source === 'topic' ? topic : undefined)
      setQuizBank(res.quiz_id, res.question_bank)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  const startQuiz = async () => {
    if (!quizId) return
    setLoading(true); setError(null)
    try {
      const res = await apiClient.startCompetitiveQuiz(quizId, numQ)
      setSession(res.session_id, res.question, res.current_difficulty)
      setSelected(null); setHint(false)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  const submitAnswer = async () => {
    if (!sessionId || !currentQuestion || !selected) return
    setLoading(true)
    try {
      const res = await apiClient.submitCompetitiveAnswer(sessionId, currentQuestion.question_id, selected)
      addToHistory({ question: currentQuestion.question, user_answer: selected, correct_answer: res.correct_answer, is_correct: res.is_correct, reward: res.reward, difficulty: currentDifficulty })
      setStats(res.stats); setAnswerResult(res); setWaitingForNext(true)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  const nextQ = () => {
    if (answerResult?.is_complete) return
    setCurrentQuestion(answerResult?.next_question, answerResult?.next_difficulty)
    setAnswerResult(null); setWaitingForNext(false); setSelected(null); setHint(false)
  }

  // Generate bank
  if (!quizId) {
    return (
      <div className="max-w-xl mx-auto py-8 space-y-6">
        <div>
          <label className="block text-sm font-medium mb-3">Question source</label>
          <div className="grid grid-cols-2 gap-3">
            {[['document', FileText, 'From your document'], ['topic', Target, 'Custom topic']].map(([k, Icon, desc]: any) => (
              <button key={k} onClick={() => setSource(k)}
                className={`p-4 rounded-xl border text-left transition-colors ${source === k ? 'border-accent bg-accent-light' : 'border-border hover:border-accent/30'}`}>
                <Icon className="w-5 h-5 mb-2" />
                <p className="font-medium capitalize">{k}</p>
                <p className="text-xs text-muted-foreground">{desc}</p>
              </button>
            ))}
          </div>
        </div>
        {source === 'topic' && (
          <input type="text" value={topic} onChange={e => setTopic(e.target.value)} placeholder="Enter topic..."
            className="w-full px-4 py-3 rounded-xl bg-card border border-border text-sm focus:outline-none focus:border-accent" />
        )}
        <button onClick={generateBank} disabled={loading} className="w-full py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2">
          {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating 30 questions...</> : 'Generate Question Bank'}
        </button>
        {error && <p className="text-sm text-error">{error}</p>}
      </div>
    )
  }

  // Start quiz
  if (!sessionId) {
    const counts = questionBank?.reduce((a: any, q: any) => { a[q.difficulty] = (a[q.difficulty] || 0) + 1; return a }, {}) || {}
    return (
      <div className="max-w-xl mx-auto py-8 space-y-6">
        <div className="p-4 rounded-xl bg-accent-light border border-accent/20">
          <p className="font-medium mb-2">Question bank ready</p>
          <div className="flex gap-3 text-xs">
            {Object.entries(counts).map(([d, c]: any) => (
              <span key={d} className="flex items-center gap-1"><span className={`w-2 h-2 rounded-full ${diffColors[d]}`} />{d}: {c}</span>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-3">Questions per quiz: {numQ}</label>
          <input type="range" min={5} max={10} value={numQ} onChange={e => setNumQ(+e.target.value)} className="w-full accent-accent" />
        </div>
        <div className="flex gap-3">
          <button onClick={startQuiz} disabled={loading} className="flex-1 py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50">
            {loading ? 'Starting...' : 'Start Quiz'}
          </button>
          <button onClick={clearAll} className="px-4 py-3 rounded-xl border border-border hover:bg-muted text-sm">New Bank</button>
        </div>
      </div>
    )
  }

  // Complete
  if (answerResult?.is_complete) {
    const s = answerResult.stats || {}
    const accuracy = s.accuracy || 0
    const correctAnswers = s.correct_answers || 0
    const questionsAnswered = s.questions_answered || 0
    const totalReward = s.total_reward || 0
    const performanceTrend = s.performance_trend || 'stable'
    const difficultyDist = s.difficulty_distribution || {}
    
    // Calculate stats by difficulty
    const difficultyStats = answerHistory.reduce((acc: any, a: any) => {
      if (!acc[a.difficulty]) {
        acc[a.difficulty] = { total: 0, correct: 0, incorrect: 0, reward: 0 }
      }
      acc[a.difficulty].total++
      if (a.is_correct) {
        acc[a.difficulty].correct++
      } else {
        acc[a.difficulty].incorrect++
      }
      acc[a.difficulty].reward += a.reward
      return acc
    }, {})
    
    return (
      <div className="max-w-2xl mx-auto py-8">
        <div className="text-center mb-8">
          <p className="text-5xl mb-4">🎉</p>
          <h2 className="text-2xl font-bold">Quiz Complete!</h2>
        </div>

        {/* Overall Performance Summary */}
        <div className="mb-8 p-6 rounded-xl bg-card border border-border">
          <h3 className="text-xl font-semibold mb-4">📊 Final Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <p className="text-2xl font-bold">{accuracy.toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground">Accuracy</p>
              <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-accent rounded-full transition-all" style={{ width: `${accuracy}%` }} />
              </div>
            </div>
            <div>
              <p className="text-2xl font-bold">{correctAnswers}/{questionsAnswered}</p>
              <p className="text-xs text-muted-foreground">Correct Answers</p>
              <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-success rounded-full transition-all" style={{ width: `${questionsAnswered ? (correctAnswers / questionsAnswered * 100) : 0}%` }} />
              </div>
            </div>
            <div>
              <p className="text-2xl font-bold">{totalReward.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground">Total Reward</p>
              <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-accent/50 rounded-full transition-all" style={{ width: `${Math.min((totalReward / (questionsAnswered * 10)) * 100, 100)}%` }} />
              </div>
            </div>
            <div>
              <p className="text-2xl font-bold capitalize">{performanceTrend}</p>
              <p className="text-xs text-muted-foreground">Performance Trend</p>
            </div>
          </div>

          {/* Visual Performance Breakdown */}
          <div className="mt-6">
            <h4 className="text-sm font-medium mb-3">Performance Breakdown</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-24">Correct</span>
                <div className="flex-1 h-6 bg-muted rounded-lg overflow-hidden flex">
                  <div className="bg-success flex items-center justify-center text-xs text-white font-medium" style={{ width: `${questionsAnswered ? (correctAnswers / questionsAnswered * 100) : 0}%` }}>
                    {correctAnswers > 0 && correctAnswers}
                  </div>
                  <div className="bg-error flex items-center justify-center text-xs text-white font-medium" style={{ width: `${questionsAnswered ? ((questionsAnswered - correctAnswers) / questionsAnswered * 100) : 0}%` }}>
                    {questionsAnswered - correctAnswers > 0 && (questionsAnswered - correctAnswers)}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded bg-success" />
                  <span>Correct ({correctAnswers})</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded bg-error" />
                  <span>Incorrect ({questionsAnswered - correctAnswers})</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Difficulty Distribution */}
        <div className="mb-8 p-6 rounded-xl bg-card border border-border">
          <h3 className="text-lg font-semibold mb-4">Difficulty Distribution</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {['low', 'medium', 'hard'].map((diff) => {
              const stats = difficultyStats[diff] || { total: 0, correct: 0, incorrect: 0, reward: 0 }
              const percentage = stats.total ? Math.round((stats.correct / stats.total) * 100) : 0
              return (
                <div key={diff} className="p-4 rounded-lg bg-muted/50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full ${diffColors[diff]}`} />
                      <span className="font-medium capitalize">{diff}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{percentage}%</span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total:</span>
                      <span>{stats.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-success">Correct:</span>
                      <span className="text-success">{stats.correct}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-error">Incorrect:</span>
                      <span className="text-error">{stats.incorrect}</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-border">
                      <span className="text-muted-foreground">Reward:</span>
                      <span className="font-medium">{stats.reward.toFixed(1)}</span>
                    </div>
                  </div>
                  {stats.total > 0 && (
                    <div className="mt-3 h-4 bg-muted rounded-lg overflow-hidden flex">
                      <div className="bg-success" style={{ width: `${(stats.correct / stats.total) * 100}%` }} />
                      <div className="bg-error" style={{ width: `${(stats.incorrect / stats.total) * 100}%` }} />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Answer History with Visual Grid */}
        <div className="mb-8 p-6 rounded-xl bg-card border border-border">
          <h3 className="text-lg font-semibold mb-4">📝 Answer History</h3>
          
          {/* Visual Grid */}
          <div className="mb-4">
            <div className="grid grid-cols-10 gap-2 mb-3">
              {answerHistory.map((a: any, i: number) => (
                <div
                  key={i}
                  className={`aspect-square rounded-lg flex flex-col items-center justify-center text-xs font-medium ${
                    a.is_correct ? 'bg-success text-white' : 'bg-error text-white'
                  }`}
                  title={`Q${i+1} (${a.difficulty}): ${a.is_correct ? 'Correct' : 'Incorrect'} - Reward: ${a.reward > 0 ? '+' : ''}${a.reward.toFixed(1)}`}
                >
                  <span>{i+1}</span>
                  <span className={`w-1.5 h-1.5 rounded-full mt-0.5 ${diffColors[a.difficulty]}`} />
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
                <span className="text-xs">• Color dot = Difficulty</span>
              </div>
            </div>
          </div>

          {/* Detailed List */}
          <div className="space-y-2 mt-4 pt-4 border-t border-border">
            {answerHistory.map((a: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted/50 text-sm">
                <div className="flex items-center gap-3">
                  <span className="font-medium">Q{i+1}</span>
                  <span className={`w-2 h-2 rounded-full ${diffColors[a.difficulty]}`} />
                  <span className="text-xs text-muted-foreground capitalize">{a.difficulty}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={a.is_correct ? 'text-success' : 'text-error'}>
                    {a.is_correct ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                  </span>
                  <span className={`text-xs font-medium ${a.reward > 0 ? 'text-success' : 'text-error'}`}>
                    {a.reward > 0 ? '+' : ''}{a.reward.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button onClick={clearSession} className="w-full py-3 rounded-xl bg-accent text-white font-medium flex items-center justify-center gap-2">
          <RotateCcw className="w-4 h-4" /> New Quiz
        </button>
      </div>
    )
  }

  // Active quiz
  const diff = currentDifficulty || 'medium'
  return (
    <div className="max-w-xl mx-auto py-8">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-muted-foreground">Question {answerHistory.length + 1}</span>
        <span className={`px-2 py-1 rounded-full text-white text-xs capitalize ${diffColors[diff]}`}>{diff}</span>
      </div>

      {stats && (
        <div className="mb-6 p-4 rounded-xl bg-card border border-border">
          <h4 className="text-sm font-medium mb-3">📊 Current Statistics</h4>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[[`${stats.accuracy?.toFixed(0)}%`, 'Accuracy'], [`${stats.correct_answers}/${stats.questions_answered}`, 'Correct'], [stats.total_reward?.toFixed(1), 'Reward']].map(([v, l]) => (
              <div key={l} className="text-center">
                <p className="text-lg font-bold">{v}</p>
                <p className="text-xs text-muted-foreground">{l}</p>
              </div>
            ))}
          </div>
          
          {/* Progress bars */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-20">Accuracy</span>
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-accent rounded-full transition-all" style={{ width: `${stats.accuracy || 0}%` }} />
              </div>
              <span className="text-xs text-muted-foreground w-12 text-right">{stats.accuracy?.toFixed(0)}%</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-20">Progress</span>
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-success rounded-full transition-all" style={{ width: `${stats.questions_answered ? (stats.correct_answers / stats.questions_answered * 100) : 0}%` }} />
              </div>
              <span className="text-xs text-muted-foreground w-12 text-right">{stats.correct_answers}/{stats.questions_answered}</span>
            </div>
          </div>

          {/* Difficulty breakdown if available */}
          {answerHistory.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border">
              <div className="flex items-center gap-4 text-xs">
                {['low', 'medium', 'hard'].map((d) => {
                  const count = answerHistory.filter((a: any) => a.difficulty === d).length
                  if (count === 0) return null
                  return (
                    <div key={d} className="flex items-center gap-1">
                      <span className={`w-2 h-2 rounded-full ${diffColors[d]}`} />
                      <span className="capitalize">{d}: {count}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {!waitingForNext ? (
        <div className="space-y-4">
          <p className="font-medium">{currentQuestion?.question}</p>
          {currentQuestion?.hint && (
            <>
              <button onClick={() => setHint(!hint)} className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground">
                <Lightbulb className="w-3 h-3" /> {hint ? 'Hide hint' : 'Show hint'}
              </button>
              {hint && <p className="text-xs text-muted-foreground p-3 rounded-xl bg-muted">{currentQuestion.hint}</p>}
            </>
          )}
          <div className="space-y-2">
            {currentQuestion?.options?.map((opt: string, i: number) => (
              <button key={i} onClick={() => setSelected(opt[0])}
                className={`w-full p-3 rounded-xl border text-left text-sm transition-colors ${selected === opt[0] ? 'border-accent bg-accent-light' : 'border-border hover:border-accent/30'}`}>
                {opt}
              </button>
            ))}
          </div>
          <button onClick={submitAnswer} disabled={!selected || loading} className="w-full py-3 rounded-xl bg-accent text-white font-medium disabled:opacity-50">
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className={`p-4 rounded-xl ${answerResult?.is_correct ? 'bg-success/10' : 'bg-error/10'}`}>
            <div className="flex items-center gap-2 mb-1">
              {answerResult?.is_correct ? <Check className="w-5 h-5 text-success" /> : <X className="w-5 h-5 text-error" />}
              <span className="font-medium">{answerResult?.is_correct ? 'Correct!' : 'Incorrect'}</span>
            </div>
            <p className="text-sm text-muted-foreground">Reward: {answerResult?.reward?.toFixed(2)}</p>
          </div>
          {!answerResult?.is_correct && <p className="text-sm"><strong>Answer:</strong> {answerResult?.correct_answer}</p>}
          {answerResult?.explanation && <p className="text-sm text-muted-foreground">{answerResult.explanation}</p>}
          <button onClick={nextQ} className="w-full py-3 rounded-xl bg-accent text-white font-medium flex items-center justify-center gap-2">
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
      {error && <p className="mt-4 text-sm text-error">{error}</p>}
    </div>
  )
}
