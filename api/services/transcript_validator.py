import re
from api.models.validation import TranscriptValidationResult

_SPEAKER_LINE_RE = re.compile(r"^\s*[A-Za-z][A-Za-z\s\-']+:\s+\S", re.MULTILINE)
_DATE_HEADER_RE = re.compile(r"Date:\s*[A-Za-z]{3}\s+\d{1,2},\s+\d{4}")
_MEETING_HEADER_RE = re.compile(r"Meeting:", re.IGNORECASE)


def validate_transcript(content: str) -> TranscriptValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not content or not content.strip():
        errors.append("Transcript is empty.")
        return TranscriptValidationResult(valid=False, errors=errors, warnings=warnings)

    if len(content) > 500_000:
        errors.append("Transcript exceeds maximum length of 500,000 characters.")

    speaker_lines = _SPEAKER_LINE_RE.findall(content)
    if len(speaker_lines) < 2:
        errors.append(
            "Transcript must contain at least 2 speaker lines (format: 'Speaker: text')."
        )

    if errors:
        return TranscriptValidationResult(valid=False, errors=errors, warnings=warnings)

    if not _DATE_HEADER_RE.search(content):
        warnings.append(
            "Missing 'Date: Mon DD, YYYY' header — due-date normalization will be skipped."
        )

    if not _MEETING_HEADER_RE.search(content):
        warnings.append("Missing 'Meeting:' header.")

    word_count = len(content.split())
    if word_count < 50:
        warnings.append(f"Transcript is very short ({word_count} words); results may be limited.")

    return TranscriptValidationResult(valid=True, errors=errors, warnings=warnings)
