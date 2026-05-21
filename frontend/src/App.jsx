import { useState } from "react";
import ResearchForm from "./components/ResearchForm";
import ReportView from "./components/ReportView";

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
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
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>Research Assistant</h1>
      <ResearchForm onSubmit={handleSubmit} loading={status === "loading"} />
      {status === "loading" && (
        <p>Researching — this takes 20 to 40 seconds...</p>
      )}
      {status === "done" && <ReportView result={result} />}
      {status === "error" && <p style={{ color: "red" }}>{result?.error}</p>}
    </div>
  );
}
