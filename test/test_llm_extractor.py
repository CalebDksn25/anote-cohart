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


def test_extract_integration_normalizes_dates():
    """
    Feed the sample transcript through a stubbed client and verify that
    date normalization runs for both action_items and follow_ups.
    """
    import os

    transcript_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_transcript_1.txt"
    )
    with open(transcript_path) as f:
        transcript = f.read()

    # Stub LLM response matching the sample transcript content
    # Jan 22, 2026 (Thursday): "by Friday" -> 2026-01-23, "by next Wednesday" -> 2026-01-28
    # "early next week" is ambiguous, "by Monday" -> 2026-01-26
    stub_response = {
        "action_items": [
            {
                "text": "Update the onboarding screens and share mocks",
                "owner": "Priya",
                "due_raw": "by Friday",
                "due": None,
                "evidence": "Priya: I'll update the onboarding screens and share mocks by Friday.",
                "needs_human_review": False,
                "reason": None,
            },
            {
                "text": "Investigate caching strategies and give a recommendation",
                "owner": "Jordan",
                "due_raw": "by next Wednesday",
                "due": None,
                "evidence": "Alex: Jordan, can you look into caching strategies and give us a recommendation by next Wednesday?",
                "needs_human_review": False,
                "reason": None,
            },
            {
                "text": "Finish the customer feedback summary",
                "owner": "Priya",
                "due_raw": "by Monday",
                "due": None,
                "evidence": "Priya: Yes, I'll send it out by Monday.",
                "needs_human_review": False,
                "reason": None,
            },
        ],
        "decisions": [
            {
                "text": "Park looping in design for the new dashboard for now",
                "evidence": "Alex: Agreed. Let's park that for now.",
            }
        ],
        "follow_ups": [
            {
                "text": "Schedule a follow-up meeting once the onboarding mocks are ready",
                "owner": "Sam",
                "due_raw": "early next week",
                "due": None,
                "evidence": "Sam: I can set that up after Priya shares the mocks.",
            }
        ],
    }

    client = StubClient(responses=[json.dumps(stub_response)])
    extractor = LLMExtractor(client=client, max_attempts=1)
    out = extractor.extract(transcript)

    # Action item due dates should be ISO strings, not None
    assert out["action_items"][0]["due"] == "2026-01-23"
    assert out["action_items"][1]["due"] == "2026-01-28"
    assert out["action_items"][2]["due"] == "2026-01-26"

    # Follow-up with ambiguous phrase should have needs_human_review set
    fu = out["follow_ups"][0]
    assert fu["due"] is None
    assert fu.get("needs_human_review") is True
    assert fu.get("reason") is not None

