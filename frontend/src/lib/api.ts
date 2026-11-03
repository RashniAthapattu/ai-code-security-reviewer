import type { ScanRequest, ScanResult } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** An error with a message that is safe to show to the user. */
export class ScanError extends Error {}

/** Send code to the backend and return the scan result. */
export async function scanCode(
  request: ScanRequest,
  baseUrl: string = API_URL,
): Promise<ScanResult> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new ScanError(
      "Could not reach the server. Check that the backend is running.",
    );
  }

  if (!response.ok) {
    throw new ScanError(await errorMessage(response));
  }
  return (await response.json()) as ScanResult;
}

async function errorMessage(response: Response): Promise<string> {
  if (response.status === 422) {
    return "The code could not be scanned. It may be empty or too long.";
  }
  if (response.status === 503) {
    return "The scanner is not available right now. Please try again later.";
  }
  return `The server returned an error (${response.status}).`;
}
