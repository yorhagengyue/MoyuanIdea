import { useState, useEffect } from 'react'
import Page1Intro from './pages/Page1Intro'
import Page2Reason from './pages/Page2Reason'
import Page3Feedback from './pages/Page3Feedback'

const BASE_OPTIONS = [
  { key: '峰', label: '山峰', subtitle: '又高又尖', imageUrl: '' },
  { key: '岭', label: '山岭', subtitle: '连绵起伏', imageUrl: '' },
  { key: '崖', label: '山崖', subtitle: '陡直落差', imageUrl: '' },
  { key: '谷', label: '山谷', subtitle: '两山低地', imageUrl: '' },
]

async function fetchJson(url, init) {
  const res = await fetch(url, init)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
async function postJson(url, body) {
  return fetchJson(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export default function App() {
  const [page, setPage] = useState(0)
  const [options, setOptions] = useState(BASE_OPTIONS)
  const [imagesLoading, setImagesLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [whyPrompt, setWhyPrompt] = useState('')
  const [whyLoading, setWhyLoading] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [feedbackLoading, setFeedbackLoading] = useState(false)
  const [lessonTheme, setLessonTheme] = useState('山的不同叫法')

  useEffect(() => {
    fetchJson('/api/lesson-pack')
      .then(pack => setLessonTheme(pack.theme || '山的不同叫法'))
      .catch(() => {})

    setImagesLoading(true)
    fetchJson('/api/classroom/option-images')
      .then(payload => {
        const mapped = {}
        ;(payload.items || []).forEach(item => { mapped[item.key] = item })
        setOptions(prev => prev.map(opt => ({
          ...opt,
          subtitle: mapped[opt.key]?.subtitle || opt.subtitle,
          imageUrl: mapped[opt.key]?.image_url || '',
        })))
      })
      .catch(() => {})
      .finally(() => setImagesLoading(false))
  }, [])

  const pageClass = (n) => {
    if (n === page) return 'page active'
    if (n < page) return 'page left'
    return 'page right'
  }

  async function handleSelectOption(option) {
    setSelected(option)
    setWhyPrompt('')
    setWhyLoading(true)
    setPage(1)
    try {
      const res = await postJson('/api/classroom/ask-why', { selected_concept: option.key })
      setWhyPrompt(`${res.question || ''} ${res.encouragement || ''}`.trim())
    } catch {
      setWhyPrompt(`你选了"${option.key}"，为什么这么选？请用"因为……"说完整句。`)
    } finally {
      setWhyLoading(false)
    }
  }

  async function handleSubmitAnswer(text) {
    if (!selected || !text.trim()) return
    const answer = /[。！？.!?]$/.test(text.trim()) ? text.trim() : text.trim() + '。'
    setFeedback(null)
    setFeedbackLoading(true)
    setPage(2)
    try {
      const res = await postJson('/api/classroom/evaluate', {
        selected_concept: selected.key,
        student_answer: answer,
      })
      setFeedback({ ...res, studentAnswer: answer })
    } catch {
      setFeedback({ error: true, studentAnswer: answer })
    } finally {
      setFeedbackLoading(false)
    }
  }

  function handleRestart() {
    setSelected(null)
    setWhyPrompt('')
    setFeedback(null)
    setFeedbackLoading(false)
    setPage(0)
  }

  return (
    <>
      <div className="paper-grain" aria-hidden="true" />

      {/* Top banner */}
      <header className="float-down sticky top-0 z-40 px-6 py-3 flex items-center justify-between gap-4
        border-b border-amber-200/60 bg-amber-50/90 backdrop-blur-sm shadow-sm">
        <div>
          <p className="text-xs font-bold tracking-widest text-amber-700 uppercase">Moyuan AI-native Classroom</p>
          <h1 className="text-xl font-black text-stone-800 leading-tight">{lessonTheme}</h1>
        </div>
        <div className="flex gap-2 text-xs font-semibold shrink-0">
          {['导入选图', '说理由', 'AI反馈'].map((label, i) => (
            <span key={i} className={`px-3 py-1 rounded-full border transition-all duration-300
              ${page === i
                ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                : 'border-stone-300 text-stone-400'}`}>
              {i + 1}. {label}
            </span>
          ))}
        </div>
      </header>

      <div className="page-wrapper">
        <div className={pageClass(0)}>
          <Page1Intro
            options={options}
            imagesLoading={imagesLoading}
            lessonTheme={lessonTheme}
            onSelect={handleSelectOption}
          />
        </div>
        <div className={pageClass(1)}>
          <Page2Reason
            options={options}
            selected={selected}
            whyPrompt={whyPrompt}
            whyLoading={whyLoading}
            onSubmit={handleSubmitAnswer}
            onBack={() => setPage(0)}
          />
        </div>
        <div className={pageClass(2)}>
          <Page3Feedback
            selected={selected}
            feedback={feedback}
            loading={feedbackLoading}
            onRestart={handleRestart}
          />
        </div>
      </div>
    </>
  )
}
