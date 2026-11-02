from app.models import Language, ScanResult
from app.scanners.bandit_scanner import ScannerError, scan_python
from app.scanners.semgrep_scanner import scan_with_semgrep

__all__ = ["ScannerError", "scan_code"]


def scan_code(code: str, language: Language) -> ScanResult:
    """Send the code to the right scanner for its language.

    Python goes to Bandit. JavaScript and TypeScript go to Semgrep.
    Findings come back in the order they appear in the code.
    """
    if language == "python":
        result = scan_python(code)
    else:
        result = scan_with_semgrep(code, language)

    result.findings.sort(key=lambda finding: (finding.line, finding.rule_id))
    return result
