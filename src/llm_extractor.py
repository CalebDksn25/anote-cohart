import json
from lib.openai_client import OpenAIClient
from lib.prompts import SYSTEM_PROMPT
from src.date_normalizer import normalize_due_raw, parse_meeting_date

class LLMExtractor:
    # Initialize the OpenAI Client
    def __init__(self, client: OpenAIClient | None = None, max_attempts: int = 3):
        self.client = client or OpenAIClient()
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        self.max_attempts = max_attempts

    @staticmethod
    def _validate_required_keys(data: dict, required: set[str], obj_name: str) -> None:
        keys = set(data.keys())
        if keys != required:
            missing = sorted(required - keys)
            extra = sorted(keys - required)
            detail = []
            if missing:
                detail.append(f"missing keys: {missing}")
            if extra:
                detail.append(f"unexpected keys: {extra}")
            raise ValueError(f"{obj_name} has invalid keys ({'; '.join(detail)}).")

    @staticmethod
    def _validate_string(value, field_name: str, allow_null: bool = False) -> None:
        if value is None and allow_null:
            return
        if not isinstance(value, str):
            null_msg = " or null" if allow_null else ""
            raise ValueError(f"Field '{field_name}' must be a string{null_msg}.")

    def _validate_schema(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise ValueError("Top-level response must be a JSON object.")

        self._validate_required_keys(
            data,
            {"action_items", "decisions", "follow_ups"},
            "Top-level object",
        )

        for array_name in ("action_items", "decisions", "follow_ups"):
            if not isinstance(data.get(array_name), list):
                raise ValueError(f"Field '{array_name}' must be an array.")

        for idx, item in enumerate(data["action_items"]):
            if not isinstance(item, dict):
                raise ValueError(f"action_items[{idx}] must be an object.")
            self._validate_required_keys(
                item,
                {"text", "owner", "due_raw", "due", "evidence", "needs_human_review", "reason"},
                f"action_items[{idx}]",
            )
            self._validate_string(item["text"], f"action_items[{idx}].text")
            self._validate_string(item["owner"], f"action_items[{idx}].owner", allow_null=True)
            self._validate_string(item["due_raw"], f"action_items[{idx}].due_raw", allow_null=True)
            if item["due"] is not None:
                raise ValueError(f"Field 'action_items[{idx}].due' must be null before normalization.")
            self._validate_string(item["evidence"], f"action_items[{idx}].evidence")
            if not isinstance(item["needs_human_review"], bool):
                raise ValueError(f"Field 'action_items[{idx}].needs_human_review' must be a boolean.")
            self._validate_string(item["reason"], f"action_items[{idx}].reason", allow_null=True)

        for idx, item in enumerate(data["decisions"]):
            if not isinstance(item, dict):
                raise ValueError(f"decisions[{idx}] must be an object.")
            self._validate_required_keys(item, {"text", "evidence"}, f"decisions[{idx}]")
            self._validate_string(item["text"], f"decisions[{idx}].text")
            self._validate_string(item["evidence"], f"decisions[{idx}].evidence")

        for idx, item in enumerate(data["follow_ups"]):
            if not isinstance(item, dict):
                raise ValueError(f"follow_ups[{idx}] must be an object.")
            self._validate_required_keys(
                item,
                {"text", "owner", "due_raw", "due", "evidence"},
                f"follow_ups[{idx}]",
            )
            self._validate_string(item["text"], f"follow_ups[{idx}].text")
            self._validate_string(item["owner"], f"follow_ups[{idx}].owner", allow_null=True)
            self._validate_string(item["due_raw"], f"follow_ups[{idx}].due_raw", allow_null=True)
            if item["due"] is not None:
                raise ValueError(f"Field 'follow_ups[{idx}].due' must be null before normalization.")
            self._validate_string(item["evidence"], f"follow_ups[{idx}].evidence")

    # Method to extract structured information from unstructured text
    def extract(self, transcript: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript}
        ]
        last_error = None

        for _ in range(self.max_attempts):
            raw = self.client.chat_completion(
                messages=messages,
                response_format={"type": "json_object"}
            )
            try:
                data = json.loads(raw)
                self._validate_schema(data)
                break
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                last_error = exc
                messages.extend(
                    [
                        {"role": "assistant", "content": str(raw)},
                        {
                            "role": "user",
                            "content": (
                                "Your previous response was invalid. "
                                f"{exc} "
                                "Return only valid JSON that exactly matches the required schema."
                            ),
                        },
                    ]
                )
        else:
            raise ValueError(
                f"Model output failed validation after {self.max_attempts} attempts: {last_error}"
            )

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
                due_raw = item.get("due_raw")
                normalized = normalize_due_raw(meeting_date, due_raw)

                # Set the normalized due date in the follow-up item dictionary. This will allow the extractor to have a standardized date format for the due dates in follow-ups as well, which can be used for further processing or evaluation.
                item["due"] = normalized.due

                if normalized.needs_human_review:
                    item["needs_human_review"] = True
                    if not item.get("reason"):
                        item["reason"] = normalized.reason

        return data
