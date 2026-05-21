import { useState } from "react";

export default function ResearchForm({ onSubmit, loading }) {
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Research topic..."
        style={{ width: "100%", marginBottom: 8, padding: 8 }}
      />
      <input
        value={domain}
        onChange={(e) => setDomain(e.target.value)}
        placeholder="Domain context (optional)"
        style={{ width: "100%", marginBottom: 8, padding: 8 }}
      />
      <button
        onClick={() => onSubmit(query, domain)}
        disabled={loading || !query.trim()}
      >
        {loading ? "Researching..." : "Research"}
      </button>
    </div>
  );
}
