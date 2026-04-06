/* Page 3 — AI 反馈 */

const FEEDBACK_CARDS = [
  { key: 'overall_judgement', label: '判断',   icon: '🏅', fallback: '部分正确' },
  { key: 'strengths',         label: '做得好', icon: '⭐', fallback: '你愿意表达，这很好！', isList: true },
  { key: 'issues',            label: '要改进', icon: '💡', fallback: '目前没有明显问题。', isIssueList: true },
  { key: 'corrected_sentence',label: '建议句', icon: '✏️',  fallback: '请再说一遍完整句。' },
  { key: 'next_hint',         label: '下一步', icon: '🚀', fallback: '用"因为……"说完整理由。' },
  { key: 'feedback_to_child', label: '鼓励',   icon: '🌟', fallback: '你已经做得很好，继续加油！' },
]

function getCardBg(index, isCorrect) {
  if (index === 0) {
    if (isCorrect === true) return 'bg-green-50 border-green-300'
    if (isCorrect === false) return 'bg-red-50 border-red-300'
    return 'bg-amber-50 border-amber-300'
  }
  return 'bg-white border-stone-200'
}

export default function Page3Feedback({ selected, feedback, loading, onRestart }) {
  const isCorrect = feedback?.is_correct

  return (
    <div className="rise-in min-h-[calc(100vh-60px)] flex flex-col md:flex-row">

      {/* Left: selected image + result badge */}
      <div className="md:w-2/5 p-6 flex flex-col items-center justify-center gap-4 bg-stone-50/60 border-b md:border-b-0 md:border-r border-stone-200">

        {/* AI robot character */}
        <div className="flex flex-col items-center gap-1">
          <div className="w-16 h-16 rounded-full bg-teal-200 border-2 border-teal-400 flex items-center justify-center text-3xl shadow">
            🤖
          </div>
          <span className="text-xs font-semibold text-teal-700">AI 老师</span>
        </div>

        {/* Selected image */}
        {selected ? (
          <div className="relative w-full max-w-xs rounded-2xl overflow-hidden shadow-lg border border-stone-200">
            {selected.imageUrl
              ? <img src={selected.imageUrl} alt={selected.key} className="w-full aspect-[4/3] object-cover" />
              : <div className="shimmer w-full aspect-[4/3]" />}

            {/* Result overlay badge */}
            {!loading && feedback && (
              <div className="absolute inset-0 flex items-center justify-center">
                {isCorrect === true && (
                  <span className="badge-pop text-7xl drop-shadow-lg">✅</span>
                )}
                {isCorrect === false && (
                  <span className="badge-pop text-7xl drop-shadow-lg">❌</span>
                )}
                {isCorrect === undefined && (
                  <span className="badge-pop text-6xl drop-shadow-lg">💬</span>
                )}
              </div>
            )}

            <div className="absolute bottom-0 inset-x-0 bg-black/40 py-2 text-center">
              <span className="text-white font-black text-lg">你选了：{selected.key}</span>
            </div>
          </div>
        ) : (
          <div className="w-full max-w-xs aspect-[4/3] rounded-2xl shimmer" />
        )}

        {/* Student answer display */}
        {feedback?.studentAnswer && (
          <div className="w-full max-w-xs rounded-xl bg-sky-50 border border-sky-200 px-4 py-3">
            <p className="text-xs font-bold text-sky-600 mb-1">你说的：</p>
            <p className="text-sm text-stone-700">{feedback.studentAnswer}</p>
          </div>
        )}

        <button
          onClick={onRestart}
          className="mt-2 px-6 py-2.5 rounded-full bg-amber-500 text-white font-bold shadow
            hover:bg-amber-600 active:scale-95 transition-all text-sm">
          🔄 再试一次
        </button>
      </div>

      {/* Right: feedback cards */}
      <div className="md:w-3/5 p-6 flex flex-col gap-3 overflow-y-auto">
        <h2 className="text-lg font-black text-stone-700 mb-1">AI 即时反馈</h2>

        {/* Loading overlay */}
        {loading && (
          <div className="flex-1 flex flex-col items-center justify-center gap-4 py-16">
            <div className="w-20 h-20 rounded-full bg-teal-200 border-2 border-teal-400 flex items-center justify-center text-4xl shadow pulse-mic">
              🤖
            </div>
            <div className="flex gap-2">
              <span className="bounce-dot bg-teal-400" />
              <span className="bounce-dot bg-teal-400" />
              <span className="bounce-dot bg-teal-400" />
            </div>
            <p className="text-sm text-stone-500 font-semibold">AI 正在分析你的回答…</p>
          </div>
        )}

        {/* Error state */}
        {!loading && feedback?.error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
            <p className="text-sm text-red-600">分析失败，请重试。</p>
          </div>
        )}

        {/* Feedback cards */}
        {!loading && feedback && !feedback.error && FEEDBACK_CARDS.map((card, i) => {
          let value = feedback[card.key]
          if (card.isList && Array.isArray(value)) value = value.filter(Boolean).join('；') || card.fallback
          else if (card.isIssueList && Array.isArray(value)) value = value.map(v => v.message).filter(Boolean).join('；') || card.fallback
          else if (!value) value = card.fallback

          return (
            <div
              key={card.key}
              className={`fade-up rounded-2xl border px-4 py-3 shadow-sm ${getCardBg(i, isCorrect)}`}
              style={{ animationDelay: `${i * 80}ms` }}>
              <p className="text-xs font-bold text-stone-500 uppercase tracking-wide mb-0.5">
                {card.icon} {card.label}
              </p>
              <p className="text-sm text-stone-800 leading-relaxed">{value}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
