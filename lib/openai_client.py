from openai import OpenAI
import os

class OpenAIClient:

    # Initialize the OpenAI client with the provided API key
    def __init__(self, api_key: str | None = None):
        # Use the provided API key or fall back to the environment variable
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Ensure that api key was provided
        if not api_key:
            raise ValueError("API key must be provided either as an argument or in the environment variable 'OPENAI_API_KEY'.")

        self.client = OpenAI(api_key=api_key)

    # Method to create a chat completion using the OpenAI client
    def chat_completion(self, 
                        messages: list[dict], 
                        model: str = "gpt-4o-mini", 
                        temperature: float = 0.7, 
                        response_format: dict | None = None
        ):
        
        # Generate a chat completion using the OpenAI client with the specified parameters
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            response_format=response_format,
        )

        # Return the content of the first message in the response choices
        return response.choices[0].message.content

