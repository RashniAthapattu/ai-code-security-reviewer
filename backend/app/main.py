from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.explainer import ExplanationError, explain_findings
from app.models import ScanRequest, ScanResult
from app.rate_limit import RateLimiter
from app.scanners import ScannerError, scan_code

app = FastAPI(
    title="AI Code Security Reviewer",
    description="Scans source code for security problems and explains them with AI.",
    version="0.1.0",
)

# Only the listed websites may call the API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().allowed_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Per-visitor limits, to protect a public demo (and its AI bill).
scan_limiter = RateLimiter()
ai_limiter = RateLimiter()


def _visitor(http_request: Request) -> str:
    return http_request.client.host if http_request.client else "unknown"


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness check used by Docker and the deployment platform."""
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResult)
def scan(request: ScanRequest, http_request: Request) -> ScanResult:
    """Scan submitted source code for security problems.

    The code is analysed statically and is never executed.
    """
    visitor = _visitor(http_request)
    if not scan_limiter.allow(visitor, get_settings().rate_limit_per_hour):
        raise HTTPException(
            status_code=429,
            detail="Too many scans. Please try again later.",
            headers={"Retry-After": str(scan_limiter.retry_after(visitor))},
        )

    try:
        result = scan_code(request.code, request.language)
    except ScannerError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if request.explain:
        _add_explanations(request, result, visitor)
    return result


def _add_explanations(request: ScanRequest, result: ScanResult, visitor: str) -> None:
    """Add AI explanations to the findings.

    The scan itself has already succeeded, so a problem with the AI never
    fails the request. It is reported in `ai_status` instead.
    """
    settings = get_settings()
    if not result.findings:
        result.ai_status = "ok"
    elif not settings.ai_enabled:
        result.ai_status = "disabled"
        result.ai_message = "AI explanations are not configured on this server"
    elif len(request.code) > settings.ai_max_code_length:
        result.ai_status = "unavailable"
        result.ai_message = (
            "This code is too long for AI explanations "
            f"(limit {settings.ai_max_code_length:,} characters)"
        )
    elif not ai_limiter.allow(visitor, settings.ai_rate_limit_per_hour):
        result.ai_status = "unavailable"
        result.ai_message = "The AI explanation limit has been reached. Try again later"
    else:
        try:
            explanations = explain_findings(
                request.code, request.language, result.findings, settings
            )
        except ExplanationError as exc:
            result.ai_status = "unavailable"
            result.ai_message = str(exc)
        else:
            for index, explanation in explanations.items():
                result.findings[index].explanation = explanation
            result.ai_status = "ok"
