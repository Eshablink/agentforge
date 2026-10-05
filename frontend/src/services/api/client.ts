import type { AgentChatResponse, ChatResponse, ConversationSummary, DocumentSummary, SessionResponse, StreamEventData, StreamEventName, StreamHandler, UserIdentity } from "../../types/app";

// Explicit Vite URL for cross-origin deployments; otherwise proxy API paths
// through the same origin. Never ship a localhost URL in a production bundle.
const configuredBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();
if (configuredBaseUrl && !/^https?:\/\/[^/]+(?:\/[^?#]*)?$/.test(configuredBaseUrl)) {
  throw new Error("VITE_API_BASE_URL must be an absolute HTTP(S) URL");
}
if (import.meta.env.PROD && configuredBaseUrl?.startsWith("http://")) {
  throw new Error("Production API must use HTTPS or a same-origin reverse proxy");
}
const baseUrl = (configuredBaseUrl || "").replace(/\/$/, "");
let accessToken: string | null = null;

export function setAccessToken(token: string | null) { accessToken = token; }

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    if (response.status === 401 && path !== "/auth/login" && path !== "/auth/register") setAccessToken(null);
    throw new Error(payload?.detail || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return await response.json() as T;
}

async function streamAgentChat(question: string, conversationId: string | undefined, onEvent: StreamHandler, signal?: AbortSignal): Promise<void> {
  if (!accessToken) throw new Error("Authentication required");
  const response = await fetch(`${baseUrl}/agent/chat/stream`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ question, conversation_id: conversationId ?? null }), signal,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    if (response.status === 401) setAccessToken(null);
    throw new Error(payload?.detail || `Stream failed with status ${response.status}`);
  }
  if (!response.body) throw new Error("Streaming response body is unavailable");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let boundary: number;
      while ((boundary = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        let eventName = "message";
        let dataText = "";
        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          else if (line.startsWith("data:")) dataText += line.slice(5).trim();
        }
        if (!dataText) continue;
        try { onEvent(eventName as StreamEventName, JSON.parse(dataText) as StreamEventData); }
        catch { onEvent("error", { message: "Invalid streaming event received", code: "invalid_event" }); }
      }
    }
  } finally { reader.releaseLock(); }
}

export const apiClient = {
  baseUrl,
  register(email: string, password: string): Promise<UserIdentity> { return request<UserIdentity>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }); },
  login(email: string, password: string): Promise<SessionResponse> { return request<SessionResponse>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }); },
  async logout(): Promise<void> { try { await request<void>("/auth/logout", { method: "POST" }); } finally { setAccessToken(null); } },
  listDocuments(): Promise<DocumentSummary[]> { return request<DocumentSummary[]>("/documents/me"); },
  async uploadDocument(file: File): Promise<DocumentSummary> { const form = new FormData(); form.append("file", file); return request<DocumentSummary>("/documents/me", { method: "POST", body: form }); },
  askQuestion(question: string, topK = 5): Promise<ChatResponse> { return request<ChatResponse>("/me/chat", { method: "POST", body: JSON.stringify({ question, top_k: topK }) }); },
  agentChat(question: string, conversationId?: string): Promise<AgentChatResponse> { return request<AgentChatResponse>("/agent/chat", { method: "POST", body: JSON.stringify({ question, conversation_id: conversationId ?? null }) }); },
  streamAgentChat,
  listConversations(): Promise<ConversationSummary[]> { return request<ConversationSummary[]>("/conversations"); },
  createConversation(title: string): Promise<ConversationSummary> { return request<ConversationSummary>("/conversations", { method: "POST", body: JSON.stringify({ title }) }); },
  getConversation(id: string): Promise<ConversationSummary> { return request<ConversationSummary>(`/conversations/${id}`); },
  sendConversationMessage(id: string, content: string): Promise<ConversationSummary> { return request<ConversationSummary>(`/conversations/${id}/messages`, { method: "POST", body: JSON.stringify({ content }) }); },
  deleteConversation(id: string): Promise<void> { return request<void>(`/conversations/${id}`, { method: "DELETE" }); },
};
