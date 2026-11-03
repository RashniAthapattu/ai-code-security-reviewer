from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.explainer import ExplanationError, explain_findings
from app.models import ScanRequest, ScanResult
from app.scanners import ScannerError, scan_code

app = FastAPI(
    title="AI Code Security Reviewer",
    description="Scans source code for security problems and explains them with AI.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness check used by Docker and the deployment platform."""
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResult)
def scan(request: ScanRequest) -> ScanResult:
    """Scan submitted source code for security problems.

    The code is analysed statically and is never executed.
    """
    try:
        result = scan_code(request.code, request.language)
    except ScannerError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if request.explain:
        _add_explanations(request, result)
    return result


def _add_explanations(request: ScanRequest, result: ScanResult) -> None:
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
