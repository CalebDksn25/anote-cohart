import json
import pytest

from src.llm_extractor import LLMExtractor


class StubClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = 0

    def chat_completion(self, messages, response_format):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def test_extract_retries_and_succeeds_after_schema_error():
    valid = {
        "action_items": [],
        "decisions": [],
        "follow_ups": [],
    }
    client = StubClient(
        responses=[
            json.dumps({"action_items": []}),
            json.dumps(valid),
        ]
    )
    extractor = LLMExtractor(client=client, max_attempts=2)

    out = extractor.extract("Meeting transcript without date header")

    assert out == valid
    assert client.calls == 2


def test_extract_raises_after_exhausting_retries():
    client = StubClient(responses=["not-json", "still-not-json"])
    extractor = LLMExtractor(client=client, max_attempts=2)

    with pytest.raises(ValueError, match="failed validation after 2 attempts"):
        extractor.extract("Meeting transcript without date header")

    assert client.calls == 2


def test_extract_rejects_non_null_due_before_normalization():
    invalid_due = {
        "action_items": [
            {
                "text": "Update deck",
                "owner": "Alex",
                "due_raw": "by Friday",
                "due": "2026-01-23",
                "evidence": "Alex: I'll update the deck by Friday.",
                "needs_human_review": False,
                "reason": None,
            }
        ],
        "decisions": [],
        "follow_ups": [],
    }
    client = StubClient(responses=[json.dumps(invalid_due)])
    extractor = LLMExtractor(client=client, max_attempts=1)

    with pytest.raises(ValueError, match="action_items\\[0\\]\\.due"):
        extractor.extract("Meeting transcript without date header")

