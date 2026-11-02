from fastapi import FastAPI

app = FastAPI(
    title="AI Code Security Reviewer",
    description="Scans source code for security problems and explains them with AI.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness check used by Docker and the deployment platform."""
    return {"status": "ok"}
