from fastapi import FastAPI, HTTPException

from app.models import ScanRequest, ScanResult
from app.scanners.bandit_scanner import ScannerError, scan_python

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
        return scan_python(request.code)
    except ScannerError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
