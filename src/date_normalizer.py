from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# Monday=0 ... Sunday=6
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

@dataclass(frozen=True)
class NormalizedDue:
    due: Optional[str]                # ISO "YYYY-MM-DD" or None
    needs_human_review: bool          # whether this due date needs human check
    reason: Optional[str] = None      # why it needs review (if True)

def parse_meeting_date(transcript: str) -> Optional[date]:
    """
    Looks for the header like: Date: Jan 22, 2026
    """

    # Use a regular expression to search for a date in the format "Date: Mon DD, YYYY" within the transcript. The regex captures the month abbreviation, day, and year as separate groups.
    m = re.search(r"Date:\s*([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})", transcript)
    
    # If the regex search does not find a match, it returns None. Otherwise, it extracts the month abbreviation, day, and year from the matched groups. It checks if the month abbreviation is valid (i.e., exists in the MONTHS dictionary). If it's not valid, it returns None. If everything is valid, it constructs and returns a date object using the extracted year, month (converted from abbreviation to number), and day.
    if not m:
        return None
    mon, day, year = m.group(1), m.group(2), m.group(3)

    # Check if the extracted month abbreviation is valid by looking it up in the MONTHS dictionary. If the month abbreviation is not found in the dictionary, return None to indicate that the date could not be parsed.
    if mon not in MONTHS:
        return None
    
    return date(int(year), MONTHS[mon], int(day))

def _next_or_same_weekday(d: date, target_weekday: int) -> date:
    """
    Returns the next date that falls on target_weekday, including today if it matches.
    """
    delta = (target_weekday - d.weekday()) % 7
    return d + timedelta(days=delta)


def _next_weekday_strictly_after(d: date, target_weekday: int) -> date:
    """
    Returns the next date that falls on target_weekday strictly AFTER d.
    """
    delta = (target_weekday - d.weekday()) % 7
    if delta == 0:
        delta = 7
    return d + timedelta(days=delta)


def normalize_due_raw(
    meeting_date: date,
    due_raw: Optional[str],
) -> NormalizedDue:
    """
    Convert a relative due phrase like:
      - "by Friday"
      - "by next Wednesday"
      - "next Wednesday"
      - "Monday"
    into an ISO date string using meeting_date as reference.

    Ambiguous phrases -> due=None and needs_human_review=True
    """
    if not due_raw:
        return NormalizedDue(due=None, needs_human_review=False)

    s = due_raw.strip().lower()

    # Mark ambiguous phrases for review (expand this list over time)
    ambiguous_markers = [
        "early next week",
        "later this week",
        "sometime next week",
        "next week",
        "soon",
        "asap",
        "end of week",
        "eow",
    ]
    if any(marker in s for marker in ambiguous_markers):
        return NormalizedDue(
            due=None,
            needs_human_review=True,
            reason=f"Ambiguous due phrase: '{due_raw}'"
        )

    # Remove leading "by" / "on" / "before" for parsing
    s = re.sub(r"^(by|on|before)\s+", "", s).strip()

    # Handle "next <weekday>" explicitly (strictly after meeting date)
    m_next = re.match(r"^next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", s)
    if m_next:
        wd = WEEKDAYS[m_next.group(1)]
        dt = _next_weekday_strictly_after(meeting_date, wd)
        return NormalizedDue(due=dt.isoformat(), needs_human_review=False)

    # Handle plain weekday (interpret as next-or-same occurrence after meeting date)
    m_wd = re.match(r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", s)
    if m_wd:
        wd = WEEKDAYS[m_wd.group(1)]
        dt = _next_or_same_weekday(meeting_date, wd)
        return NormalizedDue(due=dt.isoformat(), needs_human_review=False)

    # If we got here, we couldn't parse it confidently
    return NormalizedDue(
        due=None,
        needs_human_review=True,
        reason=f"Unrecognized due phrase: '{due_raw}'"
    )