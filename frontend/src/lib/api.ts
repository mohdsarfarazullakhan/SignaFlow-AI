const API_BASE = import.meta.env.VITE_API_URL || "/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("dsai_token");
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = "The request could not be completed.";
    try { const body = await response.json(); message = body.detail || message; } catch { /* friendly fallback */ }
    throw new ApiError(response.status, message);
  }
  return response.json() as Promise<T>;
}

export async function downloadQuotePdf(quoteId: string, reference: string) {
  const token = localStorage.getItem("dsai_token");
  const response = await fetch(`${API_BASE}/quotes/${quoteId}/pdf`, { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!response.ok) throw new Error("Could not generate the quotation PDF.");
  const url = URL.createObjectURL(await response.blob());
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = `${reference}.pdf`; anchor.click(); URL.revokeObjectURL(url);
}

