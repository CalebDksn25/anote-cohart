SCHEMA = {
    "action_items": [
        {
            "text": "string",
            "owner": "string or null",
            "due": "ISO date string (YYYY-MM-DD) or null",
            "evidence": "string",
            "needs_human_review": "boolean",
            "reason": "string or null"
        }
    ],
    "decisions": [
        {
            "text": "string",
            "evidence": "string"
        }
    ],
    "follow_ups": [
        {
            "text": "string",
            "owner": "string or null",
            "due": "ISO date string (YYYY-MM-DD) or null",
            "evidence": "string"
        }
    ]
}