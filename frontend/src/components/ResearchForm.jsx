import { useState } from "react";

export default function ResearchForm({ onSubmit, loading }) {
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");

  const inputClass = `
    w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3
    text-sm text-gray-100 placeholder-gray-500
    focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500
    transition-colors
  `;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-6">
      <h2 className="text-sm font-medium text-gray-400 mb-4 uppercase tracking-wider">
        New Research
      </h2>
      <div className="flex flex-col gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What do you want to research?"
          className={inputClass}
          onKeyDown={(e) =>
            e.key === "Enter" &&
            !loading &&
            query.trim() &&
            onSubmit(query, domain)
          }
        />
        <input
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="Domain or industry context (optional)"
          className={inputClass}
        />
        <button
          onClick={() => onSubmit(query, domain)}
          disabled={loading || !query.trim()}
          className="
            mt-1 w-full rounded-lg bg-emerald-600 px-4 py-3 text-sm font-medium
            text-white transition-colors hover:bg-emerald-500
            disabled:opacity-40 disabled:cursor-not-allowed
          "
        >
          {loading ? "Researching..." : "Research →"}
        </button>
      </div>
    </div>
  );
}
