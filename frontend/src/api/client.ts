import type { ApiErrorBody, IngestPayload, IngestResponse, ItemListResponse, QueryResponse } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(0, "network_error", "Could not reach the server. Is the backend running?");
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await response.json();
    } catch {
      // response had no JSON body; fall through to generic message
    }
    throw new ApiError(
      response.status,
      body?.error?.code ?? "unknown_error",
      body?.error?.message ?? `Request failed with status ${response.status}`
    );
  }

  return response.json() as Promise<T>;
}

export function fetchItems(): Promise<ItemListResponse> {
  return request<ItemListResponse>("/items");
}

export function ingestItem(payload: IngestPayload): Promise<IngestResponse> {
  return request<IngestResponse>("/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function askQuestion(question: string, topK?: number): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK ?? 0 }),
  });
}
