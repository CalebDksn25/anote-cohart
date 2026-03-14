import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from api.models.evaluation import EvaluationResponse, SectionMetrics
from api.services.transcript_validator import validate_transcript
from api.services.extractor_service import run_extraction
from src.evaluator import evaluate

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_endpoint(
    transcript: UploadFile = File(...),
    gold: UploadFile = File(...),
    threshold: float = Form(0.75),
):
    transcript_bytes = await transcript.read()
    gold_bytes = await gold.read()

    try:
        transcript_content = transcript_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="Transcript must be UTF-8 encoded text.")

    try:
        gold_data = json.loads(gold_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Gold file must be valid UTF-8 JSON: {exc}")

    validation = validate_transcript(transcript_content)
    if not validation.valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Transcript validation failed.",
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        )

    result = run_extraction(transcript_content)
    scores = evaluate(result.model_dump(), gold_data, text_threshold=threshold)

    def to_metrics(section: dict, has_owner_due: bool) -> SectionMetrics:
        return SectionMetrics(
            precision=section["precision"],
            recall=section["recall"],
            text_threshold=section["text_threshold"],
            owner_accuracy_on_matched=section.get("owner_accuracy_on_matched") if has_owner_due else None,
            due_accuracy_on_matched=section.get("due_accuracy_on_matched") if has_owner_due else None,
        )

    return EvaluationResponse(
        action_items=to_metrics(scores["action_items"], has_owner_due=True),
        decisions=to_metrics(scores["decisions"], has_owner_due=False),
        follow_ups=to_metrics(scores["follow_ups"], has_owner_due=True),
        text_threshold=scores["text_threshold"],
    )
