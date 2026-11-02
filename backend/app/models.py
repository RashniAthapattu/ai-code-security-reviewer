from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Upper limit for submitted code, to keep scans fast and cheap
MAX_CODE_LENGTH = 100_000


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ScanRequest(BaseModel):
    code: str = Field(min_length=1, max_length=MAX_CODE_LENGTH)
    language: Literal["python"] = "python"


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


class ScanResult(BaseModel):
    findings: list[Finding] = []
    errors: list[str] = Field(
        default=[], description="Problems that stopped part of the scan"
    )
