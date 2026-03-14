import json

import pytest

from src.eval_runner import format_evaluation_report, run_evaluation


class StubExtractor:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def extract(self, transcript):
        self.calls += 1
        return self.response


def test_run_evaluation_adds_overall_metrics(tmp_path):
    transcript_path = tmp_path / "meeting.txt"
    gold_path = tmp_path / "meeting.gold.json"

    transcript_path.write_text("Meeting: Test\nDate: Jan 22, 2026\nAlex: Fix the login bug by Friday.")
    gold = {
        "action_items": [{"text": "Fix the login bug", "owner": "Alex", "due": "2026-01-23"}],
        "decisions": [{"text": "Use the new auth flow"}],
        "follow_ups": [{"text": "Schedule a status check", "owner": "Sam", "due": "2026-01-30"}],
    }
    pred = {
        "action_items": [{"text": "Fix the login bug", "owner": "Alex", "due": "2026-01-23"}],
        "decisions": [{"text": "Use the new auth flow"}],
        "follow_ups": [],
    }
    gold_path.write_text(json.dumps(gold))

    extractor = StubExtractor(pred)
    result = run_evaluation(str(transcript_path), str(gold_path), extractor=extractor)

    assert extractor.calls == 1
    assert result["overall"]["matched"] == 2
    assert result["overall"]["hallucinations"] == 0
    assert result["overall"]["missed"] == 1
    assert result["overall"]["precision"] == pytest.approx(1.0)
    assert result["overall"]["recall"] == pytest.approx(2 / 3)


def test_run_evaluation_rejects_empty_transcript(tmp_path):
    transcript_path = tmp_path / "meeting.txt"
    gold_path = tmp_path / "meeting.gold.json"

    transcript_path.write_text("   ")
    gold_path.write_text(json.dumps({"action_items": [], "decisions": [], "follow_ups": []}))

    with pytest.raises(ValueError, match="Transcript file is empty"):
        run_evaluation(str(transcript_path), str(gold_path), extractor=StubExtractor({}))


def test_format_evaluation_report_includes_sections():
    result = {
        "transcript_path": "data/sample_transcript_1.txt",
        "gold_path": "data/sample_transcript.gold.json",
        "text_threshold": 0.75,
        "overall": {
            "precision": 0.8,
            "recall": 0.67,
            "matched": 4,
            "hallucinations": 1,
            "missed": 2,
        },
        "action_items": {
            "precision": 1.0,
            "recall": 1.0,
            "matched": [{}],
            "hallucinations": [],
            "missed": [],
            "owner_accuracy_on_matched": 1.0,
            "due_accuracy_on_matched": 1.0,
        },
        "decisions": {
            "precision": 0.5,
            "recall": 1.0,
            "matched": [{}],
            "hallucinations": [{}],
            "missed": [],
        },
        "follow_ups": {
            "precision": 0.0,
            "recall": 0.0,
            "matched": [],
            "hallucinations": [],
            "missed": [{}],
            "owner_accuracy_on_matched": 0.0,
            "due_accuracy_on_matched": 0.0,
        },
    }

    report = format_evaluation_report(result)

    assert "Evaluation Report" in report
    assert "Overall" in report
    assert "Action Items" in report
    assert "Decisions" in report
    assert "Follow Ups" in report
    assert "owner accuracy on matched: 1.00" in report
