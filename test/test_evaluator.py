import pytest
from src.evaluator import evaluate, best_text_match


def _action(text, owner=None, due=None):
    return {"text": text, "owner": owner, "due": due}


def _decision(text):
    return {"text": text}


def _follow_up(text, owner=None, due=None):
    return {"text": text, "owner": owner, "due": due}


# ── best_text_match ──────────────────────────────────────────────────────────

def test_best_text_match_returns_highest_scorer():
    gold = [_action("fix the login bug"), _action("update the dashboard")]
    idx, score = best_text_match("fix the login bug", gold, set())
    assert idx == 0
    assert score == pytest.approx(1.0)


def test_best_text_match_skips_used_indices():
    gold = [_action("fix the login bug"), _action("update the dashboard")]
    idx, score = best_text_match("fix the login bug", gold, used_gold_idxs={0})
    assert idx == 1  # index 0 is excluded; best remaining is index 1


def test_best_text_match_all_used_returns_none():
    gold = [_action("fix the login bug")]
    idx, score = best_text_match("fix the login bug", gold, used_gold_idxs={0})
    assert idx is None
    assert score == 0.0


# ── evaluate – action items ──────────────────────────────────────────────────

def test_evaluate_perfect_match():
    item = _action("Fix the login bug", owner="Alice", due="2026-01-30")
    pred = {"action_items": [item], "decisions": [], "follow_ups": []}
    gold = {"action_items": [item], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    ai = result["action_items"]
    assert ai["precision"] == pytest.approx(1.0)
    assert ai["recall"] == pytest.approx(1.0)
    assert ai["owner_accuracy_on_matched"] == pytest.approx(1.0)
    assert ai["due_accuracy_on_matched"] == pytest.approx(1.0)
    assert len(ai["matched"]) == 1
    assert len(ai["hallucinations"]) == 0
    assert len(ai["missed"]) == 0


def test_evaluate_hallucination_only():
    pred = {"action_items": [_action("Invent something new")], "decisions": [], "follow_ups": []}
    gold = {"action_items": [], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    ai = result["action_items"]
    assert ai["precision"] == pytest.approx(0.0)
    assert ai["recall"] == pytest.approx(0.0)
    assert len(ai["hallucinations"]) == 1
    assert len(ai["missed"]) == 0


def test_evaluate_missed_only():
    pred = {"action_items": [], "decisions": [], "follow_ups": []}
    gold = {"action_items": [_action("Fix the login bug")], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    ai = result["action_items"]
    assert ai["precision"] == pytest.approx(0.0)
    assert ai["recall"] == pytest.approx(0.0)
    assert len(ai["hallucinations"]) == 0
    assert len(ai["missed"]) == 1


def test_evaluate_empty_pred_and_gold():
    pred = {"action_items": [], "decisions": [], "follow_ups": []}
    gold = {"action_items": [], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    ai = result["action_items"]
    assert ai["precision"] == pytest.approx(0.0)
    assert ai["recall"] == pytest.approx(0.0)
    assert len(ai["matched"]) == 0


# ── evaluate – decisions ─────────────────────────────────────────────────────

def test_evaluate_decisions_perfect_match():
    d = _decision("We will adopt the new framework")
    pred = {"action_items": [], "decisions": [d], "follow_ups": []}
    gold = {"action_items": [], "decisions": [d], "follow_ups": []}
    result = evaluate(pred, gold)
    dec = result["decisions"]
    assert dec["precision"] == pytest.approx(1.0)
    assert dec["recall"] == pytest.approx(1.0)
    assert "owner_accuracy_on_matched" not in dec


def test_evaluate_decisions_hallucination():
    pred = {"action_items": [], "decisions": [_decision("totally wrong decision")], "follow_ups": []}
    gold = {"action_items": [], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    dec = result["decisions"]
    assert dec["precision"] == pytest.approx(0.0)
    assert len(dec["hallucinations"]) == 1


# ── evaluate – follow-ups ────────────────────────────────────────────────────

def test_evaluate_follow_ups_perfect_match():
    fu = _follow_up("Schedule sync meeting", owner="Sam", due="2026-01-30")
    pred = {"action_items": [], "decisions": [], "follow_ups": [fu]}
    gold = {"action_items": [], "decisions": [], "follow_ups": [fu]}
    result = evaluate(pred, gold)
    fup = result["follow_ups"]
    assert fup["precision"] == pytest.approx(1.0)
    assert fup["recall"] == pytest.approx(1.0)
    assert fup["owner_accuracy_on_matched"] == pytest.approx(1.0)
    assert fup["due_accuracy_on_matched"] == pytest.approx(1.0)


def test_evaluate_follow_ups_missed():
    pred = {"action_items": [], "decisions": [], "follow_ups": []}
    gold = {"action_items": [], "decisions": [], "follow_ups": [_follow_up("Send report")]}
    result = evaluate(pred, gold)
    fup = result["follow_ups"]
    assert fup["recall"] == pytest.approx(0.0)
    assert len(fup["missed"]) == 1


# ── evaluate – result structure ──────────────────────────────────────────────

def test_evaluate_result_has_all_sections():
    pred = {"action_items": [], "decisions": [], "follow_ups": []}
    gold = {"action_items": [], "decisions": [], "follow_ups": []}
    result = evaluate(pred, gold)
    assert "action_items" in result
    assert "decisions" in result
    assert "follow_ups" in result
    assert result["text_threshold"] == pytest.approx(0.75)
