from pydantic import BaseModel


class TranscriptValidationResult(BaseModel):
    valid: bool
    warnings: list[str] = []
    errors: list[str] = []
