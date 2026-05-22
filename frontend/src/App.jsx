import { useState } from "react";
import ResearchForm from "./components/ResearchForm";
import ReportView from "./components/ReportView";

export default function App() {
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);

  async function handleSubmit(query, domain) {
    setStatus("loading");
    setResult(null);
    try {
      const res = await fetch("/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, domain }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
      setStatus("done");
    } catch (err) {
      setResult({ error: err.message });
      setStatus("error");
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-3xl mx-auto px-6 py-5 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
          <h1 className="text-lg font-semibold tracking-tight">
            Research Assistant
          </h1>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-3xl mx-auto px-6 py-10">
        <ResearchForm onSubmit={handleSubmit} loading={status === "loading"} />

        {status === "loading" && (
          <div className="mt-12 flex flex-col items-center gap-4 text-gray-400">
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
            <p className="text-sm">
              Researching - this usually takes 20 to 40 seconds
            </p>
          </div>
        )}

        {status === "done" && <ReportView result={result} />}

        {status === "error" && (
          <div className="mt-8 rounded-lg border border-red-800 bg-red-950/40 px-5 py-4 text-sm text-red-300">
            {result?.error}
          </div>
        )}
      </main>
    </div>
  );
}
