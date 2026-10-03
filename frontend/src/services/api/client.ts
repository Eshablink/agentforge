import type { AgentChatResponse, ChatResponse, ConversationSummary, DocumentSummary, SessionResponse, SourceReference, UserIdentity } from "../../types/app";

const FALLBACK_API_BASE_URL = "http://localhost:8000";
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;
const baseUrl = configuredBaseUrl?.trim() || FALLBACK_API_BASE_URL;
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

export const apiClient = {
  baseUrl,
  register(email: string, password: string): Promise<UserIdentity> {
    return request("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  login(email: string, password: string): Promise<SessionResponse> {
    return request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  async logout(): Promise<void> {
    try { await request<void>("/auth/logout", { method: "POST" }); }
    finally { setAccessToken(null); }
  },
  listDocuments(): Promise<DocumentSummary[]> { return request("/documents/me"); },
  async uploadDocument(file: File): Promise<DocumentSummary> {
    const form = new FormData(); form.append("file", file);
    return request("/documents/me", { method: "POST", body: form });
  },
  askQuestion(question: string, topK = 5): Promise<ChatResponse> {
    return request("/me/chat", { method: "POST", body: JSON.stringify({ question, top_k: topK }) });
  },
  agentChat(question: string, conversationId?: string): Promise<AgentChatResponse> {
    return request("/agent/chat", { method: "POST", body: JSON.stringify({ question, conversation_id: conversationId ?? null }) });
  },
  listConversations(): Promise<ConversationSummary[]> { return request("/conversations"); },
  createConversation(title: string): Promise<ConversationSummary> {
    return request("/conversations", { method: "POST", body: JSON.stringify({ title }) });
  },
  getConversation(id: string): Promise<ConversationSummary> { return request(`/conversations/${id}`); },
  sendConversationMessage(id: string, content: string): Promise<ConversationSummary> {
    return request(`/conversations/${id}/messages`, { method: "POST", body: JSON.stringify({ content }) });
  },
  deleteConversation(id: string): Promise<void> { return request(`/conversations/${id}`, { method: "DELETE` }); },
};
