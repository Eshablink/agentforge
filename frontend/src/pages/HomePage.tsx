import { useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, FormEvent, KeyboardEvent } from "react";

import { Icon } from "../components/Icon";
import { apiClient, setAccessToken } from "../services/api/client";
import type {
  AgentChatResponse,
  AppInfo,
  DocumentSummary,
  SessionResponse,
  SourceReference,
  StreamEventData,
  StreamEventName,
} from "../types/app";

type Props = { apiUrl: string; appInfo: AppInfo };

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "recently";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(date);
}

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(date);
}

function documentStatus(status: string): "ready" | "processing" | "error" {
  const normalized = status.toLowerCase();
  if (["ready", "completed", "success", "processed"].includes(normalized)) return "ready";
  if (["failed", "error", "rejected"].includes(normalized)) return "error";
  return "processing";
}

function answerLabel(kind: AgentChatResponse["answer_kind"]): string {
  switch (kind) {
    case "RAG_GROUNDED":
      return "Grounded answer";
    case "TOOL_DERIVED":
      return "Tool-assisted";
    case "DIRECT":
      return "Direct answer";
    default:
      return "Needs more evidence";
  }
}

function shortId(value: string): string {
  return value.slice(0, 8);
}

export function HomePage({ apiUrl, appInfo }: Props) {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [registerMode, setRegisterMode] = useState(false);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);
  const [answer, setAnswer] = useState<AgentChatResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documentsOpen, setDocumentsOpen] = useState(true);
  const [activityOpen, setActivityOpen] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    try {
      return (localStorage.getItem("agentforge-theme") as "dark" | "light") || "dark";
    } catch {
      return "dark";
    }
  });

  const abortRef = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("agentforge-theme", theme);
    } catch {
      // Ignore storage failures; the theme still applies to this session.
    }
  }, [theme]);

  useEffect(() => {
    if (session) void refreshData();
  }, [session]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: busy ? "auto" : "smooth" });
  }, [answer?.answer, busy]);

  async function refreshData() {
    try {
      const [docs, chats] = await Promise.all([apiClient.listDocuments(), apiClient.listConversations()]);
      setDocuments(docs);
      setConversations(chats);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (registerMode) await apiClient.register(email.trim(), password);
      const loggedIn = await apiClient.login(email.trim(), password);
      setAccessToken(loggedIn.access_token);
      setSession(loggedIn);
      setPassword("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setError("Files must be 10 MB or smaller.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setError(null);
    try {
      await apiClient.uploadDocument(file);
      await refreshData();
      event.target.value = "";
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  }

  async function createConversation() {
    setError(null);
    try {
      const conversation = await apiClient.createConversation("New conversation");
      setActiveConversation(conversation.id);
      setConversations((prev) => [conversation, ...prev.filter((item) => item.id !== conversation.id)]);
      setAnswer(null);
      setPendingQuestion(null);
      setActivityOpen(false);
      setSidebarOpen(false);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function openConversation(id: string) {
    setActiveConversation(id);
    setAnswer(null);
    setPendingQuestion(null);
    setError(null);
    setActivityOpen(false);
    setSidebarOpen(false);
    try {
      const conversation = await apiClient.getConversation(id);
      setConversations((prev) => [conversation, ...prev.filter((item) => item.id !== id)]);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function deleteConversation(id: string) {
    if (!window.confirm("Delete this conversation? This cannot be undone.")) return;
    try {
      await apiClient.deleteConversation(id);
      setConversations((prev) => prev.filter((item) => item.id !== id));
      if (activeConversation === id) {
        setActiveConversation(null);
        setAnswer(null);
        setPendingQuestion(null);
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim() || busy) return;

    const prompt = question.trim();
    const current = ++generation.current;
    const conversationAtStart = activeConversation;

    setQuestion("");
    setPendingQuestion(prompt);
    setBusy(true);
    setError(null);
    setActiveTool(null);
    setActivityOpen(false);
    setAnswer({
      answer: "",
      answer_kind: "INSUFFICIENT_EVIDENCE",
      sources: [],
      tools_used: [],
      events: [],
      conversation_id: conversationAtStart,
    });

    const controller = new AbortController();
    abortRef.current = controller;

    let tokenText = "";
    let completed = false;
    let returnedConversationId: string | null = conversationAtStart;

    const onEvent = (eventName: StreamEventName, data: StreamEventData) => {
      if (generation.current !== current || controller.signal.aborted) return;

      if (eventName === "token") {
        tokenText += data.text ?? "";
        setAnswer((old) => (old ? { ...old, answer: tokenText } : old));
      } else if (eventName === "tool_start") {
        setActiveTool(data.tool ?? "tool");
        setAnswer((old) => (old ? {
          ...old,
          events: [...old.events, { event: "tool_start", tool: data.tool }],
        } : old));
      } else if (eventName === "tool_result") {
        setActiveTool(null);
        setAnswer((old) => (old ? {
          ...old,
          events: [...old.events, {
            event: "tool_result",
            tool: data.tool,
            detail: data.status === "success" ? "completed" : "failed",
          }],
        } : old));
      } else if (eventName === "retrieval") {
        setAnswer((old) => (old ? {
          ...old,
          events: [...old.events, { event: "retrieval", detail: String(data.count ?? 0) + " evidence results" }],
        } : old));
      } else if (eventName === "message_end") {
        completed = true;
        returnedConversationId = data.conversation_id ?? conversationAtStart;
        if (returnedConversationId && returnedConversationId !== activeConversation) {
          setActiveConversation(returnedConversationId);
        }
        setAnswer((old) => (old ? {
          ...old,
          answer: tokenText,
          answer_kind: data.answer_kind ?? "INSUFFICIENT_EVIDENCE",
          sources: data.sources ?? [],
          tools_used: data.tools_used ?? [],
          conversation_id: returnedConversationId,
        } : old));
      } else if (eventName === "error") {
        setError(data.message ?? "The response could not be completed.");
      }
    };

    try {
      await apiClient.streamAgentChat(prompt, conversationAtStart ?? undefined, onEvent, controller.signal);
      if (generation.current !== current || controller.signal.aborted) return;

      if (!completed) {
        setError("The stream ended before the answer completed.");
        return;
      }

      if (returnedConversationId) {
        const updated = await apiClient.getConversation(returnedConversationId);
        if (generation.current !== current) return;
        setConversations((prev) => [updated, ...prev.filter((item) => item.id !== updated.id)]);
        setActiveConversation(returnedConversationId);
      }

      setPendingQuestion(null);
      await refreshData();
    } catch (err) {
      if (generation.current === current && !controller.signal.aborted) {
        setError((err as Error).message);
      }
    } finally {
      if (generation.current === current) {
        abortRef.current = null;
        setActiveTool(null);
        setBusy(false);
      }
    }
  }

  function cancelStream() {
    generation.current += 1;
    abortRef.current?.abort();
    abortRef.current = null;
    setBusy(false);
    setActiveTool(null);
    setPendingQuestion(null);
  }

  async function logout() {
    cancelStream();
    try {
      await apiClient.logout();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAccessToken(null);
      setSession(null);
      setDocuments([]);
      setConversations([]);
      setActiveConversation(null);
      setAnswer(null);
    }
  }

  const activeThread = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversation) ?? null,
    [activeConversation, conversations],
  );

  const documentCountLabel = documents.length === 1 ? "document" : "documents";
  const conversationCountLabel = conversations.length === 1 ? "conversation" : "conversations";

  if (!session) {
    return (
      <main className="auth-shell">
        <section className="auth-visual" aria-label="AgentForge product overview">
          <div className="ambient ambient-one" />
          <div className="ambient ambient-two" />
          <div className="brand-lockup">
            <div className="brand-mark"><Icon name="spark" /></div>
            <span>AgentForge</span>
          </div>
          <div className="auth-copy">
            <span className="eyebrow">AGENTIC AI WORKSPACE</span>
            <h1>Turn documents into <em>decisions.</em></h1>
            <p>
              A secure full-stack AI workspace for grounded answers, validated tools and streaming agent workflows.
            </p>
          </div>
          <div className="capability-grid">
            <div className="capability-card">
              <span className="capability-icon"><Icon name="file" /></span>
              <strong>Grounded RAG</strong>
              <span>Answers backed by your indexed evidence.</span>
            </div>
            <div className="capability-card">
              <span className="capability-icon"><Icon name="wand" /></span>
              <strong>Safe tools</strong>
              <span>Typed, allowlisted actions with bounded execution.</span>
            </div>
            <div className="capability-card capability-wide">
              <span className="capability-icon"><Icon name="bot" /></span>
              <div>
                <strong>Live agent streaming</strong>
                <span>See retrieval, tools and final-answer deltas as they happen.</span>
              </div>
              <span className="live-dot" aria-label="streaming capability available" />
            </div>
          </div>
          <div className="architecture-strip" aria-hidden="true">
            <span>React</span><i>→</i><span>FastAPI</span><i>→</i><span>Agent</span><i>→</i><span>RAG + Tools</span>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-panel-inner">
            <div className="auth-topline">
              <span><span className="status-dot" /> Secure workspace</span>
              <button
                className="icon-button"
                type="button"
                aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                <Icon name={theme === "dark" ? "sun" : "moon"} />
              </button>
            </div>
            <div className="auth-heading">
              <span className="mobile-brand"><Icon name="spark" /> AgentForge</span>
              <h2>{registerMode ? "Create your workspace" : "Welcome back"}</h2>
              <p>{registerMode ? "Start building with your documents and agent tools." : "Sign in to continue to your AI workspace."}</p>
            </div>
            <form onSubmit={handleAuth} className="auth-form">
              <label>
                <span>Email address</span>
                <div className="input-wrap">
                  <Icon name="user" />
                  <input
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                  />
                </div>
              </label>
              <label>
                <span>Password</span>
                <div className="input-wrap">
                  <Icon name="settings" />
                  <input
                    type="password"
                    required
                    minLength={12}
                    autoComplete={registerMode ? "new-password" : "current-password"}
                    placeholder="12+ characters"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                </div>
              </label>
              {error && <div className="inline-error" role="alert"><Icon name="close" />{error}</div>}
              <button className="primary-action auth-submit" disabled={busy}>
                {busy ? "Authenticating…" : registerMode ? "Create account" : "Sign in"}
                {!busy && <Icon name="arrow" />}
              </button>
            </form>
            <div className="auth-switch">
              <span>{registerMode ? "Already have an account?" : "New to AgentForge?"}</span>
              <button type="button" onClick={() => { setRegisterMode((value) => !value); setError(null); }}>
                {registerMode ? "Sign in" : "Create an account"}
              </button>
            </div>
            <p className="auth-footnote">Your session uses an opaque bearer token and is scoped to your account.</p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <div className="app-grid" data-sidebar-open={sidebarOpen}>
        <aside className="sidebar">
          <div className="sidebar-head">
            <div className="brand-lockup compact">
              <div className="brand-mark"><Icon name="spark" /></div>
              <span>AgentForge</span>
            </div>
            <button
              type="button"
              className="mobile-close"
              aria-label="Close navigation"
              onClick={() => setSidebarOpen(false)}
            >
              <Icon name="close" />
            </button>
          </div>

          <button className="new-chat-button" type="button" onClick={() => void createConversation()}>
            <Icon name="plus" />
            <span>New conversation</span>
            <kbd>⌘ K</kbd>
          </button>

          <div className="sidebar-section">
            <div className="section-label">
              <span>Conversations</span>
              <span className="section-count">{conversations.length}</span>
            </div>
            <div className="conversation-list">
              {conversations.length ? conversations.map((conversation) => (
                <div key={conversation.id} className={"conversation-row " + (conversation.id === activeConversation ? "active" : "")}>
                  <button type="button" className="conversation-button" onClick={() => void openConversation(conversation.id)}>
                    <span className="conversation-icon"><Icon name="bot" /></span>
                    <span className="conversation-copy">
                      <strong>{conversation.title || "Untitled conversation"}</strong>
                      <small>{conversation.updated_at ? formatDate(conversation.updated_at) : "new"}</small>
                    </span>
                  </button>
                  <button
                    type="button"
                    className="conversation-delete"
                    aria-label={"Delete " + (conversation.title || "conversation")}
                    onClick={(event) => { event.stopPropagation(); void deleteConversation(conversation.id); }}
                  >
                    <Icon name="trash" />
                  </button>
                </div>
              )) : (
                <div className="sidebar-empty">
                  <span><Icon name="spark" /></span>
                  <p>Your first conversation is one click away.</p>
                </div>
              )}
            </div>
          </div>

          <div className="sidebar-spacer" />

          <div className="sidebar-section documents-card">
            <button className="section-toggle" type="button" onClick={() => setDocumentsOpen((value) => !value)}>
              <span><Icon name="file" /> Knowledge base <span className="section-count">{documents.length}</span></span>
              <Icon name="chevron" />
            </button>
            {documentsOpen && (
              <>
                <label className="upload-dropzone">
                  <input
                    type="file"
                    accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
                    onChange={handleUpload}
                    disabled={uploading}
                  />
                  <span className="upload-icon"><Icon name="upload" /></span>
                  <strong>{uploading ? "Indexing…" : "Add a document"}</strong>
                  <small>PDF, TXT or Markdown · up to 10 MB</small>
                </label>
                {documents.length > 0 && (
                  <div className="document-mini-list">
                    {documents.slice(0, 5).map((document) => {
                      const state = documentStatus(document.status);
                      return (
                        <div className="document-mini" key={document.id}>
                          <Icon name="file" />
                          <span>
                            <strong title={document.filename}>{document.filename}</strong>
                            <small>{document.chunk_count} chunks</small>
                          </span>
                          <span className={"status-pill " + state}>
                            {state === "ready" ? <Icon name="check" /> : <span className="status-dot" />}
                          </span>
                        </div>
                      );
                    })}
                    {documents.length > 5 && <small className="document-more">+ {documents.length - 5} more {documentCountLabel}</small>}
                  </div>
                )}
              </>
            )}
          </div>

          <div className="account-card">
            <span className="avatar"><Icon name="user" /></span>
            <span className="account-copy"><strong>{session.user.email}</strong><small>Personal workspace</small></span>
            <button type="button" className="icon-button" aria-label="Sign out" onClick={() => void logout()}>
              <Icon name="logout" />
            </button>
          </div>
        </aside>

        <section className="workspace">
          <header className="topbar">
            <div className="topbar-left">
              <button className="mobile-menu-button" type="button" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}>
                <Icon name="grid" />
              </button>
              <div>
                <span className="topbar-kicker">AI WORKSPACE</span>
                <h1>{activeThread?.title || (activeConversation ? "Conversation" : "New conversation")}</h1>
              </div>
            </div>
            <div className="topbar-actions">
              <div className="connection-pill"><span className="status-dot" /> Connected</div>
              <button
                type="button"
                className="icon-button"
                aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                <Icon name={theme === "dark" ? "sun" : "moon"} />
              </button>
            </div>
          </header>

          <div className="workspace-scroll">
            <div className="chat-wrap">
              {!activeThread?.messages.length && !answer && !pendingQuestion ? (
                <section className="welcome-state">
                  <div className="welcome-orb"><Icon name="spark" /></div>
                  <span className="eyebrow">YOUR AI WORKSPACE</span>
                  <h2>What are we building today?</h2>
                  <p>Ask questions about your documents, run a calculation, or explore an agent workflow.</p>
                  <div className="prompt-suggestions">
                    {[
                      ["Summarize my latest document", "file"],
                      ["What can you help me calculate?", "wand"],
                      ["Find the key risks in my docs", "search"],
                    ].map(([label, icon]) => (
                      <button key={label} type="button" className="suggestion-card" onClick={() => setQuestion(label)}>
                        <Icon name={icon as "file" | "wand" | "search"} />
                        <span>{label}</span>
                        <Icon name="arrow" />
                      </button>
                    ))}
                  </div>
                  <div className="capability-line">
                    <span><Icon name="check" /> Document grounded</span>
                    <span><Icon name="check" /> Registered tools</span>
                    <span><Icon name="check" /> Live streaming</span>
                  </div>
                </section>
              ) : (
                <div className="thread">
                  {activeThread?.messages.map((message) => {
                    const isUser = message.role.toLowerCase() === "user";
                    return (
                      <article className={"message " + (isUser ? "message-user" : "message-assistant")} key={message.id}>
                        <div className="message-avatar">{isUser ? <Icon name="user" /> : <Icon name="spark" />}</div>
                        <div className="message-body">
                          <div className="message-meta">
                            <strong>{isUser ? "You" : "AgentForge"}</strong>
                            <span>{formatTime(message.created_at)}</span>
                          </div>
                          <div className="message-text">{message.content}</div>
                        </div>
                      </article>
                    );
                  })}

                  {pendingQuestion && (
                    <article className="message message-user pending-message">
                      <div className="message-avatar"><Icon name="user" /></div>
                      <div className="message-body">
                        <div className="message-meta"><strong>You</strong><span>now</span></div>
                        <div className="message-text">{pendingQuestion}</div>
                      </div>
                    </article>
                  )}

                  {answer && (
                    <article className="message message-assistant live-answer">
                      <div className="message-avatar"><Icon name="spark" /></div>
                      <div className="message-body">
                        <div className="message-meta">
                          <strong>AgentForge</strong>
                          <span>{busy ? "streaming" : answerLabel(answer.answer_kind)}</span>
                        </div>
                        <div className="answer-shell">
                          {busy && !answer.answer ? (
                            <div className="thinking-line" aria-live="polite"><span /><span /><span /><em>AgentForge is working…</em></div>
                          ) : (
                            <div className="message-text" aria-live="polite">
                              {answer.answer}
                              {busy && <span className="cursor" aria-hidden="true" />}
                            </div>
                          )}

                          {activeTool && (
                            <div className="working-pill" role="status">
                              <span className="working-spinner" />
                              <span>Running <strong>{activeTool}</strong></span>
                            </div>
                          )}

                          {!busy && answer.sources.length > 0 && (
                            <div className="source-section">
                              <div className="source-heading">
                                <span>Evidence</span>
                                <small>{answer.sources.length} source{answer.sources.length === 1 ? "" : "s"}</small>
                              </div>
                              <div className="source-grid">
                                {answer.sources.map((source) => <SourceCard key={source.chunk_id} source={source} />)}
                              </div>
                            </div>
                          )}

                          {!busy && (answer.tools_used.length > 0 || answer.events.length > 0) && (
                            <div className="activity-panel">
                              <button type="button" className="activity-trigger" onClick={() => setActivityOpen((value) => !value)}>
                                <span><Icon name="wand" /> Activity</span>
                                <span>{answer.tools_used.length ? String(answer.tools_used.length) + " tool" + (answer.tools_used.length === 1 ? "" : "s") : "trace"}</span>
                                <Icon name="chevron" />
                              </button>
                              {activityOpen && (
                                <ol className="activity-list">
                                  {answer.events.map((item, index) => (
                                    <li key={item.event + "-" + index}>
                                      <span className="activity-dot"><Icon name="check" /></span>
                                      <span>
                                        {item.event.split("_").join(" ")}
                                        {item.tool ? " · " + item.tool : ""}
                                        {item.detail ? " · " + item.detail : ""}
                                      </span>
                                    </li>
                                  ))}
                                </ol>
                              )}
                            </div>
                          )}

                          {!busy && answer.sources.length === 0 && answer.answer_kind === "INSUFFICIENT_EVIDENCE" && (
                            <div className="insufficient-note"><Icon name="search" /> No included evidence matched this request.</div>
                          )}
                        </div>
                      </div>
                    </article>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            {error && (
              <div className="error-banner" role="alert">
                <div><Icon name="close" /><span>{error}</span></div>
                <button type="button" onClick={() => setError(null)} aria-label="Dismiss error"><Icon name="close" /></button>
              </div>
            )}

            <div className="composer-wrap">
              <div className="composer-hint">
                <span><Icon name="spark" /> Agent mode</span>
                <span>{documents.length} {documentCountLabel} · {conversations.length} {conversationCountLabel}</span>
                <span className="desktop-only">API: {apiUrl}</span>
              </div>
              <form className="composer" onSubmit={sendMessage}>
                <textarea
                  rows={1}
                  maxLength={5000}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  placeholder="Ask AgentForge anything…"
                  aria-label="Message AgentForge"
                  disabled={busy}
                />
                <div className="composer-bottom">
                  <span>{question.length}/5000</span>
                  <div className="composer-actions">
                    {busy && (
                      <button type="button" className="secondary-action" onClick={cancelStream}>
                        <Icon name="close" /> Stop
                      </button>
                    )}
                    <button className="primary-action send-action" disabled={busy || !question.trim()} aria-label="Send message">
                      <span>{busy ? "Working" : "Send"}</span>
                      <Icon name="send" />
                    </button>
                  </div>
                </div>
              </form>
              <p className="composer-disclaimer">AgentForge can make mistakes. Verify important information against your source documents.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function SourceCard({ source }: { source: SourceReference }) {
  return (
    <div className="source-card">
      <div className="source-icon"><Icon name="file" /></div>
      <div className="source-copy">
        <strong title={source.filename}>{source.filename}</strong>
        <span>Chunk {source.chunk_index} · similarity {source.similarity.toFixed(3)}</span>
      </div>
      <span className="source-id">#{shortId(source.chunk_id)}</span>
    </div>
  );
}
