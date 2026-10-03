import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { apiClient } from "../services/api/client";
import type { AppInfo, ChatResponse, DocumentSummary } from "../types/app";

type HomePageProps = {
  apiUrl: string;
  appInfo: AppInfo;
};

export function HomePage({ apiUrl, appInfo }: HomePageProps) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [answer, setAnswer] = useState<ChatResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refreshDocuments();
  }, []);

  async function refreshDocuments() {
    try {
      const items = await apiClient.listDocuments();
      setDocuments(items);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      await apiClient.uploadDocument(file);
      await refreshDocuments();
      event.target.value = "";
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;

    setAsking(true);
    setError(null);
    try {
      const response = await apiClient.askQuestion(question.trim(), topK);
      setAnswer(response);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAsking(false);
    }
  }

  const hasDocuments = useMemo(() => documents.length > 0, [documents.length]);

  return (
    <main>
      <section className="card">
        <h1>{appInfo.name}</h1>
        <p>{appInfo.description}</p>
        <p className="meta">Configured API base URL: {apiUrl}</p>

        <section className="panel">
          <h2>1) Upload a document (PDF / TXT / Markdown)</h2>
          <input
            type="file"
            accept=".pdf,.txt,.md,text/plain,text/markdown,application/pdf"
            onChange={handleUpload}
          />
          {uploading && <p>Uploading and processing document…</p>}
        </section>

        <section className="panel">
          <h2>2) Ingested documents</h2>
          {hasDocuments ? (
            <ul>
              {documents.map((doc) => (
                <li key={doc.id}>
                  <strong>{doc.filename}</strong> — {doc.status} — chunks: {doc.chunk_count}
                </li>
              ))}
            </ul>
          ) : (
            <p>No documents yet.</p>
          )}
        </section>

        <section className="panel">
          <h2>3) Ask grounded questions</h2>
          <form onSubmit={handleAsk}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question based on uploaded documents"
              rows={4}
              required
            />
            <div className="row">
              <label>
                Top K
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value) || 5)}
                />
              </label>
              <button type="submit" disabled={asking || !hasDocuments}>
                {asking ? "Thinking…" : "Ask"}
              </button>
            </div>
          </form>
        </section>

        {answer && (
          <section className="panel">
            <h2>Answer</h2>
            <p>{answer.answer}</p>
            <h3>Sources</h3>
            <ul>
              {answer.sources.map((source) => (
                <li key={source.chunk_id}>
                  {source.filename} — chunk {source.chunk_index} — similarity {source.similarity.toFixed(4)}
                </li>
              ))}
            </ul>
          </section>
        )}

        {error && <p className="error">{error}</p>}
      </section>
    </main>
  );
}
