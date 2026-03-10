import pytest
from datetime import date
from src.date_normalizer import normalize_due_raw, parse_meeting_date

# ── existing tests ───────────────────────────────────────────────────────────

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

# ── plain weekday (all 7 days) ───────────────────────────────────────────────
# Reference: Jan 22, 2026 is a Thursday (weekday=3)

@pytest.mark.parametrize("phrase,expected", [
    ("Monday", "2026-01-26"),     # next Monday
    ("Tuesday", "2026-01-27"),    # next Tuesday
    ("Wednesday", "2026-01-28"),  # next Wednesday
    ("Thursday", "2026-01-22"),   # same day (next-or-same)
    ("Friday", "2026-01-23"),     # next Friday
    ("Saturday", "2026-01-24"),   # next Saturday
    ("Sunday", "2026-01-25"),     # next Sunday
])
def test_plain_weekday(phrase, expected):
    out = normalize_due_raw(date(2026, 1, 22), phrase)
    assert out.due == expected
    assert out.needs_human_review is False

# ── "next <weekday>" (all 7 days) ────────────────────────────────────────────

@pytest.mark.parametrize("phrase,expected", [
    ("next Monday", "2026-01-26"),
    ("next Tuesday", "2026-01-27"),
    ("next Wednesday", "2026-01-28"),
    ("next Thursday", "2026-01-29"),  # strictly after meeting date
    ("next Friday", "2026-01-23"),
    ("next Saturday", "2026-01-24"),
    ("next Sunday", "2026-01-25"),
])
def test_next_weekday(phrase, expected):
    out = normalize_due_raw(date(2026, 1, 22), phrase)
    assert out.due == expected
    assert out.needs_human_review is False

# ── empty / None due_raw ─────────────────────────────────────────────────────

def test_none_due_raw():
    out = normalize_due_raw(date(2026, 1, 22), None)
    assert out.due is None
    assert out.needs_human_review is False

def test_empty_string_due_raw():
    out = normalize_due_raw(date(2026, 1, 22), "")
    assert out.due is None
    assert out.needs_human_review is False

# ── parse_meeting_date ───────────────────────────────────────────────────────

def test_parse_meeting_date_valid():
    transcript = "Meeting: Weekly Sync\nDate: Jan 22, 2026\nAttendees: Alice"
    d = parse_meeting_date(transcript)
    assert d == date(2026, 1, 22)

def test_parse_meeting_date_missing_header():
    transcript = "Meeting: Weekly Sync\nAttendees: Alice"
    assert parse_meeting_date(transcript) is None

def test_parse_meeting_date_invalid_month():
    transcript = "Date: Xyz 22, 2026"
    assert parse_meeting_date(transcript) is None