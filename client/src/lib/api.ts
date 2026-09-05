export type AnalyzeInput =
  | { inputType: "text" | "url" | "camera"; content: string; source?: "manual" | "interceptor" }
  | { inputType: "image"; file: File; source?: "manual" | "interceptor" };

export type ApiAnalysis = {
  score: number;
  severity: "safe" | "suspicious" | "high";
  label: string;
  summary: string;
  action: string;
  action_detail: string;
  source: string;
  entity: string;
  threats: { title: string; detail: string; severity: "safe" | "suspicious" | "high" }[];
  timestamp: string;
  trace_id: string;
  plain_english: string;
  upi_details?: {
    upi_id?: string | null;
    display_name?: string | null;
    phone_number?: string | null;
    amount?: string | null;
    currency?: string | null;
    note?: string | null;
    merchant_code?: string | null;
    confidence?: "low" | "medium" | "high";
  } | null;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export async function analyzeWithBackend(input: AnalyzeInput): Promise<ApiAnalysis> {
  const body = input.inputType === "image"
    ? (() => { const form = new FormData(); form.append("input_type", "image"); form.append("source", input.source || "manual"); form.append("file", input.file); return form; })()
    : JSON.stringify({ input_type: input.inputType, content: input.content, source: input.source || "manual" });
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, { method: "POST", headers: input.inputType === "image" ? undefined : { "Content-Type": "application/json" }, body });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail || `Analysis failed (${response.status})`);
  return response.json() as Promise<ApiAnalysis>;
}
