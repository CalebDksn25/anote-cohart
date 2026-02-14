from datetime import date
from src.date_normalizer import normalize_due_raw

def test_by_friday_from_jan_22_2026():
    # Jan 22, 2026 is a Thursday; Friday is Jan 23, 2026
    out = normalize_due_raw(date(2026, 1, 22), "by Friday")
    assert out.due == "2026-01-23"
    assert out.needs_human_review is False

def test_next_wednesday_from_jan_22_2026():
    # Next Wednesday after Jan 22, 2026 is Jan 28, 2026
    out = normalize_due_raw(date(2026, 1, 22), "by next Wednesday")
    assert out.due == "2026-01-28"
    assert out.needs_human_review is False

def test_by_monday_from_jan_22_2026():
    # Next Monday after Jan 22, 2026 is Jan 26, 2026
    out = normalize_due_raw(date(2026, 1, 22), "by Monday")
    assert out.due == "2026-01-26"
    assert out.needs_human_review is False

def test_early_next_week_is_ambiguous():
    out = normalize_due_raw(date(2026, 1, 22), "early next week")
    assert out.due is None
    assert out.needs_human_review is True