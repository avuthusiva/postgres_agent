import { FormEvent, useState } from "react";

type QueryResult = {
  sql: string;
  columns: string[];
  rows: (string | null)[][];
  execution_time_ms: number;
  truncated: boolean;
};

export default function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail ?? "The request failed.");
      }
      setResult(body as QueryResult);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to contact the API.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <div className="brand-mark" aria-hidden="true">PG</div>
        <div>
          <p className="eyebrow">DATABASE ASSISTANT</p>
          <h1>Ask your data</h1>
        </div>
      </header>

      <section className="panel">
        <form onSubmit={submitQuestion}>
          <label htmlFor="question">What would you like to know?</label>
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="For example: Show the 10 most recent orders"
            maxLength={2000}
            rows={4}
            required
          />
          <div className="form-footer">
            <span>Queries run with read-only database access.</span>
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? "Working…" : "Run query"}
            </button>
          </div>
        </form>
      </section>

      {error && <div className="error" role="alert">{error}</div>}

      {result && (
        <section className="results" aria-live="polite">
          <div className="result-heading">
            <div>
              <p className="eyebrow">GENERATED SQL</p>
              <h2>Query</h2>
            </div>
            <span className="timing">{result.execution_time_ms} ms</span>
          </div>
          <pre className="sql"><code>{result.sql}</code></pre>

          <div className="result-heading table-heading">
            <div>
              <p className="eyebrow">DATABASE RESPONSE</p>
              <h2>Results <span className="count">({result.rows.length})</span></h2>
            </div>
          </div>
          {result.truncated && (
            <p className="notice">Showing the first 500 rows. Refine your question for a smaller result.</p>
          )}
          {result.columns.length === 0 ? (
            <p className="empty">The query returned no columns.</p>
          ) : result.rows.length === 0 ? (
            <p className="empty">No rows matched your query.</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>{result.columns.map((column) => <th key={column}>{column}</th>)}</tr>
                </thead>
                <tbody>
                  {result.rows.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((value, cellIndex) => (
                        <td key={cellIndex}>{value ?? <span className="null">NULL</span>}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
      <footer>SQL generation can make mistakes. Review the query before relying on its results.</footer>
    </main>
  );
}
