from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Upper limit for submitted code, to keep scans fast and cheap
MAX_CODE_LENGTH = 100_000


Language = Literal["python", "javascript", "typescript"]


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ScanRequest(BaseModel):
    code: str = Field(min_length=1, max_length=MAX_CODE_LENGTH)
    language: Language = "python"
    explain: bool = Field(
        default=False, description="Ask the AI to explain each finding and fix it"
    )


class Explanation(BaseModel):
    """An AI-written explanation of one finding."""

    summary: str = Field(description="What the problem is, in plain language")
    risk: str = Field(description="How an attacker could abuse it")
    fix: str = Field(description="Suggested replacement code")
    false_positive_likely: bool = Field(
        description="True if the scanner is probably wrong about this one"
    )


class Finding(BaseModel):
    """One security problem reported by a scanner."""

    scanner: str
    rule_id: str
    title: str
    message: str
    severity: Severity
    confidence: Severity
    line: int
    end_line: int
    snippet: str
    cwe: int | None = Field(default=None, description="CWE number, if known")
    more_info: str | None = None
    explanation: Explanation | None = None


# not_requested: the caller did not ask for explanations
# ok:            explanations were added
# disabled:      the server has no Anthropic API key configured
# unavailable:   the AI service failed, so only scanner results are returned
AIStatus = Literal["not_requested", "ok", "disabled", "unavailable"]


class ScanResult(BaseModel):
    findings: list[Finding] = []
    errors: list[str] = Field(
        default=[], description="Problems that stopped part of the scan"
    )
    ai_status: AIStatus = "not_requested"
    ai_message: str | None = Field(
        default=None, description="Why explanations are missing, if they are"
    )
