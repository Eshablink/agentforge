import type { ChatResponse, DocumentSummary } from "../../types/app";

const FALLBACK_API_BASE_URL = "http://localhost:8000";

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;

const baseUrl = configuredBaseUrl?.trim() || FALLBACK_API_BASE_URL;

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    const message = payload?.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export const apiClient = {
  baseUrl,

  async listDocuments(): Promise<DocumentSummary[]> {
    const response = await fetch(`${baseUrl}/documents`);
    return parseJsonResponse<DocumentSummary[]>(response);
  },

  async uploadDocument(file: File): Promise<DocumentSummary> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${baseUrl}/documents`, {
      method: "POST",
      body: formData,
    });
    return parseJsonResponse<DocumentSummary>(response);
  },

  async askQuestion(question: string, topK = 5): Promise<ChatResponse> {
    const response = await fetch(`${baseUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK }),
    });
    return parseJsonResponse<ChatResponse>(response);
  },
};
