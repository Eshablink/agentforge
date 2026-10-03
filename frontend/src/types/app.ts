export type AppInfo = {
  name: string;
  description: string;
};

export type DocumentSummary = {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
};

export type SourceReference = {
  document_id: string;
  filename: string;
  chunk_id: string;
  chunk_index: number;
  similarity: number;
};

export type ChatResponse = {
  answer: string;
  sources: SourceReference[];
  retrieved_chunks: number;
};
