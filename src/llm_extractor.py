import json
from lib.openai_client import OpenAIClient
from lib.prompts import SYSTEM_PROMPT
from src.date_normalizer import normalize_due_raw, parse_meeting_date

class LLMExtractor:
    # Initialize the OpenAI Client
    def __init__(self):
        self.client = OpenAIClient()

    # Method to extract structured information from unstructured text
    def extract(self, transcript: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript}
        ]

        raw = self.client.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        # Parse the raw JSON string returned by the LLM into a Python dictionary. This will allow the extractor to work with the structured data format that the LLM is expected to return based on the system prompt.
        data = json.loads(raw)

        # Parse the meeting date from the transcript to use as a reference for normalizing due dates. This will allow the extractor to convert relative due phrases into absolute dates based on the meeting date.
        meeting_date = parse_meeting_date(transcript)

        # If a meeting date was found, add it to the data dictionary
        if meeting_date:
            # Add the meeting date to the data dictionary so that it can be used for normalizing due dates in the action items and follow-ups. This will allow the extractor to have a reference point for converting relative due phrases into absolute dates.
            for item in data.get("action_items", []):

                # Get the raw due date phrase from the item dictionary, which is expected to be set by the LLM based on the system prompt. This will allow the extractor to have access to the original due date phrase from the transcript for normalization.
                due_raw = item.get("due_raw")
                normalized = normalize_due_raw(meeting_date, due_raw)

                # Set the normalized due date in the item dictionary. This will allow the extractor to have a standardized date format for the due dates, which can be used for further processing or evaluation.
                item["due"] = normalized.due

                # Check if the normalized due date needs human review. If it does, set the needs_human_review flag in the item dictionary and provide a reason if one is not already set. This will allow the extractor to flag any due dates that are ambiguous or cannot be confidently normalized, and provide an explanation for why they need human review.
                if normalized.needs_human_review:
                    item["needs_human_review"] = True
                    if not item.get("reason"):
                        item["reason"] = normalized.reason
            
            # Repeat the same normalization process for the follow-up items in the data dictionary, using the meeting date as a reference for normalizing due dates. This will ensure that all due dates in both action items and follow-ups are normalized consistently based on the meeting date.
            for item in data.get("follow_ups", []):

                # Get the raw due date phrase from the follow-up item dictionary, which is expected to be set by the LLM based on the system prompt. This will allow the extractor to have access to the original due date phrase from the transcript for normalization.
                due_raw = item.get("follow_ups", [])
                normalized = normalize_due_raw(meeting_date, due_raw)

                # Set the normalized due date in the follow-up item dictionary. This will allow the extractor to have a standardized date format for the due dates in follow-ups as well, which can be used for further processing or evaluation.
                item["due"] = normalized.due

        return data