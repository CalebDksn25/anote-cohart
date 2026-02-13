import json
from lib.openai_client import OpenAIClient
from lib.prompts import SYSTEM_PROMPT

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

        return json.loads(raw)