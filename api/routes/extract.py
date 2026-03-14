from fastapi import APIRouter, HTTPException, UploadFile, File
from api.models.extraction import ExtractionResponse
from api.services.transcript_validator import validate_transcript
from api.services.extractor_service import run_extraction

router = APIRouter()


@router.post("/extract", response_model=ExtractionResponse)
async def extract(file: UploadFile = File(...)):
    raw_bytes = await file.read()
    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File must be UTF-8 encoded text.")

    validation = validate_transcript(content)

    if not validation.valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Transcript validation failed.",
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        )

    result = run_extraction(content)
    return ExtractionResponse(**result.model_dump(), validation=validation)
