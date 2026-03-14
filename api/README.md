# anote-cohart — Backend API

FastAPI backend that wraps the existing extraction pipeline and exposes it over HTTP. Run from the **project root** so `src/` and `lib/` stay on the Python path.

## Setup

```bash
# From the project root
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

Set your credentials in `.env`:

```env
OPENAI_API_KEY=sk-...
ALLOWED_ORIGINS=http://localhost:3000
```

## Running the server

```bash
# From the project root
uvicorn api.main:app --reload --port 8000
```

The server validates `OPENAI_API_KEY` at startup and refuses to start if it is missing or malformed.

Interactive docs are available at `http://localhost:8000/docs`.

## Endpoints

### `POST /api/extract`

Extracts action items, decisions, and follow-ups from a plain-text transcript.

**Request** — `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `.txt` file | UTF-8 encoded meeting transcript |

**Response** — `200 OK`

```json
{
  "action_items": [
    {
      "text": "Update onboarding screens and share mocks",
      "owner": "Priya",
      "due_raw": "by Friday",
      "due": "2026-01-23",
      "evidence": "Priya: I'll update the onboarding screens by Friday.",
      "needs_human_review": false,
      "reason": null
    }
  ],
  "decisions": [
    {
      "text": "Assign caching investigation to Jordan",
      "evidence": "Sam: Let's have Jordan look into caching."
    }
  ],
  "follow_ups": [],
  "validation": {
    "valid": true,
    "warnings": [],
    "errors": []
  }
}
```

**Error responses**

| Status | Cause |
|--------|-------|
| `422` | Transcript failed validation (empty, too short, no speaker lines) |
| `401` | Invalid or missing `OPENAI_API_KEY` |
| `502` | LLM extraction failed after maximum retries |

A `422` body looks like:
```json
{
  "detail": {
    "message": "Transcript validation failed.",
    "errors": ["Transcript must contain at least 2 speaker lines."],
    "warnings": []
  }
}
```

---

### `POST /api/evaluate`

Runs extraction and scores the result against a gold JSON file.

**Request** — `multipart/form-data`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `transcript` | `.txt` file | — | UTF-8 encoded meeting transcript |
| `gold` | `.json` file | — | Gold-standard extraction (same schema as response above) |
| `threshold` | `float` | `0.75` | Minimum token-F1 similarity to count as a match |

**Response** — `200 OK`

```json
{
  "action_items": {
    "precision": 1.0,
    "recall": 0.75,
    "text_threshold": 0.75,
    "owner_accuracy_on_matched": 1.0,
    "due_accuracy_on_matched": 0.67
  },
  "decisions": {
    "precision": 1.0,
    "recall": 1.0,
    "text_threshold": 0.75
  },
  "follow_ups": {
    "precision": 1.0,
    "recall": 1.0,
    "text_threshold": 0.75,
    "owner_accuracy_on_matched": 1.0,
    "due_accuracy_on_matched": 1.0
  },
  "text_threshold": 0.75
}
```

## Transcript validation rules

| Check | Result |
|-------|--------|
| Empty content | Hard error — 422 |
| Content > 500,000 chars | Hard error — 422 |
| Fewer than 2 `Speaker: text` lines | Hard error — 422 |
| Missing `Date: Mon DD, YYYY` header | Warning in response (extraction still runs; due dates won't be normalized) |
| Missing `Meeting:` header | Warning in response |
| Fewer than 50 words | Warning in response |

## Layout

```
api/
├── main.py                  App factory, CORS, lifespan startup check
├── exceptions.py            Global handler — always returns JSON
├── routes/
│   ├── extract.py           POST /api/extract
│   └── evaluate.py          POST /api/evaluate
├── models/
│   ├── validation.py        TranscriptValidationResult
│   ├── extraction.py        ActionItem, Decision, FollowUp, ExtractionResponse
│   └── evaluation.py        SectionMetrics, EvaluationResponse
└── services/
    ├── transcript_validator.py  validate_transcript()
    └── extractor_service.py     run_extraction() — thin wrapper over LLMExtractor
```

The `api/` layer is a thin HTTP adapter. It does not modify any existing `src/` or `lib/` code.
