import { useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { apiClient, setAccessToken } from "../services/api/client";
import type { AgentChatResponse, AppInfo, ConversationSummary, DocumentSummary, SessionResponse } from "../types/app";

type Props = { apiUrl: string; appInfo: AppInfo };

export function HomePage({ apiUrl, appInfo }: Props) {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [registerMode, setRegisterMode] = useState(false);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AgentChatResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const generation = useRef(0);

  useEffect(() => { if (session) void refreshData(); }, [session]);

  async function refreshData() {
    try {
      const [docs, chats] = await Promise.all([apiClient.listDocuments(), apiClient.listConversations()]);
      setDocuments(docs); setConversations(chats);
    } catch (err) { setError((err as Error).message); }
  }
  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(null);
    try {
      if (registerMode) await apiClient.register(email, password);
      const loggedIn = await apiClient.login(email, password);
      setAccessToken(loggedIn.access_token); setSession(loggedIn); setPassword("");
    } catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }
  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]; if (!file) return;
    setBusy(true); setError(null);
    try { await apiClient.uploadDocument(file); await refreshData(); event.target.value = ""; }
    catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }
  async function createConversation() {
    setBusy(true); setError(null);
    try { const c = await apiClient.createConversation("New conversation"); setActiveConversation(c.id); setConversations((prev) => [c, ...prev]); setAnswer(null); }
    catch (err) { setError((err as Error).message); }
    finally { setBusy(false); }
  }
  async function openConversation(id: string) {
    setActiveConversation(id); setAnswer(null); setError(null);
    try { const c = await apiClient.getConversation(id); setConversations((prev) => [c, ...prev.filter((item) => item.id !== id)]); }
    catch (err) { setError((err as Error).message); }
  }
  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!question.trim() || busy) return;
    const prompt = question.trim();
    const current = ++generation.current;
    setQuestion(""); setBusy(true); setError(null); setActiveTool(null);
    setAnswer({ answer: "", answer_kind: "INSUFFICIENT_EVIDENCE", sources: [], tools_used: [], events: [], conversation_id: activeConversation });
    const controller = new AbortController(); abortRef.current = controller;
    let tokenText = "";
    let completed = false;
    try {
      await apiClient.streamAgentChat(prompt, activeConversation ?? undefined, (event, data) => {
        if (generation.current !== current || controller.signal.aborted) return;
        if (event === "token") {
          tokenText += data.text ?? "";
          setAnswer((old) => old ? { ...old, answer: tokenText } : old);
        } else if (event === "tool_start") {
          setActiveTool(data.tool ?? "tool");
          setAnswer((old) => old ? { ...old, events: [...old.events, { event: "tool_start", tool: data.tool }] } : old);
        } else if (event === "tool_result") {
          setActiveTool(null);
          setAnswer((old) => old ? { ...old, events: [...old.events, { event: "tool_result", tool: data.tool, detail: data.status }] } : old);
        } else if (event === "retrieval") {
          setAnswer((old) => old ? { ...old, events: [...old.events, { event: "retrieval", detail: `${data.count ?? 0} results` }] } : old);
        } else if (event === "message_end") {
          completed = true;
          setAnswer((old) => old ? { ...old, answer: tokenText, answer_kind: data.answer_kind ?? "INSUFFICIENT_EVIDENCE", sources: data.sources ?? [], tools_used: data.tools_used ?? [], conversation_id: data.conversation_id ?? activeConversation } : old);
        } else if (event === "error") {
          setError(data.message ?? "The response could not be completed.");
        }
      }, controller.signal);
      if (generation.current !== current || controller.signal.aborted) return;
      if (!completed) { setError("Stream ended before completion"); return; }
      if (activeConversation) {
        const updated = await apiClient.getConversation(activeConversation);
        if (generation.current !== current) return;
        setConversations((prev) => [updated, ...prev.filter((item) => item.id !== updated.id)]);
      }
      await refreshData();
    } catch (err) {
      if (generation.current === current && !controller.signal.aborted) setError((err as Error).message);
    } finally {
      if (generation.current === current) { abortRef.current = null; setActiveTool(null); setBusy(false); }
    }
  }
  function cancelStream() {
    generation.current += 1;
    abortRef.current?.abort(); abortRef.current = null;
    setBusy(false); setActiveTool(null);
  }
  async function logout() {
    cancelStream();
    try { await apiClient.logout(); }
    catch (err) { setError((err as Error).message); }
    finally { setAccessToken(null); setSession(null); setDocuments([]); setConversations([]); setActiveConversation(null); setAnswer(null); }
  }
  const hasDocuments = useMemo(() => documents.length > 0, [documents.length]);
  if (!session) return (
    <main><section className="card"><h1>{appInfo.name}</h1><p>{appInfo.description}</p>
      <form onSubmit={handleAuth} className="panel"><h2>{registerMode ? "Create account" : "Sign in"}</h2>
        <label>Email<input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" required minLength={12} autoComplete={registerMode ? "new-password" : "current-password"} value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button disabled={busy}>{busy ? "Please wait…" : registerMode ? "Register" : "Login"}</button>
        <button type="button" onClick={() => setRegisterMode(!registerMode)}>{registerMode ? "Have an account? Sign in" : "Create an account"}</button>
      </form>{error && <p className="error">{error}</p>}
    </section></main>
  );
  return (
    <main><section className="card">
      <header className="row"><div><h1>{appInfo.name}</h1><p className="meta">{session.user.email} · API {apiUrl}</p></div><button onClick={() => void logout()}>Sign out</button></header>
      <section className="panel"><h2>Documents</h2><input type="file" accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" onChange={handleUpload} disabled={busy} />
        {documents.length ? <ul>{documents.map((doc) => <li key={doc.id}>{doc.filename} — {doc.status} — {doc.chunk_count} chunks</li>)}</ul> : <p>No documents yet.</p>}
      </section>
      <section className="panel"><div className="row"><h2>Conversations</h2><button onClick={() => void createConversation()} disabled={busy}>New conversation</button></div>
        {conversations.length ? <ul>{conversations.map((c) => <li key={c.id}><button onClick={() => void openConversation(c.id)}>{c.title}</button></li>)}</ul> : <p>No saved conversations. Use New conversation to persist a chat.</p>}
        {activeConversation && <p className="meta">Open conversation: {activeConversation}</p>}
      </section>
      {activeConversation && <section className="panel"><h2>Recent conversation</h2>{conversations.find((c) => c.id === activeConversation)?.messages.map((message) => <p key={message.id}><strong>{message.role}:</strong> {message.content}</p>)}</section>}
      <section className="panel"><h2>Ask AgentForge</h2><form onSubmit={sendMessage}><textarea rows={3} maxLength={5000} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about your documents or a calculation" required disabled={busy} /><button disabled={busy || (!hasDocuments && !question.trim())}>{busy ? "Streaming…" : "Send"}</button>{busy && <button type="button" onClick={cancelStream}>Cancel</button>}</form>{activeTool && <p role="status" className="meta">Working with {activeTool}…</p>}</section>
      {answer && <section className="panel"><h2>Answer · {answer.answer_kind}</h2><p aria-live="polite">{answer.answer || (busy ? "Thinking…" : "")}</p><h3>Tools used</h3><p>{answer.tools_used.length ? answer.tools_used.join(", ") : activeTool ?? "None"}</p><h3>Sources</h3>{answer.sources.length ? <ul>{answer.sources.map((source) => <li key={source.chunk_id}>{source.filename} — chunk {source.chunk_index} — similarity {source.similarity.toFixed(4)}</li>)}</ul> : <p>No document sources.</p>}<details><summary>Activity</summary><ol>{answer.events.map((item, index) => <li key={`${item.event}-${index}`}>{item.event}{item.tool ? ` · ${item.tool}` : ""}{item.detail ? ` · ${item.detail}` : ""}</li>)}</ol></details></section>}
      {error && <p className="error">{error}</p>}
    </section></main>
  );
}
