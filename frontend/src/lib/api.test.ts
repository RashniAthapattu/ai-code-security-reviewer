import { afterEach, describe, expect, it, vi } from "vitest";

import { ScanError, scanCode } from "./api";
import type { ScanRequest, ScanResult } from "./types";

const request: ScanRequest = {
  code: "eval(x)",
  language: "javascript",
  explain: false,
};

const result: ScanResult = {
  findings: [],
  errors: [],
  ai_status: "not_requested",
  ai_message: null,
};

function mockFetch(response: Response | Error) {
  const fn = vi.fn(async () => {
    if (response instanceof Error) throw response;
    return response;
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals());

describe("scanCode", () => {
  it("posts the request as JSON and returns the result", async () => {
    const fetchMock = mockFetch(Response.json(result));

    await expect(scanCode(request, "http://api.test")).resolves.toEqual(result);

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  });

  it("explains when the server cannot be reached", async () => {
    mockFetch(new TypeError("Failed to fetch"));

    await expect(scanCode(request, "http://api.test")).rejects.toThrow(
      "Could not reach the server",
    );
  });

  it.each([
    [422, "could not be scanned"],
    [429, "wait a while"],
    [503, "not available"],
    [500, "(500)"],
  ])("gives a friendly message for status %i", async (status, text) => {
    mockFetch(new Response("{}", { status }));

    const promise = scanCode(request, "http://api.test");
    await expect(promise).rejects.toBeInstanceOf(ScanError);
    await expect(promise).rejects.toThrow(text);
  });
});
