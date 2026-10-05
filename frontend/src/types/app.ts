export type AppInfo = { name: string; description: string };
export type DocumentSummary = { id: string; filename: string; content_type: string; status: string; chunk_count: number; created_at: string };
export type SourceReference = { document_id: string; filename: string; chunk_id: string; chunk_index: number; similarity: number };
export type ChatResponse = { answer: string; sources: SourceReference[]; retrieved_chunks: number };
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
export type SessionResponse = { access_token: string; token_type: string; expires_at: string; user: UserIdentity };
export type ConversationMessage = { id: string; role: string; content: string; created_at: string };
export type ConversationSummary = { id: string; title: string; created_at: string; updated_at: string; messages: ConversationMessage[] };

export type StreamEventName =
  | "message_start"
  | "tool_start"
  | "tool_result"
  | "retrieval"
  | "token"
  | "message_end"
  | "error";

export type StreamEventData = {
  request_id?: string;
  conversation_id?: string | null;
  text?: string;
  tool?: string;
  status?: "success" | "error";
  count?: number;
  answer_kind?: AgentChatResponse["answer_kind"];
  tools_used?: string[];
  sources?: SourceReference[];
  message?: string;
  code?: string;
};

export type StreamHandler = (event: StreamEventName, data: StreamEventData) => void;
