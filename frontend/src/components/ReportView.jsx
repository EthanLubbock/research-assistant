import ReactMarkdown from "react-markdown";

export default function ReportView({ result }) {
  return (
    <div className="mt-8 flex flex-col gap-6">
      {/* Report */}
      <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-6">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
          <span className="text-xs font-medium uppercase tracking-wider text-gray-400">
            Report
          </span>
        </div>
        <div
          className="prose prose-invert prose-sm max-w-none
          prose-headings:text-gray-100 prose-headings:font-semibold
          prose-p:text-gray-300 prose-p:leading-relaxed
          prose-li:text-gray-300
          prose-strong:text-gray-100
          prose-h2:text-base prose-h3:text-sm
          prose-h2:mt-6 prose-h2:mb-2"
        >
          <ReactMarkdown>{result.report}</ReactMarkdown>
        </div>
      </div>

      {/* Sources */}
      {result.sources?.length > 0 && (
        <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-1.5 h-1.5 rounded-full bg-gray-500"></div>
            <span className="text-xs font-medium uppercase tracking-wider text-gray-400">
              Sources
            </span>
          </div>
          <ul className="flex flex-col gap-2">
            {result.sources.map((s, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-xs text-gray-600 mt-0.5 w-4 shrink-0">
                  {i + 1}
                </span>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-emerald-400 hover:text-emerald-300 hover:underline transition-colors break-all"
                >
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
