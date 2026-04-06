/* Page 2 — 说理由 */
import { useState, useRef, useEffect } from 'react'

export default function Page2Reason({ options, selected, whyPrompt, whyLoading, onSubmit, onBack }) {
  const [text, setText] = useState('')
  const [recording, setRecording] = useState(false)
  const [speechAvail, setSpeechAvail] = useState(false)
  const recognizerRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) return
    setSpeechAvail(true)
    const r = new SR()
    r.lang = 'zh-CN'
    r.interimResults = false
    r.maxAlternatives = 1
    r.onresult = (e) => {
      const t = e.results?.[0]?.[0]?.transcript || ''
      setText(t)
      setRecording(false)
    }
    r.onerror = () => setRecording(false)
    r.onend = () => setRecording(false)
    recognizerRef.current = r
  }, [])

  useEffect(() => {
    if (selected) setText('')
    // focus input after why prompt loads
    if (!whyLoading && inputRef.current) inputRef.current.focus()
  }, [selected, whyLoading])

  const labels = ['A', 'B', 'C', 'D']
  const colors = ['bg-red-100 text-red-700', 'bg-green-100 text-green-700',
                  'bg-sky-100 text-sky-700', 'bg-amber-100 text-amber-700']

  function startSpeech() {
    if (!recognizerRef.current || recording) return
    setRecording(true)
    recognizerRef.current.start()
  }

  return (
    <div className="rise-in min-h-[calc(100vh-60px)] flex flex-col md:flex-row">

      {/* Left: 2×2 image grid */}
      <div className="md:w-1/2 p-6 flex flex-col justify-center">
        <h2 className="text-lg font-black text-stone-700 mb-4">你选的是哪张？</h2>
        <div className="grid grid-cols-2 gap-3 max-w-sm">
          {options.map((opt, i) => {
            const isSelected = selected?.key === opt.key
            return (
              <div key={opt.key}
                className={`relative rounded-2xl overflow-hidden border-2 transition-all duration-200
                  ${isSelected ? 'option-selected border-amber-400' : 'border-stone-200'}`}>
                {opt.imageUrl
                  ? <img src={opt.imageUrl} alt={opt.key} className="w-full aspect-[4/3] object-cover" />
                  : <div className="shimmer w-full aspect-[4/3]" />}
                <div className="absolute top-2 left-2">
                  <span className={`text-xs font-black px-2 py-0.5 rounded-full shadow ${colors[i]}`}>
                    {labels[i]}
                  </span>
                </div>
                <div className="absolute bottom-0 inset-x-0 bg-black/30 py-1 text-center">
                  <span className="text-white text-sm font-black">{opt.key}</span>
                </div>
                {isSelected && (
                  <div className="absolute inset-0 flex items-center justify-center bg-amber-400/20">
                    <span className="text-3xl badge-pop">✓</span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Right: child character + input */}
      <div className="md:w-1/2 p-6 flex flex-col gap-5 justify-center border-t md:border-t-0 md:border-l border-stone-200">

        {/* Child + AI robot row */}
        <div className="flex flex-col gap-4">

          {/* Child character with speech prompt */}
          <div className="flex items-start gap-3">
            <div className="shrink-0 flex flex-col items-center gap-1">
              <div className="w-12 h-12 rounded-full bg-sky-200 border-2 border-sky-400 flex items-center justify-center text-2xl shadow-sm">
                🧒
              </div>
              <span className="text-xs font-semibold text-sky-700">小朋友</span>
            </div>
            <div className="relative bubble-left rounded-2xl bg-sky-50 border border-sky-200 px-4 py-3 shadow-sm flex-1 min-h-[52px]">
              {selected
                ? <p className="text-sm text-stone-700">我选了&ldquo;<strong>{selected.key}</strong>&rdquo;，因为……</p>
                : <p className="text-sm text-stone-500 italic">请先在第一页选一张图。</p>}
            </div>
          </div>

          {/* AI robot with why-prompt */}
          <div className="flex items-start gap-3">
            <div className="shrink-0 flex flex-col items-center gap-1">
              <div className="w-12 h-12 rounded-full bg-teal-200 border-2 border-teal-400 flex items-center justify-center text-2xl shadow-sm">
                🤖
              </div>
              <span className="text-xs font-semibold text-teal-700">AI老师</span>
            </div>
            <div className="relative bubble-right rounded-2xl bg-teal-50 border border-teal-200 px-4 py-3 shadow-sm flex-1 min-h-[52px]">
              {whyLoading ? (
                <div className="flex items-center gap-1 py-1">
                  <span className="bounce-dot bg-teal-400" />
                  <span className="bounce-dot bg-teal-400" />
                  <span className="bounce-dot bg-teal-400" />
                  <span className="ml-2 text-xs text-teal-600">正在生成追问…</span>
                </div>
              ) : (
                <p className="text-sm text-stone-700">{whyPrompt || '说说你为什么这样选？'}</p>
              )}
            </div>
          </div>
        </div>

        {/* Input area */}
        <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-4 flex flex-col gap-3">
          <p className="text-xs font-bold text-stone-500 uppercase tracking-wider">你的回答</p>

          {/* Voice button */}
          {speechAvail && (
            <div className="flex justify-center">
              <div className="relative">
                {recording && (
                  <>
                    <div className="ripple-ring absolute inset-0 rounded-full border-2 border-sky-400" />
                    <div className="ripple-ring absolute inset-0 rounded-full border-2 border-sky-300" />
                    <div className="ripple-ring absolute inset-0 rounded-full border-2 border-sky-200" />
                  </>
                )}
                <button
                  onClick={startSpeech}
                  disabled={whyLoading || !selected}
                  className={`relative z-10 w-16 h-16 rounded-full border-2 flex items-center justify-center text-2xl shadow-md
                    transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed
                    ${recording
                      ? 'bg-red-100 border-red-400 pulse-mic'
                      : 'bg-sky-100 border-sky-400 hover:bg-sky-200 active:scale-95'}`}>
                  🎙️
                </button>
              </div>
            </div>
          )}
          {recording && (
            <p className="text-center text-xs text-red-500 font-semibold animate-pulse">录音中，请说话…</p>
          )}

          {/* Text input */}
          <div className="flex gap-2">
            <input
              ref={inputRef}
              value={text}
              onChange={e => setText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && onSubmit(text)}
              placeholder="语音不可用时可手动输入…"
              disabled={whyLoading || !selected}
              className="flex-1 px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-sm
                focus:outline-none focus:ring-2 focus:ring-amber-300 disabled:opacity-40"
            />
            <button
              onClick={() => onSubmit(text)}
              disabled={whyLoading || !selected || !text.trim()}
              className="px-4 py-2 rounded-xl bg-amber-500 text-white font-bold text-sm shadow
                hover:bg-amber-600 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed">
              提交
            </button>
          </div>
        </div>

        <button
          onClick={onBack}
          className="self-start text-xs text-stone-400 hover:text-stone-600 transition-colors underline underline-offset-2">
          ← 返回重新选图
        </button>
      </div>
    </div>
  )
}
