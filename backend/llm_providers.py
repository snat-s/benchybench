import os
from openai import OpenAI
import anthropic

class LLMProviderInterface:
    """
    A common interface for LLM calls.
    """
    def get_response(self, model: str, prompt: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")


class OpenAIProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def get_response(self, model: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()


class AnthropicProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def get_response(self, model: str, prompt: str) -> str:
        # According to Anthropic docs, this is one way to call the API.
        response = self.client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

def create_llm_provider(model: str) -> LLMProviderInterface:
    """
    Factory function for creating an LLM provider instance.
    If any substring in the openai_substrings list is found in the model name (case-insensitive),
    returns an instance of OpenAIProvider.
    If any substring in the anthropic_substrings list is found, returns an instance of AnthropicProvider.
    Otherwise, raises a ValueError.
    """
    model_lower = model.lower()
    openai_substrings = ["gpt-", "o1-", "o3-"]         # Add more OpenAI identifying substrings to this list if needed.
    anthropic_substrings = ["claude"]     # Add more Anthropic identifying substrings to this list if needed.

    if any(substr in model_lower for substr in openai_substrings):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        return OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    elif any(substr in model_lower for substr in anthropic_substrings):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")
        return AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        raise ValueError(f"Unsupported model: {model}")