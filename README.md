# AI Code Security Reviewer

A web app that scans source code for security problems and uses AI to explain each one in plain language and suggest a fix.

> **Status:** work in progress. This README grows as the project does.

## Planned features

- Scan pasted code with the Bandit and Semgrep security scanners
- AI explanations and suggested fixes for every finding
- Defences against prompt injection: the code you submit is only ever read, never run
- A clean web interface with colour-coded severity and before/after fixes

## Planned tech stack

| Area     | Tools |
|----------|-------|
| Backend  | Python, FastAPI, Bandit, Semgrep |
| AI       | Anthropic Claude API |
| Frontend | Next.js, TypeScript |
| Quality  | pytest, Docker, GitHub Actions |
