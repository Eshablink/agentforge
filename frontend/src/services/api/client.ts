import type { AppInfo, ChatResponse, DocumentSummary, SourceReference } from "../../types/app";

const FALLBACK_API_BASE_URL = "http://localhost:8000";
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;
const baseUrl = configuredBaseUrl?.trim() || FALLBACK_API_BASE_URL;
let accessToken: string | null = null;

export type AgentEvent = { event: string; tool?: string | null; detail?: string | null };
export type AgentChatResponse = {
  answer: string;
  answer_kind: "DIRECT" | "RAG_GROUNDED" | "TOOL_DERIVED" | "INSUFFICIENT_EVIDENCE";
  sources: SourceReference[];
  tools_used: string[];
  events: AgentEvent[];
  conversation_id: string | null;
};
export type UserIdentity = { id: string; email: string };
export type ConversationSummary = { id: string; title: string; created_at: string; updated_at: string; messages: ConversationMessage[] };
export type ConversationMessage = { id: string; role: string; content: string; created_at: string };
export type SessionResponse = { access_token: string; token_type: string; expires_at: string; user: UserIdentity };

export function setAccessToken(token: string | null) { accessToken = token; }

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(payload?.detail || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return await response.json() as T;
}

export const apiClient = {
  baseUrl,
  async register(email: string, password: string): Promise<UserIdentity> {
    return request("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  async login(email: string, password: string): Promise<SessionResponse> {
    return request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  async logout(): Promise<void> { await request<void>("/auth/logout", { method: "POST" }); setAccessToken(null); },
  async listDocuments(): Promise<DocumentSummary[]> { return request("/documents/me"); },
  async uploadDocument(file: File): Promise<DocumentSummary> {
    const form = new FormData(); form.append("file", file);
    return request("/documents/me", { method: "POST", body: form });
  },
  async askQuestion(question: string, topK = 5): Promise<ChatResponse> {
    return request("/me/chat", { method: "POST", body: JSON.stringify({ question, top_k: topK }) });
  },
  async agentChat(question: string, conversationId?: string): Promise<AgentChatResponse> {
    return request("/agent/chat", { method: "POST", body: JSON.stringify({ question, conversation_id: conversationId ?? null }) });
  },
  async listConversations(): Promise<ConversationSummary[]> { return request("/conversations"); },
  async createConversation(title: string): Promise<ConversationSummary> {
    return request("/conversations", { method: "POST", body: JSON.stringify({ title }) });
  },
  async getConversation(id: string): Promise<ConversationSummary> { return request(`/conversations/${id}`); },
  async sendConversationMessage(id: string, content: string): Promise<ConversationSummary> {
    return request(`/conversations/${id}/messages`, { method: "POST", body: JSON.stringify({ content }) });
  },
  async deleteConversation(id: string): Promise<void> { return request(`/conversations/${id}`, { method: "DELETE" }); },
};
