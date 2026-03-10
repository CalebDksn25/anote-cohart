#!/usr/bin/env python3
import sys
from src.llm_extractor import LLMExtractor
from src.date_normalizer import parse_meeting_date


def format_output(data: dict) -> str:
    lines = []

    action_items = data.get("action_items", [])
    lines.append("Action Items")
    lines.append("============")
    if action_items:
        for item in action_items:
            owner = f" ({item['owner']})" if item.get("owner") else ""
            due = item.get("due")
            needs_review = item.get("needs_human_review", False)
            if due:
                due_str = f" — due {due}"
            elif needs_review:
                due_str = " — \u26a0 needs review"
            else:
                due_str = ""
            lines.append(f"[ ] {item['text']}{owner}{due_str}")
    else:
        lines.append("(none)")

    lines.append("")
    decisions = data.get("decisions", [])
    lines.append("Decisions")
    lines.append("=========")
    if decisions:
        for item in decisions:
            lines.append(f"- {item['text']}")
    else:
        lines.append("(none)")

    lines.append("")
    follow_ups = data.get("follow_ups", [])
    lines.append("Follow-ups")
    lines.append("==========")
    if follow_ups:
        for item in follow_ups:
            owner = f" ({item['owner']})" if item.get("owner") else ""
            due = item.get("due")
            needs_review = item.get("needs_human_review", False)
            if due:
                due_str = f" — due {due}"
            elif needs_review:
                due_str = " — \u26a0 needs review"
            else:
                due_str = ""
            lines.append(f"- {item['text']}{owner}{due_str}")
    else:
        lines.append("(none)")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <transcript_file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r") as f:
            transcript = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    if not transcript.strip():
        print("Error: transcript file is empty.", file=sys.stderr)
        sys.exit(1)

    if parse_meeting_date(transcript) is None:
        print("Warning: no 'Date:' header found — relative due dates won't be resolved.", file=sys.stderr)

    extractor = LLMExtractor()
    data = extractor.extract(transcript)
    print(format_output(data))


if __name__ == "__main__":
    main()
