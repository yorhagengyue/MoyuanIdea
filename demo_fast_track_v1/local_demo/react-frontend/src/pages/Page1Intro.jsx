/* Page 1 — 导入 + 选图 */
export default function Page1Intro({ options, imagesLoading, lessonTheme, onSelect }) {
  return (
    <div className="rise-in min-h-[calc(100vh-60px)] flex flex-col">

      {/* Hero band */}
      <div className="relative overflow-hidden px-6 py-8 text-center"
        style={{ background: 'linear-gradient(135deg, #d2f0c8 0%, #c8e6f5 100%)' }}>
        {/* Decorative mountain silhouettes */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-center opacity-20 pointer-events-none select-none">
          <span className="text-[7rem] leading-none">⛰️⛰️⛰️</span>
        </div>
        <p className="relative text-sm font-bold text-green-700 tracking-widest uppercase mb-1">今日课题</p>
        <h2 className="relative text-3xl font-black text-stone-800 mb-1">{lessonTheme}</h2>
        <p className="relative text-base text-stone-600">找一找，哪一张是真正的&ldquo;山峰&rdquo;？</p>
      </div>

      {/* Teacher + instruction row */}
      <div className="px-6 py-4 flex items-center gap-4 bg-amber-50/60 border-b border-amber-200/50">
        {/* Teacher character */}
        <div className="shrink-0 flex flex-col items-center gap-1">
          <div className="w-14 h-14 rounded-full bg-green-200 border-2 border-green-400 flex items-center justify-center text-3xl shadow-sm">
            👩‍🏫
          </div>
          <span className="text-xs font-semibold text-green-700">老师</span>
        </div>
        {/* Speech bubble */}
        <div className="relative bubble-right rounded-2xl bg-amber-50 border border-amber-200 px-4 py-3 shadow-sm max-w-lg">
          <p className="text-sm text-stone-700 leading-relaxed">
            小朋友们，我们今天来认识山的不同叫法！<br />
            请看看下面四张图，选一个你觉得是&ldquo;<strong>山峰</strong>&rdquo;的。
          </p>
        </div>
      </div>

      {/* Option cards grid */}
      <div className="flex-1 p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {options.map((opt, i) => (
            <OptionCard
              key={opt.key}
              option={opt}
              index={i}
              loading={imagesLoading}
              onClick={() => !imagesLoading && onSelect(opt)}
            />
          ))}
        </div>

        {imagesLoading && (
          <p className="text-center text-sm text-stone-500 mt-4 flex items-center justify-center gap-2">
            <span className="bounce-dot bg-sky-400" />
            <span className="bounce-dot bg-sky-400" />
            <span className="bounce-dot bg-sky-400" />
            <span className="ml-1">AI 正在生成图片，请稍候…</span>
          </p>
        )}
      </div>
    </div>
  )
}

function OptionCard({ option, index, loading, onClick }) {
  const labels = ['A', 'B', 'C', 'D']
  const colors = ['bg-red-100 text-red-700', 'bg-green-100 text-green-700',
                  'bg-sky-100 text-sky-700', 'bg-amber-100 text-amber-700']

  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="card-reveal group relative flex flex-col rounded-2xl border-2 border-stone-200
        bg-white shadow-md hover:shadow-xl hover:-translate-y-1 hover:border-amber-300
        active:scale-95 transition-all duration-200 overflow-hidden text-left disabled:cursor-wait"
      style={{ animationDelay: `${index * 90}ms` }}>

      {/* Image area */}
      {loading || !option.imageUrl ? (
        <div className="shimmer w-full aspect-[4/3]" />
      ) : (
        <img
          src={option.imageUrl}
          alt={`${option.key}示意图`}
          className="w-full aspect-[4/3] object-cover"
          loading="lazy"
        />
      )}

      {/* Label badge */}
      <div className="absolute top-2 left-2">
        <span className={`text-xs font-black px-2 py-0.5 rounded-full shadow ${colors[index]}`}>
          {labels[index]}
        </span>
      </div>

      {/* Text info */}
      <div className="p-3 flex-1 flex flex-col gap-0.5">
        <span className="text-xl font-black text-stone-800">{option.key}</span>
        <span className="text-xs text-stone-500 font-semibold">{option.subtitle}</span>
      </div>

      {/* Hover cue */}
      <div className="absolute inset-0 rounded-2xl ring-0 group-hover:ring-2 ring-amber-400
        transition-all duration-200 pointer-events-none" />
    </button>
  )
}
