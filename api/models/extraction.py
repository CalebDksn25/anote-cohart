from pydantic import BaseModel
from api.models.validation import TranscriptValidationResult


class ActionItem(BaseModel):
    text: str
    owner: str | None
    due_raw: str | None
    due: str | None
    evidence: str
    needs_human_review: bool
    reason: str | None


class Decision(BaseModel):
    text: str
    evidence: str


class FollowUp(BaseModel):
    text: str
    owner: str | None
    due_raw: str | None
    due: str | None
    evidence: str
    needs_human_review: bool | None = None
    reason: str | None = None


class ExtractionResult(BaseModel):
    action_items: list[ActionItem] = []
    decisions: list[Decision] = []
    follow_ups: list[FollowUp] = []


class ExtractionResponse(ExtractionResult):
    validation: TranscriptValidationResult
