from fastapi import HTTPException
from src.llm_extractor import LLMExtractor
from api.models.extraction import ExtractionResult


def run_extraction(transcript: str) -> ExtractionResult:
    extractor = LLMExtractor()
    try:
        data = extractor.extract(transcript)
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Extraction failed after maximum retries: {exc}",
        )
    except Exception as exc:
        msg = str(exc).lower()
        if "auth" in msg or "api key" in msg or "unauthorized" in msg or "401" in msg:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing OpenAI API key.",
            )
        raise HTTPException(
            status_code=502,
            detail=f"Upstream LLM error: {exc}",
        )

    return ExtractionResult(**data)
