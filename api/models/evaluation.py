from pydantic import BaseModel


class SectionMetrics(BaseModel):
    precision: float
    recall: float
    text_threshold: float
    owner_accuracy_on_matched: float | None = None
    due_accuracy_on_matched: float | None = None


class EvaluationResponse(BaseModel):
    action_items: SectionMetrics
    decisions: SectionMetrics
    follow_ups: SectionMetrics
    text_threshold: float
