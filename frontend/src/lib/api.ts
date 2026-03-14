import { ExtractionResponse, ValidationErrorDetail } from "@/types/extraction";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ExtractionApiError extends Error {
  statusCode: number;
  detail: ValidationErrorDetail | string;

  constructor(statusCode: number, detail: ValidationErrorDetail | string) {
    const message =
      typeof detail === "string"
        ? detail
        : detail.message ?? "Request failed";
    super(message);
    this.name = "ExtractionApiError";
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

export async function extractTranscript(
  file: File
): Promise<ExtractionResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_URL}/api/extract`, {
    method: "POST",
    body: form,
    // Do NOT set Content-Type — browser sets multipart boundary automatically
  });

  if (!res.ok) {
    let detail: ValidationErrorDetail | string;
    try {
      const json = await res.json();
      detail = json.detail ?? json;
    } catch {
      detail = await res.text();
    }
    throw new ExtractionApiError(res.status, detail);
  }

  return res.json() as Promise<ExtractionResponse>;
}
