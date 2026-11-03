// These types mirror the backend's models (backend/app/models.py).

export type Language = "python" | "javascript" | "typescript";

export type Severity = "low" | "medium" | "high";

export type AIStatus = "not_requested" | "ok" | "disabled" | "unavailable";

export interface Explanation {
  summary: string;
  risk: string;
  fix: string;
  false_positive_likely: boolean;
}

export interface Finding {
  scanner: string;
  rule_id: string;
  title: string;
  message: string;
  severity: Severity;
  confidence: Severity;
  line: number;
  end_line: number;
  snippet: string;
  cwe: number | null;
  more_info: string | null;
  explanation: Explanation | null;
}

export interface ScanResult {
  findings: Finding[];
  errors: string[];
  ai_status: AIStatus;
  ai_message: string | null;
}

export interface ScanRequest {
  code: string;
  language: Language;
  explain: boolean;
}
