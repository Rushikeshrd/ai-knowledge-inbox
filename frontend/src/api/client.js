const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(0, "network_error", "Could not reach the server. Is the backend running?");
  }

  if (!response.ok) {
    let body = null;
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

  return response.json();
}

export function fetchItems() {
  return request("/items");
}

export function ingestItem(payload) {
  return request("/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function askQuestion(question, topK) {
  return request("/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK ?? 0 }),
  });
}
