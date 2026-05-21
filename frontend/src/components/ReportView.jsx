import ReactMarkdown from "react-markdown";

export default function ReportView({ result }) {
  return (
    <div>
      <ReactMarkdown>{result.report}</ReactMarkdown>

      {result.sources?.length > 0 && (
        <div
          style={{
            marginTop: "2rem",
            borderTop: "1px solid #eee",
            paddingTop: "1rem",
          }}
        >
          <h3>Sources</h3>
          <ul>
            {result.sources.map((s, i) => (
              <li key={i}>
                <a href={s.url} target="_blank" rel="noreferrer">
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
