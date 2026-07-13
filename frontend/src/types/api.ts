export type SourceType = "note" | "url";

export interface ItemSummary {
  id: number;
  source_type: SourceType;
  title: string;
  source_url: string | null;
  preview: string;
  chunk_count: number;
  created_at: string;
}

export interface ItemListResponse {
  items: ItemSummary[];
  count: number;
}

export interface IngestNotePayload {
  source_type: "note";
  text: string;
}

export interface IngestUrlPayload {
  source_type: "url";
  url: string;
}

export type IngestPayload = IngestNotePayload | IngestUrlPayload;

export interface IngestResponse {
  id: number;
  source_type: SourceType;
  title: string;
  chunk_count: number;
  created_at: string;
}

export interface SourceSnippet {
  item_id: number;
  title: string;
  source_type: SourceType;
  source_url: string | null;
  snippet: string;
  similarity: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceSnippet[];
  retrieved_chunk_count: number;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
